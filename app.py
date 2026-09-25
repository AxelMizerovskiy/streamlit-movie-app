import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configure the page
st.set_page_config(page_title="MovieLens Dashboard", layout="wide")
st.title("MovieLens Data Exploration")


# 1. Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("movie_ratings.csv")
    
    # Split pipe-separated genres and explode into rows
    df_exploded = df.assign(genres=df['genres'].str.split('|')).explode('genres')
    
    # Drop missing, blank, and 'unknown' entries cleanly
    invalid_genres = ['unknown', '(no genres listed)', '', 'None']
    df_exploded = df_exploded[
        df_exploded['genres'].notna() & 
        ~df_exploded['genres'].str.strip().str.lower().isin([g.lower() for g in invalid_genres])
    ]
    
    return df, df_exploded


df, df_exploded = load_data()

# 2. Interactive Widgets
st.sidebar.header("Dashboard Controls")

# Widget 1: Year Range Slider
min_year, max_year = int(df["year"].min()), int(df["year"].max())
selected_years = st.sidebar.slider(
    "Select Release Year Range", min_year, max_year, (min_year, max_year)
)

# Widget 2: Minimum Ratings Floor Slider (For Question 4)
rating_floor = st.sidebar.slider(
    "Minimum Ratings Floor (Q4)", min_value=10, max_value=200, value=50, step=10
)

# Filter data based on the year widget
df_filtered = df[(df["year"] >= selected_years[0]) & (df["year"] <= selected_years[1])]
df_exploded_filtered = df_exploded[
    (df_exploded["year"] >= selected_years[0])
    & (df_exploded["year"] <= selected_years[1])
]

# 3. Visualizations

# Question 1: Genre Breakdown
st.header("1. Genre Breakdown")
st.write(
    "To count genres accurately, pipe-separated strings (e.g., 'Action|Comedy') were split, and the dataset was 'exploded' so each genre gets its own row before counting."
)
fig1, ax1 = plt.subplots(figsize=(10, 6))
genre_counts = df_exploded_filtered["genres"].value_counts()
sns.barplot(x=genre_counts.values, y=genre_counts.index, ax=ax1, palette="viridis")
ax1.set_xlabel("Number of Ratings")
ax1.set_ylabel("Genre")
st.pyplot(fig1)

# Question 2: Genre Satisfaction
st.header("2. Genre Satisfaction (Average Rating)")

# Filter out nulls, empty strings, and the standard MovieLens placeholder '(no genres listed)'
clean_genres_df = df_exploded_filtered[
    df_exploded_filtered['genres'].notna() & 
    ~df_exploded_filtered['genres'].isin(['(no genres listed)', '', 'None'])
]

genre_avg_rating = (
    clean_genres_df.groupby('genres')['rating']
    .mean()
    .sort_values(ascending=False)
)

fig2, ax2 = plt.subplots(figsize=(10, 6))
sns.barplot(x=genre_avg_rating.values, y=genre_avg_rating.index, ax=ax2, palette="magma")
ax2.set_xlabel("Average Rating")
ax2.set_ylabel("Genre")
ax2.set_xlim(0, 5)

# Annotate values on the bars for clarity
for i, v in enumerate(genre_avg_rating.values):
    ax2.text(v + 0.05, i, f"{v:.2f}", color='black', va='center')

st.pyplot(fig2)

# Question 3: Ratings Over Time
st.header("3. Average Rating by Release Year")
fig3, ax3 = plt.subplots(figsize=(12, 5))
yearly_avg = df_filtered.groupby("year")["rating"].mean().reset_index()
sns.lineplot(data=yearly_avg, x="year", y="rating", ax=ax3, marker="o")
ax3.set_xlabel("Release Year")
ax3.set_ylabel("Average Rating")
st.pyplot(fig3)

# Question 4: Best Movies, With a Floor
st.header(f"4. Top 5 Movies (Minimum {rating_floor} Ratings)")
movie_stats = (
    df_filtered.groupby("title")
    .agg(avg_rating=("rating", "mean"), rating_count=("rating", "count"))
    .reset_index()
)

# Apply the floor threshold from the widget
top_movies = movie_stats[movie_stats["rating_count"] >= rating_floor].nlargest(
    5, "avg_rating"
)

fig4, ax4 = plt.subplots(figsize=(10, 4))
sns.barplot(
    x=top_movies["avg_rating"], y=top_movies["title"], ax=ax4, palette="cubehelix"
)
ax4.set_xlabel("Average Rating")
ax4.set_ylabel("Movie Title")
ax4.set_xlim(0, 5)
for i, v in enumerate(top_movies["avg_rating"]):
    ax4.text(v + 0.05, i, f"{v:.2f}", color="black", va="center")
st.pyplot(fig4)
