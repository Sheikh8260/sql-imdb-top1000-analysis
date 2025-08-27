# IMDb Top 1000 Movies – SQL Analysis Portfolio Project

This project demonstrates how to use SQL to explore and answer questions about a real‑world data set.  A public data set of the **IMDb Top 1000 movies** was downloaded from GitHub (a CSV file that lists the top 1000 movies by rank).  The first line of the raw file shows the column layout: the file contains a `Rank` column (movie rank), film `Title`, comma‑separated `Genre` values, a synopsis `Description`, `Director` and `Actors`, the release `Year`, the film’s run time in minutes, a user `Rating`, the number of IMDb `Votes`, the box‑office `Revenue (Millions)` and a critic `Metascore`【216002581764757†L0-L6】.  A few lines of the data look like this【216002581764757†L0-L6】:

```
Rank,Title,Genre,Description,Director,Actors,Year,Runtime (Minutes),Rating,Votes,Revenue (Millions),Metascore
1,Guardians of the Galaxy,"Action,Adventure,Sci‑Fi",A group of intergalactic criminals are forced …,James Gunn,"Chris Pratt, Vin Diesel, Bradley Cooper, Zoe Saldana",2014,121,8.1,757074,333.13,76
2,Prometheus,"Adventure,Mystery,Sci‑Fi",Following clues to the origin of mankind…,Ridley Scott,"Noomi Rapace, Logan Marshall‑Green, Michael Fassbender, Charlize Theron",2012,124,7.0,485820,126.46,65
…
```

## Project overview

The goal of this portfolio project is to show potential employers that you can answer real questions with SQL.  To achieve this, the IMDb Top 1000 data set was imported into a SQLite database and several additional tables were normalised (splitting movies into multiple genres and mapping each movie to its director).  A series of SQL queries were then written to answer practical questions such as:

* Which movies have the highest IMDb ratings?
* What is the average rating for each genre?
* Which directors have directed the most films in the top 1000 list?
* Which movies have the highest revenue each year?
* What are the top rated movies for each year and for each genre?

Screenshots of the query results are included in this repository along with the SQL files and CSV outputs.  The work is organised in the `query_results/` directory, where each query has three artefacts:

| File type          | Purpose                                             |
|--------------------|-----------------------------------------------------|
| `*.sql`            | Contains the SQL statement used for the query      |
| `*.csv`            | CSV export of the query result                      |
| `*.png`            | Screenshot of the first rows of the result table    |


## Data preparation

The original CSV file (`IMDB‑Movie‑Data.csv`) was downloaded from GitHub using the browser and saved into this project.  A Python script reads the CSV into a pandas DataFrame and writes it to a SQLite database (`imdb_top1000.db`).  To facilitate more interesting SQL queries, the following additional tables were derived:

* **movie_genres** – one row per movie/genre combination.  The original `Genre` field contains comma‑separated genres, so this table normalises that data.
* **directors** – a lookup table with one row per unique director.
* **movie_directors** – a join table linking each movie (by `Rank`) to its director in the `directors` table.

These tables allow us to perform joins and aggregations across genres and directors.

## Example queries and findings

Below is a summary of some of the SQL queries in this project.  Refer to the `query_results/` folder for the full SQL statements and outputs.

1. **Top 10 highest rated movies** – returns the ten films with the highest IMDb rating.  The query orders the movies by `Rating` descending and selects the top ten.  Unsurprisingly, critically acclaimed films like *The Shawshank Redemption* and *The Godfather* dominate the top of the list.

2. **Average rating per genre** – joins the `movies` table with `movie_genres` and computes the average rating for each genre.  Genres like *Drama* and *Crime* have higher average ratings, whereas *Fantasy* and *Adventure* skew slightly lower.

3. **Movies count per director** – groups the `movies` table by `Director` and counts how many top‑1000 titles each director has.  Directors such as Steven Spielberg and Christopher Nolan appear frequently, highlighting their productivity and popularity.

4. **Top movie per year** – uses a window function (`ROW_NUMBER() OVER (PARTITION BY Year ORDER BY Rating DESC)`) to rank movies within each year by rating.  Selecting only rows where the ranking equals 1 yields the highest rated movie of every year in the data set.

5. **Top 5 revenue earners per year** – another window function partitions movies by year and orders them by revenue in descending order.  The outer query filters to the top five movies per year based on box‑office performance.  This highlights blockbusters like *Avatar* and *Titanic* in their respective years.

6. **Average revenue per director (≥2 movies)** – this query groups films by director, computes the average revenue and filters for directors with at least two movies.  It reveals which directors consistently generate high box‑office returns.

7. **Top 5 genres by film count** – counts the number of films associated with each genre in the `movie_genres` table, showing that genres such as *Drama*, *Action* and *Comedy* are most prevalent in the top‑1000 list.

8. **Average runtime per genre** – joins movies with their genres and computes the average running time for each genre.  *Adventure* and *Drama* films tend to have longer runtimes, while *Animation* is shorter on average.

9. **Average rating per decade** – groups movies by decade (`(Year/10)*10`) and calculates the average rating for each period.  This provides an overview of how film ratings have evolved over time.

10. **Top 3 movies per genre** – uses a window function to rank movies within each genre by rating and then selects the top three.  This reveals the standout films in each genre, such as *The Dark Knight* for *Action* and *Pulp Fiction* for *Crime*.

## How to run the analysis

1. **Clone this repository** (or download the ZIP) to your local machine.
2. Install Python 3 with the `pandas`, `sqlite3` and `matplotlib` packages (these are standard in most Python distributions).
3. Run the provided Python script (`analysis_script.py`) to load `IMDB‑Movie‑Data.csv`, create the SQLite database and write the derived tables.
4. Use any SQL tool (e.g. `sqlite3`, DB Browser for SQLite, or a notebook) to open `imdb_top1000.db`.  The SQL files in `query_results/` can be executed to reproduce the results shown here.

## Conclusion

This portfolio project shows that it is possible to extract meaningful insights from a well‑structured data set using SQL.  By normalising the data and leveraging grouping, aggregation and window functions, we answered several questions about movie popularity, ratings, directors, genres and revenue.  The accompanying scripts, SQL files, CSV exports and screenshots demonstrate a clear workflow for data ingestion, transformation and analysis.
