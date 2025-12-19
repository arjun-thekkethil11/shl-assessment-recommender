import csv
import os

INPUT_FILE = "data/url_list.txt"
OUT_PATH = "data/catalog.csv"


def slug_to_name(url: str) -> str:
    """
    Convert the last segment of the URL into a readable product name.
    e.g. .../java-8-new/  ->  'Java 8 New'
    """
    slug = url.rstrip("/").split("/")[-1]
    slug = slug.replace("-", " ")
    return " ".join(word.capitalize() for word in slug.split())


def main():
    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(f"{INPUT_FILE} not found. Run scrape_catalog.py first.")

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        urls = [u.strip() for u in f if u.strip()]

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

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "url",
                "name",
                "description",
                "duration",
                "test_type",
                "remote_support",
                "adaptive_support",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Rebuilt catalog with {len(rows)} items → {OUT_PATH}")


if __name__ == "__main__":
    main()
