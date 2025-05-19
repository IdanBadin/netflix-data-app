import streamlit as st
import pandas as pd
import plotly.express as px
import random
import openai
from fpdf import FPDF
import base64

# ============ PAGE CONFIG ============
st.set_page_config(page_title="Netflix AI Dashboard", page_icon="🎬", layout="wide")

# ============ CUSTOM CSS ============
st.markdown("""
    <style>
    .animated-title {
        animation: glow 2s ease-in-out infinite alternate;
        color: #e50914;
        font-size: 36px;
        font-weight: bold;
        text-align: center;
    }
    @keyframes glow {
        from { text-shadow: 0 0 10px #e50914; }
        to { text-shadow: 0 0 20px #ff0000; }
    }
    .stButton button:hover {
        background-color: #ff4b4b;
        color: white;
        transition: 0.3s ease;
    }
    .st-emotion-cache-1avcm0n {
        background-color: #e6ffed;
        border-left: 5px solid #00c851;
        padding: 0.8em;
        margin-top: 1em;
        border-radius: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# ============ OPENAI API ============
openai.api_key = st.secrets.get("OPENAI_API_KEY", None)

# ============ LOAD DATA ============
@st.cache_data
def load_data():
    url = "https://drive.google.com/uc?id=1-C3O1uZDLsnYDVTppn0h3SjGOA4LifYE"
    df = pd.read_csv(url)
    df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
    df['year_added'] = df['date_added'].dt.year
    df['duration_num'] = df['duration'].str.extract(r'(\\d+)').astype(float)
    return df

df = load_data()

# ============ HEADER ============
st.markdown('<div class="animated-title">🎬 Netflix Visual Explorer - GPT Edition</div>', unsafe_allow_html=True)
st.markdown("""
Welcome to the **Netflix Visual Explorer** — an AI-powered dashboard built as part of the 📚 *Data Science Midterm Project* at **Reichman University**.
""")

# ============ SIDEBAR ============
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg", use_container_width=True)
st.sidebar.markdown("## 🎛️ Filter Dataset")

types = st.sidebar.multiselect("Select Type", df['type'].dropna().unique(), default=df['type'].dropna().unique())
year_range = st.sidebar.slider("Select Year Range", int(df['year_added'].min()), int(df['year_added'].max()), (2015, 2020))

df_filtered = df[(df['type'].isin(types)) & (df['year_added'].between(*year_range))]

csv = df_filtered.to_csv(index=False).encode()
st.sidebar.download_button("📥 Download CSV", csv, "netflix_filtered.csv", "text/csv")

fact = random.choice([
    "Netflix started as a DVD rental company in 1997 💿",
    "'House of Cards' was its first original series 🃏",
    "Over 100M households watched 'Squid Game' 🦑"
])
st.sidebar.markdown("### 💡 Did You Know?")
st.sidebar.info(fact)

# ============ GPT SUMMARY FUNCTION ============
def gpt_summary(df, tab_name):
    if openai.api_key is None:
        return "🔒 GPT key not set."
    prompt = f"Data from {year_range[0]}–{year_range[1]} on Netflix for {', '.join(types)}. "
    if tab_name == "Overview":
        prompt += "Summarize distribution of content types."
    elif tab_name == "Ratings":
        prompt += "What does the rating distribution say about content targeting?"
    elif tab_name == "Durations":
        prompt += "Which countries have longer average movie durations?"
    elif tab_name == "Trends" or tab_name == "Titles Over Time":
        prompt += "Describe growth in titles over time."
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ GPT error: {e}"

# ============ PDF EXPORT FUNCTION ============
def export_pdf(content, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(200, 10, txt="Netflix Insight Summary", ln=True, align='C')
    pdf.set_font("Helvetica", '', 12)
    pdf.ln(10)
    for line in content.split('\n'):
        pdf.multi_cell(0, 10, line)
    pdf.output(filename)
    with open(filename, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    return f'<a href="data:application/pdf;base64,{base64_pdf}" download="{filename}">📄 Download as PDF</a>'

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
    fig = px.histogram(df_filtered, x='type', color='type')
    st.plotly_chart(fig, use_container_width=True)
    counts = df_filtered['type'].value_counts()
    if not counts.empty:
        pct = (counts / counts.sum() * 100).round(1).to_dict()
        insight = f"In this selection, **{pct.get('Movie',0)}%** are Movies and **{pct.get('TV Show',0)}%** are TV Shows."
        st.success(insight)
    if st.button("🤖 GPT Summary", key="gpt1"):
        s = gpt_summary(df_filtered, "Overview")
        st.success(s)
        st.markdown(export_pdf(s, "overview.pdf"), unsafe_allow_html=True)

with tab2:
    st.subheader("📆 Titles Added Over Time")
    df_year = df_filtered[df_filtered['year_added'].notnull()].copy()
    df_year['year_added'] = df_year['year_added'].astype(int)
    fig = px.histogram(df_year, x='year_added', color_discrete_sequence=["#4a90e2"])
    st.plotly_chart(fig, use_container_width=True)
    if not df_year.empty:
        peak = df_year['year_added'].value_counts().idxmax()
        st.success(f"Most titles were added in **{peak}**.")
    if st.button("🤖 GPT Summary", key="gpt2"):
        s = gpt_summary(df_filtered, "Titles Over Time")
        st.success(s)
        st.markdown(export_pdf(s, "titles_over_time.pdf"), unsafe_allow_html=True)

with tab3:
    st.subheader("🏷️ Ratings Distribution by Type")
    fig = px.histogram(df_filtered, x='rating', color='type', barmode='group')
    st.plotly_chart(fig, use_container_width=True)
    if not df_filtered.empty:
        top_rating = df_filtered['rating'].value_counts().idxmax()
        st.success(f"The most frequent rating is **{top_rating}**.")
    if st.button("🤖 GPT Summary", key="gpt3"):
        s = gpt_summary(df_filtered, "Ratings")
        st.success(s)
        st.markdown(export_pdf(s, "ratings.pdf"), unsafe_allow_html=True)

with tab4:
    st.subheader("⏱️ Average Movie Duration by Country")
    df_movies = df_filtered[df_filtered['type'] == 'Movie'].copy()
    df_movies['duration_min'] = df_movies['duration'].str.extract(r'(\\d+)').astype(float)
    top = df_movies['country'].value_counts().head(5).index
    df_avg = df_movies[df_movies['country'].isin(top)].groupby('country', as_index=False)['duration_min'].mean()

    if not df_avg.empty and not df_avg['duration_min'].isna().all():
        fig = px.bar(df_avg, x='country', y='duration_min', color='country')
        st.plotly_chart(fig, use_container_width=True)
        try:
            top_country = df_avg.loc[df_avg['duration_min'].idxmax()]
            st.success(f"🏆 Longest: {top_country['country']} – {round(top_country['duration_min'])} minutes")
        except Exception:
            st.warning("⚠️ Could not determine top country.")
    else:
        st.warning("No duration data available.")
    if st.button("🤖 GPT Summary", key="gpt4"):
        s = gpt_summary(df_filtered, "Durations")
        st.success(s)
        st.markdown(export_pdf(s, "durations.pdf"), unsafe_allow_html=True)

with tab5:
    st.subheader("📈 Content Growth Trends")
    df_trend = df_filtered.groupby(['year_added', 'type']).size().reset_index(name='count')
    fig = px.line(df_trend, x='year_added', y='count', color='type', markers=True)
    st.plotly_chart(fig, use_container_width=True)
    if st.button("🤖 GPT Summary", key="gpt5"):
        s = gpt_summary(df_filtered, "Trends")
        st.success(s)
        st.markdown(export_pdf(s, "trends.pdf"), unsafe_allow_html=True)

# ============ FOOTER ============
st.markdown("---")
st.success("✨ Built with ❤️ by Idan Badin | Netflix GPT Dashboard | Reichman University 2025")
