from PIL import Image
import numpy as np
import logging
from fastapi import FastAPI, Body, HTTPException
from fastapi import Depends, status
from fastapi import Request
from fastapi.security import APIKeyHeader
from contextlib import asynccontextmanager
import base64
import io
import asyncio
from pydantic import BaseModel, Field
from typing import List
from multiprocessing import Pool
import threading
import time
import uvicorn
import os


# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
    )
logger = logging.getLogger(__name__)

# 创建进程池
process_pool = None

# 从环境变量中读取参数
max_workers = int(os.getenv("MAX_WORKERS", 1))


def str_to_bool(value):
    return value.lower() in ("true", "1", "t", "y", "yes")


use_gpu = str_to_bool(os.getenv("USE_GPU", "false"))


@asynccontextmanager
async def lifespan(app):
    global process_pool
    if process_pool is None:
        init_process_pool(max_workers=max_workers, use_gpu=use_gpu)
    yield
    if process_pool:
        logger.info("Shutting down process pool...")
        process_pool.close()
        process_pool.join()
        logger.info("Process pool shut down.")


app = FastAPI(lifespan=lifespan)


def init_worker(use_gpu):
    global ocr
    ocr = init_ocr(use_gpu)


def init_process_pool(max_workers, use_gpu):
    global process_pool
    process_pool = Pool(
        processes=max_workers, initializer=init_worker, initargs=(use_gpu,)
    )


def init_ocr(use_gpu):
    if use_gpu:
        try:
            from rapidocr_paddle import RapidOCR as RapidOCRPaddle

            ocr = RapidOCRPaddle(
                det_use_cuda=True, cls_use_cuda=True, rec_use_cuda=True
            )
            logger.info("Initialized OCR with RapidOCR Paddle (GPU)")
        except ImportError:
            logger.error(
                "Failed to import rapidocr_paddle. Make sure it's installed for GPU usage."
            )
            raise
    else:
        try:
            from rapidocr_onnxruntime import RapidOCR

            ocr = RapidOCR()
            logger.info("Initialized OCR with RapidOCR ONNX Runtime (CPU)")
        except ImportError:
            logger.error(
                "Failed to import rapidocr_onnxruntime. Make sure it's installed for CPU usage."
            )
            raise
    return ocr


def convert_ocr_results(results):
    if results is None:
        return []

    converted = []
    for result in results:
        item = {"dt_boxes": result[0], "rec_txt": result[1], "score": result[2]}
        converted.append(item)
    return converted


def predict(image_data):
    global ocr
    if ocr is None:
        raise ValueError("OCR engine not initialized")

    image = Image.open(io.BytesIO(image_data))
    img_array = np.array(image)
    results, _ = ocr(img_array)
    converted_results = convert_ocr_results(results)
    return converted_results


def convert_to_python_type(item):
    if isinstance(item, np.ndarray):
        return item.tolist()
    elif isinstance(item, np.generic):  # This includes numpy scalars like numpy.float32
        return item.item()
    elif isinstance(item, list):
        return [convert_to_python_type(sub_item) for sub_item in item]
    elif isinstance(item, dict):
        return {key: convert_to_python_type(value) for key, value in item.items()}
    else:
        return item


async def async_predict(image_data):
    loop = asyncio.get_running_loop()
    results = await loop.run_in_executor(
        None, process_pool.apply, predict, (image_data,)
    )
    return results


class OCRResult(BaseModel):
    dt_boxes: List[List[float]] = Field(..., description="Bounding box coordinates")
    rec_txt: str = Field(..., description="Recognized text")
    score: float = Field(..., description="Confidence score")

# ----------- 安全配置 -----------
API_TOKEN = os.getenv("API_TOKEN")
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

async def verify_token(api_key: str = Depends(api_key_header)):
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization Header",
        )
    # 安全比较防止时序攻击
    token = api_key.replace("Bearer ", "", 1).strip()
    if not secrets.compare_digest(token, API_TOKEN):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token",
        )
    return True

@app.post("/predict", response_model=List[OCRResult])
async def predict_base64(
    _auth: bool = Depends(verify_token),
    image_base64: str = Body(..., embed=True)
    ):
    try:
        if not image_base64:
            raise HTTPException(status_code=400, detail="Missing image_base64 field")

        # Remove header part if present
        if image_base64.startswith("data:image"):
            image_base64 = image_base64.split(",")[1]

        # Decode the base64 image
        image_data = base64.b64decode(image_base64)

        # 直接传递图像数据给async_predict
        ocr_result = await async_predict(image_data)

        return convert_to_python_type(ocr_result)

    except Exception as e:
        logging.error(f"Error during OCR processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


shutdown_event = threading.Event()


def signal_handler(signum, frame):
    logger.info("Received interrupt signal. Initiating shutdown...")
    shutdown_event.set()


def run_server(app, host, port):
    config = uvicorn.Config(app, host=host, port=port, loop="asyncio")
    server = uvicorn.Server(config)
    server.install_signal_handlers = (
        lambda: None
    )  # Disable Uvicorn's own signal handlers

    async def serve():
        await server.serve()

    thread = threading.Thread(target=asyncio.run, args=(serve(),))
    thread.start()

    try:
        while not shutdown_event.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Initiating shutdown...")
    finally:
        shutdown_event.set()
        logger.info("Stopping the server...")
        asyncio.run(server.shutdown())
        thread.join()
        logger.info("Server stopped.")


if __name__ == "__main__":
    import uvicorn
    import argparse

    parser = argparse.ArgumentParser(description="OCR Service")
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run the OCR service on",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=1,
        help="Maximum number of worker threads for OCR processing",
    )
    parser.add_argument(
        "--gpu",
        action="store_true",
        help="Use GPU for OCR processing",
    )

    args = parser.parse_args()
    port = args.port
    max_workers = args.max_workers
    use_gpu = args.gpu

    run_server(app, "0.0.0.0", port)

