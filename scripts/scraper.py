import os
import feedparser
import json
import google.generativeai as genai
from datetime import datetime
from newspaper import Article # 뉴스 추출 전문 라이브러리

# 환경 설정
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
# 모델명을 최신 안정화 버전으로 변경 (404 방지)
model = genai.GenerativeModel('gemini-2.5-flash-lite')

def get_article_data(url):
    """newspaper3k를 사용하여 본문과 이미지를 추출"""
    try:
        article = Article(url, language='ko')
        article.download()
        article.parse()
        
        # 본문과 대표 이미지 주소 반환
        return article.text[:2000], article.top_image
    except Exception as e:
        print(f"⚠️ 기사 추출 실패: {e}")
        return "", None

def analyze_with_gemini(title, content, top_image):
    """Gemini를 사용해 요약문 생성"""
    # 이미 top_image가 있다면 LLM에게 이미지 선택을 시킬 필요가 없음 (비용 절약)
    prompt = f"""
    뉴스 제목: {title}
    뉴스 본문: {content}

    작업: 뉴스 내용을 1문장으로 아주 섹시하고 임팩트 있게 요약해줘.
    형식: {{"summary": "요약 내용"}} (JSON 형식으로만 대답해)
    """
    
    try:
        response = model.generate_content(prompt)
        json_text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(json_text)
    except Exception as e:
        print(f"⚠️ Gemini 분석 실패: {e}")
        return {"summary": "요약을 불러오지 못했습니다."}

def main():
    RSS_URL = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(RSS_URL)
    processed_news = []
    
    for entry in feed.entries[:6]:
        print(f"🚀 처리 중: {entry.title}")
        
        # 1. 전문 도구로 데이터 추출
        content, top_image = get_article_data(entry.link)
        
        # 2. Gemini로 요약만 수행
        analysis = analyze_with_gemini(entry.title, content, top_image)
        
        processed_news.append({
            "title": entry.title,
            "link": entry.link,
            "source": entry.source.title if hasattr(entry, 'source') else "Google News",
            "pubDate": entry.published,
            "summary": analysis.get("summary"),
            "image": top_image # newspaper3k가 찾은 대표 이미지
        })

    result_data = {
        "lastUpdate": datetime.now().isoformat(),
        "items": processed_news
    }

    os.makedirs('public', exist_ok=True)
    with open('public/news.json', 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 완료! {len(processed_news)}개의 뉴스가 저장되었습니다.")

if __name__ == "__main__":
    main()