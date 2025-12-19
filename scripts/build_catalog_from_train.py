import os
import pandas as pd
from urllib.parse import urlparse

DATASET_XLSX = "data/Gen_AI Dataset.xlsx"
OUT_PATH = "data/catalog.csv"


def slug_to_name(url: str) -> str:
    try:
        path = urlparse(url).path.rstrip("/")
        slug = path.split("/")[-1]
        parts = slug.replace("-", " ").split()
        return " ".join(p.capitalize() for p in parts)
    except Exception:
        return url


def main():
    if not os.path.exists(DATASET_XLSX):
        raise FileNotFoundError(f"{DATASET_XLSX} not found.")

    xls = pd.ExcelFile(DATASET_XLSX)
    df_train = pd.read_excel(xls, "Train-Set")

    urls = sorted(set(df_train["Assessment_url"].dropna().astype(str)))

    rows = []
    for u in urls:
        rows.append(
            {
                "url": u,
                "name": slug_to_name(u),
                "description": "",
                "duration": 0,
                "test_type": "",
                "remote_support": "Unknown",
                "adaptive_support": "Unknown",
            }
        )

    os.makedirs("data", exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT_PATH, index=False)
    print(f"Built {len(rows)} rows into {OUT_PATH}")


if __name__ == "__main__":
    main()
