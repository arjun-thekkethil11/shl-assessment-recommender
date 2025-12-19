import os
import logging
from typing import List

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .recommender import AssessmentRecommender
from .config import CATALOG_PATH, MAX_K

# ----- logging -----
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("shl_recommender_api")

# ----- FastAPI app -----
app = FastAPI(title="SHL Assessment Recommendation API")

# ----- CORS config via env var (comma-separated origins) -----
# Example:
#   ALLOWED_ORIGINS="https://your-site.netlify.app,http://localhost:5173"
allowed = os.environ.get("ALLOWED_ORIGINS", "*")
if allowed.strip() == "*" or allowed.strip() == "":
    allow_origins = ["*"]
else:
    # split on commas and strip whitespace
    allow_origins = [o.strip() for o in allowed.split(",") if o.strip()]

logger.info("CORS allow_origins=%s", allow_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- recommender (initialized at startup) -----
recommender = None


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


# ----- startup handler -----
@app.on_event("startup")
def startup():
    global recommender
    try:
        logger.info("Initializing AssessmentRecommender (catalog=%s, max_k=%s)", CATALOG_PATH, MAX_K)
        recommender = AssessmentRecommender(catalog_path=CATALOG_PATH, max_k=MAX_K)
        logger.info("Recommender initialized: %d items", len(recommender.catalog_df))
    except Exception as e:
        logger.exception("Failed to initialize recommender: %s", e)
        # Re-raise so the process fails to start (Render/Proc manager will show logs)
        raise


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest, request: Request):
    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="query must be a non-empty string")

    try:
        # default k=10 (still limited by recommender.max_k internally)
        recs = recommender.recommend(req.query, k=10)
        assessments = [Assessment(**r) for r in recs]
        return RecommendResponse(recommended_assessments=assessments)
    except Exception as e:
        logger.exception("Error while generating recommendations for query=%r: %s", req.query, e)
        # Surface a clear error to the client
        raise HTTPException(status_code=500, detail="Internal error generating recommendations")
