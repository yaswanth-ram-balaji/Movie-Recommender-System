import pickle
import pandas as pd

movies = pd.DataFrame(pickle.load(open("movie_dict.pkl", "rb")))

print(movies[["movie_id", "title", "poster_path"]].head(20))
print("\nMissing posters:", movies["poster_path"].isna().sum())
print("Total movies:", len(movies))
