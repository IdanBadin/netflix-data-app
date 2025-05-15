import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder

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

# ============ CUSTOM HEADER ============
st.title("🎬 Netflix Visual Explorer")
st.markdown("Explore trends, content types, ratings, durations, and raw Netflix data in this modern Streamlit dashboard.")
with st.expander("📄 About this App", expanded=True):
    st.markdown("""
    This app is part of a Data Science midterm project by **Idan Badin**, using **pandas**, **seaborn**, and **streamlit**.  
    It provides a visual and interactive analysis of Netflix content across multiple dimensions.
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
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Type Distribution",
    "📆 Titles Over Time",
    "🔖 Rating Breakdown",
    "🎯 Duration by Country",
    "📈 Trends Over Time",
    "📋 Data Table"
])

# TAB 1
with tab1:
    st.subheader("📊 Content Type Distribution")
    fig1, ax1 = plt.subplots(figsize=(6, 3.5))
    sns.countplot(data=df_filtered, x='type', palette='Set2', ax=ax1)
    ax1.set_title("Distribution of Movies and TV Shows")
    st.pyplot(fig1)

# TAB 2
with tab2:
    st.subheader("📆 Titles Added to Netflix Over Time")
    fig2, ax2 = plt.subplots(figsize=(8, 3.5))
    sns.countplot(data=df_filtered[df_filtered['year_added'].notnull()], x='year_added', color='#4a90e2', ax=ax2)
    ax2.set_title("Titles Added Each Year")
    ax2.set_xlabel("Year")
    ax2.set_ylabel("Number of Titles")
    plt.xticks(rotation=45)
    st.pyplot(fig2)

# TAB 3
with tab3:
    st.subheader("🔖 Rating Distribution by Content Type")
    fig3, ax3 = plt.subplots(figsize=(8, 3.5))
    sns.countplot(data=df_filtered, x='rating', hue='type', palette='pastel', ax=ax3)
    ax3.set_title("Ratings by Content Type")
    ax3.set_xlabel("Rating")
    ax3.set_ylabel("Count")
    plt.xticks(rotation=45)
    st.pyplot(fig3)

# TAB 4
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

# TAB 5
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

# TAB 6 – AGGRID TABLE
with tab6:
    st.subheader("📋 Explore the Raw Netflix Dataset")
    st.markdown("Use this table to explore the raw Netflix dataset — sort, search, and select any rows you want to analyze.")

    try:
        gb = GridOptionsBuilder.from_dataframe(df_filtered)
        gb.configure_pagination(paginationAutoPageSize=True)
        gb.configure_side_bar()
        gb.configure_selection("multiple", use_checkbox=True)
        grid_options = gb.build()

        AgGrid(
            df_filtered,
            gridOptions=grid_options,
            height=350,
            theme="alpine",
            enable_enterprise_modules=False,
            fit_columns_on_grid_load=True
        )
    except Exception as e:
        st.error("⚠️ Unable to render interactive table. Please check your data or dependencies.")
        st.exception(e)

# FOOTER
st.markdown("---")
st.success("✨ Created by Idan Badin | Netflix Project | Data Science 2025 | Reichman University")
