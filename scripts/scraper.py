import feedparser
import json
import datetime
import os

def fetch_news():
    # 1. 구글 뉴스 RSS URL (한국어, 대한민국 기준)
    RSS_URL = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"
    
    # 2. 뉴스 데이터 가져오기
    print("구글 뉴스 피드를 읽어오는 중...")
    feed = feedparser.parse(RSS_URL)
    
    news_list = []
    
    # 3. 최신 뉴스 20개만 추출
    for entry in feed.entries[:20]:
        news_list.append({
            "title": entry.title,
            "link": entry.link,
            "pubDate": entry.published,
            "source": entry.source.get('title', 'Google News')
        })
    
    # 4. 저장할 데이터 구조 만들기
    data = {
        "lastUpdate": datetime.datetime.now().isoformat(),
        "totalItems": len(news_list),
        "items": news_list
    }
    
    # 5. 저장 경로 설정 (리액트의 public 폴더)
    # 로컬에서 실행할 때를 대비해 public 폴더가 없으면 생성해
    os.makedirs('public', exist_ok=True)
    
    file_path = "public/news.json"
    
    # 6. JSON 파일로 저장
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"성공! {len(news_list)}개의 뉴스가 {file_path}에 저장되었습니다.")

if __name__ == "__main__":
    fetch_news()