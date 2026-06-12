import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
csv_path = BASE_DIR / "yt_api_12-06-2026.csv"



# -------------------------
# Page Configuration
# -------------------------
st.set_page_config(
    page_title="YouTube Analytics Dashboard",
    page_icon="📺",
    layout="wide"
)

st.title("📺 YouTube Analytics Dashboard")
st.caption("MrBeast YouTube Analytics | Snapshot-based Dashboard")

# -------------------------
# Load Data
# -------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(csv_path)

    # Convert data types
    df["Published_at"] = pd.to_datetime(df["Published_at"])
    numeric_cols = ["View_count", "Like_count", "Comment_count"]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


df = load_data()

# -------------------------
# Last Updated
# -------------------------
last_updated = df["Published_at"].max()

st.info(
    f"📌 Dashboard Snapshot Date: "
    f"{last_updated.strftime('%d %B %Y')}"
)

# -------------------------
# KPI Cards
# -------------------------
total_views = int(df["View_count"].sum())
total_likes = int(df["Like_count"].sum())
total_comments = int(df["Comment_count"].sum())
total_videos = df["Video_id"].nunique()

col1, col2, col3, col4 = st.columns(4)

col1.metric(" Videos", f"{total_videos:,}")
col2.metric(" Total Views", f"{total_views:,}")
col3.metric(" Total Likes", f"{total_likes:,}")
col4.metric(" Total Comments", f"{total_comments:,}")

st.divider()

# -------------------------
# Top 10 Videos by Views
# -------------------------
st.subheader(" Top 10 Videos by Views")

top_views = (
    df.nlargest(10, "View_count")
    [["Video_title", "View_count"]]
)

fig_top_views = px.bar(
    top_views,
    x="View_count",
    y="Video_title",
    orientation="h",
    title="Top Performing Videos",
)

fig_top_views.update_layout(
    yaxis={"categoryorder": "total ascending"},
    xaxis_title="Views",
    yaxis_title=""
)

st.plotly_chart(fig_top_views, width='stretch')

# -------------------------
# Top 10 Videos by Likes
# -------------------------
st.subheader(" Top 10 Videos by Likes")

top_likes = (
    df.nlargest(10, "Like_count")
    [["Video_title", "Like_count"]]
)

fig_top_likes = px.bar(
    top_likes,
    x="Like_count",
    y="Video_title",
    orientation="h",
    title="Most Liked Videos",
)

fig_top_likes.update_layout(
    yaxis={"categoryorder": "total ascending"},
    xaxis_title="Likes",
    yaxis_title=""
)

st.plotly_chart(fig_top_likes, width='stretch')

# -------------------------
# Engagement Analysis
# -------------------------
st.subheader(" Engagement Analysis")

fig_engagement = px.scatter(
    df,
    x="View_count",
    y="Like_count",
    size="Comment_count",
    hover_name="Video_title",
    title="Views vs Likes (Bubble Size = Comments)"
)

st.plotly_chart(fig_engagement, width='stretch')

# -------------------------
# Publishing Trend
# -------------------------
st.subheader(" Publishing Trend")

monthly_uploads = (
    df.set_index("Published_at")
      .resample("ME")
      .size()
      .reset_index(name="Videos")
)

fig_uploads = px.line(
    monthly_uploads,
    x="Published_at",
    y="Videos",
    markers=True,
    title="Videos Published Over Time"
)

fig_uploads.update_layout(
    xaxis_title="Date",
    yaxis_title="Number of Videos"
)

st.plotly_chart(fig_uploads, width='stretch')

# -------------------------
# Engagement Rate Ranking
# -------------------------
st.subheader(" Highest Engagement Videos")

engagement_df = df.copy()

engagement_df["Engagement_Rate"] = (
    (
        engagement_df["Like_count"] +
        engagement_df["Comment_count"]
    )
    / engagement_df["View_count"].replace(0, pd.NA)
) * 100

top_engagement = (
    engagement_df
    .dropna(subset=["Engagement_Rate"])
    .nlargest(
        10,
        "Engagement_Rate"
    )[
        [
            "Video_title",
            "Engagement_Rate",
            "View_count"
        ]
    ]
)

top_engagement["Engagement_Rate"] = (
    top_engagement["Engagement_Rate"]
    .round(2)
)

st.dataframe(
    top_engagement,
    width='stretch'
)

# -------------------------
# Recent Uploads
# -------------------------
st.subheader(" Most Recent Uploads")

recent = (
    df.sort_values(
        "Published_at",
        ascending=False
    )
    .head(10)[
        [
            "Video_title",
            "Published_at",
            "View_count",
            "Like_count",
            "Comment_count"
        ]
    ]
)

st.dataframe(
    recent,
    width='stretch'
)

# -------------------------
# Raw Data
# -------------------------
with st.expander(" View Raw Dataset"):
    st.dataframe(df, width='stretch')

