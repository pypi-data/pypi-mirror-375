from typing import List
import numpy as np
from .config import settings
import logging
import httpx
import logfire
from functools import lru_cache
import hashlib
import json

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
model = None
device = None


def init_embedding_model():
    import torch
    from sentence_transformers import SentenceTransformer
    
    global model, device
    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")

    if settings.embedding.use_modelscope:
        from modelscope import snapshot_download
        model_dir = snapshot_download(settings.embedding.model)
        logger.info(f"Model downloaded from ModelScope to: {model_dir}")
    else:
        model_dir = settings.embedding.model
        logger.info(f"Using model: {model_dir}")

    model = SentenceTransformer(model_dir, trust_remote_code=True)
    model.to(device)
    logger.info(f"Embedding model initialized on device: {device}")


def generate_embeddings(texts: List[str]) -> List[List[float]]:
    global model

    if model is None:
        init_embedding_model()

    if not texts:
        return []

    embeddings = model.encode(texts, convert_to_tensor=True, show_progress_bar=False)
    embeddings = embeddings.cpu().numpy()

    # Normalize embeddings
    norms = np.linalg.norm(embeddings, ord=2, axis=1, keepdims=True)
    norms[norms == 0] = 1
    embeddings = embeddings / norms

    return embeddings.tolist()


def _hash_texts(texts: List[str]) -> str:
    """Generate a stable hash for a list of texts."""
    texts_json = json.dumps(texts, sort_keys=True)
    return hashlib.sha256(texts_json.encode()).hexdigest()


@logfire.instrument
@lru_cache(maxsize=100)  # Cache last 100 requests
def get_embeddings_cached(texts_hash: str, texts_tuple: tuple) -> List[List[float]]:
    """Internal cached function that works with immutable types."""
    texts = list(texts_tuple)
    if settings.embedding.use_local:
        embeddings = generate_embeddings(texts)
    else:
        embeddings = get_remote_embeddings(texts)

    # Round the embedding values to 5 decimal places
    return [
        [round(float(x), 5) for x in embedding]
        for embedding in embeddings
    ]


@logfire.instrument
def get_embeddings(texts: List[str]) -> List[List[float]]:
    """Get embeddings with caching support."""
    # Convert texts to immutable type and create a hash
    texts_hash = _hash_texts(texts)
    texts_tuple = tuple(texts)
    return get_embeddings_cached(texts_hash, texts_tuple)


def get_remote_embeddings(texts: List[str]) -> List[List[float]]:
    headers = {
        "Content-Type": "application/json"
    }
    
    if settings.embedding.token.get_secret_value():
        headers["Authorization"] = f"Bearer {settings.embedding.token.get_secret_value()}"

    endpoint = settings.embedding.endpoint
    is_ollama = endpoint.endswith("/embed")

    if is_ollama:
        payload = {"model": settings.embedding.model, "input": texts}
    else:  # openai compatible api
        payload = {
            "input": texts,
            "model": settings.embedding.model,
            "encoding_format": "float"
        }

    with httpx.Client(timeout=60) as client:
        try:
            response = client.post(endpoint, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()

            if is_ollama:
                return result["embeddings"]
            else:  # openai compatible api
                return [item["embedding"] for item in result["data"]]
        except httpx.RequestError as e:
            logger.error(f"Error fetching embeddings from remote endpoint: {e}")
            return []  # Return an empty list instead of raising an exception
