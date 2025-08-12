import pandas as pd
import matplotlib.pyplot as plt
import pathlib

# ========== CLEANING PHASE (COMMENTED OUT AFTER EXECUTION) ===========

# # read in data from csv, sample 1%
# data = pd.read_csv("./data/charts.csv")
# data = data.sample(frac=0.01, random_state=42)

# # # general info about columns and a peek at the data
# # print(data.head())
# # print(data.info())

# # # get more insight into the shape (columns and rows) and memory usage of the data
# # print(data.shape)
# # print(data.memory_usage(deep=True).sum() / 1024**2, "MB")

# # # get some value counts to see what's going on
# # print(data["chart"].value_counts())
# # print(data["region"].value_counts())

# # get rid of the url column, not used for analysis
# data.drop(columns=["url"], inplace=True)

# # rename columns to give them more specificity
# data.rename(columns={
#     "title": "track_title",
#     "artist": "artist_name",
#     "date": "chart_date",
#     "streams": "daily_streams",
#     "trend": "trending_direction"
# }, inplace=True)

# # ensure chart_date is type datetime, data type validation
# data["chart_date"] = pd.to_datetime(data["chart_date"])

# # top 10 most streamed songs
# # print("Top 10 Most Streamed Songs:")
# # print(data.groupby("track_title")["daily_streams"].sum().sort_values(ascending=False).head(10))
# top_songs = data.groupby("track_title")["daily_streams"].sum().sort_values(ascending=False).head(10)

# # plot top_songs 
# plt.figure(figsize=(10, 6))
# top_songs.plot(kind='barh', color='skyblue')
# plt.title("Top 10 Most Streamed Songs")
# plt.xlabel("Total Streams")
# plt.ylabel("Song Title")
# plt.gca().invert_yaxis()  # Puts the highest at the top
# plt.tight_layout()
# pathlib.Path("./plots").mkdir(parents=True, exist_ok=True)
# plt.savefig("./plots/top_songs.png", dpi=300)

# # top 10 artists in the US
# # print("Top 10 Artists in the US:")
# # print(data[data["region"] == "United States"].groupby("artist_name")["daily_streams"].sum().sort_values(ascending=False).head(10))
# top_artists_us = data[data["region"] == "United States"].groupby("artist_name")["daily_streams"].sum().sort_values(ascending=False).head(10)

# # plot top_artists_us
# plt.figure(figsize=(10, 6))
# top_artists_us.plot(kind='barh', color='lightgreen')
# plt.title("Top 10 Artists in the US (by Total Streams)")
# plt.xlabel("Total Streams")
# plt.ylabel("Artist")
# plt.gca().invert_yaxis()
# plt.tight_layout()
# plt.savefig("./plots/top_artists_us.png", dpi=300)

# # export cleaned version of US only data
# data_us_sample = data[data["region"] == "United States"].copy()
# pathlib.Path("./data").mkdir(parents=True, exist_ok=True)
# data_us_sample.to_csv("./data/spotify_us_cleaned.csv", index=False)


# ========== DATABASE INITIALIZATION =========

import sqlite3

# function for formatting commas
def fmt_commas(df, cols, decimals=0):
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")  # Ensure numeric
            df[c] = df[c].apply(
                lambda x: f"{x:,.{decimals}f}" if pd.notnull(x) else ""
            )
    return df


# create db after checking to make sure db folder exists
pathlib.Path("db").mkdir(parents=True, exist_ok=True)
con = sqlite3.connect("db/spotify.db")

# read in cleaned data and add to db
data = pd.read_csv("./data/spotify_us_cleaned.csv")
data["chart_date"] = pd.to_datetime(data["chart_date"], errors="coerce")
data["daily_streams"] = pd.to_numeric(data["daily_streams"], errors="coerce")
data.to_sql("spotify_us", con, if_exists="replace", index=False)
con.execute("CREATE INDEX IF NOT EXISTS idx_artist ON spotify_us(artist_name)")
con.execute("CREATE INDEX IF NOT EXISTS idx_date ON spotify_us(chart_date)")
con.execute("CREATE INDEX IF NOT EXISTS idx_rank ON spotify_us(rank)")
con.commit()
# print(data.shape)
# print(list(data.columns)[:10])

# create cursor, view database for testing
# cur = con.cursor()
# cur.execute("PRAGMA table_info(spotify_us);")
# schema = cur.fetchall()
# for col in schema:
#     print(col)

# create query to get the top 10 arists by total streams grouped by artist name from the db, US only
query = """
SELECT artist_name, SUM(daily_streams) as total_streams
FROM spotify_us
GROUP BY artist_name
ORDER BY total_streams DESC
LIMIT 10
"""

# execute the query and print to console
top_artists = pd.read_sql_query(query, con)
top_artists = fmt_commas(top_artists, ['total_streams'])
print(f"TOP 10 ARTISTS IN US:\n{top_artists}")


# ========== ANSWERING MEANINGFUL QUESTIONS ==========

# Which day had the highest total streams in the US?
query = """
SELECT chart_date, SUM(daily_streams) as total_streams
FROM spotify_us
GROUP BY chart_date
ORDER BY total_streams DESC
LIMIT 10
"""

highest_streamed_dates = pd.read_sql_query(query, con)
highest_streamed_dates = fmt_commas(highest_streamed_dates, ['total_streams'])

pathlib.Path("./exports").mkdir(parents=True, exist_ok=True)

# save query results to csv in exports folder
highest_streamed_dates.to_csv("./exports/streams_by_day_us.csv", index=False)


# What's the average daily streams for each chart position (rank)? US only
query = """
SELECT rank, AVG(daily_streams) as average_daily_streams
FROM spotify_us
GROUP BY rank
ORDER BY rank ASC
LIMIT 10
"""

average_daily_streams_by_rank = pd.read_sql_query(query, con)
average_daily_streams_by_rank = fmt_commas(average_daily_streams_by_rank, ['average_daily_streams'])
# save query results to csv in exports folder
average_daily_streams_by_rank.to_csv("./exports/avg_streams_by_rank_us.csv", index=False)


# Which 10 tracks stayed in the top 10 the longest (cumulative)?
query = """
WITH weekly AS (
    SELECT DISTINCT track_title, strftime('%Y-%W', chart_date) as year_week
    FROM spotify_us
    WHERE rank <= 10
)
SELECT track_title, COUNT(DISTINCT year_week) AS weeks_in_top_10
FROM weekly
GROUP BY track_title
ORDER BY weeks_in_top_10 DESC
LIMIT 10
"""

weeks_in_top_10 = pd.read_sql_query(query, con)
# save query results to csv in exports folder
weeks_in_top_10.to_csv("./exports/weeks_in_top10_us.csv", index=False)


con.close()