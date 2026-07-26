from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

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
    df["publishedAt"] = pd.to_datetime(df["publishedAt"])
    numeric_cols = ["viewCount", "likeCount", "commentCount"]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df


df = load_data()

# -------------------------
# Last Updated
# -------------------------
last_updated = df["publishedAt"].max()

st.info(
    f"📌 Dashboard Snapshot Date: "
    f"{last_updated.strftime('%d %B %Y')}"
)

# -------------------------
# KPI Cards
# -------------------------
total_views = int(df["viewCount"].sum())
total_likes = int(df["likeCount"].sum())
total_comments = int(df["commentCount"].sum())
total_videos = df["video_id"].nunique()

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
    df.nlargest(10, "viewCount")
    [["title", "viewCount"]]
)

fig_top_views = px.bar(
    top_views,
    x="viewCount",
    y="title",
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
    df.nlargest(10, "likeCount")
    [["title", "likeCount"]]
)

fig_top_likes = px.bar(
    top_likes,
    x="likeCount",
    y="title",
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
st.subheader(" Engagement Analysis ")

fig_engagement = px.scatter(
    df,
    x="viewCount",
    y="likeCount",
    size="commentCount",
    hover_name="title",
    title="Views vs Likes (Bubble Size = Comments)"
)

st.plotly_chart(fig_engagement, width='stretch')

# -------------------------
# Publishing Trend
# -------------------------
st.subheader(" Publishing Trend")

monthly_uploads = (
    df.set_index("publishedAt")
      .resample("ME")
      .size()
      .reset_index(name="Videos")
)

fig_uploads = px.line(
    monthly_uploads,
    x="publishedAt",
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
st.subheader(" Highest Engagement Videos [Engagement_rate = (Likes + Comments) / Views]")

engagement_df = df.copy()

engagement_df["Engagement_Rate"] = (
    (
        engagement_df["likeCount"] +
        engagement_df["commentCount"]
    )
    / engagement_df["viewCount"].replace(0, pd.NA)
) * 100

top_engagement = (
    engagement_df
    .dropna(subset=["Engagement_Rate"])
    .nlargest(
        10,
        "Engagement_Rate"
    )[
        [
            "title",
            "Engagement_Rate",
            "viewCount"
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
        "publishedAt",
        ascending=False
    )
    .head(10)[
        [
            "title",
            "publishedAt",
            "viewCount",
            "likeCount",
            "commentCount"
        ]
    ]
)

st.dataframe(
    recent,
    width='stretch'
)
# ==========================================
# Shorts vs Normal Analysis
# ==========================================

st.divider()
st.subheader(" Shorts vs Normal Videos")

# Create comparison table
comparison = (
    df.groupby("Video_type")
      .agg(
          Videos=("video_id", "count"),
          Avg_Views=("viewCount", "mean"),
          Avg_Likes=("likeCount", "mean"),
          Avg_Comments=("commentCount", "mean"),
      )
      .round(0)
)

# Engagement Rate
engagement_rate = (
    (
        df.groupby("Video_type")["likeCount"].sum()
        + df.groupby("Video_type")["commentCount"].sum()
    )
    / df.groupby("Video_type")["viewCount"].sum()
    * 100
).round(2)

comparison["Engagement_Rate (%)"] = engagement_rate

# Format numbers nicely
comparison["Avg_Views"] = comparison["Avg_Views"].astype(int)
comparison["Avg_Likes"] = comparison["Avg_Likes"].astype(int)
comparison["Avg_Comments"] = comparison["Avg_Comments"].astype(int)

st.dataframe(comparison, use_container_width=True)

# ==========================================
# Average Views Comparison
# ==========================================

st.subheader(" Average Views by Video Type")

avg_views = (
    df.groupby("Video_type")["viewCount"]
      .mean()
      .reset_index()
)

fig_views = px.bar(
    avg_views,
    x="Video_type",
    y="viewCount",
    title="Average Views: Shorts vs Normal",
    text_auto=".0f",
)

fig_views.update_layout(
    xaxis_title="Video Type",
    yaxis_title="Average Views"
)

st.plotly_chart(fig_views, use_container_width=True)

# ==========================================
# Average Likes Comparison
# ==========================================

st.subheader(" Average Likes by Video Type")

avg_likes = (
    df.groupby("Video_type")["likeCount"]
      .mean()
      .reset_index()
)

fig_likes = px.bar(
    avg_likes,
    x="Video_type",
    y="likeCount",
    title="Average Likes: Shorts vs Normal",
    text_auto=".0f",
)

fig_likes.update_layout(
    xaxis_title="Video Type",
    yaxis_title="Average Likes"
)

st.plotly_chart(fig_likes, use_container_width=True)

# ==========================================
# Engagement Rate Comparison
# ==========================================

st.subheader(" Engagement Rate by Video Type")

engagement_df = engagement_rate.reset_index()
engagement_df.columns = ["Video_type", "Engagement_Rate"]

fig_engagement = px.bar(
    engagement_df,
    x="Video_type",
    y="Engagement_Rate",
    title="Engagement Rate (%)",
    text_auto=".2f",
)

fig_engagement.update_layout(
    xaxis_title="Video Type",
    yaxis_title="Engagement Rate (%)"
)

st.plotly_chart(fig_engagement, use_container_width=True)

# -------------------------
# Raw Data
# -------------------------
with st.expander(" View Raw Dataset"):
    st.dataframe(df, width='stretch')