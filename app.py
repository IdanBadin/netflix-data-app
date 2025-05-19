import streamlit as st
import pandas as pd
import plotly.express as px
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
Welcome to the **Netflix Visual Explorer** — an interactive and AI-powered dashboard built as part of the 📚 *Data Science Midterm Project* at **Reichman University**.

This app combines data analysis and storytelling to explore how **Netflix's catalog evolved** over time, using real-world data.

You'll discover:
- 📊 What types of content dominate Netflix's library  
- 📆 When titles were added and how growth changed year to year  
- 🏷️ Which ratings are most common  
- ⏱️ Where movies tend to be the longest  
- 📈 How streaming trends evolved globally  

With the power of **OpenAI’s GPT**, each view includes intelligent summaries that update with your filters, helping you uncover deeper insights — effortlessly.
""")

# ============ SIDEBAR ============
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg", use_container_width=True)
st.sidebar.markdown("## 🎛️ Filter Dataset")

types = st.sidebar.multiselect("Select Type", df['type'].dropna().unique(), default=df['type'].dropna().unique())
year_range = st.sidebar.slider("Select Year Range", int(df['year_added'].min()), int(df['year_added'].max()), (2015, 2020))

df_filtered = df[(df['type'].isin(types)) & (df['year_added'].between(*year_range))]

# ============ DOWNLOAD ============
csv = df_filtered.to_csv(index=False).encode()
st.sidebar.download_button("📥 Download Filtered CSV", csv, "netflix_filtered.csv", "text/csv")

# ============ FUN FACT ============
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
def gpt_summary(df, tab_name):
    if openai.api_key is None:
        return "🔒 GPT key not set in Streamlit secrets."

    base_prompt = f"You are analyzing a Netflix dataset with {df.shape[0]} rows.\n"
    year_info = f"The selected year range is from {year_range[0]} to {year_range[1]}.\n"
    type_info = f"The selected content types are: {', '.join(types)}.\n"

    if tab_name == "Overview":
        specific = "Summarize what this says about the balance of Movies and TV Shows."
    elif tab_name == "Titles Over Time":
        specific = "What patterns are visible in title additions over time?"
    elif tab_name == "Ratings":
        specific = "Which ratings are most common and what does it imply about content targeting?"
    elif tab_name == "Durations":
        specific = "Which countries appear to have longer average movie durations?"
    elif tab_name == "Trends":
        specific = "Describe growth trends across content types by year."

    full_prompt = base_prompt + year_info + type_info + specific

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": full_prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ GPT error: {str(e)}"

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
    st.markdown(f"**{df_filtered.shape[0]} titles** from **{year_range[0]} to {year_range[1]}** | Types: {', '.join(types)}")
    fig = px.histogram(df_filtered, x='type', color='type')
    st.plotly_chart(fig, use_container_width=True)

    if not df_filtered.empty:
        count_info = df_filtered['type'].value_counts().to_dict()
        explanation = f"Movies: {count_info.get('Movie', 0)}, TV Shows: {count_info.get('TV Show', 0)}"
        st.success(f"📊 Breakdown → {explanation}")

    if st.button("🤖 GPT Summary of This View", key="gpt1"):
        st.markdown("#### 💬 GPT Summary")
        summary = gpt_summary(df_filtered, "Overview")
        st.success(summary)

with tab2:
    st.subheader("📆 Titles Added Over Time")
    df_year = df_filtered[df_filtered['year_added'].notnull()].copy()
    df_year['year_added'] = df_year['year_added'].astype(int)
    fig = px.histogram(df_year, x='year_added', color_discrete_sequence=["#4a90e2"])
    st.plotly_chart(fig, use_container_width=True)

    if not df_year.empty:
        most = int(df_year['year_added'].mode()[0])
        st.info(f"🎯 Most titles were added in {most}")

    if st.button("🤖 GPT Summary of This View", key="gpt2"):
        st.markdown("#### 💬 GPT Summary")
        summary = gpt_summary(df_filtered, "Titles Over Time")
        st.success(summary)

with tab3:
    st.subheader("🏷️ Ratings by Content Type")
    fig = px.histogram(df_filtered, x='rating', color='type', barmode='group')
    st.plotly_chart(fig, use_container_width=True)

    if not df_filtered.empty:
        rating = df_filtered['rating'].value_counts().idxmax()
        st.warning(f"🏷️ Most common rating: {rating}")

    if st.button("🤖 GPT Summary of This View", key="gpt3"):
        st.markdown("#### 💬 GPT Summary")
        summary = gpt_summary(df_filtered, "Ratings")
        st.success(summary)

with tab4:
    st.subheader("⏱️ Average Movie Duration by Country")
    df_movies = df_filtered[df_filtered['type'] == 'Movie'].copy()
    df_movies['duration_min'] = df_movies['duration'].str.extract(r'(\\d+)').astype(float)
    top = df_movies['country'].value_counts().head(5).index
    df_avg = df_movies[df_movies['country'].isin(top)].groupby('country', as_index=False)['duration_min'].mean()

    if not df_avg.empty:
        fig = px.bar(df_avg, x='country', y='duration_min', color='country')
        st.plotly_chart(fig, use_container_width=True)
        top_country = df_avg.loc[df_avg['duration_min'].idxmax()]
        st.success(f"⏱️ Longest average: {top_country['country']} – {round(top_country['duration_min'])} min")
    else:
        st.warning("No data available for movie durations.")

    if st.button("🤖 GPT Summary of This View", key="gpt4"):
        st.markdown("#### 💬 GPT Summary")
        summary = gpt_summary(df_filtered, "Durations")
        st.success(summary)

with tab5:
    st.subheader("📈 Content Growth Over Time")
    df_trend = df_filtered.groupby(['year_added', 'type']).size().reset_index(name='count')
    fig = px.line(df_trend, x='year_added', y='count', color='type', markers=True)
    st.plotly_chart(fig, use_container_width=True)

    if st.button("🤖 GPT Summary of This View", key="gpt5"):
        st.markdown("#### 💬 GPT Summary")
        summary = gpt_summary(df_filtered, "Trends")
        st.success(summary)

# ============ FOOTER ============
st.markdown("---")
st.markdown("✨ Built with ❤️ by **Idan Badin** | Netflix GPT Dashboard | Reichman University 2025")
