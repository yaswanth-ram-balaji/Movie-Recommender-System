import streamlit as st
import pickle
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import time
import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ---------------------------
# TMDB POSTER FETCH FUNCTION
# ---------------------------

def fetch_poster(movie_id):
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))

    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=2560e91e5a3a55a1fe723caf35df2542&language=en-US"
        response = session.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        poster_path = data.get("poster_path")

        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
        else:
            return "https://via.placeholder.com/500x750.png?text=No+Image"

    except Exception as e:
        print(f"Error fetching poster for movie ID {movie_id}: {e}")
        return "https://via.placeholder.com/500x750.png?text=No+Image"


# ---------------------------
# SAFE LOAD OR REGENERATE SIMILARITY MATRIX
# ---------------------------

def get_similarity_matrix(movies_df):
    if os.path.exists("similarity.pkl"):
        return pickle.load(open("similarity.pkl", "rb"))

    # If no similarity.pkl → regenerate
    st.warning("similarity.pkl not found. Generating similarity matrix... (one-time process)")

    cv = CountVectorizer(max_features=5000, stop_words='english')
    vectors = cv.fit_transform(movies_df['tags']).toarray()
    similarity = cosine_similarity(vectors)

    # Save it for next time
    pickle.dump(similarity, open("similarity.pkl", "wb"))

    return similarity


# ---------------------------
# RECOMMEND FUNCTION
# ---------------------------

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))
        time.sleep(0.2)

    return recommended_movies, recommended_posters


# ---------------------------
# LOAD MOVIE DATA
# ---------------------------

movies_dict = pickle.load(open("movie_dict.pkl", "rb"))
movies = pd.DataFrame(movies_dict)

similarity = get_similarity_matrix(movies)   # 🔥 FIX


# ---------------------------
# STREAMLIT UI
# ---------------------------

st.title("🎬 Movie Recommender System")

selected_movie_name = st.selectbox(
    "Select a movie to get recommendations:",
    movies["title"].values
)

if st.button("Recommend"):
    names, posters = recommend(selected_movie_name)

    cols = st.columns(5)
    for idx, col in enumerate(cols):
        with col:
            st.text(names[idx])
            st.image(posters[idx])
