import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
  
# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Mental Health Awareness Dashboard",
    page_icon="🧠",
    layout="wide"
)

COLOR_PALETTE = ["#0D4D97", "#06695F", "#047A61", "#566CE6", "#105C54", "#3A3B3B"]

# ============================================================
# LOAD DATA
# ============================================================

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(BASE_DIR, "survey.csv"))

# ============================================================
# EDA / DATA CLEANING
# ============================================================

df = df.dropna(how="all")
df = df.drop_duplicates()

# --- Clean Gender (real dataset has 49 messy variants) ---
df["Gender"] = df["Gender"].astype(str).str.strip().str.lower()

male_terms = ["m", "male", "man", "cis male", "cis man", "male-ish", "maile",
              "mail", "make", "mal", "malr", "male (cis)", "msle", "guy (-ish) ^_^"]
female_terms = ["f", "female", "woman", "femake", "cis female", "female (cis)",
                "cis-female/femme", "female "]

df["Gender"] = df["Gender"].apply(
    lambda x: "Male" if x in male_terms
    else ("Female" if x in female_terms else "Other")
)

# --- Clean Age (real dataset has -1726 and 99999999999) ---
df["Age"] = pd.to_numeric(df["Age"], errors="coerce")
df = df[(df["Age"] >= 15) & (df["Age"] <= 100)]

# --- Drop columns not useful for dashboard ---
df = df.drop(columns=["comments", "state", "Timestamp"], errors="ignore")

# --- Strip whitespace from text columns ---
for col in df.select_dtypes(include="object").columns:
    df[col] = df[col].astype(str).str.strip()

df = df.reset_index(drop=True)

# ============================================================
# STYLE
# ============================================================

st.markdown("""
<style>
.stApp { background-color: #D9D9D9; }
.main-title { font-size: 40px; font-weight: 700; color: #263238; text-align: center; margin-bottom: 5px; }
.subtitle { text-align: center; color: #455A64; font-size: 18px; margin-bottom: 25px; }
.kpi-card {
    background: linear-gradient(135deg, #ffffff 0%, #f3f0fb 100%);
    border: 1px solid #d9d2f0;
    border-top: 4px solid #6c5ce7;
    border-radius: 14px;
    padding: 18px 16px;
    text-align: center;
    box-shadow: 0 4px 14px rgba(108, 92, 231, 0.12);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    min-height: 130px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}
.kpi-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 20px rgba(108, 92, 231, 0.22);
}
.kpi-title {
    font-size: 13px;
    font-weight: 600;
    color: #6c5ce7;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 6px;
    min-height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
}
.kpi-v
[data-testid="stSidebar"] .stMultiSelect > div > div {
    background-color: #66C2B8 !important;
    border-radius: 8px;
}
[data-testid="stSidebar"] label {
    color: #263238 !important;
    font-weight: 600;
}
.section-title { color: #263238; font-size: 25px; font-weight: 700; }
h2 { color: #000000 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🧠 Code & Mind: Mental Health Insights</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Interactive analysis of mental health, treatment, workplace support and employee attitudes</div>', unsafe_allow_html=True)

# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("🔎 Dashboard Filters")

country_filter = st.sidebar.multiselect("Country", sorted(df["Country"].dropna().unique()))
gender_filter = st.sidebar.multiselect("Gender", sorted(df["Gender"].dropna().unique()))
treatment_filter = st.sidebar.multiselect("Treatment", sorted(df["treatment"].dropna().unique()))
remote_filter = st.sidebar.multiselect("Remote Work", sorted(df["remote_work"].dropna().unique()))

filtered_df = df.copy()
if country_filter:
    filtered_df = filtered_df[filtered_df["Country"].isin(country_filter)]
if gender_filter:
    filtered_df = filtered_df[filtered_df["Gender"].isin(gender_filter)]
if treatment_filter:
    filtered_df = filtered_df[filtered_df["treatment"].isin(treatment_filter)]
if remote_filter:
    filtered_df = filtered_df[filtered_df["remote_work"].isin(remote_filter)]

# ============================================================
# KPI CARDS
# ============================================================

total_respondents = len(filtered_df)
treatment_yes = filtered_df["treatment"].eq("Yes").sum()
family_history_yes = filtered_df["family_history"].eq("Yes").sum()
benefits_yes = filtered_df["benefits"].eq("Yes").sum()
remote_workers = filtered_df["remote_work"].eq("Yes").sum()

st.markdown('<div class="section-title">📊 Key Performance Indicators</div>', unsafe_allow_html=True)
st.write("")

col1, col2, col3, col4, col5 = st.columns(5)

kpis = [
    ("Total Respondents", total_respondents, None),
    ("Treatment: Yes", treatment_yes, treatment_yes / total_respondents * 100 if total_respondents else 0),
    ("Family History: Yes", family_history_yes, family_history_yes / total_respondents * 100 if total_respondents else 0),
    ("Benefits: Yes", benefits_yes, benefits_yes / total_respondents * 100 if total_respondents else 0),
    ("Remote Workers", remote_workers, remote_workers / total_respondents * 100 if total_respondents else 0),
]

for col, (title, value, pct) in zip([col1, col2, col3, col4, col5], kpis):
    with col:
        if pct is not None:
            pct_html = f'<div class="kpi-sub">{pct:.1f}% of total</div>'
        else:
            pct_html = ""
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">{title}</div>
                <div class="kpi-value">{value:,}</div>
                {pct_html}
            </div>
        """, unsafe_allow_html=True)

