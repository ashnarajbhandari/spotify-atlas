# Spotify · the music atlas

an interactive dashboard exploring 114,000 songs across 114 genres, mapped by the features that make them feel the way they do.

every song is a coordinate. every genre, a constellation.

## features

- **radar chart** — compare audio features like danceability, energy, and valence across genres
- **scatter plot** — explore relationships between any two features across thousands of tracks
- **bar chart** — rank genres by any audio feature
- **popularity histogram** — see how popularity is distributed within genres
- **correlation heatmap** — discover which features move together within a genre

## built with

- [Dash](https://dash.plotly.com/) — web application framework
- [Plotly](https://plotly.com/) — interactive visualizations
- [Pandas](https://pandas.pydata.org/) — data manipulation
- Python

## data

dataset sourced from Kaggle. 114,000 tracks across 114 genres with audio features from the Spotify API.

## running locally
```bash
pip install -r requirements.txt
python spotify_atlas.py
```

then open `http://localhost:8051` in your browser.
