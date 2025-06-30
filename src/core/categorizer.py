
from typing import List, Dict

class Categorizer:
    def __init__(self):
        self.categories = {
            "Business": ["business", "finance", "economy", "market", "investment", "company", "ceo", "entrepreneur", "trade", "stock", "earning", "merger", "acquisition", "venture capital", "fund", "funding", "ipo", "revenue", "profit", "loss", "growth", "strategy", "management", "corporate", "industry", "report", "analyst", "bank", "banking", "loan", "credit", "debt", "tax", "regulation", "policy", "consumer", "retail", "e-commerce", "supply chain", "logistics", "manufacturing", "production", "export", "import", "gdp", "inflation", "recession", "interest rate", "central bank", "fiscal", "monetary", "startup", "techfin", "fintech", "proptech", "edtech", "agritech", "insurtech"],
            "Market": ["market", "stock", "trading", "economy", "finance", "investment", "shares", "indices", "commodities", "forex", "cryptocurrency", "bitcoin", "ethereum", "nasdaq", "dow jones", "s&p", "bse", "nse", "sensex", "nifty", "bond", "yield", "portfolio", "broker", "trader", "bull", "bear", "volatility", "liquidity", "ipo", "public offering", "valuation", "equity", "debt market", "capital market"],
            "Technology": ["tech", "technology", "ai", "software", "hardware", "innovation", "cybersecurity", "gadget", "internet", "web", "app", "developer", "programming", "coding", "machine learning", "data science", "blockchain", "cloud", "robotics", "quantum computing", "metaverse", "virtual reality", "augmented reality", "semiconductor", "chip", "processor", "network", "telecom", "5g", "biometric", "deep learning", "neural network", "algorithm", "automation", "digital", "platform", "api", "open source", "big data", "analytics", "computing", "server", "database", "mobile", "wearable", "smart home", "iot", "drone", "space tech", "biotech"],
            "Health": ["health", "medical", "medicine", "disease", "cure", "hospital", "doctor", "patient", "research", "pharma", "biotech", "wellness", "fitness", "nutrition", "vaccine", "virus", "pandemic", "epidemic", "therapy", "drug", "clinical trial", "healthcare", "insurance", "public health", "mental health", "diagnosis", "treatment", "surgery", "clinic", "hospital", "patient care", "medical device", "genomics", "crispr", "longevity"],
            "Sports": ["sport", "football", "basketball", "soccer", "tennis", "olympics", "athlete", "game", "match", "league", "championship", "team", "player", "coach", "tournament", "cup", "medal", "record", "training", "fitness", "injury", "stadium", "fan", "club", "premier league", "nba", "fifa", "ipl", "cricket", "formula 1", "golf", "boxing", "mma", "athletics", "swimming", "gymnastics", "winter sports", "extreme sports"],
            "Science": ["science", "research", "discovery", "physics", "chemistry", "biology", "astronomy", "space", "environment", "climate", "genetics", "evolution", "universe", "galaxy", "planet", "star", "experiment", "theory", "data", "analysis", "lab", "laboratory", "innovation", "breakthrough", "ecology", "geology", "meteorology", "oceanography", "paleontology", "zoology", "botany", "quantum", "particle", "cosmos", "biodiversity", "conservation", "sustainability", "renewable energy", "fusion", "nuclear", "material science", "nanotechnology"],
            "Politics": ["politics", "government", "election", "democracy", "policy", "law", "parliament", "president", "prime minister", "diplomacy", "international relations", "vote", "campaign", "legislature", "judiciary", "executive", "constitution", "bill", "act", "treaty", "summit", "protest", "activism", "human rights", "justice", "security", "defense", "foreign policy", "domestic policy", "public service", "senate", "congress", "house", "court", "supreme court", "legislation", "geopolitics", "national security", "election commission", "political party", "leader", "minister", "ambassador"],
            "Entertainment": ["entertainment", "movie", "film", "music", "celebrity", "hollywood", "art", "culture", "tv", "show", "series", "actor", "actress", "director", "artist", "album", "song", "concert", "festival", "theater", "broadway", "gallery", "museum", "fashion", "design", "gaming", "esports", "streaming", "youtube", "tiktok", "netflix", "disney", "warner bros", "media", "pop culture", "celebrity news", "red carpet", "awards", "oscar", "grammy", "emmy", "golden globe"],
            "World News": ["world", "global", "international", "country", "nation", "conflict", "crisis", "war", "peace", "humanitarian", "diplomacy", "united nations", "geopolitics", "refugee", "migration", "disaster", "natural disaster", "summit", "treaty", "alliance", "sanction", "embassy", "ambassador", "foreign affairs", "unrest", "protest", "coup", "terrorism", "security council", "g7", "g20", "nato", "eu", "africa", "asia", "europe", "americas", "middle east", "oceania"],
            "General": [] # Default category if no match is found
        }

    def categorize_news(self, news_item: Dict) -> str:
        """Categorizes a news item based on its title and full text."""
        text_to_categorize = (news_item.get('title', '') + " " + news_item.get('full_text', '')).lower()

        # Prioritize more specific categories first
        priority_categories = ["Business", "Market", "Health", "Sports", "Science", "Politics", "Entertainment", "World News", "Technology"]

        for category in priority_categories:
            keywords = self.categories[category]
            for keyword in keywords:
                if keyword in text_to_categorize:
                    return category
        return "General"
