"""
FAISS index helper for storing and querying resume embeddings.
Uses Inner Product (cosine-ready if embeddings are normalized).
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import numpy as np

try:
    import faiss

    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

logger = logging.getLogger(__name__)


class FaissIndex:
    """
    Lightweight FAISS index wrapper (Flat IP).
    Stores mapping from FAISS ids to resume ids for retrieval.
    """

    def __init__(self, dim: int, index_path: Path | str = Path("./data/cache/faiss.index")):
        if not FAISS_AVAILABLE:
            raise RuntimeError("faiss is not available. Install faiss-cpu to use FaissIndex.")

        self.dim = dim
        self.index_path = Path(index_path)
        self.id_map: Dict[int, str] = {}

        if self.index_path.exists():
            self._load()
        else:
            self.index = faiss.IndexFlatIP(dim)

    def add_embeddings(self, embeddings: np.ndarray, resume_ids: List[str]):
        """
        Add embeddings with their resume_ids.
        """
        if embeddings.shape[0] != len(resume_ids):
            raise ValueError("embeddings and resume_ids length mismatch")

        start_id = len(self.id_map)
        ids = np.arange(start_id, start_id + embeddings.shape[0])

        # Normalize for cosine-ready IP
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings)
        for faiss_id, resume_id in zip(ids, resume_ids):
            self.id_map[int(faiss_id)] = resume_id

    def search(self, query_embeddings: np.ndarray, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Search top-k resume_ids with scores.
        """
        if self.index.ntotal == 0:
            return []
        faiss.normalize_L2(query_embeddings)
        scores, idxs = self.index.search(query_embeddings, top_k)
        results: List[Tuple[str, float]] = []
        for score, idx in zip(scores[0], idxs[0]):
            if int(idx) in self.id_map:
                results.append((self.id_map[int(idx)], float(score)))
        return results

    def save(self):
        try:
            self.index_path.parent.mkdir(parents=True, exist_ok=True)
            faiss.write_index(self.index, str(self.index_path))
            # Save mapping
            map_path = self.index_path.with_suffix(".map")
            with open(map_path, "w", encoding="utf-8") as f:
                for k, v in self.id_map.items():
                    f.write(f"{k}\t{v}\n")
            logger.info(f"Saved FAISS index to {self.index_path}")
        except Exception as exc:
            logger.error(f"Failed to save FAISS index: {exc}")

    def _load(self):
        try:
            self.index = faiss.read_index(str(self.index_path))
            map_path = self.index_path.with_suffix(".map")
            if map_path.exists():
                with open(map_path, "r", encoding="utf-8") as f:
                    for line in f:
                        k, v = line.strip().split("\t", 1)
                        self.id_map[int(k)] = v
            logger.info(f"Loaded FAISS index from {self.index_path} with {len(self.id_map)} entries")
        except Exception as exc:
            logger.error(f"Failed to load FAISS index: {exc}")
            self.index = faiss.IndexFlatIP(self.dim)
            self.id_map = {}

