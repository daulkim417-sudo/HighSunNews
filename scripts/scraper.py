import os
import feedparser
import json
import google.generativeai as genai
from datetime import datetime, timedelta
import time
from newspaper import Article
from googlenewsdecoder import gnewsdecoder

# 1. 환경 설정
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_real_url(google_url):
    try:
        decoded_url_obj = gnewsdecoder(google_url, interval=1)
        if decoded_url_obj.get("status"):
            return decoded_url_obj["decoded_url"]
        return google_url
    except Exception as e:
        print(f"🔗 디코딩 실패: {e}")
        return google_url

def get_article_data(google_url):
    actual_url = get_real_url(google_url)
    try:
        article = Article(actual_url, language='ko')
        article.download()
        article.parse()
        return article.text[:2000], article.top_image, actual_url
    except Exception as e:
        return "", None, actual_url

def analyze_with_gemini(title, content):
    if not content or len(content) < 100:
        return {"summary": "본문을 가져오지 못했습니다."}
    
    # 요약 시 좀 더 임팩트 있는 '속보' 스타일 요청
    prompt = f"뉴스 제목: {title}\n본문: {content}\n\n이 뉴스는 지금 막 들어온 속보야. 아주 긴박하고 섹시하게 1문장으로 요약해줘. JSON: {{\"summary\": \"내용\"}}"
    try:
        response = model.generate_content(prompt)
        json_text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(json_text)
    except:
        return {"summary": title}

def is_breaking(entry):
    """속보 여부를 판단하는 로직"""
    breaking_keywords = ['속보', '단독', '종합', '[', '특징주', '발표']
    title = entry.title
    
    # 1. 제목에 키워드가 포함되어 있는지 확인
    has_keyword = any(kw in title for kw in breaking_keywords)
    
    # 2. 시간 확인 (최근 2시간 이내 기사만 우선순위)
    # entry.published_parsed는 구조체 형태임
    published_time = datetime.fromtimestamp(time.mktime(entry.published_parsed))
    is_recent = datetime.now() - published_time < timedelta(hours=2)
    
    return has_keyword or is_recent

def main():
    RSS_URL = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(RSS_URL)
    
    # 속보 후보 솎아내기
    breaking_news_candidates = [e for e in feed.entries if is_breaking(e)]
    
    # 만약 속보 후보가 너무 적으면 그냥 최신순으로 채움
    if len(breaking_news_candidates) < 6:
        breaking_news_candidates = feed.entries[:10]

    processed_news = []
    count = 0
    
    for entry in breaking_news_candidates:
        if count >= 6: break # 최대 6개만
        
        print(f"🚀 [속보 검출] 처리 중: {entry.title}")
        
        content, top_image, actual_url = get_article_data(entry.link)
        
        # 이미지가 없는 기사는 리스트에서 제외 (비주얼 중심 사이트라면)
        if not top_image:
            continue
            
        analysis = analyze_with_gemini(entry.title, content)
        
        processed_news.append({
            "title": entry.title,
            "link": actual_url,
            "source": entry.source.title if hasattr(entry, 'source') else "Google News",
            "pubDate": entry.published,
            "summary": analysis.get("summary"),
            "image": top_image
        })
        count += 1

    result_data = {"lastUpdate": datetime.now().isoformat(), "items": processed_news}
    os.makedirs('public', exist_ok=True)
    with open('public/news.json', 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    print(f"✅ 속보 업데이트 완료! ({len(processed_news)}개)")

if __name__ == "__main__":
    main()