# ============================================================
# NAVIGATION
# ============================================================

st.sidebar.divider()
page = st.sidebar.radio(
    "📑 Dashboard Sections",
    ["Overview", "Mental Health & Treatment", "Geographic Analysis",
     "Workplace Support", "Workplace Attitudes", "Key Insights"]
)

# ============================================================
# PAGE 1 — OVERVIEW
# ============================================================

if page == "Overview":
    st.header("📌 Overview")

    with st.expander("🔍 View EDA & Data Cleaning Summary"):
        st.markdown(f"""
        **Data Cleaning Steps Performed:**
        - Removed fully empty rows and duplicate entries
        - Standardized 49+ messy Gender entries into Male / Female / Other
        - Filtered invalid Age values (kept only ages between 15–100)
        - Dropped unused columns: `comments`, `state`, `Timestamp`
        - Stripped whitespace from all text columns

        **Dataset Summary:**
        - Total respondents after cleaning: **{len(df):,}**
        - Total columns: **{len(df.columns)}**
        - Countries represented: **{df['Country'].nunique()}**
        """)
        st.markdown("**Cleaned Dataset (duplicates & empty rows removed):**")
        st.dataframe(df, use_container_width=True)

        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Cleaned Dataset (CSV)",
            data=csv_data,
            file_name="cleaned_survey_data.csv",
            mime="text/csv"
        )

    col1, col2 = st.columns(2)

    with col1:
        gender_data = filtered_df["Gender"].value_counts().reset_index()
        gender_data.columns = ["Gender", "Count"]
        fig = px.bar(gender_data, x="Gender", y="Count", title="Respondents by Gender",
                     color="Gender", color_discrete_sequence=COLOR_PALETTE)
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        treatment_data = filtered_df["treatment"].value_counts().reset_index()
        treatment_data.columns = ["Treatment", "Count"]
        fig = px.pie(treatment_data, names="Treatment", values="Count", title="Mental Health Treatment",
                     color_discrete_sequence=COLOR_PALETTE)
        st.plotly_chart(fig, use_container_width=True)

    fig = px.histogram(filtered_df, x="Age", nbins=20, title="Age Distribution",
                        color_discrete_sequence=["#1565C0"])
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# PAGE 2 — MENTAL HEALTH & TREATMENT
# ============================================================

