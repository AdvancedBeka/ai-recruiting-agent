"""
Lightweight embedding store with optional on-disk persistence.

Used to cache resume/job embeddings to avoid repeated encoding.
"""
from __future__ import annotations

import logging
import pickle
from pathlib import Path
from typing import Dict, Optional

import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingStore:
    """
    Minimal embedding cache.

    - In-memory dict for fast lookup
    - Optional disk persistence (pickle)
    - Thread-safety not handled here (assume single worker or wrap externally)
    """

    def __init__(self, cache_path: Optional[Path | str] = None):
        self.cache: Dict[str, np.ndarray] = {}
        self.cache_path = Path(cache_path) if cache_path else None
        if self.cache_path:
            self._load()

    def get(self, key: str) -> Optional[np.ndarray]:
        return self.cache.get(key)

    def set(self, key: str, embedding: np.ndarray):
        self.cache[key] = embedding

    def get_or_compute(self, key: str, text: str, encoder) -> np.ndarray:
        """
        Get embedding from cache or compute with encoder.encode([text]).
        """
        if key in self.cache:
            return self.cache[key]
        emb = encoder.encode([text])[0]
        self.cache[key] = emb
        return emb

    def save(self):
        if not self.cache_path:
            return
        try:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_path, "wb") as f:
                pickle.dump(self.cache, f)
            logger.info(f"Saved embeddings cache to {self.cache_path}")
        except Exception as exc:
            logger.error(f"Failed to save embeddings cache: {exc}")

    def _load(self):
        if not self.cache_path or not self.cache_path.exists():
            return
        try:
            with open(self.cache_path, "rb") as f:
                self.cache = pickle.load(f)
            logger.info(f"Loaded embeddings cache from {self.cache_path}")
        except Exception as exc:
            logger.error(f"Failed to load embeddings cache: {exc}")
