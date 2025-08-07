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

# ========== DATABASE PRACTICE =========
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
print(f"TOP 10 ARTISTS:\n{top_artists}")

con.close()