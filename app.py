# 🔥 Netflix Visual Explorer - Final AI-Powered Version
import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import random
import json
import openai

# ============ SETUP =============
st.set_page_config(page_title="Netflix AI Dashboard", page_icon="🎬", layout="wide")
openai.api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else "sk-your-key"

# ============ LOAD DATA ==========
@st.cache_data
def load_data():
    url = "https://drive.google.com/uc?id=1-C3O1uZDLsnYDVTppn0h3SjGOA4LifYE"
    df = pd.read_csv(url)
    df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
    df['year_added'] = df['date_added'].dt.year
    df['duration_num'] = df['duration'].str.extract(r'(\\d+)').astype(float)
    return df

df = load_data()

# ============ SIDEBAR FILTERS + FLOAT NAV ==========
with st.sidebar:
    st.markdown("## 🎛️ Navigation")
    tab = st.radio("", ["📊 Overview", "📆 Titles Over Time", "🏷️ Ratings", "⏱️ Durations", "📈 Trends"], index=0)

    st.markdown("### 🧲 Filter")
    types = st.multiselect("Type", df['type'].dropna().unique(), default=df['type'].dropna().unique())
    year_range = st.slider("Year Added", int(df['year_added'].min()), int(df['year_added'].max()), (2015, 2020))

    df_filtered = df[(df['type'].isin(types)) & (df['year_added'].between(*year_range))]

    # Download button
    csv = df_filtered.to_csv(index=False).encode()
    st.download_button("📥 Download Filtered CSV", csv, "netflix_data.csv", "text/csv")

    # Easter Egg
    if df_filtered.shape[0] == 1984:
        st.balloons()
        st.success("🎉 You found 1984 titles exactly. Secret unlocked!")

    # Random fact
    fact = random.choice([
        "Netflix started as a DVD rental company in 1997 💿",
        "'House of Cards' was its first original series 🃏",
        "Over 100M households watched 'Squid Game' 🦑",
        "Netflix operates in 190+ countries 🌎",
        "The Netflix logo got its current look in 2014 🔴"
    ])
    st.markdown("### 💡 Did You Know?")
    st.info(fact)

# ============ GPT LIVE SUMMARY ==========
def gpt_summary(df, title="Netflix Data"):
    prompt = f"Summarize the following Netflix dataset of {df.shape[0]} rows in 2 sentences:\n\n{df.head(10).to_string(index=False)}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return "🔒 GPT key not set or limit reached."

# ============ SPEAK FUNCTION =============
def speak(text):
    st.markdown(f"""
    <script>
    var msg = new SpeechSynthesisUtterance("{text}");
    window.speechSynthesis.speak(msg);
    </script>
    """, unsafe_allow_html=True)

# ============ APP HEADER ==========
st.markdown("<h2 style='color:#E50914;'>🎬 Netflix Visual Explorer - GPT Edition</h2>", unsafe_allow_html=True)
st.markdown(f"🎯 Filtered: **{df_filtered.shape[0]} titles**, Years: {year_range[0]} to {year_range[1]}")

# ============ MAIN PANELS ==============
if tab == "📊 Overview":
    st.subheader("📊 Content Type Overview")
    fig = px.histogram(df_filtered, x='type', color='type', title="Distribution of Movies vs TV Shows")
    st.plotly_chart(fig, use_container_width=True)
    insight = f"Most content is of type {df_filtered['type'].mode()[0]}."
    st.success(insight)
    speak(insight)

elif tab == "📆 Titles Over Time":
    st.subheader("📆 Titles Added Each Year")
    df_year = df_filtered[df_filtered['year_added'].notnull()].copy()
    df_year['year_added'] = df_year['year_added'].astype(int)
    fig = px.histogram(df_year, x='year_added', color_discrete_sequence=["#4a90e2"])
    st.plotly_chart(fig, use_container_width=True)
    most = int(df_year['year_added'].mode()[0]) if not df_year.empty else "N/A"
    insight = f"The peak year for new titles was {most}."
    st.info(insight)
    speak(insight)

elif tab == "🏷️ Ratings":
    st.subheader("🏷️ Content Ratings by Type")
    fig = px.histogram(df_filtered, x='rating', color='type', barmode='group')
    st.plotly_chart(fig, use_container_width=True)
    rating = df_filtered['rating'].value_counts().idxmax() if not df_filtered.empty else "N/A"
    insight = f"The most common rating is {rating}."
    st.warning(insight)
    speak(insight)

elif tab == "⏱️ Durations":
    st.subheader("⏱️ Average Movie Duration by Country")
    df_movies = df_filtered[df_filtered['type'] == 'Movie'].copy()
    df_movies['duration_min'] = df_movies['duration'].str.extract(r'(\\d+)').astype(float)
    top = df_movies['country'].value_counts().head(5).index
    df_avg = df_movies[df_movies['country'].isin(top)].groupby('country')['duration_min'].mean().reset_index()
    fig = px.bar(df_avg, x='country', y='duration_min', color='country')
    st.plotly_chart(fig, use_container_width=True)
    if not df_avg.empty:
        top_country = df_avg.loc[df_avg['duration_min'].idxmax()]
        insight = f"{top_country['country']} has the longest average movie duration: {round(top_country['duration_min'])} minutes."
        st.success(insight)
        speak(insight)

elif tab == "📈 Trends":
    st.subheader("📈 Content Growth Trends")
    df_trend = df_filtered.groupby(['year_added', 'type']).size().reset_index(name='count')
    fig = px.line(df_trend, x='year_added', y='count', color='type', markers=True)
    st.plotly_chart(fig, use_container_width=True)
    insight = f"From {year_range[0]} to {year_range[1]}, Netflix saw consistent growth across content types."
    st.info(insight)
    speak(insight)

# ============ GPT AUTO SUMMARY ==========
if st.button("🤖 GPT Summary of This View"):
    summary = gpt_summary(df_filtered)
    st.markdown("#### 💬 GPT Summary")
    st.success(summary)
    speak(summary)

# ============ FOOTER ==========
st.markdown("---")
st.markdown("✨ Built with ❤️ by **Idan Badin** | AI-Powered Netflix Streamlit Project | Reichman University 2025")
