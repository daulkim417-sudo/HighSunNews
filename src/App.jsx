import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'

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

  if (loading) return (
    <div className="flex items-center justify-center min-h-screen bg-black">
      <motion.div 
        animate={{ scale: [1, 1.1, 1], opacity: [0.3, 1, 0.3] }}
        transition={{ duration: 1.5, repeat: Infinity }}
        className="text-white font-black italic text-5xl tracking-tighter"
      >
        ANALYZING...
      </motion.div>
    </div>
  )

  return (
    <div className="min-h-screen bg-black text-white selection:bg-fuchsia-500 selection:text-white overflow-x-hidden font-sans">
      
      {/* 헤더 섹션 */}
      <header className="relative pt-32 pb-16 px-6 border-b border-white/5">
        <div className="max-w-7xl mx-auto relative z-10">
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className="flex flex-col md:flex-row items-start md:items-end justify-between gap-8"
          >
            <div>
              <h1 className="text-8xl md:text-[12rem] font-black italic tracking-tighter leading-[0.8] uppercase select-none">
                HighSun<br/>
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-fuchsia-600 via-purple-500 to-indigo-400 animate-gradient-x">News.</span>
              </h1>
              <div className="mt-10 flex gap-6 text-[10px] font-black tracking-[0.4em] uppercase text-zinc-600">
                <span>// AI CURATED FEED</span>
                <span>// VERSION 2.0</span>
              </div>
            </div>

            {newsData && (
              <div className="bg-zinc-900/50 backdrop-blur-sm border border-white/5 p-6 rounded-none text-right min-w-[200px]">
                <p className="text-[10px] text-fuchsia-500 font-bold mb-2 uppercase tracking-widest italic">Live Updates</p>
                <p className="text-2xl font-black font-mono leading-none tracking-tighter">
                  {new Date(newsData.lastUpdate).toLocaleTimeString('ko-KR', { hour12: false })}
                </p>
              </div>
            )}
          </motion.div>
        </div>
      </header>

      {/* 뉴스 그리드 */}
      <main className="max-w-7xl mx-auto px-6 py-24">
        <motion.div 
          initial="hidden"
          animate="visible"
          variants={{
            visible: { transition: { staggerChildren: 0.1 } }
          }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-12"
        >
          {newsData?.items.map((item, index) => (
            <motion.article
              key={index}
              variants={{
                hidden: { opacity: 0, y: 20 },
                visible: { opacity: 1, y: 0 }
              }}
              className="group flex flex-col cursor-pointer relative"
              onClick={() => window.open(item.link, '_blank')}
            >
              {/* 이미지 영역: 봇 탐지 우회 정책 적용 */}
              <div className="relative aspect-[16/10] mb-6 overflow-hidden bg-zinc-900 border border-white/5">
                {item.image ? (
                  <img 
                    src={item.image} 
                    alt={item.title}
                    referrerPolicy="no-referrer"
                    className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110 grayscale group-hover:grayscale-0"
                    onError={(e) => {
                      e.target.style.display = 'none'; // 이미지 로드 실패 시 가림
                    }}
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-zinc-900 to-black">
                    <span className="text-zinc-800 font-black italic text-5xl italic tracking-tighter select-none">HSN.</span>
                  </div>
                )}
                <div className="absolute top-4 left-4 bg-black/80 backdrop-blur-md px-2 py-1 text-[9px] font-black tracking-widest text-white uppercase border border-white/10">
                  {item.source}
                </div>
              </div>

              {/* 텍스트 영역 */}
              <div className="flex flex-col flex-grow">
                <h3 className="text-2xl font-bold leading-tight tracking-tighter mb-4 group-hover:text-fuchsia-500 transition-colors">
                  {item.title}
                </h3>
                
                {/* AI 요약문 (Summary) */}
                <p className="text-zinc-500 text-sm leading-relaxed mb-8 line-clamp-3 font-medium">
                  {item.summary || "No summary available for this feed."}
                </p>

                <div className="mt-auto pt-4 border-t border-white/5 flex justify-between items-center text-[10px] font-bold text-zinc-600 tracking-widest uppercase italic">
                  <span>{new Date(item.pubDate).toLocaleDateString()}</span>
                  <span className="group-hover:text-white transition-colors">Read Article +</span>
                </div>
              </div>
            </motion.article>
          ))}
        </motion.div>
      </main>

      {/* 푸터 */}
      <footer className="pt-60 pb-20 px-6 border-t border-white/5">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-12 text-zinc-800 font-black tracking-tighter italic text-6xl md:text-9xl select-none overflow-hidden uppercase whitespace-nowrap opacity-20">
          HighSun Independent News HighSun Independent News
        </div>
        <div className="max-w-7xl mx-auto mt-20 flex justify-between items-end">
          <p className="text-[10px] font-mono text-zinc-700 uppercase tracking-widest">© 2026 HSN. All Rights Reserved.</p>
          <div className="w-12 h-px bg-zinc-800"></div>
        </div>
      </footer>
    </div>
  )
}

export default App