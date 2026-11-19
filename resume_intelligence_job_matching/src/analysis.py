import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SKILLS=["python","java","c++","sql","mysql","postgresql","mongodb","excel","power bi","tableau","pandas","numpy","scikit-learn","machine learning","deep learning","nlp","rag","langchain","llm","generative ai","data analysis","data visualization","statistics","matplotlib","seaborn","plotly","tensorflow","pytorch","aws","azure","google cloud","docker","kubernetes","git","github","linux","html","css","javascript","typescript","react","next.js","node.js","flask","fastapi","django","rest api","communication","leadership","project management","problem solving","agile","data structures","algorithms","operating systems","database management","cybersecurity","networking"]

def extract_skills(text):
    t=re.sub(r"\s+"," ",text.lower()); found=[]
    for s in SKILLS:
        if re.search(r"(?<![a-z0-9+#.])"+re.escape(s)+r"(?![a-z0-9+#.])",t): found.append(s)
    return sorted(set(found))

def build_resume_profile(text):
    email=re.search(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}",text,re.I)
    phone=re.search(r"(?<!\d)(?:\\+?\d[\d\s().-]{7,}\d)(?!\d)",text)
    return {"word_count":len(text.split()),"skills":extract_skills(text),"email":email.group(0) if email else "","phone":phone.group(0).strip() if phone else ""}

def analyze_resume(text,profile=None):
    p=profile or build_resume_profile(text); t=text.lower(); tips=[]
    if len(text.split())<180: tips.append("Add relevant projects, experience and measurable achievements where applicable.")
    if not re.search(r"\b(experience|intern|employment|work history)\b",t): tips.append("Consider adding a clearly labelled Experience section.")
    if not re.search(r"\b(projects?|portfolio)\b",t): tips.append("Add projects describing the problem, your contribution, technologies and outcome.")
    if not re.search(r"\b(education|bachelor|degree|university|college)\b",t): tips.append("Add your qualification, institution and graduation year.")
    if not re.search(r"\b(achieved|improved|increased|reduced|built|developed|automated|led|created)\b",t): tips.append("Use truthful action verbs and quantify outcomes where possible.")
    if not p["skills"]: tips.append("Include a concise Skills section with technologies you can confidently discuss.")
    tips.append("Tailor your summary and project bullets to each role; only include keywords that accurately describe your experience.")
    return tips

def _similarity(a,b):
    try:
        m=TfidfVectorizer(stop_words="english",ngram_range=(1,2),max_features=6000).fit_transform([a,b])
        return float(cosine_similarity(m[0:1],m[1:2])[0][0])
    except ValueError: return 0.0

def match_jobs(resume,jobs):
    rs=set(extract_skills(resume)); out=[]
    for j in jobs:
        js=set(extract_skills(j["text"])); matched=sorted(rs&js); missing=sorted(js-rs)
        coverage=len(matched)/max(1,len(js)) if js else 0
        score=round((.65*coverage+.35*_similarity(resume,j["text"]))*100)
        rec=[]
        if missing: rec.append("Prioritize relevant missing skills through learning or a small demonstrable project.")
        if not re.search(r"\bprojects?\b",resume,re.I): rec.append("Add relevant projects that demonstrate requested skills.")
        if not re.search(r"\b(achieved|improved|increased|reduced|built|developed|automated|led|created)\b",resume,re.I): rec.append("Strengthen suitable bullets with truthful actions and measurable outcomes.")
        if not rec: rec.append("Tailor your summary and strongest evidence to the role's priorities.")
        out.append({"title":j["title"],"company":j.get("company",""),"match_score":score,"matched_skills_count":len(matched),"missing_skills_count":len(missing),"matched_skills":matched,"missing_skills":missing,"recommendations":rec,"explanation":f"Score = 65% detected skill coverage + 35% TF-IDF text similarity. {len(matched)} of {len(js)} detected job skills also appear in the resume. This is a heuristic, not a hiring probability."})
    return sorted(out,key=lambda x:x["match_score"],reverse=True)
