import os
import feedparser
import json
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from datetime import datetime

# 1. 환경 설정 (GitHub Secrets 혹은 로컬 환경 변수)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ 에러: GEMINI_API_KEY가 설정되지 않았습니다.")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash-lite')

def get_article_content(url):
    """뉴스 원문에서 본문 텍스트와 이미지 후보들을 추출"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 불필요한 태그 제거
        for s in soup(['script', 'style', 'nav', 'footer', 'header']):
            s.decompose()
            
        # 본문 텍스트 (앞부분 2000자만)
        content = soup.get_text(separator=' ', strip=True)[:2000]
        
        # 모든 이미지 태그 추출
        images = [img.get('src') for img in soup.find_all('img') if img.get('src') and img.get('src').startswith('http')]
        
        return content, images
    except Exception as e:
        print(f"⚠️ 원문 파싱 실패 ({url}): {e}")
        return "", []

def analyze_with_gemini(title, content, images):
    """Gemini를 사용해 요약 및 최적의 이미지 선정"""
    prompt = f"""
    뉴스 제목: {title}
    뉴스 본문: {content}
    이미지 후보 리스트: {images[:10]}

    위 정보를 바탕으로 다음 작업을 수행해:
    1. 뉴스 내용을 1문장으로 아주 섹시하고 임팩트 있게 요약해줘.
    2. 이미지 후보 리스트 중에서 뉴스 내용과 가장 관련 있는 이미지 URL 하나만 골라줘. 
       만약 적절한 이미지가 없거나 리스트가 비어있다면 "None"이라고 답해줘.

    출력 형식은 반드시 아래 JSON 형식만 지켜줘:
    {{
      "summary": "요약 내용",
      "image": "이미지 URL 혹은 None"
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        # JSON 응답만 추출 (가끔 AI가 설명을 붙이는 경우 방지)
        json_text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(json_text)
    except Exception as e:
        print(f"⚠️ Gemini 분석 실패: {e}")
        return {"summary": "요약을 불러오지 못했습니다.", "image": None}

def main():
    # 구글 뉴스 RSS (대한민국/한국어)
    RSS_URL = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(RSS_URL)
    
    processed_news = []
    
    # 깃허브 액션 실행 시간과 API 호출 제한을 고려해 최신 6개만 처리
    for entry in feed.entries[:6]:
        print(f"🚀 처리 중: {entry.title}")
        
        # 원문 콘텐츠 및 이미지 후보 가져오기
        content, images = get_article_content(entry.link)
        
        # Gemini AI 분석
        analysis = analyze_with_gemini(entry.title, content, images)
        
        processed_news.append({
            "title": entry.title,
            "link": entry.link,
            "source": entry.source.title if hasattr(entry, 'source') else "Google News",
            "pubDate": entry.published,
            "summary": analysis.get("summary"),
            "image": analysis.get("image") if analysis.get("image") != "None" else None
        })

    # 결과 저장
    result_data = {
        "lastUpdate": datetime.now().isoformat(),
        "items": processed_news
    }

    # public 폴더가 없으면 생성 (로컬 테스트용)
    os.makedirs('public', exist_ok=True)
    
    with open('public/news.json', 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 완료! {len(processed_news)}개의 뉴스가 저장되었습니다.")

if __name__ == "__main__":
    main()