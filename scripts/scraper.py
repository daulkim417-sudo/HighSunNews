import os
import feedparser
import json
import base64
import requests
import google.generativeai as genai
from datetime import datetime
from newspaper import Article

# 환경 설정
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def decode_google_news_url(url):
    """구글 뉴스 RSS의 암호화된 URL을 실제 원문 URL로 디코딩"""
    try:
        if "articles/" not in url:
            return url
        
        # URL에서 암호화된 부분 추출
        base64_str = url.split("articles/")[1].split("?")[0]
        
        # 패딩 처리 및 디코딩
        padding = '=' * (4 - len(base64_str) % 4)
        decoded_bytes = base64.urlsafe_b64decode(base64_str + padding)
        
        # 디코딩된 바이트에서 실제 URL 부분 추출 (바이너리 구조상 뒷부분에 위치)
        decoded_str = decoded_bytes.decode('latin-1')
        
        # 보통 http로 시작하는 문자열을 찾아냄
        if "http" in decoded_str:
            actual_url = "http" + decoded_str.split("http")[-1]
            # 노이즈 제거
            actual_url = "".join(c for c in actual_url if ord(c) >= 32 and ord(c) <= 126)
            return actual_url
    except Exception as e:
        print(f"🔗 URL 디코딩 실패 (기본값 사용): {e}")
    return url

def get_article_data(google_url):
    """디코딩된 URL로 실제 기사 데이터를 추출"""
    actual_url = decode_google_news_url(google_url)
    print(f"🔗 원문 주소 확인: {actual_url}")
    
    try:
        article = Article(actual_url, language='ko')
        article.download()
        article.parse()
        
        # 구글 서버 이미지가 아닌 실제 언론사 서버 이미지를 가져옴
        return article.text[:2000], article.top_image
    except Exception as e:
        print(f"⚠️ 원문 파싱 실패: {e}")
        return "", None

def analyze_with_gemini(title, content):
    """Gemini AI 요약"""
    prompt = f"뉴스 제목: {title}\n본문: {content}\n\n위 내용을 1문장으로 섹시하게 요약해줘. JSON 형식: {{\"summary\": \"내용\"}}"
    try:
        response = model.generate_content(prompt)
        json_text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(json_text)
    except:
        return {"summary": title}

def main():
    RSS_URL = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(RSS_URL)
    processed_news = []
    
    for entry in feed.entries[:6]:
        print(f"🚀 처리 중: {entry.title}")
        content, top_image = get_article_data(entry.link)
        analysis = analyze_with_gemini(entry.title, content)
        
        processed_news.append({
            "title": entry.title,
            "link": decode_google_news_url(entry.link), # 링크도 원문 주소로 저장
            "source": entry.source.title if hasattr(entry, 'source') else "Google News",
            "pubDate": entry.published,
            "summary": analysis.get("summary"),
            "image": top_image
        })

    # 파일 저장 로직 (이전과 동일)
    result_data = {"lastUpdate": datetime.now().isoformat(), "items": processed_news}
    os.makedirs('public', exist_ok=True)
    with open('public/news.json', 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()