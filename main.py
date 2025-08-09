import pandas as pd
import matplotlib.pyplot as plt

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
# plt.savefig("top_songs.png", dpi=300)

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
# plt.savefig("top_artists_us.png", dpi=300)

# # export cleaned version of US only data
# data_us_sample = data[data["region"] == "United States"].copy()
# data_us_sample.to_csv("./data/spotify_us_cleaned.csv", index=False)


# ========== DATABASE INITIALIZATION =========

import sqlite3
import pathlib
import os


# create db after checking to make sure db folder exists
pathlib.Path("db").mkdir(parents=True, exist_ok=True)
con = sqlite3.connect("db/spotify.db")

# read in cleaned data and add to db
data = pd.read_csv("./data/spotify_us_cleaned.csv")
data.to_sql("spotify_us", con, if_exists="replace", index=False)
# print(data.shape)
# print(list(data.columns)[:10])

# create cursor, view database for testing
# cur = con.cursor()
# cur.execute("PRAGMA table_info(spotify_us);")
# schema = cur.fetchall()
# for col in schema:
#     print(col)

# create query to get the top 10 arists by total streams grouped by artist name from the db
query = """
SELECT artist_name, SUM(daily_streams) as total_streams
FROM spotify_us
GROUP BY artist_name
ORDER BY total_streams DESC
LIMIT 10
"""

# execute the query and print to console
top_artists = pd.read_sql_query(query, con)
top_artists['total_streams'] = (
    top_artists['total_streams'].apply(lambda x: f"{x:,.0f}")
)
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
highest_streamed_dates['total_streams'] = (
    highest_streamed_dates['total_streams'].apply(lambda x: f"{x:,.0f}")
)
print(f"TOP 10 HIGHEST STREAMING DAYS IN US:\n{highest_streamed_dates}")

# What's the average daily streams for each chart position (rank)?
query = """
SELECT rank, AVG(daily_streams) as average_daily_streams
FROM spotify_us
GROUP BY rank
ORDER BY rank ASC
LIMIT 10
"""

average_daily_streams_by_rank = pd.read_sql_query(query, con)
average_daily_streams_by_rank['average_daily_streams'] = (
    average_daily_streams_by_rank['average_daily_streams']
    .apply(lambda x: f"{x:,.0f}")
)
print(f"AVERAGE DAILY STREAMS BY RANK:\n{average_daily_streams_by_rank}")

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

cum_weeks_in_top_10 = pd.read_sql_query(query, con)
print(f"TOP 10 CUMULATIVE WEEKS IN TOP 10 IN THE US:\n{cum_weeks_in_top_10}")


con.close()