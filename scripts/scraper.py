import os
import feedparser
import json
import google.generativeai as genai
from datetime import datetime
from newspaper import Article
from googlenewsdecoder import gnewsdecoder # 라이브러리 명칭 주의

# 1. 환경 설정
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_real_url(google_url):
    """구글 뉴스 링크를 실제 언론사 URL로 해독 (요청 없이 알고리즘으로 해결)"""
    try:
        # gnewsdecoder는 dict 형태를 반환하며, 'decoded_url' 키에 실제 주소가 담김
        decoded_url = gnewsdecoder(google_url)
        return decoded_url.get('decoded_url', google_url)
    except Exception as e:
        print(f"🔗 URL 디코딩 실패: {e}")
        return google_url

def get_article_data(google_url):
    """해독된 URL을 통해 원문 기사 및 이미지 추출"""
    actual_url = get_real_url(google_url)
    print(f"🔗 원문 주소 확인: {actual_url}")
    
    try:
        article = Article(actual_url, language='ko')
        article.download()
        article.parse()
        
        # 본문(2000자 제한)과 대표 이미지 URL 반환
        return article.text[:2000], article.top_image, actual_url
    except Exception as e:
        print(f"⚠️ 원문 파싱 실패: {e}")
        return "", None, actual_url

def analyze_with_gemini(title, content):
    """Gemini AI를 활용한 섹시한 한 줄 요약"""
    if not content or len(content) < 100:
        return {"summary": "본문 내용을 충분히 가져오지 못해 요약할 수 없습니다."}
        
    prompt = f"""
    뉴스 제목: {title}
    본문 내용: {content}
    
    작업: 위 내용을 바탕으로 아주 섹시하고 임팩트 있는 한 줄 요약을 작성해줘.
    출력 형식: 반드시 {{"summary": "요약문"}} 형태의 JSON으로만 대답할 것.
    """
    
    try:
        response = model.generate_content(prompt)
        # 마크다운 태그 제거 및 정제
        json_text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(json_text)
    except Exception as e:
        print(f"⚠️ Gemini 분석 실패: {e}")
        return {"summary": title}

def main():
    RSS_URL = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(RSS_URL)
    processed_news = []
    
    print(f"📡 구글 뉴스 피드 읽기 시작... (총 {len(feed.entries)}개 중 6개 처리)")
    
    for entry in feed.entries[:6]:
        print(f"\n🚀 처리 중: {entry.title}")
        
        # 1. 데이터 추출
        content, top_image, actual_url = get_article_data(entry.link)
        
        # 2. AI 요약
        analysis = analyze_with_gemini(entry.title, content)
        
        # 3. 데이터 조립
        processed_news.append({
            "title": entry.title,
            "link": actual_url,
            "source": entry.source.title if hasattr(entry, 'source') else "Google News",
            "pubDate": entry.published,
            "summary": analysis.get("summary"),
            "image": top_image
        })

    # 4. JSON 파일 저장
    result_data = {
        "lastUpdate": datetime.now().isoformat(),
        "items": processed_news
    }

    os.makedirs('public', exist_ok=True)
    with open('public/news.json', 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 작업 완료! {len(processed_news)}개의 뉴스가 public/news.json에 저장되었습니다.")

if __name__ == "__main__":
    main()