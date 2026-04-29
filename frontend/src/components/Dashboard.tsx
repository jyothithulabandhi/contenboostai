import React, { useState, useEffect } from "react"
import { Button } from "./ui/button"
import { Loader2, Copy, Save, ExternalLink, Shield, History, Sparkles } from "lucide-react"

const Dashboard = () => {
  const [productName, setProductName] = useState("")
  const [category, setCategory] = useState("Electronics - Audio")
  const [description, setDescription] = useState("")
  const [keywords, setKeywords] = useState("")
  const [urls, setUrls] = useState(["", "", ""])
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<any>(null)
  const [history, setHistory] = useState<any[]>([])
  const [activeTab, setActiveTab] = useState("optimizer")
  const [status, setStatus] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchStatus()
    fetchHistory()
  }, [])

  const fetchStatus = async () => {
    try {
      const res = await fetch("http://localhost:5000/api/status")
      const data = await res.json()
      setStatus(data)
    } catch (e) {
      console.error("Failed to fetch status", e)
    }
  }

  const fetchHistory = async () => {
    try {
      const res = await fetch("http://localhost:5000/api/history")
      const data = await res.json()
      setHistory(data)
    } catch (e) {
      console.error("Failed to fetch history", e)
    }
  }

  const handleOptimize = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!productName) return

    setLoading(true)
    setError(null)
    try {
      const res = await fetch("http://localhost:5000/api/optimize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          product_name: productName,
          category,
          current_description: description,
          target_keywords: keywords,
          competitor_urls: urls.filter(u => u.trim() !== "")
        })
      })
      
      if (!res.ok) {
        const errorData = await res.json()
        throw new Error(errorData.error || "Optimization failed")
      }
      
      const data = await res.json()
      setResults(data)
      fetchHistory()
    } catch (e: any) {
      console.error("Optimization failed", e)
      setError(e.message || "Could not connect to the optimization engine. Make sure the backend (api.py) is running.")
    } finally {
      setLoading(false)
    }
  }

  const handleSaveBest = async (variant: any) => {
    try {
      await fetch("http://localhost:5000/api/save-best", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          product_name: productName || results.current_product,
          category,
          original_description: description,
          variant
        })
      })
      fetchHistory()
      alert("Variant saved successfully!")
    } catch (e) {
      console.error("Save failed", e)
    }
  }

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-foreground font-sora pt-24 px-6 md:px-12 pb-12">
      {/* Header Info */}
      <div className="max-w-7xl mx-auto mb-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h2 className="text-3xl font-bold tracking-tight mb-2">
            CONTROL <span className="text-primary">CENTER</span>
          </h2>
          <p className="text-muted-foreground">Manage your AI-powered security product optimizations.</p>
        </div>
        
        <div className="flex items-center gap-3">
          {status && (
            <>
              <StatusPill name="Claude" active={status.claude} />
              <StatusPill name="Firecrawl" active={status.firecrawl} />
              <StatusPill name="Mem0" active={status.mem0} />
              <div className={`px-3 py-1 rounded-full text-[10px] font-bold tracking-widest uppercase ${status.mode === 'LIVE' ? 'bg-primary/20 text-primary border border-primary/30' : 'bg-yellow-500/20 text-yellow-500 border border-yellow-500/30'}`}>
                {status.mode} MODE
              </div>
            </>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="max-w-7xl mx-auto mb-8 border-b border-white/10 flex gap-8">
        <button 
          onClick={() => setActiveTab("optimizer")}
          className={`pb-4 text-sm font-medium transition-all relative ${activeTab === "optimizer" ? "text-primary" : "text-muted-foreground hover:text-foreground"}`}
        >
          Optimizer
          {activeTab === "optimizer" && <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary" />}
        </button>
        <button 
          onClick={() => setActiveTab("history")}
          className={`pb-4 text-sm font-medium transition-all relative ${activeTab === "history" ? "text-primary" : "text-muted-foreground hover:text-foreground"}`}
        >
          History
          {activeTab === "history" && <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary" />}
        </button>
      </div>

      <div className="max-w-7xl mx-auto">
        {activeTab === "optimizer" ? (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            {/* Left: Form */}
            <div className="lg:col-span-4 space-y-6">
              <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-sm font-semibold uppercase tracking-widest text-primary flex items-center gap-2">
                    <Shield className="w-4 h-4" /> Product Details
                  </h3>
                  <button 
                    type="button"
                    onClick={() => {
                      setProductName("ProSound Elite Wireless Headphones")
                      setCategory("Electronics - Audio")
                      setDescription("Good wireless headphones with noise cancellation. Long battery life. Comfortable fit.")
                      setKeywords("wireless headphones, noise cancelling, bluetooth headphones")
                      setUrls(["https://competitor1.example.com/headphones", "https://competitor2.example.com/headphones", ""])
                      setError(null)
                    }}
                    className="text-[10px] text-muted-foreground hover:text-primary transition-colors uppercase tracking-widest"
                  >
                    Load Sample
                  </button>
                </div>
                
                <form onSubmit={handleOptimize} className="space-y-4">
                  <div className="space-y-2">
                    <label className="text-xs text-muted-foreground uppercase tracking-wider">Product Name</label>
                    <input 
                      value={productName}
                      onChange={(e) => setProductName(e.target.value)}
                      placeholder="e.g. ContentBoost Pro Wireless Earbuds"
                      className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-primary/50 transition-colors"
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="text-xs text-muted-foreground uppercase tracking-wider">Category</label>
                    <select 
                      value={category}
                      onChange={(e) => setCategory(e.target.value)}
                      className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-primary/50 transition-colors appearance-none"
                    >
                      <option>Electronics - Audio</option>
                      <option>Electronics - Wearables</option>
                      <option>Home & Kitchen</option>
                      <option>Other</option>
                    </select>
                  </div>

                  <div className="space-y-2">
                    <label className="text-xs text-muted-foreground uppercase tracking-wider">Current Description</label>
                    <textarea 
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      placeholder="Paste your current description..."
                      className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-primary/50 transition-colors h-32 resize-none"
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="text-xs text-muted-foreground uppercase tracking-wider">Target Keywords</label>
                    <input 
                      value={keywords}
                      onChange={(e) => setKeywords(e.target.value)}
                      placeholder="security, AI, access control..."
                      className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-primary/50 transition-colors"
                    />
                  </div>

                  <div className="space-y-2">
                    <label className="text-xs text-muted-foreground uppercase tracking-wider">Competitor URLs</label>
                    {urls.map((url, idx) => (
                      <input 
                        key={idx}
                        value={url}
                        onChange={(e) => {
                          const newUrls = [...urls]
                          newUrls[idx] = e.target.value
                          setUrls(newUrls)
                        }}
                        placeholder={`https://competitor-${idx+1}.com`}
                        className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-primary/50 transition-colors mb-2"
                      />
                    ))}
                  </div>

                  <Button 
                    type="submit" 
                    disabled={loading || !productName}
                    className="w-full py-6 text-base font-bold uppercase tracking-widest"
                  >
                    {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : "Optimize Now"}
                  </Button>
                </form>
              </div>
            </div>

            {/* Center: Results */}
            <div className="lg:col-span-5 space-y-6">
              <h3 className="text-sm font-semibold uppercase tracking-widest text-primary flex items-center gap-2">
                <Sparkles className="w-4 h-4" /> Generated Variants
              </h3>

              {error && (
                <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-6 text-center space-y-3">
                  <p className="text-red-500 text-sm font-semibold">Backend Error</p>
                  <p className="text-xs text-foreground/70 leading-relaxed">{error}</p>
                  <p className="text-[10px] text-muted-foreground uppercase tracking-widest">Tip: Run "python api.py" in your terminal</p>
                </div>
              )}

              {!results && !error ? (
                <div className="bg-white/5 border border-white/10 rounded-xl p-12 text-center flex flex-col items-center justify-center space-y-4">
                  <div className="w-16 h-16 bg-white/5 rounded-full flex items-center justify-center">
                    <Sparkles className="w-8 h-8 text-white/20" />
                  </div>
                  <p className="text-muted-foreground text-sm max-w-xs">Enter your product details and click optimize to generate high-performance descriptions.</p>
                </div>
              ) : results && (
                <div className="space-y-6">
                  {results?.variants?.map((variant: any, idx: number) => (
                    <VariantCard 
                      key={idx} 
                      variant={variant} 
                      onSave={() => handleSaveBest(variant)}
                    />
                  ))}
                </div>
              )}
            </div>

            {/* Right: Insights */}
            <div className="lg:col-span-3 space-y-6">
              <h3 className="text-sm font-semibold uppercase tracking-widest text-primary flex items-center gap-2">
                <History className="w-4 h-4" /> Intelligence
              </h3>

              {results && results.competitor_analysis ? (
                <div className="space-y-4">
                  <InsightBox title="Market Tone" content={results.competitor_analysis.tone} />
                  <InsightBox title="Competitor USPs" list={results.competitor_analysis.usps} />
                  <InsightBox title="Strategic Gaps" list={results.competitor_analysis.gaps} />
                </div>
              ) : (
                <div className="bg-white/5 border border-white/10 rounded-xl p-6 text-center">
                  <p className="text-muted-foreground text-xs italic">Intelligence data will populate after optimization.</p>
                </div>
              )}

              {results && results.memory_context && (
                <div className="bg-white/5 border border-primary/20 rounded-xl p-6">
                  <h4 className="text-[10px] font-bold uppercase tracking-widest text-primary mb-3">Memory Retrieval</h4>
                  <p className="text-xs text-foreground/70 leading-relaxed italic">"{results.memory_context}"</p>
                </div>
              )}
            </div>
          </div>
        ) : (
          /* History View */
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-4">
              <h3 className="text-sm font-semibold uppercase tracking-widest text-primary mb-4">Past Optimizations</h3>
              <div className="bg-white/5 border border-white/10 rounded-xl overflow-hidden">
                <table className="w-full text-left text-sm">
                  <thead className="bg-white/5 border-b border-white/10">
                    <tr>
                      <th className="px-6 py-4 font-semibold uppercase tracking-wider text-[10px] text-muted-foreground">Product</th>
                      <th className="px-6 py-4 font-semibold uppercase tracking-wider text-[10px] text-muted-foreground">Type</th>
                      <th className="px-6 py-4 font-semibold uppercase tracking-wider text-[10px] text-muted-foreground">Score</th>
                      <th className="px-6 py-4 font-semibold uppercase tracking-wider text-[10px] text-muted-foreground">Date</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {history.map((item, idx) => (
                      <tr key={idx} className="hover:bg-white/5 transition-colors">
                        <td className="px-6 py-4 font-medium">{item.product_name}</td>
                        <td className="px-6 py-4">
                          <span className={`text-[10px] px-2 py-0.5 rounded-full border ${getTypeColor(item.variant_type)}`}>
                            {item.variant_type}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <span className={`font-bold ${getScoreColor(item.seo_score)}`}>{item.seo_score}</span>
                        </td>
                        <td className="px-6 py-4 text-muted-foreground text-xs">{new Date(item.created_at).toLocaleDateString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
            
            <div className="space-y-4">
              <h3 className="text-sm font-semibold uppercase tracking-widest text-primary mb-4">Quick Stats</h3>
              <div className="bg-white/5 border border-white/10 rounded-xl p-6 space-y-6">
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground text-sm">Total Optimized</span>
                  <span className="text-2xl font-bold">{history.length}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground text-sm">Avg. SEO Score</span>
                  <span className="text-2xl font-bold text-primary">
                    {history.length ? Math.round(history.reduce((a, b) => a + b.seo_score, 0) / history.length) : 0}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

const StatusPill = ({ name, active }: { name: string, active: boolean }) => (
  <div className="flex items-center gap-2 bg-white/5 px-3 py-1.5 rounded-full border border-white/10">
    <div className={`w-1.5 h-1.5 rounded-full ${active ? 'bg-primary animate-pulse' : 'bg-red-500'}`} />
    <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">{name}</span>
  </div>
)

const InsightBox = ({ title, content, list }: { title: string, content?: string, list?: string[] }) => (
  <div className="bg-white/5 border border-white/10 rounded-xl p-5">
    <h4 className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground mb-3">{title}</h4>
    {content && <p className="text-xs leading-relaxed text-foreground/80">{content}</p>}
    {list && (
      <ul className="space-y-2">
        {list.slice(0, 4).map((item, i) => (
          <li key={i} className="text-xs text-foreground/80 flex gap-2">
            <span className="text-primary mt-0.5">•</span> {item}
          </li>
        ))}
      </ul>
    )}
  </div>
)

const VariantCard = ({ variant, onSave }: { variant: any, onSave: () => void }) => {
  const [expanded, setExpanded] = useState(false)
  
  return (
    <div className="bg-white/5 border border-white/10 rounded-xl p-6 hover:border-primary/30 transition-all group">
      <div className="flex justify-between items-start mb-4">
        <span className={`text-[10px] font-bold uppercase tracking-widest px-2 py-0.5 rounded border ${getTypeColor(variant.variant_type)}`}>
          {variant.variant_type}
        </span>
        <div className="text-right">
          <div className={`text-xl font-black ${getScoreColor(variant.seo_score)}`}>{variant.seo_score}</div>
          <div className="text-[8px] uppercase tracking-tighter text-muted-foreground">SEO Score</div>
        </div>
      </div>
      
      <h4 className="text-lg font-bold mb-2 leading-tight group-hover:text-primary transition-colors">{variant.title}</h4>
      <p className="text-xs text-muted-foreground italic mb-4">{variant.short_description}</p>
      
      <div className={`text-sm leading-relaxed text-foreground/70 mb-6 ${expanded ? '' : 'line-clamp-3'}`}>
        {variant.long_description}
      </div>

      <div className="flex items-center gap-2">
        <Button 
          variant="ghost" 
          size="sm" 
          className="text-[10px] uppercase tracking-widest h-8"
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? "Show Less" : "Read Full"}
        </Button>
        <Button 
          variant="ghost" 
          size="sm" 
          className="text-[10px] uppercase tracking-widest h-8 gap-2"
          onClick={() => {
            navigator.clipboard.writeText(`${variant.title}\n\n${variant.long_description}`)
            alert("Copied to clipboard!")
          }}
        >
          <Copy className="w-3 h-3" /> Copy
        </Button>
        <Button 
          variant="navCta" 
          size="sm" 
          className="text-[10px] uppercase tracking-widest h-8 gap-2 ml-auto"
          onClick={onSave}
        >
          <Save className="w-3 h-3" /> Save Best
        </Button>
      </div>
    </div>
  )
}

const getTypeColor = (type: string) => {
  switch (type) {
    case 'seo': return 'border-emerald-500/30 text-emerald-500 bg-emerald-500/10'
    case 'conversion': return 'border-blue-500/30 text-blue-500 bg-blue-500/10'
    case 'brand': return 'border-purple-500/30 text-purple-500 bg-purple-500/10'
    default: return 'border-white/20 text-white/50'
  }
}

const getScoreColor = (score: number) => {
  if (score >= 80) return 'text-primary'
  if (score >= 60) return 'text-yellow-500'
  return 'text-red-500'
}

export default Dashboard
