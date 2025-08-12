# Spotify Data Cleaning & Exploration

This project explores a large public dataset of global Spotify chart data (3GB+).
I am exploring the basics of data exploration, analysis, databases, and visualization using Pandas, SQLite, and Matplotlib.

Due to file size, the raw CSV is not included in this repository.
It can be downloaded from https://www.kaggle.com/datasets/dhruvildave/spotify-charts

## Phase 1 - Cleaning Phase

- Loaded a large CSV dataset using Pandas
- Cleaned and renamed key fields (e.g. `title` -> `track_title`)
- Converted date strings to a usable format
- Analyzed top streamed songs and top artists in the U.S.
- Created visualizations using Matplotlib
- Exported the cleaned dataset and plots

## Phase 2 - Database Initialization

- Initialized sqlite database
- Connected cleaned data to database
- Ran a query to identify the top 10 artists by total streams in the US
- Formatted and printed results to the console

## Phase 3 - Answering Meaningful Questions

- Answered the following 3 questions using SQL:
    - What day had the highest total streams in the US?
    - What is the average daily streams for each chart position (rank)?
    - Which 10 tracks stayed in the top 10 the longest (cumulative)?
- Exported query results to CSVs