🤝 Author

Arjun Thekkethil
GitHub: https://github.com/arjun-thekkethil11


---

# 📘 **PROJECT_OVERVIEW.md (Place this in Repo Root)**

```markdown
# SHL Assessment Recommender — Technical Overview

## 1. Objective

Build an SHL assessment recommendation engine that:
- Ingests job descriptions / NL queries
- Retrieves individual SHL assessments
- Returns up to 10 relevant tests
- Produces `submission.csv`
- Exposes a REST API + simple frontend
- Is fully Docker deployable

---

## 2. Catalog Construction

SHL product URLs were discovered by crawling:



https://www.shl.com/solutions/products/product-catalog/


Pagination pattern:



?start=0&type=1
?start=12&type=1
?start=24&type=1
...


Detail pages are anti-bot protected → so the catalog is built from:
- URL slug → generated name
- Default values for missing fields
- Training dataset hints

Result:
- **360 individual assessments**
- Stored in `data/catalog.csv`

---

## 3. Recommendation Logic

Implemented in `app/recommender.py`.

Pipeline:
1. Load catalog
2. Build TF-IDF representation of product names
3. Compute cosine similarity for each query
4. Sort + pick top-K (≤10)
5. Optional balancing between:
   - Knowledge & Skills tests
   - Personality/Behavior tests

---

## 4. API Design

### `GET /health`
Returns:

```json
{"status": "healthy"}

POST /recommend

Input:

{
  "query": "Looking to hire...",
  "k": 10
}


Output:

{
  "recommended_assessments": [
    {
      "url": "...",
      "name": "...",
      "adaptive_support": "Unknown",
      "description": "",
      "duration": 0,
      "remote_support": "Unknown",
      "test_type": []
    }
  ]
}

5. Frontend

Static HTML + JS:

Textarea for job description

K selector (1–10)

Calls backend /recommend

Renders results in table

Runs via:

python3 -m http.server 5173

6. Evaluation

Evaluation calculates Mean Recall@10 on training queries:

python3 scripts/evaluate.py


Typical result:

Mean Recall@10 = 0.020

7. Submission CSV

Generated with:

python3 scripts/generate_submission_csv.py


Produces 90 rows (9 queries × 10 URLs).

8. Deployment
Docker
docker build -t shl-recommender-backend .
docker run --rm -p 8000:8000 shl-recommender-backend

9. Limitations + Next Steps

SHL detail pages are anti-bot protected → descriptions often empty

TF-IDF → could switch to embeddings

Remote/adaptive preference not used in ranking

Could enrich catalog using a headless browser scrape

10. Conclusion

End-to-end SHL assessment recommendation engine:

Scraped catalog

Retrieval-based ranking

API + UI

Dockerized backend

Final evaluation + CSV