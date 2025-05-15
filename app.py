import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from st_aggrid import AgGrid  # for advanced grid display

# ============ PAGE CONFIG =================
st.set_page_config(
    page_title="Netflix Visual Dashboard",
    page_icon="🎬",
    layout="wide"
)

# ============ CUSTOM CSS FOR DESIGN ============
st.markdown("""
<style>
    .big-title {
        font-size: 42px;
        font-weight: bold;
        color: #E50914;
        text-align: center;
        background-color: rgba(0,0,0,0.2);
        padding: 10px;
        border-radius: 15px;
    }
    .description-text {
        font-size: 18px;
        color: #333;
        text-align: center;
        margin-top: 10px;
    }
    .big-btn {
        background-color: #E50914;
        color: white;
        font-size: 16px;
        border-radius: 10px;
        padding: 10px 20px;
        margin-top: 10px;
    }
    .title-card {
        font-size: 20px;
        font-weight: bold;
        color: #E50914;
        margin-bottom: 10px;
    }
    .card {
        background-color: #f5f5f5;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ================= HEADER AND WELCOME =====================
st.markdown('<div class="big-title">🎬 Netflix Visual Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="description-text">Explore trends, distribution, and insights into Netflix\'s movie and TV show content. A stunning data science app built by **Idan Badin** for the **Data Science 2025 Midterm**.</div>', unsafe_allow_html=True)

# ================== FILTER AND USER INTERACTION =====================
st.sidebar.title("⚙️ Filters")
selected_types = st.sidebar.multiselect("Select Content Type:", df['type'].dropna().unique(), default=df['type'].dropna().unique())
year_range = st.sidebar.slider("Year Added:", int(df['year_added'].min()), int(df['year_added'].max()), (2015, 2020))

df_filtered = df[(df['type'].isin(selected_types)) & (df['year_added'].between(*year_range))]

# ================== METRICS ======================
col1, col2, col3 = st.columns(3)
col1.metric("🎞️ Total Titles", f"{df_filtered.shape[0]}")
col2.metric("🎬 Movies", f"{(df_filtered['type'] == 'Movie').sum()}")
col3.metric("📺 TV Shows", f"{(df_filtered['type'] == 'TV Show').sum()}")

# ================ VISUAL INSIGHTS WITH TABS ===================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Type Distribution",
    "📆 Titles Over Time",
    "🔖 Rating Breakdown",
    "🎯 Duration by Country",
    "📈 Trends Over Time"
])

# 1️⃣ Content Type Distribution
with tab1:
    st.subheader("📊 Content Type Distribution")
    fig1, ax1 = plt.subplots(figsize=(7, 4))
    sns.countplot(data=df_filtered, x='type', palette='Set2', ax=ax1)
    ax1.set_title("Distribution of Movies and TV Shows")
    st.pyplot(fig1)

# 2️⃣ Titles Over Time
with tab2:
    st.subheader("📆 Titles Added to Netflix Over Time")
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    sns.countplot(data=df_filtered[df_filtered['year_added'].notnull()], x='year_added', color='#4a90e2', ax=ax2)
    ax2.set_title("Titles Added Each Year")
    ax2.set_xlabel("Year")
    ax2.set_ylabel("Number of Titles")
    plt.xticks(rotation=45)
    st.pyplot(fig2)

# 3️⃣ Rating Breakdown
with tab3:
    st.subheader("🔖 Rating Distribution by Content Type")
    fig3, ax3 = plt.subplots(figsize=(8, 4))
    sns.countplot(data=df_filtered, x='rating', hue='type', palette='pastel', ax=ax3)
    ax3.set_title("Ratings by Content Type")
    ax3.set_xlabel("Rating")
    ax3.set_ylabel("Count")
    plt.xticks(rotation=45)
    st.pyplot(fig3)

# 4️⃣ Duration by Country
with tab4:
    st.subheader("🎯 Average Movie Duration by Country (Top 5)")
    df_movies = df_filtered[df_filtered['type'] == 'Movie'].copy()
    df_movies['duration_min'] = df_movies['duration'].str.extract('(\d+)').astype(float)
    top_countries = df_movies['country'].value_counts().head(5).index
    df_movies_top = df_movies[df_movies['country'].isin(top_countries)]

    fig4, ax4 = plt.subplots(figsize=(8, 4))
    sns.pointplot(data=df_movies_top, x='country', y='duration_min', hue='country',
                  palette='Set1', capsize=.2, ax=ax4, legend=False)
    ax4.set_title("Movie Duration by Country")
    ax4.set_ylabel("Average Duration (Minutes)")
    st.pyplot(fig4)

# 5️⃣ Trend of Movies vs TV Shows
with tab5:
    st.subheader("📈 Movies vs TV Shows Over Time")
    df_trend = df_filtered.groupby(['year_added', 'type']).size().reset_index(name='count')
    fig5, ax5 = plt.subplots(figsize=(8, 4))
    sns.lineplot(data=df_trend, x='year_added', y='count', hue='type', marker='o',
                 palette=['#8ecae6', '#219ebc'], ax=ax5)
    ax5.set_title("Content Trends Over Time")
    ax5.set_xlabel("Year")
    ax5.set_ylabel("Number of Titles")
    st.pyplot(fig5)

# ================== FOOTER ====================
st.markdown("---")
st.success("✨ Built by Idan Badin | Netflix Project | Data Science 2025 | Reichman University")
