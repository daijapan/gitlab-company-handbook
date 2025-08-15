"""Configuration file for eKYC News Crawler"""

RSS_FEEDS = {
    "Academic": {
        "arXiv Computer Science": "https://rss.arxiv.org/rss/cs",
        "arXiv Cryptography": "https://rss.arxiv.org/rss/cs.CR",
        "arXiv Machine Learning": "https://rss.arxiv.org/rss/cs.LG",
    },
    "RegTech": {
        "A Team Insight RegTech": "https://a-teaminsight.com/category/regtech-insight/feed/",
        "Fintech News Switzerland RegTech": "https://fintechnews.ch/regtech/feed/",
        "RegtechTimes": "https://regtechtimes.com/feed/",
        "The Fintech Times RegTech": "https://thefintechtimes.com/category/regtech/feed/",
        "TechBullion RegTech": "https://techbullion.com/regtech/feed/",
        "TheFinanser Regulation": "https://thefinanser.com/category/regulation/feed",
        "Encompass RegTech Blog": "https://www.encompasscorporation.com/blog/feed/",
    },
    "Industry": {
        "Risk.net Regulation": "https://www.risk.net/feeds/rss/category/regulation",
        "Finextra Risk": "https://www.finextra.com/rss/risk.xml",
        "Biometric Update": "https://www.biometricupdate.com/feed",
        "Identity Week": "https://identityweek.net/feed/",
    },
    "Cybersecurity": {
        "NIST Cybersecurity": "https://www.nist.gov/news-events/cybersecurity/rss.xml",
        "Dark Reading Identity": "https://www.darkreading.com/rss/identity-and-access-management.xml",
        "Security Week Identity": "https://www.securityweek.com/category/identity-management/feed/",
    }
}

KEYWORDS = [
    "ekyc", "e-kyc", "digital identity", "identity verification", "biometric",
    "kyc", "aml", "know your customer", "anti-money laundering",
    "digital onboarding", "identity management", "authentication",
    "verification", "compliance", "regtech", "fintech identity",
    "blockchain identity", "self-sovereign identity", "ssi",
    "zero-knowledge", "privacy-preserving", "gdpr", "data protection"
]

OUTPUT_DIR = "output"
MAX_ARTICLES_PER_FEED = 20
