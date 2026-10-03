import streamlit as st
import json
import os
from services.demographic_analyzer import DemographicAnalyzer
from services.agent_engine import AgentEngine
from config import DATA_DIR

st.set_page_config(page_title="Multi-Agent Book Review Dashboard", layout="wide")

# Initialize Engine Instances
analyzer = DemographicAnalyzer()
engine = AgentEngine()

# Ensure Data Folder Exists
os.makedirs(DATA_DIR, exist_ok=True)
CONTEXT_FILE = os.path.join(DATA_DIR, "context_store.json")

# Load existing story context
if "story_context" not in st.session_state:
    if os.path.exists(CONTEXT_FILE):
        with open(CONTEXT_FILE, "r") as f:
            st.session_state.story_context = json.load(f)
    else:
        st.session_state.story_context = {"genre": "", "synopsis": "", "characters": ""}

# APP HEADER
st.title("📚 Book Writing & Multi-Agent Review Interface")
st.caption("Submit chapter drafts for parallel critique across 5 publisher/reader personas and automated demographic profiling.")

# TOP METADATA EXPANDER
with st.expander("📖 Story Context & Settings (Optional)", expanded=False):
    col_g, col_s = st.columns([1, 2])
    with col_g:
        st.session_state.story_context["genre"] = st.text_input("Target Genre", value=st.session_state.story_context.get("genre", ""))
    with col_s:
        st.session_state.story_context["synopsis"] = st.text_area("High-Level Premise / Synopsis", value=st.session_state.story_context.get("synopsis", ""), height=70)
    
    if st.button("Save Context"):
        with open(CONTEXT_FILE, "w") as f:
            json.dump(st.session_state.story_context, f, indent=2)
        st.success("Story context updated successfully.")

st.divider()

# MAIN TWO-COLUMN DASHBOARD
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.subheader("📝 Chapter Input")
    chapter_title = st.text_input("Chapter Title / Number", value="Chapter 1")
    chapter_text = st.text_area("Paste Chapter Content Here", height=450, placeholder="Once upon a time...")
    
    word_count = len(chapter_text.split()) if chapter_text else 0
    st.caption(f"Word Count: {word_count} words | Character Count: {len(chapter_text)} characters")
    
    run_button = st.button("🚀 Run Multi-Agent Review Pipeline", type="primary", use_container_width=True)

with col_right:
    st.subheader("📊 Analysis & Feedback Dashboard")
    
    if chapter_text:
        # Run Demographic Analysis on Text Input
        metrics = analyzer.analyze(chapter_text)
        
        # Demographic Header Cards
        st.markdown("### 🎯 Projected Consumer Demographic")
        m1, m2, m3 = st.columns(3)
        m1.metric("Target Age Group", metrics["projected_demographic"])
        m2.metric("Grade Reading Level", f"Grade {metrics['flesch_kincaid_grade']}")
        m3.metric("Reading Ease", f"{metrics['reading_ease']} / 100")
        st.divider()

    if run_button:
        if not chapter_text.strip():
            st.warning("Please paste chapter text before running the evaluation.")
        else:
            with st.spinner("Analyzing text across 5 reviewer personas..."):
                context_str = f"Genre: {st.session_state.story_context.get('genre', 'General')}\nSynopsis: {st.session_state.story_context.get('synopsis', 'N/A')}"
                results = engine.run_all_agents(chapter_text, context_str)
                st.session_state.latest_results = results
                st.session_state.latest_chapter_title = chapter_title

    if "latest_results" in st.session_state:
        results = st.session_state.latest_results
        
        # Tabs for filtering feedback per agent
        tabs = st.tabs(["Publisher", "Editor", "Writer", "Genre Fan", "Skeptic"])
        
        roles = ["Publisher", "Developmental Editor", "Fellow Writer", "Genre Fan", "Genre Skeptic"]
        for tab, role in zip(tabs, roles):
            with tab:
                data = results.get(role, {})
                if data.get("status") in ["success", "mock"]:
                    fb = data["feedback"]
                    st.markdown(f"#### {role} Verdict")
                    st.info(fb.get("verdict", "No verdict returned."))
                    
                    # Output nested JSON components cleanly
                    for key, val in fb.items():
                        if key != "verdict":
                            st.markdown(f"**{key.replace('_', ' ').title()}:**")
                            if isinstance(val, list):
                                for item in val:
                                    st.write(f"- {item}")
                            else:
                                st.write(val)
                elif data.get("status") == "error":
                    st.error(f"Error executing agent review: {data.get('error')}")

        # Download Report Option
        st.divider()
        compiled_report = f"# Review Report for: {st.session_state.latest_chapter_title}\n\n"
        compiled_report += f"## Demographic Projection: {metrics['projected_demographic']} (Flesch Grade {metrics['flesch_kincaid_grade']})\n\n"
        for role, data in results.items():
            compiled_report += f"### {role}\n{json.dumps(data.get('feedback', {}), indent=2)}\n\n"

        st.download_button(
            label="📥 Download Full Review Report (.md)",
            data=compiled_report,
            file_name=f"{st.session_state.latest_chapter_title.replace(' ', '_')}_review.md",
            mime="text/markdown",
            use_container_width=True
        )