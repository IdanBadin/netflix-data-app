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

# ============ CUSTOM CSS ==============
st.markdown("""
<style>
.big-title {
    font-size: 36px;
    font-weight: bold;
    color: #E50914;
}
.description-text {
    font-size: 16px;
    color: #444;
}
</style>
""", unsafe_allow_html=True)

# ============ HEADER SECTION ============
st.markdown('<div class="big-title">🎬 Netflix Visual Explorer</div>', unsafe_allow_html=True)
st.markdown('<div class="description-text">An interactive dashboard exploring Netflix content trends by year, type, rating, and country. Built by Idan Badin for the Data Science midterm at Reichman University (2025).</div>', unsafe_allow_html=True)

with st.expander("📄 About this App", expanded=True):
    st.markdown("""
    This app presents a visual and interactive exploration of the Netflix dataset using tools from the course: **Pandas, Seaborn, and Streamlit**.  
    The dashboard covers:
    - 📊 Distributions of content types, release years, and ratings  
    - 🌍 Cross-country duration comparison  
    - 📈 Time-based trends for added content  
    - 🎛️ Filters for content type and year range  
    - 📌 Data-driven insights in a clean, modern format
    """)

# ============ SIDEBAR FILTERS ============
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/7/75/Netflix_icon.svg", width=90)
st.sidebar.title("⚙️ Filter Options")
selected_types = st.sidebar.multiselect("Select Content Type", df['type'].dropna().unique(), default=df['type'].dropna().unique())
year_range = st.sidebar.slider("Year Added", int(df['year_added'].min()), int(df['year_added'].max()), (2015, 2020))

df_filtered = df[(df['type'].isin(selected_types)) & (df['year_added'].between(*year_range))]

# ============ METRICS SECTION ============
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

# ============ TAB 1: TYPE DISTRIBUTION ============
with tab1:
    st.subheader("📊 Content Type Distribution")
    fig1, ax1 = plt.subplots(figsize=(6, 3.5))
    sns.countplot(data=df_filtered, x='type', palette='Set2', ax=ax1)
    ax1.set_title("Distribution of Movies and TV Shows")
    st.pyplot(fig1)

# ============ TAB 2: YEAR DISTRIBUTION ============
with tab2:
    st.subheader("📆 Titles Added to Netflix Per Year")
    fig2, ax2 = plt.subplots(figsize=(8, 3.5))
    sns.countplot(data=df_filtered[df_filtered['year_added'].notnull()], x='year_added', color='#4a90e2', ax=ax2)
    ax2.set_xlabel("Year Added")
    ax2.set_ylabel("Number of Titles")
    ax2.set_title("Total Titles Added by Year")
    plt.xticks(rotation=45)
    st.pyplot(fig2)

# ============ TAB 3: RATING ============
with tab3:
    st.subheader("🔖 Rating Distribution by Content Type")
    fig3, ax3 = plt.subplots(figsize=(10, 3.5))
    sns.countplot(data=df_filtered, x='rating', hue='type', palette='pastel', ax=ax3)
    ax3.set_xlabel("Rating")
    ax3.set_ylabel("Count")
    ax3.set_title("Content Ratings by Type")
    plt.xticks(rotation=45)
    st.pyplot(fig3)

# ============ TAB 4: DURATION ============
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
    ax4.set_ylabel("Average Duration (Minutes)")
    st.pyplot(fig4)

# ============ TAB 5: TRENDS ============
with tab5:
    st.subheader("📈 Trend of Movies vs TV Shows Over Time")
    df_trend = df_filtered.groupby(['year_added', 'type']).size().reset_index(name='count')
    fig5, ax5 = plt.subplots(figsize=(10, 3.5))
    sns.lineplot(data=df_trend, x='year_added', y='count', hue='type', marker='o',
                 palette=['#8ecae6', '#219ebc'], ax=ax5)
    ax5.set_xlabel("Year")
    ax5.set_ylabel("Number of Titles")
    ax5.set_title("Growth Trend by Content Type")
    st.pyplot(fig5)

# ============ FOOTER ============
st.markdown("---")
st.success("✨ Created by Idan Badin | Netflix Project | Reichman University | Data Science 2025")
