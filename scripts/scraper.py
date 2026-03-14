import os
import feedparser
import json
import requests
import google.generativeai as genai
from datetime import datetime
from newspaper import Article

# 환경 설정
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_real_url(google_url):
    """구글 리다이렉션 링크를 따라가서 실제 언론사 원문 URL을 알아냄"""
    try:
        # 구글 뉴스 링크는 봇 방지가 까다로울 수 있어 User-Agent 설정 필수
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        # allow_redirects=True로 설정하여 최종 목적지까지 추적
        response = requests.get(google_url, headers=headers, timeout=10, allow_redirects=True)
        return response.url
    except Exception as e:
        print(f"🔗 URL 추적 실패: {e}")
        return google_url

def get_article_data(google_url):
    # 1. 실제 주소부터 따낸다
    actual_url = get_real_url(google_url)
    print(f"🔗 원문 주소 확인: {actual_url}")
    
    try:
        # 2. 진짜 주소로 newspaper3k 실행
        article = Article(actual_url, language='ko')
        article.download()
        article.parse()
        
        # 본문과 대표 이미지 추출
        return article.text[:2000], article.top_image, actual_url
    except Exception as e:
        print(f"⚠️ 원문 파싱 실패: {e}")
        return "", None, actual_url

def analyze_with_gemini(title, content):
    if not content or len(content) < 100:
        return {"summary": "본문 내용을 가져오지 못해 요약할 수 없습니다."}
        
    prompt = f"뉴스 제목: {title}\n본문: {content}\n\n위 내용을 1문장으로 섹시하고 임팩트 있게 요약해줘. JSON 형식: {{\"summary\": \"내용\"}}"
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
    
    # 상위 6개 기사 처리
    for entry in feed.entries[:6]:
        print(f"🚀 처리 중: {entry.title}")
        
        # 기사 데이터 가져오기 (실제 URL 포함)
        content, top_image, actual_url = get_article_data(entry.link)
        
        # Gemini 요약
        analysis = analyze_with_gemini(entry.title, content)
        
        processed_news.append({
            "title": entry.title,
            "link": actual_url, # 이제 진짜 주소가 저장됨
            "source": entry.source.title if hasattr(entry, 'source') else "Google News",
            "pubDate": entry.published,
            "summary": analysis.get("summary"),
            "image": top_image
        })

    # 저장 로직
    result_data = {"lastUpdate": datetime.now().isoformat(), "items": processed_news}
    os.makedirs('public', exist_ok=True)
    with open('public/news.json', 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    print(f"✅ 완료! {len(processed_news)}개의 뉴스가 저장되었습니다.")

if __name__ == "__main__":
    main()