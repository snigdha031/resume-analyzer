import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import io
from scipy import stats

BACKEND_URL = "https://resume-analyzer-236k.onrender.com/full-analysis/"
EXPLAIN_URL = "https://resume-analyzer-236k.onrender.com/explain-ranking/"

st.set_page_config(page_title="AI Resume Analyzer", layout="wide")

st.title("📄 AI-Powered Resume Analyzer")
st.markdown("Upload multiple resumes and evaluate them against a job description.")

# -------------------------------
# 📌 Input Section
# -------------------------------
jd_text = st.text_area("📝 Paste Job Description Here", height=250)

uploaded_files = st.file_uploader(
    "📂 Upload Resume PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

analyze_button = st.button("🚀 Analyze Resumes")

# Init session state
if "results" not in st.session_state:
    st.session_state.results = []

# -------------------------------
# 🚀 Processing
# -------------------------------
if analyze_button:

    if not jd_text:
        st.error("Please paste a Job Description.")
        st.stop()

    if not uploaded_files:
        st.error("Please upload at least one resume.")
        st.stop()

    results = []

    with st.spinner("Analyzing resumes..."):

        for file in uploaded_files:

            files = {"file": (file.name, file.getvalue(), "application/pdf")}
            data = {"jd_text": jd_text}

            try:
                response = requests.post(BACKEND_URL, files=files, data=data)

                if response.status_code == 200:
                    result = response.json()
                    results.append({
                        "Candidate": file.name,
                        "Rule Score": result.get("rule_based_score", 0),
                        "Semantic Score": result.get("semantic_score", 0),
                        "Final Score": result.get("final_hybrid_score", 0),
                        "Matched Skills": ", ".join(result.get("matched_skills", [])),
                        "Missing Skills": ", ".join(result.get("missing_skills", [])),
                        "Matched Skills List": result.get("matched_skills", []),
                        "Missing Skills List": result.get("missing_skills", []),
                        "AI Strengths": result.get("ai_strengths", []),
                        "AI Weaknesses": result.get("ai_weaknesses", []),
                        "Suggestions": result.get("improvement_suggestions", []),
                        "Summary": result.get("tailored_summary", "")
                    })
                else:
                    st.error(f"Error analyzing {file.name}")

            except requests.exceptions.ConnectionError:
                st.error("⚠️ Backend is not running. Start FastAPI first.")
                st.stop()

    st.session_state.results = results

# -------------------------------
# 📊 Results Section
# -------------------------------
if st.session_state.results:

    df = pd.DataFrame(st.session_state.results)
    df = df.sort_values("Final Score", ascending=False).reset_index(drop=True)

    st.subheader("📊 Resume Comparison Table")
    st.dataframe(
        df[["Candidate", "Rule Score", "Semantic Score", "Final Score"]],
        use_container_width=True
    )

    # ✅ Export Full Results
    st.markdown("### 📥 Export Results")
    csv_buffer = io.StringIO()
    df[["Candidate", "Rule Score", "Semantic Score", "Final Score", "Matched Skills", "Missing Skills"]].to_csv(csv_buffer, index=False)
    st.download_button(
        label="⬇️ Download Full Results as CSV",
        data=csv_buffer.getvalue(),
        file_name="resume_analysis_results.csv",
        mime="text/csv"
    )

    best_candidate = df.iloc[0]
    st.success(
        f"🏆 Best Match: {best_candidate['Candidate']} "
        f"(Score: {best_candidate['Final Score']})"
    )

    # ====================================================
    # 🧠 Insights & Analytics
    # ====================================================
    st.subheader("🧠 Insights & Analytics")

    col1, col2, col3 = st.columns(3)
    col1.metric("📌 Average Score", f"{df['Final Score'].mean():.2f}")
    col2.metric("📈 Highest Score", f"{df['Final Score'].max():.2f}")
    col3.metric("📉 Lowest Score", f"{df['Final Score'].min():.2f}")

    if df["Semantic Score"].std() == 0 or df["Rule Score"].std() == 0:
        st.warning("⚠️ Semantic Score is 0 for all candidates — correlation cannot be computed.")
    else:
        correlation = df["Rule Score"].corr(df["Semantic Score"])
        st.info(f"📊 Correlation (Rule vs Semantic): {correlation:.2f}")

    st.markdown("### 🔥 High Performers (Score > 80)")
    high_performers = df[df["Final Score"] > 80]
    if not high_performers.empty:
        st.dataframe(high_performers[["Candidate", "Final Score"]])
    else:
        st.write("No high-performing candidates found.")

    st.markdown("### 🎯 Filter Candidates")
    min_score = st.slider("Select Minimum Score", 0, 100, 30)
    filtered_df = df[df["Final Score"] >= min_score]
    st.dataframe(filtered_df[["Candidate", "Final Score"]])

    filtered_csv_buffer = io.StringIO()
    filtered_df[["Candidate", "Final Score"]].to_csv(filtered_csv_buffer, index=False)
    st.download_button(
        label="⬇️ Download Filtered Results as CSV",
        data=filtered_csv_buffer.getvalue(),
        file_name=f"filtered_results_min_score_{min_score}.csv",
        mime="text/csv",
        key="filtered_download"
    )

    # -------------------------------
    # 📊 Analytics Dashboard
    # -------------------------------
    st.subheader("📊 Analytics Dashboard")

    st.markdown("### 📊 Score Distribution")
    fig_hist = px.histogram(df, x="Final Score", nbins=10, title="Distribution of Final Scores")
    st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown("### 📈 Candidate Ranking")
    fig_bar = px.bar(df, x="Candidate", y="Final Score", color="Final Score", title="Candidate Ranking by Final Score")
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("### 📉 Rule vs Semantic Score")
    fig_scatter = px.scatter(df, x="Rule Score", y="Semantic Score", text="Candidate", size="Final Score", title="Rule vs Semantic Relationship")
    fig_scatter.update_traces(textposition="top center")
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("### 📦 Score Spread Analysis")
    df_melted = df.melt(
        id_vars=["Candidate"],
        value_vars=["Rule Score", "Semantic Score", "Final Score"],
        var_name="Score Type",
        value_name="Score"
    )
    fig_box = px.box(df_melted, x="Score Type", y="Score", title="Score Distribution by Type")
    st.plotly_chart(fig_box, use_container_width=True)

    # ====================================================
    # 🔥 SKILL GAP ANALYTICS
    # ====================================================
    st.subheader("🔥 Skill Gap Analytics")

    all_matched = []
    all_missing = []
    for _, row in df.iterrows():
        all_matched.extend(row["Matched Skills List"])
        all_missing.extend(row["Missing Skills List"])

    all_skills = list(set(all_matched + all_missing))

    if all_skills:

        st.markdown("### 🗺️ Candidate × Skill Coverage Heatmap")
        st.caption("Green = skill present  |  Red = skill missing")

        heatmap_data = []
        for _, row in df.iterrows():
            candidate_name = row["Candidate"].replace(".pdf", "")
            for skill in all_skills:
                heatmap_data.append({
                    "Candidate": candidate_name,
                    "Skill": skill,
                    "Has Skill": 1 if skill in row["Matched Skills List"] else 0
                })

        heatmap_df = pd.DataFrame(heatmap_data)
        heatmap_pivot = heatmap_df.pivot(index="Candidate", columns="Skill", values="Has Skill")

        fig_heatmap = px.imshow(
            heatmap_pivot,
            color_continuous_scale=["#FF4B4B", "#21C354"],
            title="Skill Coverage per Candidate",
            labels={"color": "Has Skill"},
            aspect="auto"
        )
        fig_heatmap.update_layout(xaxis_tickangle=-35, coloraxis_showscale=False)
        st.plotly_chart(fig_heatmap, use_container_width=True)

        st.markdown("### 📉 Skill Demand vs Supply Gap")
        st.caption("Shows which skills are most lacking across all candidates")

        total_candidates = len(df)
        skill_stats = []
        for skill in all_skills:
            have_count = sum(1 for _, row in df.iterrows() if skill in row["Matched Skills List"])
            missing_count = total_candidates - have_count
            skill_stats.append({
                "Skill": skill,
                "Candidates With Skill": have_count,
                "Candidates Missing Skill": missing_count,
                "Gap %": round((missing_count / total_candidates) * 100, 1)
            })

        skill_stats_df = pd.DataFrame(skill_stats).sort_values("Gap %", ascending=False)

        fig_gap = px.bar(
            skill_stats_df,
            x="Skill",
            y=["Candidates With Skill", "Candidates Missing Skill"],
            title="Skill Supply vs Demand Gap Across All Candidates",
            barmode="stack",
            color_discrete_map={
                "Candidates With Skill": "#21C354",
                "Candidates Missing Skill": "#FF4B4B"
            }
        )
        fig_gap.update_layout(xaxis_tickangle=-35, legend_title="")
        st.plotly_chart(fig_gap, use_container_width=True)

        st.markdown("### 🚨 Top Missing Skills Summary")
        top_missing = skill_stats_df[skill_stats_df["Gap %"] > 0][["Skill", "Candidates Missing Skill", "Gap %"]].reset_index(drop=True)
        if not top_missing.empty:
            st.dataframe(top_missing, use_container_width=True)
        else:
            st.success("✅ All candidates have all required skills!")
    else:
        st.info("No skill data available to generate heatmap.")

    # ====================================================
    # 📐 STATISTICAL ANALYSIS
    # ====================================================
    st.subheader("📐 Statistical Analysis")

    st.markdown("### ⚖️ Weighted Score Experiment")
    st.caption("Adjust how much weight to give Rule-Based vs Semantic scoring and see how rankings change.")

    col_w1, col_w2 = st.columns(2)
    with col_w1:
        rule_weight = st.slider("📏 Rule-Based Weight (%)", 0, 100, 50, step=5, key="rule_weight")
    with col_w2:
        semantic_weight = 100 - rule_weight
        st.metric("🧠 Semantic Weight (%)", semantic_weight)

    df["Weighted Score"] = round(
        (df["Rule Score"] * rule_weight / 100) +
        (df["Semantic Score"] * semantic_weight / 100), 2
    )

    weighted_df = df[["Candidate", "Rule Score", "Semantic Score", "Final Score", "Weighted Score"]].copy()
    weighted_df = weighted_df.sort_values("Weighted Score", ascending=False).reset_index(drop=True)
    st.dataframe(weighted_df, use_container_width=True)

    fig_weighted = px.bar(
        weighted_df,
        x="Candidate",
        y=["Final Score", "Weighted Score"],
        barmode="group",
        title=f"Original vs Weighted Score (Rule: {rule_weight}% / Semantic: {semantic_weight}%)",
        color_discrete_map={"Final Score": "#636EFA", "Weighted Score": "#FF7F0E"}
    )
    st.plotly_chart(fig_weighted, use_container_width=True)

    st.markdown("### 📊 Z-Score Normalization")
    st.caption("Z-score shows how far each candidate is from the average. Positive = above average, Negative = below average.")

    if df["Final Score"].std() > 0:
        df["Z-Score"] = stats.zscore(df["Final Score"]).round(2)
    else:
        df["Z-Score"] = 0.0

    zscore_df = df[["Candidate", "Final Score", "Z-Score"]].copy()
    zscore_df = zscore_df.sort_values("Z-Score", ascending=False).reset_index(drop=True)

    def zscore_label(z):
        if z > 0.5:
            return "🟢 Above Average"
        elif z < -0.5:
            return "🔴 Below Average"
        else:
            return "🟡 Average"

    zscore_df["Standing"] = zscore_df["Z-Score"].apply(zscore_label)
    st.dataframe(zscore_df, use_container_width=True)

    fig_zscore = px.bar(
        zscore_df,
        x="Candidate",
        y="Z-Score",
        color="Z-Score",
        color_continuous_scale=["#FF4B4B", "#FFDD57", "#21C354"],
        title="Z-Score Distribution Across Candidates",
        text="Z-Score"
    )
    fig_zscore.add_hline(y=0, line_dash="dash", line_color="white", annotation_text="Mean")
    fig_zscore.update_traces(textposition="outside")
    st.plotly_chart(fig_zscore, use_container_width=True)

    st.markdown("### 🏅 Percentile Ranking")
    st.caption("Percentile shows what % of candidates each person outperforms.")

    df["Percentile"] = df["Final Score"].rank(pct=True).mul(100).round(1)
    percentile_df = df[["Candidate", "Final Score", "Percentile"]].copy()
    percentile_df = percentile_df.sort_values("Percentile", ascending=False).reset_index(drop=True)

    def percentile_label(p):
        if p >= 90:
            return "🥇 Top 10%"
        elif p >= 75:
            return "🥈 Top 25%"
        elif p >= 50:
            return "🥉 Top 50%"
        else:
            return "📉 Bottom 50%"

    percentile_df["Tier"] = percentile_df["Percentile"].apply(percentile_label)
    st.dataframe(percentile_df, use_container_width=True)

    fig_percentile = px.bar(
        percentile_df,
        x="Candidate",
        y="Percentile",
        color="Percentile",
        color_continuous_scale=["#FF4B4B", "#FFDD57", "#21C354"],
        title="Candidate Percentile Rankings",
        text="Percentile"
    )
    fig_percentile.add_hline(y=50, line_dash="dash", line_color="white", annotation_text="50th Percentile")
    fig_percentile.update_traces(textposition="outside")
    st.plotly_chart(fig_percentile, use_container_width=True)

    # ====================================================
    # 🤖 AI RANKING EXPLANATION (NEW)
    # ====================================================
    st.subheader("🤖 AI Ranking Explanation")
    st.caption("Ask AI to explain in plain English why candidates ranked the way they did.")

    if len(df) >= 2:

        explain_button = st.button("💬 Generate AI Explanation")

        if explain_button:

            # Build a summary of all candidates to send to Gemini
            candidate_summaries = []
            for _, row in df.iterrows():
                candidate_summaries.append({
                    "name": row["Candidate"].replace(".pdf", ""),
                    "final_score": row["Final Score"],
                    "rule_score": row["Rule Score"],
                    "semantic_score": row["Semantic Score"],
                    "matched_skills": row["Matched Skills"],
                    "missing_skills": row["Missing Skills"],
                    "percentile": row["Percentile"]
                })

            with st.spinner("🤖 AI is generating explanation..."):
                try:
                    explain_response = requests.post(
                        EXPLAIN_URL,
                        json={"candidates": candidate_summaries},
                        timeout=30
                    )

                    if explain_response.status_code == 200:
                        explanation = explain_response.json().get("explanation", "")
                        st.markdown("---")
                        st.markdown(explanation)
                    else:
                        st.error("Failed to get explanation from backend.")

                except requests.exceptions.ConnectionError:
                    st.error("⚠️ Backend is not running.")
                except requests.exceptions.Timeout:
                    st.error("⚠️ Request timed out. Try again.")

    else:
        st.info("Upload at least 2 resumes to generate a comparative AI explanation.")

    # -------------------------------
    # 📌 Detailed Analysis
    # -------------------------------
    st.subheader("📌 Detailed Analysis")

    for index, row in df.iterrows():
        with st.expander(f"🔎 {row['Candidate']} — Score: {row['Final Score']}"):

            st.markdown("### ✅ Matched Skills")
            st.write(row["Matched Skills"])

            st.markdown("### ❌ Missing Skills")
            st.write(row["Missing Skills"])

            st.markdown("### 💪 AI Strengths")
            for strength in row["AI Strengths"]:
                st.write(f"- {strength}")

            st.markdown("### ⚠️ AI Weaknesses")
            for weakness in row["AI Weaknesses"]:
                st.write(f"- {weakness}")

            st.markdown("### 🚀 Improvement Suggestions")
            for suggestion in row["Suggestions"]:
                st.write(f"- {suggestion}")

            st.markdown("### 🧾 Tailored Summary")
            st.write(row["Summary"])