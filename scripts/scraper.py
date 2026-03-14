import os
import feedparser
import json
import google.generativeai as genai
from datetime import datetime
from newspaper import Article
# 공식 문서에 따른 정확한 임포트
from googlenewsdecoder import gnewsdecoder

# 1. 환경 설정
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_real_url(google_url):
    """구글 뉴스 링크를 실제 언론사 URL로 해독"""
    try:
        # 공식 문서 권장 사용법: interval을 주어 안정성 확보
        decoded_url_obj = gnewsdecoder(google_url, interval=1)
        
        if decoded_url_obj.get("status"):
            return decoded_url_obj["decoded_url"]
        else:
            print(f"🔗 디코딩 실패: {decoded_url_obj.get('message')}")
            return google_url
    except Exception as e:
        print(f"🔗 디코딩 중 예외 발생: {e}")
        return google_url

def get_article_data(google_url):
    """해독된 URL을 통해 원문 기사 본문 및 이미지 추출"""
    actual_url = get_real_url(google_url)
    print(f"🔗 원문 주소 확인: {actual_url}")
    
    try:
        article = Article(actual_url, language='ko')
        article.download()
        article.parse()
        
        # 본문 2000자 제한 및 대표 이미지 URL 추출
        return article.text[:2000], article.top_image, actual_url
    except Exception as e:
        print(f"⚠️ 원문 파싱 실패: {e}")
        return "", None, actual_url

def analyze_with_gemini(title, content):
    """Gemini AI 한 줄 요약"""
    if not content or len(content) < 100:
        return {"summary": "본문 내용을 가져오지 못해 요약할 수 없습니다."}
        
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
    
    # 상위 6개 기사 처리
    for entry in feed.entries[:6]:
        print(f"🚀 처리 중: {entry.title}")
        
        content, top_image, actual_url = get_article_data(entry.link)
        analysis = analyze_with_gemini(entry.title, content)
        
        processed_news.append({
            "title": entry.title,
            "link": actual_url,
            "source": entry.source.title if hasattr(entry, 'source') else "Google News",
            "pubDate": entry.published,
            "summary": analysis.get("summary"),
            "image": top_image
        })

    # 결과 저장
    result_data = {"lastUpdate": datetime.now().isoformat(), "items": processed_news}
    os.makedirs('public', exist_ok=True)
    with open('public/news.json', 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    print(f"✅ 완료! {len(processed_news)}개의 뉴스가 저장되었습니다.")

if __name__ == "__main__":
    main()