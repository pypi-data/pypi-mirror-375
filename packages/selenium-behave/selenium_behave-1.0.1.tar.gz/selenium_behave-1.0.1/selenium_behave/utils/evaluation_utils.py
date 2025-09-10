import re, requests
from bs4 import BeautifulSoup
from .bedrock_client import bedrock_claude_chat

def ai_similarity_score(context, output):
    prompt = f"On scale 0-100 how similar:\nContext:\n{context}\nOutput:\n{output}"
    resp = bedrock_claude_chat(prompt)
    try:
        return float(re.findall(r"\d+\.?\d*", resp)[0])
    except:
        return None

def detect_hallucination(context, output):
    return bedrock_claude_chat(f"Context:\n{context}\n\nOutput:\n{output}\n\nIs hallucinated? Yes/No")

def coverage_check(context, output):
    return bedrock_claude_chat(f"Missing info from context:\n{context}\n\nOutput:\n{output}")

def extract_links(text):
    return re.findall(r'https?://\S+', text)

def normalize_url(url):
    return re.sub(r'[\s\)\]\>\.,]+$', '', url.rstrip('/'))

def compare_links(expected, actual):
    expected_set = {normalize_url(l) for l in expected}
    actual_set = {normalize_url(l) for l in actual}
    return {
        "matched": list(expected_set & actual_set),
        "missing": list(expected_set - actual_set),
        "extra": list(actual_set - expected_set),
    }

def verify_link_validity(links):
    results = []
    for link in links:
        try:
            resp = requests.get(link, timeout=5)
            title = BeautifulSoup(resp.text, 'html.parser').title
            results.append((link, "Valid", title.string if title else "No Title"))
        except Exception as e:
            results.append((link, "Invalid", str(e)))
    return results

def factual_check(output):
    return bedrock_claude_chat(f"Fact check:\n{output}")