elif page == "Mental Health & Treatment":
    st.header("🧠 Mental Health & Treatment")
    col1, col2 = st.columns(2)

    with col1:
        data = filtered_df["family_history"].value_counts().reset_index()
        data.columns = ["Family History", "Count"]
        fig = px.bar(data, x="Family History", y="Count", title="Family History of Mental Illness",
                     color="Family History", color_discrete_sequence=COLOR_PALETTE)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        data = filtered_df["work_interfere"].dropna().value_counts().reset_index()
        data.columns = ["Work Interference", "Count"]
        fig = px.bar(data, x="Work Interference", y="Count", title="Mental Health Impact on Work",
                     color="Work Interference", color_discrete_sequence=COLOR_PALETTE)
        st.plotly_chart(fig, use_container_width=True)

# ============================================================
# PAGE 3 — GEOGRAPHIC ANALYSIS
# ============================================================

elif page == "Geographic Analysis":
    st.header("🌍 Geographic Analysis")
    country_data = filtered_df["Country"].value_counts().head(10).reset_index()
    country_data.columns = ["Country", "Respondents"]
    fig = px.bar(country_data, x="Respondents", y="Country", orientation="h",
                 title="Top 10 Countries by Number of Respondents",
                 color="Country", color_discrete_sequence=COLOR_PALETTE)
    st.plotly_chart(fig, use_container_width=True)
    st.info("The project specifically asks you to explore how mental health frequency and attitudes vary by geographic location.")

# ============================================================
# PAGE 4 — WORKPLACE SUPPORT
# ============================================================

elif page == "Workplace Support":
    st.header("🏢 Workplace Mental Health Support")
    support_columns = ["benefits", "care_options", "wellness_program", "seek_help", "anonymity"]

    support_summary = []
    for column in support_columns:
        yes_count = filtered_df[column].eq("Yes").sum()
        support_summary.append({"Support Type": column, "Yes Count": yes_count})

    support_df = pd.DataFrame(support_summary)
    fig = px.bar(support_df, x="Support Type", y="Yes Count", title="Workplace Support Availability",
                 color="Support Type", color_discrete_sequence=COLOR_PALETTE)
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# PAGE 5 — WORKPLACE ATTITUDES
# ============================================================

elif page == "Workplace Attitudes":
    st.header("💬 Workplace Attitudes Towards Mental Health")
    col1, col2 = st.columns(2)

    with col1:
        data = filtered_df["mental_health_consequence"].value_counts().reset_index()
        data.columns = ["Response", "Count"]
        fig = px.bar(data, x="Response", y="Count", title="Fear of Negative Consequences (Mental Health)",
                     color="Response", color_discrete_sequence=COLOR_PALETTE)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        data = filtered_df["coworkers"].value_counts().reset_index()
        data.columns = ["Response", "Count"]
        fig = px.bar(data, x="Response", y="Count", title="Willingness to Discuss with Coworkers",
                     color="Response", color_discrete_sequence=COLOR_PALETTE)
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        data = filtered_df["supervisors"].value_counts().reset_index() if "supervisors" in filtered_df.columns else filtered_df["supervisor"].value_counts().reset_index()
        data.columns = ["Response", "Count"]
        fig = px.bar(data, x="Response", y="Count", title="Willingness to Discuss with Supervisor",
                     color="Response", color_discrete_sequence=COLOR_PALETTE)
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        data = filtered_df["mental_health_interview"].value_counts().reset_index()
        data.columns = ["Response", "Count"]
        fig = px.bar(data, x="Response", y="Count", title="Would Bring Up in an Interview",
                     color="Response", color_discrete_sequence=COLOR_PALETTE)
        st.plotly_chart(fig, use_container_width=True)

# ============================================================
# PAGE 6 — KEY INSIGHTS
# ============================================================

