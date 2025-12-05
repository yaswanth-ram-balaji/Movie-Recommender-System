import pandas as pd
import pickle
import requests
import time

API_KEY = "2560e91e5a3a55a1fe723caf35df2542"

# Load the TMDB movies file
movies = pd.read_csv("tmdb_5000_movies.csv")

# Select only required columns
movies = movies[['id', 'title', 'overview']]

# Rename id → movie_id
movies.rename(columns={'id': 'movie_id'}, inplace=True)

poster_paths = []

print("Fetching posters...")

for movie_id in movies['movie_id']:
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"

    try:
        r = requests.get(url).json()
        poster_paths.append(r.get("poster_path"))
    except:
        poster_paths.append(None)

    time.sleep(0.1)

# Add poster paths to DataFrame
movies["poster_path"] = poster_paths

# Create tags from overview
movies['overview'] = movies['overview'].fillna('')
movies['tags'] = movies['overview']

# Save final pickle file
pickle.dump(movies.to_dict('records'), open("movie_dict.pkl", "wb"))

print("✔ movie_dict.pkl created successfully with poster_path!")