import streamlit as st
import pandas as pd
import plotly.express as px
from src.parsers import extract_text
from src.analysis import build_resume_profile, analyze_resume, match_jobs
from src.rag import answer_question

st.set_page_config(page_title="CareerLens AI", page_icon="🎯", layout="wide")
st.markdown("""<style>
.block-container{max-width:1400px;padding-top:1.5rem}
.hero{padding:1.5rem 1.8rem;border:1px solid #e5eaf0;border-radius:18px;background:linear-gradient(110deg,#f4f8ff,#f2fbf7);margin-bottom:1rem}
.hero h1{margin:0;color:#17243a}.hero p{color:#667085;margin:.4rem 0 0}
.pill{display:inline-block;background:#edf4ff;color:#2856a6;border-radius:20px;padding:4px 9px;margin:3px;font-size:.82rem}
</style>""", unsafe_allow_html=True)
for key, default in [("resume_text",""),("resume_name",""),("jobs",[]),("matches",None)]:
    if key not in st.session_state: st.session_state[key]=default

with st.sidebar:
    st.title("🎯 CareerLens AI")
    st.caption("Resume intelligence • Job matching • Evidence-based Q&A")
    page=st.radio("Workspace",["Overview","Resume analysis","Job matching","Ask your documents"])
    st.divider()
    st.caption("Upload a resume → add job descriptions → compare evidence → ask questions.")

st.markdown('<div class="hero"><h1>CareerLens AI</h1><p>Turn your resume and job descriptions into clear, explainable career insights.</p></div>',unsafe_allow_html=True)

if page=="Overview":
    a,b,c=st.columns(3)
    a.metric("Resume loaded","Yes" if st.session_state.resume_text else "Not yet")
    b.metric("Job descriptions",len(st.session_state.jobs))
    c.metric("Analysis","Ready" if st.session_state.matches else "Awaiting")
    st.subheader("Get started")
    st.write("Upload a resume, add job descriptions, review transparent match scores and ask questions grounded in your documents.")
    st.info("This is a decision-support prototype, not an automated hiring decision system. Match scores are heuristic indicators, not hiring probabilities.")
    x,y,z=st.columns(3)
    x.markdown("**📄 Resume intelligence**\n\nExtract skills and identify improvement opportunities.")
    y.markdown("**🧭 Job matching**\n\nCompare skills and textual relevance against job requirements.")
    z.markdown("**🔎 RAG assistant**\n\nRetrieve relevant evidence passages from your documents.")

elif page=="Resume analysis":
    st.subheader("Upload your resume")
    up=st.file_uploader("PDF, DOCX or TXT",type=["pdf","docx","txt"])
    if up:
        try:
            txt=extract_text(up.getvalue(),up.name)
            if txt.strip():
                st.session_state.resume_text=txt; st.session_state.resume_name=up.name
                st.success(f"Loaded {up.name} ({len(txt.split())} words).")
            else: st.error("No readable text found. Scanned PDFs need OCR before upload.")
        except Exception as e: st.error(str(e))
    if st.session_state.resume_text:
        with st.expander("Review extracted text"): st.text_area("Resume text",st.session_state.resume_text,height=250)
        profile=build_resume_profile(st.session_state.resume_text)
        a,b,c=st.columns(3); a.metric("Words",profile["word_count"]); b.metric("Detected skills",len(profile["skills"])); c.metric("Email found","Yes" if profile["email"] else "No")
        st.markdown("### Detected skills")
        st.markdown(" ".join(f'<span class="pill">{s}</span>' for s in profile["skills"]) or "No skills detected.",unsafe_allow_html=True)
        if profile["email"]: st.caption("Email: "+profile["email"])
        st.markdown("### Improvement suggestions")
        for tip in analyze_resume(st.session_state.resume_text,profile): st.write("• "+tip)

elif page=="Job matching":
    st.subheader("Add job descriptions")
    with st.form("job_form",clear_on_submit=True):
        title=st.text_input("Job title",placeholder="Junior Data Analyst")
        company=st.text_input("Company (optional)")
        jd=st.text_area("Paste job description",height=180)
        submit=st.form_submit_button("Add job description",type="primary")
        if submit:
            if title.strip() and jd.strip():
                st.session_state.jobs.append({"title":title.strip(),"company":company.strip(),"text":jd.strip()})
                st.success("Job description added.")
            else: st.error("Enter a title and job description.")
    jobfile=st.file_uploader("Or upload a TXT job description",type=["txt"],key="jobtxt")
    if jobfile and st.button("Add uploaded job"):
        st.session_state.jobs.append({"title":jobfile.name.rsplit(".",1)[0],"company":"","text":jobfile.getvalue().decode("utf-8",errors="ignore")})
        st.success("Job added.")
    for i,j in enumerate(st.session_state.jobs):
        with st.expander(f"{i+1}. {j['title']} — {j['company'] or 'Company not specified'}"):
            st.write(j["text"])
            if st.button("Remove",key=f"remove{i}"): st.session_state.jobs.pop(i); st.rerun()
    if st.session_state.jobs:
        if not st.session_state.resume_text: st.warning("Upload a resume first in Resume analysis.")
        elif st.button("Calculate job matches",type="primary"):
            st.session_state.matches=match_jobs(st.session_state.resume_text,st.session_state.jobs)
    if st.session_state.matches:
        df=pd.DataFrame(st.session_state.matches)
        st.markdown("### Match results")
        st.dataframe(df[["title","company","match_score","matched_skills_count","missing_skills_count"]],use_container_width=True,hide_index=True)
        fig=px.bar(df.sort_values("match_score"),x="match_score",y="title",orientation="h",range_x=[0,100],labels={"match_score":"Match score (%)"})
        st.plotly_chart(fig,use_container_width=True)
        for r in st.session_state.matches:
            with st.expander(f"{r['title']} — {r['match_score']}%"):
                st.write(r["explanation"])
                l,rr=st.columns(2); l.markdown("**Matched skills**"); l.write(", ".join(r["matched_skills"]) or "None detected")
                rr.markdown("**Skills to strengthen**"); rr.write(", ".join(r["missing_skills"]) or "No major detected gaps")
                st.markdown("**Next steps**")
                for t in r["recommendations"]: st.write("• "+t)
        st.download_button("Download CSV report",df.to_csv(index=False).encode(), "career_match_report.csv","text/csv")

elif page=="Ask your documents":
    docs=[]
    if st.session_state.resume_text: docs.append(("Resume",st.session_state.resume_text))
    docs += [(f"{j['title']} — {j['company'] or 'Job description'}",j["text"]) for j in st.session_state.jobs]
    if not docs: st.info("Upload a resume and add job descriptions first.")
    else:
        q=st.text_input("Ask a question",placeholder="Which required skills are missing from my resume?")
        if st.button("Find answer",type="primary",disabled=not q.strip()):
            answer,sources=answer_question(q,docs)
            st.markdown("### Retrieved answer"); st.write(answer)
            st.markdown("### Evidence passages")
            for s in sources:
                with st.expander(f"{s['document']} · relevance {s['score']:.2f}"): st.write(s["text"])
