"""Analysis script for the IMDb Top 1000 portfolio project.

This script downloads the `IMDB‑Movie‑Data.csv` file from the repository (if it
exists locally, the download step is skipped), loads it into a pandas
DataFrame, writes the data into a SQLite database and creates several
normalised tables.  It then executes a collection of SQL queries, saves
the results to CSV files and generates simple PNG images of the first
few rows of each result using Matplotlib.  Running this script end‑to‑end
reproduces the artefacts stored in the `query_results` directory.

Usage:

    python analysis_script.py

Dependencies:
    * pandas
    * sqlite3 (standard library)
    * matplotlib

"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import urllib.request


REPO_URL = (
    "https://github.com/peetck/IMDB-Top1000-Movies/raw/master/IMDB-Movie-Data.csv"
)


def download_csv(csv_path: Path) -> None:
    """Download the IMDb Top 1000 CSV if it does not already exist."""
    if csv_path.exists():
        print(f"CSV already present at {csv_path}")
        return
    print(f"Downloading data to {csv_path}…")
    req = urllib.request.Request(REPO_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as response, open(csv_path, "wb") as out:
        out.write(response.read())
    print("Download complete.")


def build_database(csv_path: Path, db_path: Path) -> None:
    """Load the CSV into SQLite and create additional tables."""
    print("Loading CSV…")
    movies = pd.read_csv(csv_path)

    print(f"Writing data to database {db_path}…")
    conn = sqlite3.connect(db_path)
    # Base table
    movies.to_sql("movies", conn, if_exists="replace", index=False)

    # Create movie_genres table
    records = []
    for _, row in movies.iterrows():
        genres = [g.strip() for g in str(row["Genre"]).split(",")]
        for g in genres:
            records.append({"Rank": row["Rank"], "Genre": g})
    pd.DataFrame(records).to_sql("movie_genres", conn, if_exists="replace", index=False)

    # Create directors and movie_directors tables
    unique_directors = pd.DataFrame({"Director": movies["Director"].unique()})
    unique_directors["director_id"] = unique_directors.index + 1
    unique_directors.to_sql("directors", conn, if_exists="replace", index=False)
    movies_dir = movies[["Rank", "Director"]].merge(
        unique_directors, on="Director", how="left"
    )
    movies_dir[["Rank", "director_id"]].to_sql(
        "movie_directors", conn, if_exists="replace", index=False
    )
    conn.close()
    print("Database built.")


def run_queries(db_path: Path, output_dir: Path) -> None:
    """Execute predefined SQL queries and save results."""
    queries = {
        "01_top_10_highest_rated.sql": """
            SELECT Title, Year, Rating
            FROM movies
            ORDER BY Rating DESC
            LIMIT 10;
        """,
        "02_average_rating_per_genre.sql": """
            SELECT mg.Genre, ROUND(AVG(m.Rating), 2) AS avg_rating
            FROM movies m
            JOIN movie_genres mg ON mg.Rank = m.Rank
            GROUP BY mg.Genre
            ORDER BY avg_rating DESC;
        """,
        "03_movies_count_per_director.sql": """
            SELECT Director, COUNT(*) AS movie_count
            FROM movies
            GROUP BY Director
            ORDER BY movie_count DESC
            LIMIT 10;
        """,
        "04_movies_count_per_year.sql": """
            SELECT Year, COUNT(*) AS movie_count
            FROM movies
            GROUP BY Year
            ORDER BY Year DESC;
        """,
        "05_top_movie_per_year.sql": """
            SELECT Year, Title, Rating
            FROM (
                SELECT Year, Title, Rating,
                       ROW_NUMBER() OVER (PARTITION BY Year ORDER BY Rating DESC) AS rn
                FROM movies
            ) t
            WHERE rn = 1
            ORDER BY Year DESC;
        """,
        "06_top_5_revenue_per_year.sql": """
            SELECT Year, Title, [Revenue (Millions)] AS Revenue
            FROM (
                SELECT Year, Title, [Revenue (Millions)],
                       ROW_NUMBER() OVER (PARTITION BY Year ORDER BY [Revenue (Millions)] DESC) AS rn
                FROM movies
                WHERE [Revenue (Millions)] IS NOT NULL
            ) t
            WHERE rn <= 5
            ORDER BY Year DESC, rn;
        """,
        "07_avg_revenue_per_director.sql": """
            SELECT Director, ROUND(AVG([Revenue (Millions)]), 2) AS avg_revenue, COUNT(*) AS movies_count
            FROM movies
            WHERE [Revenue (Millions)] IS NOT NULL
            GROUP BY Director
            HAVING COUNT(*) >= 2
            ORDER BY avg_revenue DESC
            LIMIT 10;
        """,
        "08_top_5_genres_by_count.sql": """
            SELECT mg.Genre, COUNT(*) AS movie_count
            FROM movie_genres mg
            GROUP BY mg.Genre
            ORDER BY movie_count DESC
            LIMIT 5;
        """,
        "09_avg_runtime_per_genre.sql": """
            SELECT mg.Genre, ROUND(AVG([Runtime (Minutes)]), 2) AS avg_runtime
            FROM movies m
            JOIN movie_genres mg ON mg.Rank = m.Rank
            GROUP BY mg.Genre
            ORDER BY avg_runtime DESC;
        """,
        "10_avg_rating_per_decade.sql": """
            SELECT (Year/10)*10 AS decade, ROUND(AVG(Rating), 2) AS avg_rating, COUNT(*) AS movie_count
            FROM movies
            GROUP BY decade
            ORDER BY decade;
        """,
        "11_top_3_movies_per_genre.sql": """
            SELECT Genre, Title, Rating
            FROM (
                SELECT mg.Genre, m.Title, m.Rating,
                       ROW_NUMBER() OVER (PARTITION BY mg.Genre ORDER BY m.Rating DESC) AS rn
                FROM movie_genres mg
                JOIN movies m ON m.Rank = mg.Rank
            ) t
            WHERE rn <= 3
            ORDER BY Genre ASC, rn;
        """,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    for fname, sql in queries.items():
        sql = sql.strip()
        # Save SQL
        with open(output_dir / fname, "w") as f:
            f.write(sql + "\n")
        # Execute
        df = pd.read_sql(sql, conn)
        # Save CSV
        df.to_csv(output_dir / fname.replace(".sql", ".csv"), index=False)
        # Save image of first few rows
        n_rows = min(15, len(df))
        fig, ax = plt.subplots(figsize=(8, 0.4 + 0.25 * n_rows))
        ax.axis("off")
        table = ax.table(
            cellText=df.head(n_rows).values,
            colLabels=df.columns,
            cellLoc="center",
            loc="center",
        )
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 1.5)
        plt.savefig(output_dir / fname.replace(".sql", ".png"), bbox_inches="tight")
        plt.close(fig)
    conn.close()
    print(f"Saved query results to {output_dir}")


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    csv_path = base_dir / "IMDB-Movie-Data.csv"
    db_path = base_dir / "imdb_top1000.db"
    output_dir = base_dir / "query_results"
    download_csv(csv_path)
    build_database(csv_path, db_path)
    run_queries(db_path, output_dir)


if __name__ == "__main__":
    main()
