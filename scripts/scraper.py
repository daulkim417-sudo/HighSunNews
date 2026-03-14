import os
import feedparser
import json
import google.generativeai as genai
from datetime import datetime
import time
from newspaper import Article
from googlenewsdecoder import gnewsdecoder

# 환경 설정
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 긁어올 뉴스 소스 리스트 (RSS 기반)
NEWS_SOURCES = [
    {"name": "Google News", "url": "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"},
    {"name": "Yonhap Breaking", "url": "https://www.yonhapnewstv.co.kr/browse/feed/"}, # 예시
    # 추가하고 싶은 RSS 주소가 있다면 여기에 더 넣으면 돼
]

def get_real_url(google_url):
    try:
        if "news.google.com" in google_url:
            decoded = gnewsdecoder(google_url, interval=1)
            return decoded.get('decoded_url', google_url) if decoded.get("status") else google_url
        return google_url
    except: return google_url

def analyze_and_translate(title, content):
    """Gemini를 사용해 3개 국어로 요약 생성 (엄격한 JSON 모드)"""
    if not content or len(content) < 100:
        return {"ko": title, "en": title, "zh": title}
    
    # 프롬프트를 아주 명확하고 단순하게 수정
    prompt = f"""
    Title: {title}
    Content: {content}
    
    Task: Summarize the news in one sentence and translate it into Korean(ko), English(en), and Chinese(zh).
    Constraint: Response MUST be a valid JSON object only. No extra text.
    
    Format:
    {{
        "ko": "한국어 요약",
        "en": "English summary",
        "zh": "中文摘要"
    }}
    """
    try:
        response = model.generate_content(prompt)
        # 텍스트에서 JSON 부분만 추출하는 로직 강화
        raw_text = response.text.strip()
        start = raw_text.find('{')
        end = raw_text.rfind('}') + 1
        json_clean = raw_text[start:end]
        
        return json.loads(json_clean)
    except Exception as e:
        print(f"❌ 번역 생성 실패: {e}")
        return {"ko": title, "en": title, "zh": title}
        
def main():
    all_entries = []
    for source in NEWS_SOURCES:
        feed = feedparser.parse(source['url'])
        all_entries.extend(feed.entries[:10])

    processed_news = []
    # 중복 제거 및 속보 필터링
    seen_titles = set()
    
    for entry in all_entries:
        if entry.title in seen_titles: continue
        
        # '속보' 혹은 최신순 필터링
        is_urgent = any(kw in entry.title for kw in ['속보', '[단독]', 'Breaking', '종합'])
        if not is_urgent and len(processed_news) >= 10: continue

        print(f"🚀 처리 중: {entry.title}")
        actual_url = get_real_url(entry.link)
        
        try:
            article = Article(actual_url, language='ko')
            article.download()
            article.parse()
            
            if not article.top_image: continue
            
            translations = analyze_and_translate(entry.title, article.text[:1500])
            
            processed_news.append({
                "title": entry.title,
                "link": actual_url,
                "source": entry.source.title if hasattr(entry, 'source') else "Breaking News",
                "pubDate": entry.published,
                "image": article.top_image,
                "summaries": translations # 다국어 요약 데이터 저장
            })
            seen_titles.add(entry.title)
            if len(processed_news) >= 12: break # 최대 12개
        except: continue

    result = {"lastUpdate": datetime.now().isoformat(), "items": processed_news}
    os.makedirs('public', exist_ok=True)
    with open('public/news.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()