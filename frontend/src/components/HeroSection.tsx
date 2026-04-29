import React, { Suspense, useState, useEffect } from "react"
import { Link } from "react-router-dom"
import { ArrowUp } from "lucide-react"

const Spline = React.lazy(() => import("@splinetool/react-spline"))

const HeroSection = () => {
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 })

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePos({ x: e.clientX, y: e.clientY })
    }
    window.addEventListener("mousemove", handleMouseMove)
    return () => window.removeEventListener("mousemove", handleMouseMove)
  }, [])

  return (
    <div className="flex flex-col relative">
      <section className="relative min-h-screen flex items-end bg-hero-bg overflow-x-hidden">
        {/* Spline 3D Background - pointer-events-auto allows Spline to track mouse movement */}
        <div className="absolute inset-0 z-0">
          <Suspense fallback={<div className="absolute inset-0 bg-hero-bg" />}>
            <Spline 
              scene="https://prod.spline.design/Slk6b8kz3LRlKiyk/scene.splinecode" 
              className="w-full h-full"
            />
          </Suspense>
        </div>

        {/* Mouse Tracking Spotlight - Improved visibility and z-index */}
        <div 
          className="fixed inset-0 z-[5] pointer-events-none transition-opacity duration-300"
          style={{
            background: `radial-gradient(circle at ${mousePos.x}px ${mousePos.y}px, rgba(119, 253, 0, 0.15), transparent 50%)`
          }}
        />

        {/* Dark overlay */}
        <div className="absolute inset-0 bg-black/40 z-[1] pointer-events-none" />

        {/* Content container */}
        <div className="relative z-10 pointer-events-none w-full max-w-[90%] sm:max-w-md lg:max-w-2xl px-6 md:px-10 pb-20 pt-32">
          <div className="flex flex-col items-start">
            <h1 
              className="text-[clamp(3rem,8vw,6rem)] font-bold leading-[1.05] tracking-[-0.05em] text-foreground mb-2 md:mb-4 uppercase opacity-0 animate-fade-up"
              style={{ animationDelay: "0.2s" }}
            >
              CONTENTBOOST <span className="text-primary">AI</span>
            </h1>

            <p 
              className="text-foreground/80 text-[clamp(1.125rem,2.5vw,1.875rem)] font-light mb-3 md:mb-6 opacity-0 animate-fade-up"
              style={{ animationDelay: "0.4s" }}
            >
              Product Optimization Engine.
            </p>

            <p 
              className="text-muted-foreground text-[clamp(0.875rem,1.5vw,1.25rem)] font-light mb-4 md:mb-8 opacity-0 animate-fade-up"
              style={{ animationDelay: "0.55s" }}
            >
              The ultimate solution for e-commerce teams to generate high-performance product descriptions using AI-driven competitor analysis and historical memory.
            </p>

            <div 
              className="flex flex-wrap gap-3 font-bold opacity-0 animate-fade-up"
              style={{ animationDelay: "0.7s" }}
            >
              <Link to="/dashboard">
                <button className="bg-primary text-primary-foreground px-6 py-3 md:px-8 md:py-4 text-sm rounded-sm cursor-pointer hover:brightness-110 transition-all active:scale-[0.97] pointer-events-auto">
                  Open Optimizer
                </button>
              </Link>
              <a href="#services" className="pointer-events-auto">
                <button className="bg-white text-background px-6 py-3 md:px-8 md:py-4 text-sm rounded-sm cursor-pointer hover:brightness-90 transition-all active:scale-[0.97]">
                  Our Tech
                </button>
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Services Section */}
      <section id="services" className="py-24 bg-[#0a0a0a] px-6 md:px-12 border-t border-white/5">
        <div className="max-w-7xl mx-auto">
          <div className="mb-16">
            <h2 className="text-3xl font-bold uppercase tracking-tight mb-4">Core <span className="text-primary">Intelligence</span></h2>
            <div className="h-1 w-20 bg-primary" />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <ServiceCard 
              title="Competitor Scraper" 
              desc="Powered by Firecrawl to extract real-time insights from competitor product pages. Scrapes up to 5 competitor pages in under 10 seconds."
              icon="01"
            />
            <ServiceCard 
              title="Historical Memory" 
              desc="Utilizes Mem0 to store and retrieve past successful optimizations for better consistency. Gets smarter with every product you optimize."
              icon="02"
            />
            <ServiceCard 
              title="SEO Engine" 
              desc="Generates highly differentiated descriptions that outrank competitors on search engines. Scores each variant 0–100 so you know exactly what to publish."
              icon="03"
            />
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about-us" className="py-24 bg-white/5 px-6 md:px-12">
        <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          <div>
            <h2 className="text-4xl font-bold mb-8 uppercase tracking-tighter">Retail & <span className="text-primary">E-Commerce</span></h2>
            <p className="text-muted-foreground text-lg mb-6 leading-relaxed">
              Managing thousands of product listings can be overwhelming. ContentBoost AI solves the problem of generic, low-converting descriptions by analyzing your competitors and learning from your brand's history.
            </p>
            <p className="text-muted-foreground text-lg mb-8 leading-relaxed">
              By combining Firecrawl's scraping power with advanced LLM reasoning, we provide descriptions that aren't just unique, but strategically engineered to convert.
            </p>
          </div>
          <div className="bg-white/5 border border-white/10 rounded-2xl p-8 flex flex-col gap-6">
            <PipelineStep 
              number="01" 
              title="10x Faster Listings" 
              desc="Go from blank page to 3 publish-ready descriptions in under 60 seconds."
            />
            <div className="h-4 w-px bg-primary/30 ml-4" />
            <PipelineStep 
              number="02" 
              title="Higher Search Rankings" 
              desc="Keyword-engineered copy that outranks generic competitor descriptions on Google."
            />
            <div className="h-4 w-px bg-primary/30 ml-4" />
            <PipelineStep 
              number="03" 
              title="Brand Consistency" 
              desc="Memory learning ensures every description sounds like your brand — not a generic template."
            />
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-white/5 bg-black px-8">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-8">
          <div className="text-xl font-bold tracking-tighter uppercase">ContentBoost <span className="text-primary">AI</span></div>
          <div className="text-sm text-muted-foreground">© 2024 ContentBoost. All Rights Reserved.</div>
        </div>
      </footer>
    </div>
  )
}

const ServiceCard = ({ title, desc, icon }: { title: string, desc: string, icon: string }) => (
  <div className="p-8 border border-white/5 bg-white/[0.02] rounded-lg hover:border-primary/50 transition-all group">
    <div className="text-primary text-4xl font-black mb-6 opacity-20 group-hover:opacity-100 transition-opacity">{icon}</div>
    <h3 className="text-xl font-bold mb-4 uppercase">{title}</h3>
    <p className="text-muted-foreground leading-relaxed">{desc}</p>
  </div>
)

const PipelineStep = ({ number, title, desc }: { number: string, title: string, desc: string }) => (
  <div className="flex gap-6 items-start">
    <div className="text-primary font-bold text-sm tracking-tighter bg-primary/10 border border-primary/20 px-2 py-1 rounded">
      {number}
    </div>
    <div>
      <h4 className="text-sm font-bold uppercase tracking-widest mb-1">{title}</h4>
      <p className="text-xs text-muted-foreground leading-relaxed">{desc}</p>
    </div>
  </div>
)

export default HeroSection
