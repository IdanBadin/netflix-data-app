import streamlit as st
import pandas as pd
import plotly.express as px
import random
import openai
from fpdf import FPDF
import base64

# Page setup
st.set_page_config(page_title="Netflix AI Dashboard", page_icon="🎬", layout="wide")

# Styling
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

# Load data
@st.cache_data
def load_data():
    url = "https://drive.google.com/uc?id=1-C3O1uZDLsnYDVTppn0h3SjGOA4LifYE"
    df = pd.read_csv(url)
    df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
    df['year_added'] = df['date_added'].dt.year
    df['duration_num'] = df['duration'].str.extract(r'(\\d+)')
    df['duration_num'] = pd.to_numeric(df['duration_num'], errors='coerce')
    return df

df = load_data()

# Header
st.markdown('<div class="animated-title">🎬 Netflix Visual Explorer - GPT Edition</div>', unsafe_allow_html=True)
st.markdown("Welcome to the **Netflix Visual Explorer** — created as part of the 📚 *Data Science Midterm Project* at **Reichman University**.")

# Sidebar
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg", use_container_width=True)
types = st.sidebar.multiselect("Select Type", df['type'].dropna().unique(), default=df['type'].dropna().unique())
year_range = st.sidebar.slider("Select Year Range", int(df['year_added'].min()), int(df['year_added'].max()), (2015, 2020))
df_filtered = df[(df['type'].isin(types)) & (df['year_added'].between(*year_range))]

st.sidebar.download_button("📥 Download CSV", df_filtered.to_csv(index=False).encode(), "netflix_filtered.csv", "text/csv")

fact = random.choice([
    "Netflix started as a DVD rental company in 1997 💿",
    "'House of Cards' was its first original series 🃏",
    "Over 100M households watched 'Squid Game' 🦑"
])
st.sidebar.markdown("### 💡 Fun Fact")
st.sidebar.info(fact)

# GPT summary
openai.api_key = st.secrets.get("OPENAI_API_KEY", None)

def gpt_summary(df, tab):
    if openai.api_key is None:
        return "🔒 GPT key not set."
    prompt = f"Netflix data from {year_range[0]} to {year_range[1]} for types {', '.join(types)}. "
    prompt += {
        "Overview": "Summarize the distribution of content types.",
        "Ratings": "Summarize rating distribution and content maturity.",
        "Durations": "Which countries tend to have longer movies?",
        "Trends": "Summarize content growth trends.",
        "Titles Over Time": "Summarize annual title addition trends."
    }.get(tab, "Provide insights.")
    try:
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ GPT error: {e}"

# PDF export
def export_pdf(content, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(200, 10, "Netflix Insight Summary", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Helvetica", size=12)
    for line in content.split('\n'):
        pdf.multi_cell(0, 10, line)
    pdf.output(filename)
    with open(filename, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f'<a href="data:application/pdf;base64,{b64}" download="{filename}">📄 Download PDF</a>'

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Overview", "📆 Titles Over Time", "🏷️ Ratings", "⏱️ Durations", "📈 Trends"])

with tab1:
    st.subheader("📊 Content Type Overview")
    fig = px.histogram(df_filtered, x='type', color='type')
    st.plotly_chart(fig, use_container_width=True)
    counts = df_filtered['type'].value_counts(normalize=True).round(2)*100
    st.success(f"{counts.to_dict()}")
    if st.button("GPT Summary", key="gpt1"):
        s = gpt_summary(df_filtered, "Overview")
        st.success(s)
        st.markdown(export_pdf(s, "overview.pdf"), unsafe_allow_html=True)

with tab2:
    st.subheader("📆 Titles Over Time")
    df_yr = df_filtered[df_filtered['year_added'].notnull()].copy()
    df_yr['year_added'] = df_yr['year_added'].astype(int)
    fig = px.histogram(df_yr, x='year_added', color_discrete_sequence=["#4a90e2"])
    st.plotly_chart(fig, use_container_width=True)
    if st.button("GPT Summary", key="gpt2"):
        s = gpt_summary(df_filtered, "Titles Over Time")
        st.success(s)
        st.markdown(export_pdf(s, "titles.pdf"), unsafe_allow_html=True)

with tab3:
    st.subheader("🏷️ Ratings by Type")
    fig = px.histogram(df_filtered, x='rating', color='type', barmode='group')
    st.plotly_chart(fig, use_container_width=True)
    if st.button("GPT Summary", key="gpt3"):
        s = gpt_summary(df_filtered, "Ratings")
        st.success(s)
        st.markdown(export_pdf(s, "ratings.pdf"), unsafe_allow_html=True)

with tab4:
    st.subheader("⏱️ Avg Movie Duration by Country")
    df_movies = df_filtered[(df_filtered['type'] == 'Movie') & df_filtered['duration_num'].notnull() & df_filtered['country'].notnull()]
    if df_movies.empty:
        st.warning("⚠️ No valid movie data with both duration and country.")
    else:
        top_countries = df_movies['country'].value_counts().head(5).index
        df_top = df_movies[df_movies['country'].isin(top_countries)]
        df_avg = df_top.groupby('country')['duration_num'].mean().reset_index()
        fig = px.bar(df_avg, x='country', y='duration_num', color='country')
        st.plotly_chart(fig, use_container_width=True)
        max_country = df_avg.loc[df_avg['duration_num'].idxmax()]
        st.success(f"🏆 Longest avg movie: {max_country['country']} — {round(max_country['duration_num'])} min")
        if st.button("GPT Summary", key="gpt4"):
            s = gpt_summary(df_filtered, "Durations")
            st.success(s)
            st.markdown(export_pdf(s, "durations.pdf"), unsafe_allow_html=True)

with tab5:
    st.subheader("📈 Content Growth Trends")
    df_trend = df_filtered.groupby(['year_added', 'type']).size().reset_index(name='count')
    fig = px.line(df_trend, x='year_added', y='count', color='type', markers=True)
    st.plotly_chart(fig, use_container_width=True)
    if st.button("GPT Summary", key="gpt5"):
        s = gpt_summary(df_filtered, "Trends")
        st.success(s)
        st.markdown(export_pdf(s, "trends.pdf"), unsafe_allow_html=True)

# Footer
st.markdown("---")
st.success("✨ Built with ❤️ by Idan Badin | Netflix GPT Dashboard | Reichman University 2025")
