# Ultra-Premium Netflix Streamlit App (Dark Mode + Smart Features)
# Prepared for Idan Badin's Data Science Midterm Project

import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from streamlit_lottie import st_lottie
import json

# ============ PAGE CONFIG ==============
st.set_page_config(
    page_title="🎬 Netflix Visual Explorer",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ LOAD ANIMATION FUNCTION ==============
def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

# ============ LOAD DATA ==============
@st.cache_data
def load_data():
    url = "https://drive.google.com/uc?id=1-C3O1uZDLsnYDVTppn0h3SjGOA4LifYE"
    df = pd.read_csv(url)
    df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
    df['year_added'] = df['date_added'].dt.year
    df['duration_num'] = df['duration'].str.extract(r'(\d+)').astype(float)
    return df

df = load_data()

# ============ CUSTOM DARK THEME CSS ==============
st.markdown("""
    <style>
    html, body, [class*="css"]  {
        background-color: #121212;
        color: #FFFFFF;
    }
    .stApp {
        background: linear-gradient(to bottom, #0f0f0f, #1c1c1c);
    }
    .block-container {
        padding-top: 2rem;
    }
    .metric-box {
        background-color: #1f1f1f;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 0 10px rgba(255, 0, 0, 0.2);
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# ============ HEADER ==============
st.title("🎬 Netflix Visual Explorer")

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("""
    Dive into Netflix's streaming catalog with interactive visuals.  
    Explore how content evolved over time, broken down by type, rating, country and duration.
    """)
with col2:
    lottie_animation = load_lottiefile("lottie_movie.json")
    st_lottie(lottie_animation, height=120, key="movie")

# ============ SIDEBAR ==============
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg", use_column_width=True)
st.sidebar.markdown("## 🔍 Filter Content")

selected_types = st.sidebar.multiselect("Select Content Type", df['type'].dropna().unique(), default=df['type'].dropna().unique())
year_range = st.sidebar.slider("Year Added", int(df['year_added'].min()), int(df['year_added'].max()), (2015, 2020))

# ============ FILTER DATA ==============
df_filtered = df[(df['type'].isin(selected_types)) & (df['year_added'].between(*year_range))]

# ============ SMART METRICS ==============
st.markdown("### 📊 At a Glance")
col1, col2, col3 = st.columns(3)
col1.markdown(f"""<div class='metric-box'>🎞️ <br><strong>Total Titles</strong><br>{df_filtered.shape[0]}</div>""", unsafe_allow_html=True)
col2.markdown(f"""<div class='metric-box'>🎬 <br><strong>Movies</strong><br>{(df_filtered['type'] == 'Movie').sum()}</div>""", unsafe_allow_html=True)
col3.markdown(f"""<div class='metric-box'>📺 <br><strong>TV Shows</strong><br>{(df_filtered['type'] == 'TV Show').sum()}</div>""", unsafe_allow_html=True)

# ============ TABS ==============
tab1, tab2, tab3 = st.tabs(["📈 Trends", "🏷️ Ratings", "🌍 Duration by Country"])

with tab1:
    st.subheader("📈 Titles Added Over Time")
    df_trend = df_filtered.groupby(['year_added', 'type']).size().reset_index(name='count')
    fig = px.line(df_trend, x='year_added', y='count', color='type', markers=True,
                  title="Titles Added Per Year by Type",
                  color_discrete_sequence=px.colors.qualitative.Set1)
    fig.update_layout(template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("🏷️ Content Ratings")
    fig = px.histogram(df_filtered, x='rating', color='type', barmode='group',
                       title="Distribution of Ratings",
                       color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_layout(template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("🌍 Average Duration by Country (Top 5)")
    df_movies = df_filtered[df_filtered['type'] == 'Movie'].copy()
    df_movies['duration_min'] = df_movies['duration'].str.extract(r'(\d+)').astype(float)
    top_countries = df_movies['country'].value_counts().head(5).index
    df_top = df_movies[df_movies['country'].isin(top_countries)]
    df_avg = df_top.groupby('country')['duration_min'].mean().reset_index()
    fig = px.bar(df_avg, x='country', y='duration_min', color='country',
                 title="Average Movie Duration by Country",
                 color_discrete_sequence=px.colors.sequential.Reds)
    fig.update_layout(template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)

# ============ FOOTER ==============
st.markdown("---")
st.markdown("✨ Built with ❤️ by **Idan Badin** | Netflix Midterm Project | Reichman University 2025")
