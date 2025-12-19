# SHL Assessment Recommendation Engine

This project implements a complete **Assessment Recommendation Engine** based on the SHL product catalogue and the provided **Gen_AI Dataset.xlsx**.  
The engine ingests job descriptions or natural-language hiring queries and returns up to **10 SHL individual test assessments**.

The system includes:
- A production-ready **FastAPI backend**
- A clean, modern **frontend UI (HTML + JS)**
- A robust catalog-building pipeline
- A **Dockerized** backend
- Evaluation scripts (Mean Recall@10)
- Final submission CSV

---

## 🚀 Quickstart

### 1. Clone the repository

```bash
git clone https://github.com/arjun-thekkethil11/shl-assessment-recommender.git
cd shl-assessment-recommender

⚙️ Backend (Local)
2. Create virtualenv
python3 -m venv venv
source venv/bin/activate

3. Install dependencies
pip install -r requirements.txt

4. Run FastAPI backend
uvicorn app.api:app --reload --host 0.0.0.0 --port 8000


Test:

curl http://localhost:8000/health

5. Test /recommend
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"query": "Looking to hire a Python + SQL developer"}'

🐳 Backend (Docker Deployment)
Build the image
docker build -t shl-recommender-backend .

Run container
docker run --rm -p 8000:8000 shl-recommender-backend

🌐 Frontend
Run static server
cd frontend
python3 -m http.server 5173


Open:

http://localhost:5173

📊 Evaluation

Compute Mean Recall@10:

python3 scripts/evaluate.py

📄 Submission CSV

Generate final file:

python3 scripts/generate_submission_csv.py


This writes:

submission.csv


Format:

Query,Assessment_url
<q1>,<url1>
<q1>,<url2>
...

🧠 Catalog

The final catalog (data/catalog.csv) contains 360 individual assessment URLs, all discovered automatically by crawling SHL and then validated.

A helper script regenerates it:

python3 scripts/rebuild_catalog_from_urls.py

🖥 Project Structure
app/                # backend logic
scripts/            # evaluations + scraper + catalog build
data/               # catalog + SHL dataset
frontend/           # UI
Dockerfile          # backend container
submission.csv      # final evaluation output
requirements.txt
README.md
PROJECT_OVERVIEW.md

✔ Requirements Satisfaction

The solution satisfies every SHL requirement:

Scraped SHL individual assessments (~360 URLs)

Recommender returns 5–10 items

API returns all required fields

Frontend functional

Dockerized backend

Mean Recall@10 evaluation

Submission CSV in correct format

2-page final report included (PROJECT_OVERVIEW.md)

