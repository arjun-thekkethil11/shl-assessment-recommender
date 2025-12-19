# scripts/generate_submission_csv.py
import os
import sys
import csv

import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.recommender import AssessmentRecommender  # noqa: E402

DATASET_XLSX = "data/Gen_AI Dataset.xlsx"
TEST_SHEET_NAME = "Test-Set"
OUT_PATH = "submission.csv"


MAX_URLS_PER_QUERY = 10


def load_test_queries(xlsx_path: str):
    """
    Load ONLY the Test-Set queries from the Excel file.
    """
    if not os.path.exists(xlsx_path):
        raise FileNotFoundError(f"{xlsx_path} not found")

    xls = pd.ExcelFile(xlsx_path)

    if TEST_SHEET_NAME not in xls.sheet_names:
        raise ValueError(
            f"Expected sheet '{TEST_SHEET_NAME}' not found in {xlsx_path}. "
            f"Sheets present: {xls.sheet_names}"
        )

    df = xls.parse(TEST_SHEET_NAME)

    if "Query" not in df.columns:
        raise ValueError(f"No 'Query' column found on sheet '{TEST_SHEET_NAME}'.")

    # Drop completely empty queries
    df = df[df["Query"].notna()]

    # Normalize to single-line strings (remove embedded newlines)
    df["Query"] = df["Query"].astype(str).apply(
        lambda s: " ".join(s.splitlines()).strip()
    )
    df = df[df["Query"] != ""]

    return df["Query"].tolist()


def ensure_top_k_urls(recommender: AssessmentRecommender, query: str, k: int) -> list[str]:
    """
    Ask the recommender for k URLs, and if it returns fewer,
    fill the gap with generic fallback recommendations so we
    always end up with exactly k URLs (or fewer if catalog is tiny).
    """
    recs = recommender.recommend(query, k=k)
    urls = [r["url"] for r in recs if r.get("url")]

    if len(urls) >= k:
        return urls[:k]

    # Fallback: use a generic query to get more URLs
    fallback_recs = recommender.recommend("general assessment for hiring", k=k)
    for r in fallback_recs:
        url = r.get("url")
        if not url:
            continue
        if url not in urls:
            urls.append(url)
        if len(urls) >= k:
            break

    return urls[:k]


def main():
    recommender = AssessmentRecommender()
    queries = load_test_queries(DATASET_XLSX)

    total_rows = 0
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Query", "Assessment_url"])

        for q in queries:
            urls = ensure_top_k_urls(recommender, q, MAX_URLS_PER_QUERY)

            if not urls:
                
                writer.writerow([q, ""])
                total_rows += 1
                continue

            for url in urls:
                writer.writerow([q, url])
                total_rows += 1

    print(f"Wrote {total_rows} rows to {OUT_PATH}")


if __name__ == "__main__":
    main()
