
# 🧠 Netflix Super App - Final Premium Version by Idan Badin

import streamlit as st
import pandas as pd
import plotly.express as px
import pyttsx3
import base64
import random
import json

# ============ PAGE CONFIG ==============
st.set_page_config(page_title="Netflix AI Dashboard", page_icon="🎬", layout="wide")

# ============ AUDIO NARRATION ============
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

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

# ============ FILTERS + MEMORY ============
if "selected_tab" not in st.session_state:
    st.session_state.selected_tab = "Overview"

tabs = ["Overview", "Titles Over Time", "Ratings", "Durations", "Trends"]

selected_tab = st.sidebar.radio("📍 Navigate", tabs, index=tabs.index(st.session_state.selected_tab))
st.session_state.selected_tab = selected_tab

st.sidebar.markdown("### 🎛️ Filter Dataset")
types = st.sidebar.multiselect("Select Type", df['type'].dropna().unique(), default=df['type'].dropna().unique())
year_range = st.sidebar.slider("Select Year Range", int(df['year_added'].min()), int(df['year_added'].max()), (2015, 2020))

df_filtered = df[(df['type'].isin(types)) & (df['year_added'].between(*year_range))]

# ============ CSV DOWNLOAD ============
def get_table_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="netflix_filtered.csv">📥 Download CSV</a>'
    return href

# ============ EASTER EGG ============
if df_filtered.shape[0] == 1984:
    st.balloons()
    st.success("🎉 You unlocked a secret Netflix number... 1984 titles exactly!")

# ============ APP HEADER ============
st.markdown(f"<h2 style='color:#E50914;'>🎬 Netflix Visual Explorer - Premium AI Edition</h2>", unsafe_allow_html=True)
st.markdown(f"Filtered dataset: **{df_filtered.shape[0]} titles**, Years: {year_range[0]} to {year_range[1]}")
st.markdown(get_table_download_link(df_filtered), unsafe_allow_html=True)

# ============ LIVE AI SUMMARY (Placeholder) ============
if st.button("🤖 Summarize this View"):
    summary = f"This filtered view contains {df_filtered.shape[0]} titles spanning {year_range[1] - year_range[0] + 1} years, mostly of type {df_filtered['type'].mode()[0]}."
    st.info("💬 GPT says: " + summary)
    if st.button("🔊 Narrate Summary"):
        speak(summary)

# ============ EACH TAB CONTENT ============
if selected_tab == "Overview":
    st.subheader("📊 Content Type Overview")
    fig = px.histogram(df_filtered, x='type', color='type', title="Distribution of Movies vs TV Shows",
                       color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(fig, use_container_width=True)
    insight = f"Most content is of type {df_filtered['type'].mode()[0]}."
    st.success("🧠 Insight: " + insight)
    if st.button("🎧 Narrate Insight - Overview"):
        speak(insight)

elif selected_tab == "Titles Over Time":
    st.subheader("📆 Titles Added Over Time")
    df_clean = df_filtered[df_filtered['year_added'].notnull()].copy()
    df_clean['year_added'] = df_clean['year_added'].astype(int)
    fig = px.histogram(df_clean, x='year_added', nbins=20, color_discrete_sequence=['#4a90e2'])
    st.plotly_chart(fig, use_container_width=True)
    if not df_clean.empty:
        year = int(df_clean['year_added'].mode()[0])
        insight = f"Most titles were added in {year}."
        st.info("🧠 Insight: " + insight)
        if st.button("🎧 Narrate Insight - Titles Over Time"):
            speak(insight)

elif selected_tab == "Ratings":
    st.subheader("🏷️ Rating Distribution")
    fig = px.histogram(df_filtered, x='rating', color='type', barmode='group',
                       title="Content Ratings by Type",
                       color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig, use_container_width=True)
    top_rating = df_filtered['rating'].value_counts().idxmax() if not df_filtered.empty else "N/A"
    insight = f"The most frequent rating is {top_rating}."
    st.warning("🧠 Insight: " + insight)
    if st.button("🎧 Narrate Insight - Ratings"):
        speak(insight)

elif selected_tab == "Durations":
    st.subheader("⏱️ Average Movie Duration by Country")
    df_movies = df_filtered[df_filtered['type'] == 'Movie'].copy()
    df_movies['duration_min'] = df_movies['duration'].str.extract(r'(\d+)').astype(float)
    top_countries = df_movies['country'].value_counts().head(5).index
    df_top = df_movies[df_movies['country'].isin(top_countries)]
    df_avg = df_top.groupby('country')['duration_min'].mean().reset_index()
    fig = px.bar(df_avg, x='country', y='duration_min', color='country')
    st.plotly_chart(fig, use_container_width=True)
    if not df_top.empty:
        max_dur = df_avg.loc[df_avg['duration_min'].idxmax()]
        insight = f"{max_dur['country']} has the longest average movie duration: {round(max_dur['duration_min'])} minutes."
        st.success("🧠 Insight: " + insight)
        if st.button("🎧 Narrate Insight - Duration"):
            speak(insight)

elif selected_tab == "Trends":
    st.subheader("📈 Content Growth Over Time")
    df_trend = df_filtered.groupby(['year_added', 'type']).size().reset_index(name='count')
    fig = px.line(df_trend, x='year_added', y='count', color='type', markers=True,
                  title="Growth of Content Types Over Time",
                  color_discrete_sequence=px.colors.qualitative.Bold)
    st.plotly_chart(fig, use_container_width=True)
    insight = f"From {year_range[0]} to {year_range[1]}, Netflix saw consistent growth across content types."
    st.info("🧠 Insight: " + insight)
    if st.button("🎧 Narrate Insight - Trends"):
        speak(insight)

# ============ FOOTER ==============
st.markdown("---")
st.markdown("✨ Built with ❤️ by **Idan Badin** | AI-Powered Netflix Dashboard | Reichman University 2025")
