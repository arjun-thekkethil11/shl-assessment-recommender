# app/recommender.py
from __future__ import annotations

from typing import List, Dict

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .config import USE_EMBEDDINGS, EMBEDDING_MODEL_NAME, CATALOG_PATH, MAX_K
from .query_analysis import analyze_query_with_llm


class AssessmentRecommender:
    def __init__(self, catalog_path: str = CATALOG_PATH, max_k: int = MAX_K):
        self.catalog_path = catalog_path
        self.max_k = max_k

        self.catalog_df = pd.read_csv(self.catalog_path)

        required_cols = [
            "url",
            "name",
            "description",
            "duration",
            "test_type",
            "remote_support",
            "adaptive_support",
        ]
        for col in required_cols:
            if col not in self.catalog_df.columns:
                raise ValueError(f"Missing column {col} in catalog.csv")

        self.catalog_df.fillna(
            {
                "name": "",
                "description": "",
                "test_type": "",
                "remote_support": "Unknown",
                "adaptive_support": "Unknown",
            },
            inplace=True,
        )

        # test_type_list kept for compatibility (may be empty in current catalog)
        self.catalog_df["test_type_list"] = self.catalog_df["test_type"].apply(
            lambda s: [x.strip() for x in str(s).split(";") if x.strip()]
        )

        # 🔑 Retrieval text: use clean product names only
        self.catalog_df["text"] = self.catalog_df["name"].fillna("").astype(str)

        self.use_embeddings = USE_EMBEDDINGS
        self._init_index()

    def _init_index(self):
        if self.use_embeddings:
            from sentence_transformers import SentenceTransformer

            self.embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)
            self.doc_matrix = self.embedder.encode(
                self.catalog_df["text"].tolist(), show_progress_bar=False
            )
        else:
            self.vectorizer = TfidfVectorizer(
                ngram_range=(1, 2),
                stop_words="english",
                min_df=1,
            )
            self.doc_matrix = self.vectorizer.fit_transform(self.catalog_df["text"])

    def _score(self, query: str) -> np.ndarray:
        if self.use_embeddings:
            q_vec = self.embedder.encode([query])[0]
            doc_mat = self.doc_matrix
            q_norm = q_vec / (np.linalg.norm(q_vec) + 1e-8)
            d_norm = doc_mat / (np.linalg.norm(doc_mat, axis=1, keepdims=True) + 1e-8)
            sims = d_norm @ q_norm
            return sims
        else:
            q_vec = self.vectorizer.transform([query])
            sims = cosine_similarity(q_vec, self.doc_matrix)[0]
            return sims

    def _search_indices(self, query: str, top_k: int) -> List[int]:
        sims = self._score(query)
        idxs = np.argsort(sims)[::-1]  

        
        filtered = [i for i in idxs if sims[i] > 0]

        if not filtered:
            
            return list(idxs[: top_k * 3])

        return filtered[: top_k * 3]

    def _build_result(self, idx: int) -> Dict:
        row = self.catalog_df.iloc[idx]
        return {
            "url": row["url"],
            "name": row["name"],
            "adaptive_support": str(row["adaptive_support"]),
            "description": row["description"],
            "duration": int(row["duration"]) if not pd.isna(row["duration"]) else 0,
            "remote_support": str(row["remote_support"]),
            "test_type": row["test_type_list"],
        }

    def recommend(self, query: str, k: int = 10) -> List[Dict]:
        k = min(k, self.max_k)
        profile = analyze_query_with_llm(query)

        idxs = self._search_indices(query, top_k=k)

        # If no special balancing needed, just take top-k
        if not (profile.has_technical and profile.has_behavioral):
            return [self._build_result(i) for i in idxs[:k]]

        # Mixed query: try to balance Knowledge & Skills vs Personality & Behavior
        knowledge_idxs = []
        personality_idxs = []
        for i in idxs:
            ttypes = set(self.catalog_df.iloc[i]["test_type_list"])
            is_k = any("Knowledge" in t or "Skill" in t for t in ttypes)
            is_p = any("Personality" in t or "Behavior" in t for t in ttypes)

            if is_k and not is_p:
                knowledge_idxs.append(i)
            elif is_p and not is_k:
                personality_idxs.append(i)
            else:
               
                pass

        results = []
        i_k = 0
        i_p = 0
        target_k = k // 2
        target_p = k - target_k

        # alternate picking
        while len(results) < k and (i_k < len(knowledge_idxs) or i_p < len(personality_idxs)):
            if len(results) < k and i_k < len(knowledge_idxs) and len(
                [r for r in results if "Knowledge" in " ".join(r["test_type"])]
            ) < target_k:
                results.append(self._build_result(knowledge_idxs[i_k]))
                i_k += 1

            if len(results) < k and i_p < len(personality_idxs) and len(
                [r for r in results if "Personality" in " ".join(r["test_type"])]
            ) < target_p:
                results.append(self._build_result(personality_idxs[i_p]))
                i_p += 1

            if i_k >= len(knowledge_idxs) and i_p >= len(personality_idxs):
                break

        # If still fewer than k, fill from overall top list
        if len(results) < k:
            used = {r["url"] for r in results}
            for i in idxs:
                if self.catalog_df.iloc[i]["url"] in used:
                    continue
                results.append(self._build_result(i))
                if len(results) >= k:
                    break

        return results
