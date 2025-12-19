import os
import sys

# ✨ Force Python to see the project root so "app" becomes importable
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

import pandas as pd
from app.recommender import AssessmentRecommender

TRAIN_XLSX = "data/Gen_AI Dataset.xlsx"


def load_train_queries():
    xls = pd.ExcelFile(TRAIN_XLSX)
    df = pd.read_excel(xls, "Train-Set")

    grouped = df.groupby("Query")["Assessment_url"].apply(list).to_dict()
    return grouped


def main():
    train_queries = load_train_queries()
    rec = AssessmentRecommender()

    recalls = []
    for query, relevant_urls in train_queries.items():
        recs = rec.recommend(query, k=10)
        pred_urls = [r["url"] for r in recs]

        relevant = set(relevant_urls)
        hits = len(set(pred_urls) & relevant)
        recall = hits / len(relevant) if len(relevant) > 0 else 0
        recalls.append(recall)

    mean = sum(recalls) / len(recalls)
    print(f"Mean Recall@10 on Train-Set: {mean:.3f}")


if __name__ == "__main__":
    main()