elif page == "Key Insights":
    st.header("🔑 Key Insights")

    treatment_rate = round((filtered_df["treatment"].eq("Yes").sum() / len(filtered_df)) * 100, 1) if len(filtered_df) > 0 else 0
    family_history_rate = round((filtered_df["family_history"].eq("Yes").sum() / len(filtered_df)) * 100, 1) if len(filtered_df) > 0 else 0
    obs_consequence_rate = round((filtered_df["obs_consequence"].eq("Yes").sum() / len(filtered_df)) * 100, 1) if len(filtered_df) > 0 else 0

    st.markdown(f"""
    - **{treatment_rate}%** of respondents have sought treatment for a mental health condition.
    - **{family_history_rate}%** report a family history of mental illness.
    - **{obs_consequence_rate}%** have observed negative consequences for coworkers with mental health conditions.
    - Respondents in **{filtered_df['Country'].mode()[0] if not filtered_df.empty else 'N/A'}** make up the largest share of the dataset.
    - Employees who report family history of mental illness are more likely to have sought treatment — explore the Mental Health & Treatment tab to see the pattern.
    """)

    st.dataframe(filtered_df.head(50), use_container_width=True)
    st.markdown("---")
st.header("🧭 How Are You Feeling? A Quick Self-Check")
st.write("This is a reflection tool, not a diagnosis. Answer honestly — only you will see your result.")

with st.form("self_check_form"):
    q1 = st.slider("Over the past 2 weeks, how often have you felt stressed at work?", 
                    0, 5, 2, help="0 = Never, 5 = Constantly")
    q2 = st.slider("How well have you been sleeping?", 
                    0, 5, 3, help="0 = Very poorly, 5 = Very well")
    q3 = st.radio("Do you feel comfortable talking to your manager about mental health?",
                   ["Yes", "No", "Not sure"])
    q4 = st.slider("How supported do you feel by your workplace?", 
                    0, 5, 3, help="0 = Not at all, 5 = Very supported")
    
    submitted = st.form_submit_button("See My Reflection")

if submitted:
    score = q1 + (5 - q2) + (5 - q4)
    if q3 == "No":
        score += 2

    st.subheader("Your Reflection")
    if score <= 4:
        st.success("You seem to be managing well right now. Keep checking in with yourself regularly.")
    elif score <= 9:
        st.warning("You might be carrying more stress than usual. Consider talking to someone you trust, or a professional, about how you're feeling.")
    else:
        st.error("It sounds like things have been genuinely tough lately. Please consider reaching out to a mental health professional or a helpline soon — you don't have to handle this alone.")

    st.caption("This tool is for reflection only and is not a substitute for professional diagnosis or advice.")
    
st.markdown('<div class="section-title">✨ Treatment Uptake, Visualized</div>', unsafe_allow_html=True)

categories = ["Sought Treatment", "Family History", "Benefits Access", "Remote Workers"]
final_values = [treatment_yes, family_history_yes, benefits_yes, remote_workers]

frames = []
n_steps = 20
for step in range(1, n_steps + 1):
    frame_values = [v * step / n_steps for v in final_values]
    frames.append(go.Frame(data=[go.Bar(x=categories, y=frame_values, marker_color=COLOR_PALETTE)]))

fig_animated = go.Figure(
    data=[go.Bar(x=categories, y=[0]*4, marker_color=COLOR_PALETTE)],
    frames=frames
)
fig_animated.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    height=380,
    font=dict(color="#263238"),
    margin=dict(t=20, b=20),
    updatemenus=[{
        "type": "buttons",
        "showactive": False,
        "x": 0.02, "y": 1.15,
        "buttons": [{
            "label": "▶ Animate",
            "method": "animate",
            "args": [None, {"frame": {"duration": 40, "redraw": True}, "fromcurrent": True}]
        }]
    }]
)
st.plotly_chart(fig_animated, width='stretch')

