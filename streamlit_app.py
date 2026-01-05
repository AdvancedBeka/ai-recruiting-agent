import os
import json
import requests
import streamlit as st

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="AI Recruiting Agent", layout="wide")

# --- Styles ---
st.markdown(
    """
    <style>
    body { background: #f7f9fb; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    .pill { background:#eef2f7; padding:4px 10px; border-radius:12px; margin-right:6px; display:inline-block; }
    .card { padding: 18px; border-radius: 14px; background: white; border: 1px solid #e9edf5; box-shadow: 0 8px 24px rgba(15,23,42,0.06); }
    .accent { color: #0f62fe; font-weight: 600; }
    </style>
    """,
    unsafe_allow_html=True,
)


def api_get(path, **params):
    resp = requests.get(f"{API_BASE}{path}", params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def api_post(path, json_body=None, files=None, params=None):
    resp = requests.post(f"{API_BASE}{path}", json=json_body, files=files, params=params, timeout=60)
    resp.raise_for_status()
    return resp.json()


st.title("AI Recruiting Agent")
st.caption(f"Backend: {API_BASE}")

# --- Load reference data ---
jobs_data = api_get("/jobs")
jobs = jobs_data.get("jobs", [])
resumes_data = api_get("/resumes")

left, right = st.columns([1.2, 1])

# ---------------- Upload & Job ----------------
with left:
    st.subheader("Upload Resume")
    with st.container():
        lang = st.selectbox("Language", ["en", "ru"], index=0)
        upload_file = st.file_uploader("Resume file (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
        if st.button("Upload", type="primary", disabled=not upload_file, use_container_width=True):
            if upload_file:
                files = {"file": (upload_file.name, upload_file.getvalue(), upload_file.type or "application/octet-stream")}
                res = api_post("/resumes/upload", files=files, params={"language": lang})
                st.success(f"Uploaded {res.get('resume_id')} • {res.get('candidate_name') or 'Unknown'}")
                extracted_skills = res.get('extracted_skills', [])
                extracted_keywords = res.get('extracted_keywords', [])
                if extracted_skills:
                    st.markdown(f"**Skills:** {', '.join(extracted_skills[:15])}")
                if extracted_keywords:
                    st.markdown(f"**Keywords:** {', '.join(extracted_keywords[:15])}")

    st.subheader("Create Job")
    with st.container():
        with st.form("job_form"):
            title = st.text_input("Title")
            company = st.text_input("Company")
            required_skills = st.text_area("Required skills (comma-separated)")
            nice_to_have = st.text_area("Nice to have (comma-separated)")
            description = st.text_area("Description", height=160)
            submitted = st.form_submit_button("Save Job", use_container_width=True)
            if submitted:
                payload = {
                    "title": title,
                    "company": company,
                    "description": description,
                    "required_skills": [s.strip() for s in required_skills.split(",") if s.strip()],
                    "nice_to_have_skills": [s.strip() for s in nice_to_have.split(",") if s.strip()],
                }
                job_res = api_post("/jobs", json_body=payload)
                st.success(f"Job created: {job_res['job_id']}")

# ---------------- Recommendations ----------------
with right:
    st.subheader("Recommendations")
    with st.container():
        job_options = {f"{j['title']} ({j['job_id']})": j["job_id"] for j in jobs}
        selected_job = st.selectbox("Select job", [""] + list(job_options.keys()))
        matcher_type = st.selectbox("Matcher", ["semantic", "tfidf", "cross_encoder", "llm", "tfidf_ml"])
        top_n = st.slider("Top N", 1, 10, 5)
        rec_lang = st.selectbox("Response language", ["en", "ru"], index=0)
        run = st.button("Get Recommendations", type="primary", disabled=not selected_job, use_container_width=True)

    if run and selected_job:
        job_id = job_options.get(selected_job, None)
        res = api_get(
            "/recommendations",
            job_id=job_id,
            matcher_type=matcher_type,
            top_n=top_n,
            language=rec_lang,
        )
        st.markdown("#### Top candidates")
        rows = []
        for c in res["top_candidates"]:
            rows.append({
                "Resume": c["resume_id"],
                "Name": c.get("candidate_name"),
                "Score": round(c["overall_score"], 3),
                "Sem/LLM": round(c["semantic_similarity"] or 0, 3),
                "Skills": round(c["skills_match"], 3),
                "Matched": ", ".join(c.get("matched_skills", [])[:4]),
                "Missing": ", ".join(c.get("missing_skills", [])[:4]),
                "Method": c.get("matching_method"),
            })
        if rows:
            st.dataframe(rows, use_container_width=True, hide_index=True)
        else:
            st.info("No candidates found.")

# ---------------- Resumes Snapshot ----------------
st.markdown("### Resumes")
if resumes_data.get("resumes"):
    table = []
    for r in resumes_data["resumes"]:
        table.append({
            "Resume ID": r.get("resume_id"),
            "Name": r.get("name"),
            "Email": r.get("email"),
            "Skills": r.get("skills_count"),
            "Keywords": r.get("keywords_count"),
        })
    st.dataframe(table, use_container_width=True, hide_index=True)
else:
    st.info("No resumes uploaded yet.")
