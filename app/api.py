from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .recommender import AssessmentRecommender
from .config import CATALOG_PATH, MAX_K

app = FastAPI(title="SHL Assessment Recommendation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

recommender = AssessmentRecommender(catalog_path=CATALOG_PATH, max_k=MAX_K)



class RecommendRequest(BaseModel):
    query: str


class Assessment(BaseModel):
    url: str
    name: str
    adaptive_support: str
    description: str
    duration: int
    remote_support: str
    test_type: List[str]


class RecommendResponse(BaseModel):
    recommended_assessments: List[Assessment]


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest):
    recs = recommender.recommend(req.query, k=10)
    assessments = [Assessment(**r) for r in recs]
    return RecommendResponse(recommended_assessments=assessments)
