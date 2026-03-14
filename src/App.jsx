import { useEffect, useState } from 'react'

function App() {
  const [newsData, setNewsData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // GitHub Pages 배포 환경에서도 잘 작동하도록 상대 경로 사용
    fetch('./news.json')
      .then((res) => res.json())
      .then((data) => {
        setNewsData(data)
        setLoading(false)
      })
      .catch((err) => {
        console.error("데이터 로딩 실패:", err)
        setLoading(false)
      })
  }, [])

  if (loading) return <div style={{ padding: '20px' }}>뉴스를 불러오는 중...</div>

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px', fontFamily: 'sans-serif' }}>
      <header style={{ borderBottom: '2px solid #333', marginBottom: '20px', paddingBottom: '10px' }}>
        <h1 style={{ margin: 0 }}>📰 실시간 뉴스 봇</h1>
        {newsData && (
          <p style={{ color: '#666', fontSize: '0.9rem' }}>
            마지막 업데이트: {new Date(newsData.lastUpdate).toLocaleString('ko-KR')}
          </p>
        )}
      </header>

      <main>
        {newsData?.items.length > 0 ? (
          newsData.items.map((item, index) => (
            <article key={index} style={{ 
              marginBottom: '20px', 
              padding: '15px', 
              border: '1px solid #ddd', 
              borderRadius: '8px',
              transition: 'transform 0.2s',
              cursor: 'pointer'
            }}
            onMouseOver={(e) => e.currentTarget.style.transform = 'scale(1.01)'}
            onMouseOut={(e) => e.currentTarget.style.transform = 'scale(1)'}
            onClick={() => window.open(item.link, '_blank')}
            >
              <h3 style={{ margin: '0 0 10px 0', color: '#007bff' }}>{item.title}</h3>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', color: '#888' }}>
                <span>출처: {item.source}</span>
                <span>{item.pubDate}</span>
              </div>
            </article>
          ))
        ) : (
          <p>표시할 뉴스가 없습니다.</p>
        )}
      </main>

      <footer style={{ marginTop: '40px', textAlign: 'center', color: '#aaa', fontSize: '0.8rem' }}>
        <p>GitHub Actions + React (Serverless Project)</p>
      </footer>
    </div>
  )
}

export default App