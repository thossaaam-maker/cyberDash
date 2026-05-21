import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Layout configuration
st.set_page_config(
    page_title="Global Cybersecurity Threats Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling to give a high-tech cybersecurity theme feel
st.markdown("""
    <style>
    .main-title { font-size: 38px; font-weight: bold; color: #1E3A8A; margin-bottom: 5px; }
    .subtitle { font-size: 16px; color: #4B5563; margin-bottom: 25px; }
    div[data-testid="stMetricValue"] { font-size: 28px; font-weight: 700; color: #0F172A; }
    </style>
""", unsafe_allow_html=True)

# 2. Dynamic Data Loading (Handles both Repository file or Web Drag-and-Drop)
@st.cache_data
def load_data(file_source):
    df = pd.read_csv(file_source)
    return df

st.sidebar.title("🛡️ Threat Control Center")
st.sidebar.markdown("---")

uploaded_file = None
try:
    # Try reading locally from the repo directory first
    df = load_data("Global_Cybersecurity_Threats_2015-2024.csv")
except Exception:
    # If file isn't in the repository, show online file uploader
    st.sidebar.warning("📊 Local dataset file not found in repository.")
    uploaded_file = st.sidebar.file_uploader("Upload 'Global_Cybersecurity_Threats_2015-2024.csv' here:", type=["csv"])
    if uploaded_file is not None:
        df = load_data(uploaded_file)
    else:
        st.info("👋 Welcome! Please upload the dataset file via the sidebar to view the dashboard analysis.")
        st.stop()

# 3. Interactive Filters in Sidebar
st.sidebar.subheader("🔍 Filter & Drill-down")

# Multi-select for Country
all_countries = sorted(df["Country"].unique())
selected_countries = st.sidebar.multiselect("Select Countries", options=all_countries, default=all_countries)

# Slider for Year Range
min_year, max_year = int(df["Year"].min()), int(df["Year"].max())
selected_years = st.sidebar.slider("Select Year Range", min_value=min_year, max_value=max_year, value=(min_year, max_year))

# Multi-select for Target Industry
all_industries = sorted(df["Target Industry"].unique())
selected_industries = st.sidebar.multiselect("Select Industries", options=all_industries, default=all_industries)

# Filter Data application
filtered_df = df[
    (df["Country"].isin(selected_countries)) &
    (df["Year"].between(selected_years[0], selected_years[1])) &
    (df["Target Industry"].isin(selected_industries))
]

# Dashboard Main Header
st.markdown('<div class="main-title">🛡️ Global Cybersecurity Threats Incident Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Analyze cybersecurity incident patterns, financial losses, vulnerabilities, and resolution times across global sectors.</div>', unsafe_allow_html=True)

if filtered_df.empty:
    st.warning("⚠️ No data matches the selected filter configuration. Please adjust your filters in the sidebar.")
    st.stop()

# 4. Top KPI Summary Metrics
total_incidents = len(filtered_df)
total_financial_loss = filtered_df["Financial Loss (in Million $)"].sum()
avg_resolution_time = filtered_df["Incident Resolution Time (in Hours)"].mean()
total_users_affected = filtered_df["Number of Affected Users"].sum()

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric(label="💥 Total Incidents", value=f"{total_incidents:,}")
with kpi2:
    st.metric(label="💰 Total Financial Impact", value=f"${total_financial_loss:,.1f}M")
with kpi3:
    st.metric(label="⏳ Avg Resolution Time", value=f"{avg_resolution_time:.1f} Hours")
with kpi4:
    st.metric(label="👥 Total Users Impacted", value=f"{total_users_affected:,}")

st.markdown("---")

# 5. Dashboard Row 1: Key Trends and Loss Matrix
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("📈 Threat Evolution & Incidents Trend")
    yearly_trends = filtered_df.groupby("Year").size().reset_index(name="Incident Count")
    fig_line = px.line(
        yearly_trends, 
        x="Year", 
        y="Incident Count", 
        markers=True,
        line_shape="spline",
        color_discrete_sequence=["#0284C7"]
    )
    fig_line.update_layout(xaxis=dict(tickmode='linear'), margin=dict(l=20, r=20, t=10, b=20))
    st.plotly_chart(fig_line, use_container_width=True)

with row1_col2:
    st.subheader("💰 Financial Loss by Target Industry")
    industry_loss = filtered_df.groupby("Target Industry")["Financial Loss (in Million $)"].sum().reset_index()
    industry_loss = industry_loss.sort_values(by="Financial Loss (in Million $)", ascending=True)
    fig_ind = px.bar(
        industry_loss, 
        y="Target Industry", 
        x="Financial Loss (in Million $)", 
        orientation="h",
        color="Financial Loss (in Million $)",
        color_continuous_scale="Blues",
        text_auto=".1f"
    )
    fig_ind.update_layout(showlegend=False, margin=dict(l=20, r=20, t=10, b=20))
    st.plotly_chart(fig_ind, use_container_width=True)

st.markdown("---")

# 6. Dashboard Row 2: Vector and Vulnerability Breakdown
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("☣️ Common Attack Vectors")
    attack_counts = filtered_df["Attack Type"].value_counts().reset_index()
    attack_counts.columns = ["Attack Type", "Incident Count"]
    fig_attack = px.bar(
        attack_counts.sort_values(by="Incident Count", ascending=True), 
        y="Attack Type", 
        x="Incident Count", 
        orientation="h",
        color="Incident Count",
        color_continuous_scale="Tealgrn"
    )
    fig_attack.update_layout(showlegend=False, margin=dict(l=20, r=20, t=10, b=20))
    st.plotly_chart(fig_attack, use_container_width=True)

with row2_col2:
    st.subheader("🔓 Primary Attack Sources")
    source_counts = filtered_df["Attack Source"].value_counts().reset_index()
    source_counts.columns = ["Attack Source", "Incident Count"]
    fig_source = px.pie(
        source_counts, 
        names="Attack Source", 
        values="Incident Count",
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    fig_source.update_layout(margin=dict(l=20, r=20, t=10, b=20))
    st.plotly_chart(fig_source, use_container_width=True)

st.markdown("---")

# 7. Dashboard Row 3: Security Mechanisms & Vulnerabilities
row3_col1, row3_col2 = st.columns(2)

with row3_col1:
    st.subheader("🛡️ Defense Mechanisms Deployed")
    defense_counts = filtered_df["Defense Mechanism Used"].value_counts().reset_index()
    defense_counts.columns = ["Defense Mechanism Used", "Count"]
    fig_defense = px.bar(
        defense_counts, 
        x="Defense Mechanism Used", 
        y="Count", 
        color="Defense Mechanism Used",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_defense.update_layout(showlegend=False, margin=dict(l=20, r=20, t=10, b=20))
    st.plotly_chart(fig_defense, use_container_width=True)

with row3_col2:
    st.subheader("🔍 Top Exploited Security Vulnerabilities")
    vuln_counts = filtered_df["Security Vulnerability Type"].value_counts().reset_index()
    vuln_counts.columns = ["Security Vulnerability Type", "Count"]
    fig_vuln = px.bar(
        vuln_counts.sort_values(by="Count", ascending=True), 
        y="Security Vulnerability Type", 
        x="Count", 
        orientation="h",
        color="Count",
        color_continuous_scale="Purp"
    )
    fig_vuln.update_layout(showlegend=False, margin=dict(l=20, r=20, t=10, b=20))
    st.plotly_chart(fig_vuln, use_container_width=True)

st.markdown("---")

# 8. Data Sheet Expander
with st.expander("🔍 View Raw Filtered Dataset Records"):
    st.dataframe(filtered_df, use_container_width=True)
