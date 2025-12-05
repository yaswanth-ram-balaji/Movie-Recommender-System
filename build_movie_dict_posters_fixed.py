import pandas as pd
import pickle
import requests
import time

API_KEY = "2560e91e5a3a55a1fe723caf35df2542"

# Load TMDB movies
movies = pd.read_csv("tmdb_5000_movies.csv")
movies = movies[['id', 'title', 'overview']]
movies.rename(columns={'id': 'movie_id'}, inplace=True)

poster_paths = []

headers = {
    "accept": "application/json"
}

print("Fetching poster paths (this will take 5–8 minutes)...")

for movie_id in movies["movie_id"]:

    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"

    poster_path = None

    # RETRY 3 TIMES
    for attempt in range(3):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()

            if "poster_path" in data and data["poster_path"]:
                poster_path = data["poster_path"]
            break
        except Exception as e:
            print(f"Retry {attempt+1} failed for {movie_id}: {e}")
            time.sleep(0.5)

    poster_paths.append(poster_path)

    # Prevent rate-limit banning
    time.sleep(0.15)

movies["poster_path"] = poster_paths

# Create tags
movies["overview"] = movies["overview"].fillna("")
movies["tags"] = movies["overview"]

# Save pickle
pickle.dump(movies.to_dict("records"), open("movie_dict.pkl", "wb"))

print("✔ movie_dict.pkl created successfully with valid poster_path values!")
