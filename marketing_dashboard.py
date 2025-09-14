import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

# ------------------------
# Load & Prepare Data
# ------------------------
def load_and_prepare_data():
    # Load all CSVs (use exact lowercase names as in repo)
    business_df = pd.read_csv("business.csv")
    facebook_df = pd.read_csv("facebook.csv")
    google_df = pd.read_csv("google.csv")
    tiktok_df = pd.read_csv("tiktok.csv")

    # Normalize column names
    for df in [business_df, facebook_df, google_df, tiktok_df]:
        df.columns = df.columns.str.strip().str.lower()

    # Parse dates
    for df in [business_df, facebook_df, google_df, tiktok_df]:
        if "date" in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors="coerce")

    # Add platform labels
    facebook_df['platform'] = "Facebook"
    google_df['platform'] = "Google"
    tiktok_df['platform'] = "TikTok"

    # Combine ads data
    ads_df = pd.concat([facebook_df, google_df, tiktok_df], ignore_index=True)

    # Calculate metrics safely
    if "clicks" in ads_df.columns and "impression" in ads_df.columns and "spend" in ads_df.columns:
        ads_df['ctr'] = (
            ads_df['clicks'] / ads_df['impression'].replace(0, np.nan) * 100
        ).fillna(0)
        ads_df['cpc'] = (
            ads_df['spend'] / ads_df['clicks'].replace(0, np.nan)
        ).fillna(0)

    return business_df, ads_df

# ------------------------
# Dashboard
# ------------------------
def main():
    st.set_page_config(page_title="Marketing Dashboard", layout="wide")
    st.title("📊 Marketing Performance Dashboard")

    business_df, ads_df = load_and_prepare_data()

    # Sidebar filters
    st.sidebar.header("Filters")
    platform_filter = st.sidebar.multiselect(
        "Select Platform(s)", ads_df['platform'].unique(), default=ads_df['platform'].unique()
    )

    filtered_ads = ads_df[ads_df['platform'].isin(platform_filter)]

    # ------------------------
    # KPI Metrics
    # ------------------------
    st.markdown("### 🔑 Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)

    total_spend = filtered_ads['spend'].sum()
    total_clicks = filtered_ads['clicks'].sum()
    avg_ctr = filtered_ads['ctr'].mean()
    total_revenue = filtered_ads['attributed revenue'].sum()

    col1.metric("💰 Total Spend", f"${total_spend:,.2f}")
    col2.metric("🖱️ Total Clicks", f"{total_clicks:,}")
    col3.metric("📈 Avg. CTR", f"{avg_ctr:.2f}%")
    col4.metric("💵 Revenue", f"${total_revenue:,.2f}")

    st.divider()

    # ------------------------
    # Business Data Trends
    # ------------------------
    st.subheader("📦 Business KPIs Over Time")
    fig_business = px.line(
        business_df,
        x="date", y=["total revenue", "gross profit"],
        title="Revenue & Gross Profit Over Time"
    )
    st.plotly_chart(fig_business, use_container_width=True)

    # ------------------------
    # Ad Campaign Data
    # ------------------------
    st.subheader("📢 Ad Campaign Performance")

    # Impressions
    fig1 = px.line(filtered_ads, x="date", y="impression", color="platform",
                   title="Impressions Over Time")
    st.plotly_chart(fig1, use_container_width=True)

    # Clicks
    fig2 = px.line(filtered_ads, x="date", y="clicks", color="platform",
                   title="Clicks Over Time")
    st.plotly_chart(fig2, use_container_width=True)

    # CTR Distribution
    fig3 = px.box(filtered_ads, x="platform", y="ctr", title="CTR Distribution by Platform")
    st.plotly_chart(fig3, use_container_width=True)

    # Spend vs Revenue
    fig4 = px.scatter(filtered_ads, x="spend", y="attributed revenue",
                      color="platform", size="clicks", title="Spend vs Revenue")
    st.plotly_chart(fig4, use_container_width=True)

    # Show raw data option
    with st.expander("📊 Show Raw Data"):
        st.write(filtered_ads)


if __name__ == "__main__":
    main()
