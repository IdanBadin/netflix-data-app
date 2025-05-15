import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# ============ PAGE CONFIG ==============
st.set_page_config(
    page_title="Netflix Visual Dashboard",
    page_icon="🎬",
    layout="wide"
)

# ============ LOAD DATA ==============
@st.cache_data
def load_data():
    url = "https://drive.google.com/uc?id=1-C3O1uZDLsnYDVTppn0h3SjGOA4LifYE"
    df = pd.read_csv(url)
    df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
    df['year_added'] = df['date_added'].dt.year
    df['duration_num'] = df['duration'].str.extract('(\d+)').astype(float)
    return df

with st.spinner("🔄 Loading Netflix data..."):
    df = load_data()

# ============ HEADER ============
st.title("🎬 Netflix Visual Explorer")

st.markdown("""
Explore content trends, types, ratings, durations, and time-based insights from Netflix's public dataset in this fully interactive Streamlit dashboard.  
Use the filters on the left to focus on specific years or content types, and observe how Netflix's strategy evolved over time.
""")

with st.expander("📄 About this App", expanded=True):
    st.markdown("""
This app was developed by **Idan Badin** as part of the **Data Science midterm project (2025)** at **Reichman University**.  
It is based on a cleaned Netflix dataset and built using core tools from the course including:

- 📦 **Pandas** for data manipulation  
- 🎨 **Seaborn + Matplotlib** for visual exploration  
- 🖥️ **Streamlit** for dashboard design and interactivity  

The app reflects several key investigation techniques taught in class:
- Dataset structure inspection  
- Variable distributions (shape)  
- Relationships and comparisons between variables  
- Time-based content trends  
- Generating insights from visual patterns

Each graph includes a **dynamic textual insight** that updates based on user-selected filters.  
The project was designed with clarity, usability, and insight in mind — to bring data storytelling to life.
""")

# ============ SIDEBAR ============
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/7/75/Netflix_icon.svg", width=90)
st.sidebar.title("⚙️ Filters")
selected_types = st.sidebar.multiselect("Select Content Type", df['type'].dropna().unique(), default=df['type'].dropna().unique())
year_range = st.sidebar.slider("Year Added", int(df['year_added'].min()), int(df['year_added'].max()), (2015, 2020))
df_filtered = df[(df['type'].isin(selected_types)) & (df['year_added'].between(*year_range))]

# ============ METRICS ============
col1, col2, col3 = st.columns(3)
col1.metric("🎞️ Total Titles", f"{df_filtered.shape[0]}")
col2.metric("🎬 Movies", f"{(df_filtered['type'] == 'Movie').sum()}")
col3.metric("📺 TV Shows", f"{(df_filtered['type'] == 'TV Show').sum()}")

st.markdown("---")

# ============ TABS ============
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Type Distribution",
    "📆 Titles Over Time",
    "🔖 Rating Breakdown",
    "🎯 Duration by Country",
    "📈 Trends Over Time"
])

# TAB 1 – Type Distribution
with tab1:
    st.subheader("📊 Content Type Distribution")
    fig1, ax1 = plt.subplots(figsize=(6, 3.5))
    sns.countplot(data=df_filtered, x='type', palette='Set2', ax=ax1)
    ax1.set_title("Distribution of Movies and TV Shows")
    st.pyplot(fig1)

    total = df_filtered.shape[0]
    movie_count = (df_filtered['type'] == 'Movie').sum()
    show_count = (df_filtered['type'] == 'TV Show').sum()
    percent_movies = round(100 * movie_count / total) if total > 0 else 0
    percent_shows = round(100 * show_count / total) if total > 0 else 0

    st.markdown(f"""
    **Insight:** In the selected range ({year_range[0]}–{year_range[1]}), Netflix has **{total} titles**.  
    **{percent_movies}%** are Movies (**{movie_count}**) and **{percent_shows}%** are TV Shows (**{show_count}**).
    """)

