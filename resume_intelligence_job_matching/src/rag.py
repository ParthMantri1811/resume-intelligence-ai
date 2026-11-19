from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def chunk_text(text,size=180,overlap=35):
    words=text.split(); chunks=[]; start=0
    while start<len(words):
        end=min(len(words),start+size); chunks.append(" ".join(words[start:end]))
        if end==len(words): break
        start=end-overlap
    return chunks

def retrieve(question,documents,top_k=4):
    passages=[]
    for name,text in documents:
        for i,chunk in enumerate(chunk_text(text)):
            passages.append({"document":name,"chunk":i+1,"text":chunk})
    if not passages: return []
    try:
        v=TfidfVectorizer(stop_words="english",ngram_range=(1,2),max_features=8000)
        m=v.fit_transform([question]+[p["text"] for p in passages])
        scores=cosine_similarity(m[0:1],m[1:]).flatten()
    except ValueError: return []
    ranked=sorted(zip(scores,passages),key=lambda x:x[0],reverse=True)
    return [{**p,"score":float(s)} for s,p in ranked[:top_k] if s>.01]

def answer_question(question,documents):
    sources=retrieve(question,documents)
    if not sources: return "I couldn't find relevant evidence in the uploaded documents. Try using terms from the resume or job description.",[]
    excerpts=[]
    for s in sources[:3]:
        text=s["text"].strip()
        excerpts.append(f"From **{s['document']}**: {text[:647]}{'...' if len(text)>650 else ''}")
    return ("I found these relevant passages. This answer is grounded in retrieved text and does not infer facts absent from your documents.\n\n"+"\n\n".join(excerpts)),sources
