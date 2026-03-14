import { useEffect, useState } from 'react'
import { motion } from 'framer-motion' // 프레이머 모션 불러오기

function App() {
  const [newsData, setNewsData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
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

  // 애니메이션 설정값
  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.1 } // 자식 요소들이 0.1초 간격으로 순차적으로 등장
    }
  }

  const itemAnim = {
    hidden: { y: 20, opacity: 0 },
    show: { y: 0, opacity: 1 }
  }

  if (loading) return (
    <div className="flex items-center justify-center min-h-screen bg-gray-950">
      <div className="text-sky-500 animate-pulse text-xl font-bold">뉴스를 긁어오는 중...</div>
    </div>
  )

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 selection:bg-sky-500/30">
      {/* 상단 헤더 */}
      <header className="sticky top-0 z-50 backdrop-blur-md bg-gray-950/70 border-b border-gray-800">
        <div className="max-w-4xl mx-auto px-6 py-6 flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <h1 className="text-4xl font-black tracking-tighter bg-gradient-to-r from-sky-400 to-blue-600 bg-clip-text text-transparent">
              HIGHSUN NEWS
            </h1>
            <p className="text-gray-500 text-sm mt-1 font-medium tracking-widest uppercase">Real-time Feed</p>
          </div>
          
          {newsData && (
            <div className="text-xs font-mono text-gray-500 bg-gray-900/50 px-3 py-1 rounded-full border border-gray-800">
              LAST UPDATE: {new Date(newsData.lastUpdate).toLocaleString('ko-KR')}
            </div>
          )}
        </div>
      </header>

      {/* 메인 콘텐츠 */}
      <main className="max-w-4xl mx-auto px-6 py-12">
        {newsData?.items.length > 0 ? (
          <motion.div 
            variants={container}
            initial="hidden"
            animate="show"
            className="grid gap-6"
          >
            {newsData.items.map((item, index) => (
              <motion.article
                key={index}
                variants={itemAnim}
                whileHover={{ scale: 1.01, x: 5 }}
                className="group relative overflow-hidden bg-gray-900/40 border border-gray-800 p-6 rounded-2xl hover:border-sky-500/50 transition-colors cursor-pointer"
                onClick={() => window.open(item.link, '_blank')}
              >
                {/* 배경 장식 */}
                <div className="absolute -right-4 -top-4 w-24 h-24 bg-sky-500/5 blur-3xl group-hover:bg-sky-500/10 transition-colors" />
                
                <div className="relative z-10">
                  <h3 className="text-xl font-bold text-gray-100 group-hover:text-sky-400 transition-colors leading-tight mb-4">
                    {item.title}
                  </h3>
                  
                  <div className="flex items-center justify-between text-xs tracking-wider font-semibold">
                    <span className="text-sky-500 uppercase">{item.source}</span>
                    <span className="text-gray-600 italic">
                      {new Date(item.pubDate).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </motion.article>
            ))}
          </motion.div>
        ) : (
          <div className="text-center text-gray-600 py-20">뉴스가 없습니다.</div>
        )}
      </main>

      <footer className="py-20 text-center border-t border-gray-900">
        <p className="text-gray-600 text-xs font-mono tracking-widest">
          &copy; 2026 HIGHSUN PROJECT. ALL RIGHTS RESERVED.
        </p>
      </footer>
    </div>
  )
}

export default App