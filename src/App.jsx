import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

function App() {
  const [newsData, setNewsData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [lang, setLang] = useState('ko') // 기본 언어: 한국어

  useEffect(() => {
    // 강력 새로고침 시에도 최신 데이터를 가져오도록 쿼리 스트링 추가
    fetch(`./news.json?t=${new Date().getTime()}`)
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
        animate={{ scale: [1, 1.05, 1], opacity: [0.3, 1, 0.3] }}
        transition={{ duration: 1.2, repeat: Infinity }}
        className="text-white font-black italic text-5xl tracking-tighter"
      >
        ANALYZING...
      </motion.div>
    </div>
  )

  return (
    <div className="min-h-screen bg-black text-white selection:bg-fuchsia-500 selection:text-white overflow-x-hidden font-sans antialiased">
      
      {/* 헤더 섹션: 신뢰감을 주는 타이포그래피 정돈 */}
      <header className="relative pt-32 pb-16 px-6 border-b border-white/5 bg-black/50 backdrop-blur-lg sticky top-0 z-50">
        <div className="max-w-7xl mx-auto relative z-10">
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className="flex flex-col md:flex-row items-start md:items-end justify-between gap-8"
          >
            <div>
              <h1 className="text-8xl md:text-[10rem] font-black italic tracking-tighter leading-[0.8] uppercase select-none">
                HighSun<br/>
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-fuchsia-600 via-purple-500 to-indigo-400">News.</span>
              </h1>
              <div className="mt-10 flex flex-wrap gap-6 items-center">
                <div className="flex gap-6 text-[10px] font-black tracking-[0.4em] uppercase text-zinc-500">
                  <span>// AI CURATED INTELLIGENCE</span>
                  <span>// V2.5 MULTILINGUAL</span>
                </div>
                
                {/* 세련된 언어 선택 토글: 더 명확한 시각적 피드백 */}
                <div className="flex bg-zinc-900/50 p-1 border border-white/10 rounded-sm">
                  {['ko', 'en', 'zh'].map((l) => (
                    <button
                      key={l}
                      onClick={() => setLang(l)}
                      className={`px-4 py-1 text-[11px] font-black transition-all duration-300 ${
                        lang === l 
                        ? 'bg-fuchsia-600 text-white shadow-lg shadow-fuchsia-600/20' 
                        : 'text-zinc-500 hover:text-white'
                      }`}
                    >
                      {l.toUpperCase()}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {newsData && (
              <div className="bg-zinc-900/30 backdrop-blur-md border border-white/5 p-6 rounded-none text-right min-w-[220px]">
                <p className="text-[10px] text-fuchsia-500 font-bold mb-2 uppercase tracking-[0.2em] italic">Live Synchronized</p>
                <p className="text-3xl font-black font-mono leading-none tracking-tighter text-zinc-200">
                  {new Date(newsData.lastUpdate).toLocaleTimeString('ko-KR', { hour12: false })}
                </p>
                <p className="text-[9px] text-zinc-600 mt-2 font-bold uppercase tracking-widest leading-none">Standard Time Zone</p>
              </div>
            )}
          </motion.div>
        </div>
      </header>

      {/* 뉴스 그리드: 카드 디자인 가독성 강화 */}
      <main className="max-w-7xl mx-auto px-6 py-24">
        <motion.div 
          initial="hidden"
          animate="visible"
          variants={{
            visible: { transition: { staggerChildren: 0.1 } }
          }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-x-12 gap-y-20"
        >
          {newsData?.items.map((item, index) => (
            <motion.article
              key={index}
              variants={{
                hidden: { opacity: 0, y: 30 },
                visible: { opacity: 1, y: 0 }
              }}
              className="group flex flex-col cursor-pointer relative"
              onClick={() => window.open(item.link, '_blank')}
            >
              {/* 이미지 영역: 엑박 방지 프록시 + 세련된 오버레이 */}
              <div className="relative aspect-[16/10] mb-8 overflow-hidden bg-zinc-900 border border-white/5">
                {item.image ? (
                  <img 
                    src={`https://images.weserv.nl/?url=${encodeURIComponent(item.image)}&w=800&q=80`} 
                    alt={item.title}
                    referrerPolicy="no-referrer"
                    className="w-full h-full object-cover transition-transform duration-1000 group-hover:scale-105 grayscale-[0.5] group-hover:grayscale-0"
                    onError={(e) => { e.target.parentElement.innerHTML = '<div class="w-full h-full flex items-center justify-center bg-zinc-950 font-black italic text-4xl text-zinc-800">HSN.</div>'; }}
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-zinc-900 to-black">
                    <span className="text-zinc-800 font-black italic text-5xl tracking-tighter select-none">HSN.</span>
                  </div>
                )}
                <div className="absolute top-0 left-0 bg-fuchsia-600 px-3 py-1 text-[10px] font-black tracking-widest text-white uppercase italic">
                  {item.source}
                </div>
              </div>

              {/* 텍스트 영역: 가독성 중심 설계 */}
              <div className="flex flex-col flex-grow px-1">
                <h3 className="text-2xl font-bold leading-tight tracking-tight mb-4 group-hover:text-fuchsia-500 transition-colors duration-300">
                  {item.title}
                </h3>
                
                {/* 다국어 요약문 출력: 애니메이션 추가 */}
                <div className="min-h-[4.5rem] relative overflow-hidden">
                  <AnimatePresence mode="wait">
                    <motion.p 
                      key={lang}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      transition={{ duration: 0.3 }}
                      className="text-zinc-400 text-[15px] leading-relaxed mb-8 line-clamp-3 font-medium italic"
                    >
                      {item.summaries && item.summaries[lang] ? item.summaries[lang] : (item.summary || "Summary analysis in progress...")}
                    </motion.p>
                  </AnimatePresence>
                </div>

                <div className="mt-auto pt-6 border-t border-white/5 flex justify-between items-center text-[10px] font-bold text-zinc-600 tracking-widest uppercase italic">
                  <span>{new Date(item.pubDate).toLocaleDateString('ko-KR', { year: 'numeric', month: 'short', day: 'numeric' })}</span>
                  <span className="flex items-center gap-2 group-hover:text-white transition-all duration-300">
                    READ ARTICLE <span className="text-fuchsia-600">+</span>
                  </span>
                </div>
              </div>
            </motion.article>
          ))}
        </motion.div>
      </main>

      {/* 푸터: 압도적인 스케일로 마무리 */}
      <footer className="pt-60 pb-20 px-6 border-t border-white/5 bg-zinc-950/20">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-12 text-zinc-900 font-black tracking-tighter italic text-6xl md:text-[12rem] select-none overflow-hidden uppercase whitespace-nowrap opacity-10 leading-none">
          HighSun Independent News HighSun Independent News
        </div>
        <div className="max-w-7xl mx-auto mt-20 flex justify-between items-end border-t border-white/5 pt-10">
          <div>
            <p className="text-[10px] font-mono text-zinc-600 uppercase tracking-widest mb-1">Based on Gemini 1.5 Flash Model</p>
            <p className="text-[10px] font-mono text-zinc-700 uppercase tracking-widest">© 2026 HSN. All Rights Reserved.</p>
          </div>
          <div className="w-24 h-[1px] bg-fuchsia-600/50"></div>
        </div>
      </footer>
    </div>
  )
}

export default App