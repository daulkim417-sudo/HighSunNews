import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

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
        animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
        transition={{ duration: 2, repeat: Infinity }}
        className="text-white font-black italic text-5xl tracking-tighter"
      >
        LOADING...
      </motion.div>
    </div>
  )

  return (
    <div className="min-h-screen bg-black text-white selection:bg-fuchsia-500 selection:text-white overflow-x-hidden">
      
      {/* 초과감한 히어로 섹션 */}
      <header className="relative pt-20 pb-10 px-6 border-b border-white/10">
        <div className="max-w-6xl mx-auto relative z-10">
          <motion.div
            initial={{ x: -100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            className="flex flex-col md:flex-row items-start md:items-end justify-between gap-6"
          >
            <div>
              <h1 className="text-7xl md:text-9xl font-black italic tracking-tighter leading-none uppercase">
                HighSun<br/>
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-fuchsia-500 via-purple-500 to-sky-500 animate-gradient-x">News.</span>
              </h1>
              <div className="mt-6 flex gap-4 text-xs font-bold tracking-[0.3em] uppercase text-zinc-500">
                <span>// Independent Feed</span>
                <span>// Source: Google RSS</span>
              </div>
            </div>

            {newsData && (
              <div className="bg-zinc-900 border border-white/10 p-4 rounded-sm text-right">
                <p className="text-[10px] text-zinc-500 font-mono leading-none mb-1 uppercase tracking-tighter">Sync Status: Active</p>
                <p className="text-sm font-mono text-fuchsia-500 uppercase tracking-tighter">
                  {new Date(newsData.lastUpdate).toLocaleTimeString()} KST
                </p>
              </div>
            )}
          </motion.div>
        </div>

        {/* 배경에 깔리는 거대한 텍스트 데코레이션 */}
        <div className="absolute top-10 right-0 text-[15rem] font-black text-white/[0.03] select-none pointer-events-none italic leading-none">
          VOL.26
        </div>
      </header>

      {/* 메인 뉴스 리스트 */}
      <main className="max-w-6xl mx-auto px-6 py-20">
        <motion.div 
          initial="hidden"
          animate="visible"
          variants={{
            visible: { transition: { staggerChildren: 0.05 } }
          }}
          className="grid grid-cols-1 md:grid-cols-12 gap-px bg-zinc-800 border-x border-zinc-800 shadow-2xl shadow-fuchsia-500/10"
        >
          {newsData?.items.map((item, index) => (
            <motion.article
              key={index}
              variants={{
                hidden: { opacity: 0, y: 30 },
                visible: { opacity: 1, y: 0 }
              }}
              whileHover={{ backgroundColor: "rgba(255,255,255,0.03)" }}
              className="md:col-span-6 lg:col-span-4 bg-black p-8 flex flex-col justify-between min-h-[320px] relative group cursor-pointer transition-all border-b border-zinc-800"
              onClick={() => window.open(item.link, '_blank')}
            >
              {/* 호버 시 나타나는 네온 인디케이터 */}
              <div className="absolute top-0 left-0 w-1 h-0 bg-fuchsia-500 group-hover:h-full transition-all duration-300" />
              
              <div>
                <div className="flex justify-between items-start mb-6">
                  <span className="text-[10px] font-black tracking-[0.2em] text-fuchsia-500 uppercase">
                    [{index + 1}]
                  </span>
                  <span className="text-[10px] font-bold text-zinc-600 uppercase">
                    {item.source}
                  </span>
                </div>
                
                <h3 className="text-2xl font-bold leading-[1.1] tracking-tight group-hover:text-fuchsia-400 transition-colors">
                  {item.title}
                </h3>
              </div>

              <div className="mt-10 flex items-end justify-between">
                <div className="text-[10px] font-mono text-zinc-500">
                  {new Date(item.pubDate).toLocaleDateString()}
                </div>
                <div className="text-zinc-700 group-hover:text-white transition-colors">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M7 17L17 7M17 7H7M17 7V17" />
                  </svg>
                </div>
              </div>
            </motion.article>
          ))}
        </motion.div>
      </main>

      {/* 푸터 */}
      <footer className="py-40 px-6 bg-zinc-950 border-t border-white/5">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-start md:items-end gap-10">
          <div className="text-8xl font-black italic text-zinc-900 select-none">
            HSN.
          </div>
          <div className="text-right">
            <p className="text-zinc-500 text-xs font-mono uppercase tracking-[0.3em]">Built for the edge</p>
            <p className="text-zinc-700 text-[10px] mt-2 tracking-tighter uppercase">© 2026 HighSun. System Status: Operational</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App