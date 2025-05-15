import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# ================== Page Config ==================
st.set_page_config(page_title="Netflix Visual Explorer", layout="wide", page_icon="🎬")

# ================== Title ==================
st.title("🎬 Netflix Visual Explorer")
st.markdown("""
Welcome to an interactive and beautifully designed data science project analyzing Netflix content.  
Created by **Idan Badin** as part of the Data Science midterm project at Reichman University (2025).
""")

# ================== Load Data ==================
@st.cache_data
def load_data():
    url = "https://drive.google.com/uc?id=1-C3O1uZDLsnYDVTppn0h3SjGOA4LifYE"
    df = pd.read_csv(url)
    df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
    df['year_added'] = df['date_added'].dt.year
    df['duration_num'] = df['duration'].str.extract('(\d+)').astype(float)
    return df

with st.spinner("Loading Netflix dataset... 🔄"):
    df = load_data()

# ================== Sidebar Filters ==================
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/7/75/Netflix_icon.svg", width=90)
st.sidebar.title("⚙️ Filters")
selected_types = st.sidebar.multiselect("Choose Content Type:", df['type'].dropna().unique(), default=df['type'].dropna().unique())
year_range = st.sidebar.slider("Year Added", int(df['year_added'].min()), int(df['year_added'].max()), (2015, 2020))

df_filtered = df[(df['type'].isin(selected_types)) & (df['year_added'].between(*year_range))]

# ================== Content Type Distribution ==================
st.markdown("## 📊 Insight 1: Content Type Distribution")
fig1, ax1 = plt.subplots(figsize=(6, 3.5))
sns.countplot(data=df_filtered, x='type', palette='Set2', ax=ax1)
ax1.set_title("Distribution of Content Types", fontsize=13, weight='bold')
st.pyplot(fig1)

# ================== Titles Over Time ==================
st.markdown("## 📈 Insight 2: Titles Added Over Time")
fig2, ax2 = plt.subplots(figsize=(8, 3.5))
sns.countplot(data=df_filtered[df_filtered['year_added'].notnull()], x='year_added', color='#4a90e2', ax=ax2)
ax2.set_title("Titles Added Per Year", fontsize=13, weight='bold')
ax2.set_xlabel("Year Added")
ax2.set_ylabel("Number of Titles")
plt.xticks(rotation=45)
st.pyplot(fig2)

# ================== Rating Distribution ==================
st.markdown("## 🔖 Insight 3: Rating Distribution")
fig3, ax3 = plt.subplots(figsize=(10, 3.5))
sns.countplot(data=df_filtered, x='rating', hue='type', palette='pastel', ax=ax3)
ax3.set_title("Ratings by Content Type", fontsize=13, weight='bold')
ax3.set_xlabel("Rating")
ax3.set_ylabel("Count")
plt.xticks(rotation=45)
st.pyplot(fig3)

# ================== Movie Duration by Country ==================
st.markdown("## 🎯 Insight 4: Movie Duration by Country (Top 5)")
df_movies = df_filtered[df_filtered['type'] == 'Movie'].copy()
df_movies['duration_min'] = df_movies['duration'].str.extract('(\d+)').astype(float)
top_countries = df_movies['country'].value_counts().head(5).index
df_movies_top = df_movies[df_movies['country'].isin(top_countries)]

fig4, ax4 = plt.subplots(figsize=(8, 3.5))
sns.pointplot(data=df_movies_top, x='country', y='duration_min', hue='country',
              palette='Set1', capsize=.2, ax=ax4, legend=False)
ax4.set_title("Avg. Movie Duration by Country", fontsize=13, weight='bold')
ax4.set_xlabel("Country")
ax4.set_ylabel("Average Duration (minutes)")
st.pyplot(fig4)

# ================== Trend: Movies vs Shows ==================
st.markdown("## 🔄 Insight 5: Trend of Movies vs TV Shows Over Time")
df_trend = df_filtered.groupby(['year_added', 'type']).size().reset_index(name='count')
fig5, ax5 = plt.subplots(figsize=(10, 3.5))
sns.lineplot(data=df_trend, x='year_added', y='count', hue='type', marker='o',
             palette=['#8ecae6', '#219ebc'], ax=ax5)
ax5.set_title("Content Trends Over Time", fontsize=13, weight='bold')
ax5.set_xlabel("Year")
ax5.set_ylabel("Number of Titles")
st.pyplot(fig5)

# ================== Footer ==================
st.markdown("---")
st.success("✨ Built by Idan Badin | Data Science Course | Reichman University | 2025")
