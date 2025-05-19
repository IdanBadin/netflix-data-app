import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import random
import openai

# ============ PAGE CONFIG ============
st.set_page_config(page_title="Netflix AI Dashboard", page_icon="🎬", layout="wide")

# ============ OPENAI API ============
openai.api_key = st.secrets.get("OPENAI_API_KEY", None)

# ============ LOAD DATA ============
@st.cache_data
def load_data():
    url = "https://drive.google.com/uc?id=1-C3O1uZDLsnYDVTppn0h3SjGOA4LifYE"
    df = pd.read_csv(url)
    df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
    df['year_added'] = df['date_added'].dt.year
    df['duration_num'] = df['duration'].str.extract(r'(\d+)').astype(float)
    return df

df = load_data()

# ============ HEADER ============
st.title("🎬 Netflix Visual Explorer - GPT Edition")
st.markdown("""
This AI-powered dashboard was created as part of the **Data Science Midterm Project** at **Reichman University** 🎓.  
It uses **OpenAI's GPT** to generate summaries of Netflix insights based on your filtered data.

Explore:
- 📊 Type distributions  
- 📆 Titles over time  
- 🏷️ Ratings  
- ⏱️ Durations by country  
- 📈 Growth trends
""")

# ============ SIDEBAR ============
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg", use_container_width=True)
st.sidebar.markdown("## 🎛️ Filter Dataset")

types = st.sidebar.multiselect("Select Type", df['type'].dropna().unique(), default=df['type'].dropna().unique())
year_range = st.sidebar.slider("Select Year Range", int(df['year_added'].min()), int(df['year_added'].max()), (2015, 2020))

df_filtered = df[(df['type'].isin(types)) & (df['year_added'].between(*year_range))]

# ============ CSV DOWNLOAD ============
csv = df_filtered.to_csv(index=False).encode()
st.sidebar.download_button("📥 Download Filtered CSV", csv, "netflix_filtered.csv", "text/csv")

# ============ RANDOM FACT ============
fact = random.choice([
    "Netflix started as a DVD rental company in 1997 💿",
    "'House of Cards' was its first original series 🃏",
    "Over 100M households watched 'Squid Game' 🦑",
    "Netflix operates in 190+ countries 🌎",
    "The Netflix logo got its current look in 2014 🔴"
])
st.sidebar.markdown("### 💡 Did You Know?")
st.sidebar.info(fact)

# ============ GPT SUMMARY FUNCTION ============
def gpt_summary(df):
    if openai.api_key is None:
        return "🔒 GPT key not set. Add it in Streamlit Secrets."
    try:
        prompt = f"Summarize this Netflix dataset with {df.shape[0]} rows:\n\n{df.head(10).to_string(index=False)}"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return "⚠️ GPT error or usage limit reached."

# ============ TABS ============
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview",
    "📆 Titles Over Time",
    "🏷️ Ratings",
    "⏱️ Durations",
    "📈 Trends"
])

with tab1:
    st.subheader("📊 Content Type Overview")
    st.markdown(f"Showing **{df_filtered.shape[0]} titles** from **{year_range[0]} to {year_range[1]}**")
    fig = px.histogram(df_filtered, x='type', color='type', title="Distribution of Movies vs TV Shows")
    st.plotly_chart(fig, use_container_width=True)
    if not df_filtered.empty:
        insight = f"Most content is of type {df_filtered['type'].mode()[0]}."
        st.success(insight)

    if st.button("🤖 GPT Summary of This View", key="gpt1"):
        st.markdown("#### 💬 GPT Summary")
        summary = gpt_summary(df_filtered)
        st.success(summary)

with tab2:
    st.subheader("📆 Titles Added Each Year")
    df_year = df_filtered[df_filtered['year_added'].notnull()].copy()
    df_year['year_added'] = df_year['year_added'].astype(int)
    fig = px.histogram(df_year, x='year_added', color_discrete_sequence=["#4a90e2"])
    st.plotly_chart(fig, use_container_width=True)
    if not df_year.empty:
        most = int(df_year['year_added'].mode()[0])
        st.info(f"The peak year for new titles was {most}.")

    if st.button("🤖 GPT Summary of This View", key="gpt2"):
        st.markdown("#### 💬 GPT Summary")
        summary = gpt_summary(df_filtered)
        st.success(summary)

with tab3:
    st.subheader("🏷️ Content Ratings by Type")
    fig = px.histogram(df_filtered, x='rating', color='type', barmode='group')
    st.plotly_chart(fig, use_container_width=True)
    if not df_filtered.empty:
        rating = df_filtered['rating'].value_counts().idxmax()
        st.warning(f"The most common rating is {rating}.")

    if st.button("🤖 GPT Summary of This View", key="gpt3"):
        st.markdown("#### 💬 GPT Summary")
        summary = gpt_summary(df_filtered)
        st.success(summary)

with tab4:
    st.subheader("⏱️ Average Movie Duration by Country")
    df_movies = df_filtered[df_filtered['type'] == 'Movie'].copy()
    df_movies['duration_min'] = df_movies['duration'].str.extract(r'(\d+)').astype(float)
    top = df_movies['country'].value_counts().head(5).index
    df_avg = df_movies[df_movies['country'].isin(top)].groupby('country', as_index=False)['duration_min'].mean()
    if not df_avg.empty:
        fig = px.bar(df_avg, x='country', y='duration_min', color='country')
        st.plotly_chart(fig, use_container_width=True)
        top_country = df_avg.loc[df_avg['duration_min'].idxmax()]
        st.success(f"{top_country['country']} has the longest average movie duration: {round(top_country['duration_min'])} minutes.")
    else:
        st.warning("No data available for movie durations.")

    if st.button("🤖 GPT Summary of This View", key="gpt4"):
        st.markdown("#### 💬 GPT Summary")
        summary = gpt_summary(df_filtered)
        st.success(summary)

with tab5:
    st.subheader("📈 Content Growth Trends")
    df_trend = df_filtered.groupby(['year_added', 'type']).size().reset_index(name='count')
    fig = px.line(df_trend, x='year_added', y='count', color='type', markers=True)
    st.plotly_chart(fig, use_container_width=True)
    st.info(f"From {year_range[0]} to {year_range[1]}, Netflix saw consistent growth across content types.")

    if st.button("🤖 GPT Summary of This View", key="gpt5"):
        st.markdown("#### 💬 GPT Summary")
        summary = gpt_summary(df_filtered)
        st.success(summary)

# ============ FOOTER ============
st.markdown("---")
st.markdown("✨ Built with ❤️ by **Idan Badin** | Netflix GPT Dashboard | Reichman University 2025")