# TAB 2 – Titles Over Time
with tab2:
    st.subheader("📆 Titles Added to Netflix Over Time")
    fig2, ax2 = plt.subplots(figsize=(8, 3.5))
    sns.countplot(data=df_filtered[df_filtered['year_added'].notnull()], x='year_added', color='#4a90e2', ax=ax2)
    ax2.set_title("Titles Added Each Year")
    ax2.set_xlabel("Year")
    ax2.set_ylabel("Number of Titles")
    plt.xticks(rotation=45)
    st.pyplot(fig2)

    year_counts = df_filtered['year_added'].value_counts().sort_index()
    most_year = year_counts.idxmax() if not year_counts.empty else "N/A"
    most_count = year_counts.max() if not year_counts.empty else 0

    st.markdown(f"""
    **Insight:** The year with the highest number of titles added is **{int(most_year)}**, with **{most_count} titles**.
    """)

# TAB 3 – Ratings
with tab3:
    st.subheader("🔖 Rating Distribution by Content Type")
    fig3, ax3 = plt.subplots(figsize=(8, 3.5))
    sns.countplot(data=df_filtered, x='rating', hue='type', palette='pastel', ax=ax3)
    ax3.set_title("Ratings by Content Type")
    ax3.set_xlabel("Rating")
    ax3.set_ylabel("Count")
    plt.xticks(rotation=45)
    st.pyplot(fig3)

    top_rating = df_filtered['rating'].value_counts().idxmax() if not df_filtered.empty else "N/A"
    st.markdown(f"""
    **Insight:** The most common rating in this selection is **{top_rating}**.
    """)

# TAB 4 – Duration
with tab4:
    st.subheader("🎯 Average Movie Duration by Country (Top 5)")
    df_movies = df_filtered[df_filtered['type'] == 'Movie'].copy()
    df_movies['duration_min'] = df_movies['duration'].str.extract('(\d+)').astype(float)
    top_countries = df_movies['country'].value_counts().head(5).index
    df_movies_top = df_movies[df_movies['country'].isin(top_countries)]

    fig4, ax4 = plt.subplots(figsize=(8, 3.5))
    sns.pointplot(data=df_movies_top, x='country', y='duration_min', hue='country',
                  palette='Set1', capsize=.2, ax=ax4, legend=False)
    ax4.set_title("Movie Duration by Country")
    ax4.set_ylabel("Avg. Duration (Minutes)")
    st.pyplot(fig4)

    avg_duration = df_movies['duration_min'].mean()
    st.markdown(f"""
    **Insight:** The average movie duration in this selection is **{round(avg_duration)} minutes**.
    """)

# TAB 5 – Trends
with tab5:
    st.subheader("📈 Movies vs TV Shows Over Time")
    df_trend = df_filtered.groupby(['year_added', 'type']).size().reset_index(name='count')
    fig5, ax5 = plt.subplots(figsize=(8, 3.5))
    sns.lineplot(data=df_trend, x='year_added', y='count', hue='type', marker='o',
                 palette=['#8ecae6', '#219ebc'], ax=ax5)
    ax5.set_title("Content Trends Over Time")
    ax5.set_xlabel("Year")
    ax5.set_ylabel("Number of Titles")
    st.pyplot(fig5)

    years = df_trend['year_added'].unique()
    if len(years) > 0:
        min_year = int(min(years))
        max_year = int(max(years))
        content_types = ', '.join(df_trend['type'].unique())
        st.markdown(f"""
        **Insight:** This trend shows how Netflix's content evolved from **{min_year}** to **{max_year}**,  
        with consistent growth in {content_types}.
        """)
    else:
        st.markdown("**Insight:** No data available for the selected range.")

# FOOTER
st.markdown("---")
st.success("✨ Created by Idan Badin | Netflix Data Project | Data Science Midterm Course Project 2025 | Reichman University")
