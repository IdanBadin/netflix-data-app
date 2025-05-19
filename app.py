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
        animation: fadein 2s;
    }
    @keyframes fadein {
        from { opacity: 0; }
        to   { opacity: 1; }
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
    <div style='padding: 1rem; background-color: #1f1f1f; border-radius: 10px; box-shadow: 0 0 12px rgba(255, 0, 0, 0.3); animation: fadein 1.5s;'>
        <h3 style='color: #FF4B4B;'>📊 Netflix Visual Explorer</h3>
        <p style='font-size: 16px; line-height: 1.6;'>
            This interactive dashboard was created as a midterm project for the <strong>Introduction to Data Science</strong> course at <strong>Reichman University</strong> 🎓.<br><br>
            The app analyzes Netflix’s global streaming catalog using modern data science tools like <strong>Pandas</strong>, <strong>Seaborn</strong>, <strong>Plotly</strong>, and <strong>Streamlit</strong>.📈<br><br>
            It offers insights into how Netflix has evolved over time by exploring:
            <ul>
                <li>🗂️ Content types (Movies vs. TV Shows)</li>
                <li>📆 Titles added over the years</li>
                <li>🏷️ Ratings & audience targeting</li>
                <li>🌍 Geographic differences</li>
                <li>📈 Time-based growth trends</li>
            </ul>
            Use the filters in the sidebar to explore the dataset interactively.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    try:
        lottie_animation = load_lottiefile("lottie_movie.json")
        st_lottie(lottie_animation, height=180, key="movie")
    except:
        st.warning("⚠️ Animation failed to load.")

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
tabs = st.tabs([
    "📊 Type Distribution", 
    "📆 Titles Over Time",
    "🏷️ Ratings", 
    "🌍 Duration by Country",
    "📈 Trends Over Time"
])

with tabs[0]:
    st.subheader("📊 Content Type Distribution")
    fig = px.histogram(df_filtered, x='type', color='type', title="Distribution of Movies vs TV Shows",
                       color_discrete_sequence=px.colors.qualitative.Set2)
    fig.update_layout(template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)

    movie_count = (df_filtered['type'] == 'Movie').sum()
    show_count = (df_filtered['type'] == 'TV Show').sum()
    st.markdown(f"""
    **Insight:** In this selection, there are **{movie_count} Movies** and **{show_count} TV Shows**.
    """)

with tabs[1]:
    st.subheader("📆 Titles Added Over Time")
    df_filtered_clean = df_filtered[df_filtered['year_added'].notnull()].copy()
    df_filtered_clean['year_added'] = df_filtered_clean['year_added'].astype(int)
    fig = px.histogram(df_filtered_clean, x='year_added', color_discrete_sequence=['#4a90e2'])
    fig.update_layout(template='plotly_dark', title="Titles Added Each Year")
    st.plotly_chart(fig, use_container_width=True)

    year_counts = df_filtered_clean['year_added'].value_counts().sort_index()
    if not year_counts.empty:
        most_year = int(year_counts.idxmax())
        most_count = int(year_counts.max())
        st.markdown(f"""
        **Insight:** The year with the most content added is **{most_year}**, with **{most_count} titles**.
        """)

with tabs[2]:
    st.subheader("🏷️ Content Ratings")
    fig = px.histogram(df_filtered, x='rating', color='type', barmode='group',
                       title="Distribution of Ratings",
                       color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_layout(template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)

    if not df_filtered.empty:
        top_rating = df_filtered['rating'].value_counts().idxmax()
        st.markdown(f"""
        **Insight:** The most common rating in this selection is **{top_rating}**.
        """)

with tabs[3]:
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

    avg_all = df_top['duration_min'].mean()
    st.markdown(f"""
    **Insight:** The average movie duration in top countries is **{round(avg_all)} minutes**.
    """)

with tabs[4]:
    st.subheader("📈 Movies vs TV Shows Over Time")
    df_trend = df_filtered.groupby(['year_added', 'type']).size().reset_index(name='count')
    fig = px.line(df_trend, x='year_added', y='count', color='type', markers=True,
                  title="Content Growth Over Time",
                  color_discrete_sequence=px.colors.qualitative.Set1)
    fig.update_layout(template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)

    if not df_trend.empty:
        years = df_trend['year_added'].dropna().astype(int)
        min_year = int(years.min())
        max_year = int(years.max())
        types = ', '.join(df_trend['type'].unique())
        st.markdown(f"""
        **Insight:** This trend shows how Netflix's content evolved from **{min_year}** to **{max_year}**,  
        with consistent growth in {types}.
        """)

# ============ FOOTER ==============
st.markdown("---")
st.markdown("✨ Built with ❤️ by **Idan Badin** | Netflix Midterm Project | Reichman University 2025")
