import { Link, useLocation } from "react-router-dom"
import { Button } from "./ui/button"

const Navbar = () => {
  const navLinks = ["Home", "Services", "About Us"]
  const location = useLocation()
  const isHome = location.pathname === "/"

  const scrollToTop = (e: React.MouseEvent) => {
    if (isHome) {
      e.preventDefault()
      window.scrollTo({ top: 0, behavior: "smooth" })
    }
  }

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-8 lg:px-16 py-5 bg-transparent backdrop-blur-sm">
      <Link 
        to="/" 
        onClick={scrollToTop}
        className="text-foreground text-xl font-semibold tracking-tight hover:text-primary transition-colors"
      >
        CONTENTBOOST
      </Link>
      
      <div className="hidden md:flex items-center gap-8">
        {isHome ? (
          navLinks.map((link) => (
            <a
              key={link}
              href={link === "Home" ? "#" : `#${link.toLowerCase().replace(" ", "-")}`}
              onClick={link === "Home" ? scrollToTop : undefined}
              className="text-sm text-muted-foreground hover:text-foreground transition-colors uppercase tracking-widest"
            >
              {link}
            </a>
          ))
        ) : (
          <Link to="/" className="text-sm text-muted-foreground hover:text-foreground transition-colors uppercase tracking-widest">
            Home
          </Link>
        )}
      </div>

      <div className="flex items-center gap-4">
        {isHome && (
          <Button 
            asChild
            variant="navCta" 
            size="lg" 
            className="hidden md:inline-flex rounded-lg uppercase text-xs tracking-widest px-6"
          >
            <Link to="/dashboard">Dashboard</Link>
          </Button>
        )}
      </div>
    </nav>
  )
}

export default Navbar
