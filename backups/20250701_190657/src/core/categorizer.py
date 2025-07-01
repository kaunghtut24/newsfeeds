
from typing import List, Dict
import re

class Categorizer:
    def __init__(self):
        # Define categories with weighted keywords and patterns
        self.categories = {
            "Technology": {
                "high_priority": ["artificial intelligence", "machine learning", "deep learning", "neural network", "chatgpt", "openai", "tesla", "spacex", "apple", "google", "microsoft", "amazon", "meta", "facebook", "twitter", "x.com", "github", "stackoverflow", "techcrunch", "hacker news", "ycombinator", "startup", "silicon valley", "programming", "coding", "developer", "software engineer", "data scientist", "cybersecurity", "blockchain", "cryptocurrency", "bitcoin", "ethereum", "quantum computing", "cloud computing", "aws", "azure", "gcp"],
                "medium_priority": ["tech", "technology", "ai", "ml", "software", "hardware", "app", "mobile", "web", "internet", "digital", "platform", "api", "database", "server", "network", "5g", "iot", "robotics", "automation", "algorithm", "computing", "processor", "chip", "semiconductor", "gadget", "innovation", "virtual reality", "augmented reality", "metaverse", "drone", "smart home", "wearable"],
                "low_priority": ["computer", "laptop", "smartphone", "tablet", "device", "electronic", "online", "website", "email", "social media", "streaming", "video", "gaming", "esports"]
            },
            "Business": {
                "high_priority": ["merger", "acquisition", "ipo", "venture capital", "private equity", "investment banking", "wall street", "stock market", "nasdaq", "dow jones", "s&p 500", "earnings report", "quarterly results", "ceo", "cfo", "board of directors", "shareholder", "dividend", "market cap", "valuation", "revenue", "profit", "loss", "bankruptcy", "restructuring", "iron ore producer", "mining company", "commodity prices", "ore prices", "steel producer", "mining industry", "commodity trading"],
                "medium_priority": ["business", "company", "corporation", "enterprise", "industry", "market", "finance", "financial", "investment", "funding", "capital", "stock", "shares", "trading", "economy", "economic", "commercial", "corporate", "management", "executive", "strategy", "growth", "expansion", "partnership", "iron ore", "mining", "commodity", "steel", "metals", "ore", "prices", "slashes", "cuts", "reduces"],
                "low_priority": ["money", "cost", "price", "sales", "customer", "client", "service", "product", "brand", "marketing", "advertising", "retail", "consumer", "supply chain", "manufacturing", "production"]
            },
            "Science": {
                "high_priority": ["research paper", "peer review", "clinical trial", "scientific study", "nature journal", "science journal", "nobel prize", "breakthrough discovery", "space exploration", "nasa", "spacex", "mars mission", "climate change", "global warming", "renewable energy", "nuclear fusion", "crispr", "gene editing", "genome sequencing", "particle physics", "quantum mechanics", "relativity theory"],
                "medium_priority": ["science", "research", "study", "experiment", "discovery", "physics", "chemistry", "biology", "astronomy", "space", "environment", "climate", "genetics", "evolution", "universe", "galaxy", "planet", "star", "lab", "laboratory", "theory", "analysis", "data", "innovation"],
                "low_priority": ["nature", "earth", "ocean", "weather", "animal", "plant", "ecosystem", "conservation", "sustainability", "energy", "material", "substance", "element", "molecule", "atom"]
            },
            "Health": {
                "high_priority": ["covid-19", "coronavirus", "pandemic", "vaccine", "vaccination", "clinical trial", "fda approval", "medical breakthrough", "cancer treatment", "alzheimer", "diabetes", "heart disease", "mental health", "depression", "anxiety", "therapy", "pharmaceutical", "drug development", "biotech", "medical device", "surgery", "hospital", "healthcare system"],
                "medium_priority": ["health", "medical", "medicine", "disease", "illness", "treatment", "cure", "doctor", "physician", "patient", "healthcare", "wellness", "fitness", "nutrition", "diet", "exercise", "virus", "bacteria", "infection", "diagnosis", "symptom", "prevention"],
                "low_priority": ["food", "eating", "sleep", "stress", "lifestyle", "habit", "body", "mind", "brain", "heart", "blood", "immune", "vitamin", "supplement", "organic", "natural"]
            },
            "Politics": {
                "high_priority": ["election", "voting", "campaign", "president", "prime minister", "congress", "parliament", "senate", "house of representatives", "supreme court", "legislation", "bill", "law", "policy", "government", "administration", "democracy", "republic", "constitution", "impeachment", "scandal", "corruption", "diplomacy", "foreign policy", "international relations", "treaty", "sanctions", "war", "conflict"],
                "medium_priority": ["politics", "political", "politician", "leader", "minister", "governor", "mayor", "representative", "senator", "judge", "court", "legal", "justice", "rights", "freedom", "liberty", "protest", "demonstration", "activism", "reform", "regulation"],
                "low_priority": ["vote", "citizen", "public", "community", "society", "nation", "country", "state", "city", "local", "federal", "national", "international", "global", "world"]
            },
            "Sports": {
                "high_priority": ["olympics", "world cup", "super bowl", "nba finals", "world series", "champions league", "premier league", "formula 1", "wimbledon", "masters tournament", "nfl", "nba", "mlb", "nhl", "fifa", "uefa", "ioc", "espn", "sports illustrated"],
                "medium_priority": ["sport", "sports", "football", "basketball", "soccer", "baseball", "tennis", "golf", "hockey", "cricket", "rugby", "volleyball", "swimming", "athletics", "track and field", "gymnastics", "boxing", "mma", "wrestling", "cycling", "marathon", "triathlon"],
                "low_priority": ["game", "match", "tournament", "championship", "league", "team", "player", "athlete", "coach", "training", "fitness", "exercise", "competition", "victory", "defeat", "score", "goal", "point"]
            },
            "Entertainment": {
                "high_priority": ["hollywood", "netflix", "disney", "warner bros", "universal studios", "paramount", "sony pictures", "marvel", "dc comics", "star wars", "game of thrones", "stranger things", "the office", "friends", "breaking bad", "oscar", "academy awards", "golden globe", "emmy", "grammy", "cannes", "sundance", "comic con"],
                "medium_priority": ["movie", "film", "cinema hall", "tv show", "television", "series", "episode", "season", "actor", "actress", "director", "film producer", "movie producer", "celebrity", "star", "music", "song", "album", "artist", "band", "concert", "festival", "theater", "broadway", "video streaming", "youtube", "tiktok"],
                "low_priority": ["entertainment", "show", "performance", "art", "culture", "magazine", "book", "novel", "story", "character", "plot", "scene", "audience", "fan", "review", "rating"]
            },
            "Market": {
                "high_priority": ["stock market", "bull market", "bear market", "market crash", "market rally", "trading halt", "circuit breaker", "volatility index", "vix", "futures", "options", "derivatives", "commodities", "forex", "currency", "exchange rate", "inflation", "deflation", "recession", "depression", "gdp", "unemployment", "interest rate", "federal reserve", "central bank", "commodity market", "iron ore prices", "steel prices", "metal prices", "ore trading", "commodity trading"],
                "medium_priority": ["market", "trading", "trader", "investor", "investment", "portfolio", "asset", "security", "bond", "equity", "debt", "yield", "return", "risk", "hedge", "fund", "etf", "mutual fund", "index", "benchmark", "commodity", "iron ore", "steel", "metals", "ore", "mining stocks"],
                "low_priority": ["buy", "sell", "price", "value", "worth", "cost", "expensive", "cheap", "high", "low", "up", "down", "gain", "loss", "profit", "margin", "volume", "liquidity"]
            },
            "World News": {
                "high_priority": ["united nations", "un security council", "nato", "european union", "g7", "g20", "world bank", "imf", "international monetary fund", "world health organization", "who", "international court", "war crimes", "genocide", "humanitarian crisis", "refugee crisis", "climate summit", "peace treaty", "ceasefire", "sanctions", "embargo", "diplomatic relations"],
                "medium_priority": ["world", "global", "international", "foreign", "country", "nation", "government", "conflict", "war", "peace", "crisis", "disaster", "emergency", "humanitarian", "refugee", "migration", "border", "embassy", "ambassador", "summit", "conference", "alliance", "cooperation"],
                "low_priority": ["news", "report", "update", "development", "situation", "event", "incident", "issue", "problem", "solution", "response", "reaction", "statement", "announcement", "declaration", "agreement", "deal", "negotiation"]
            },
            "General": {
                "high_priority": [],
                "medium_priority": [],
                "low_priority": []
            }
        }

        # Source-based categorization rules
        self.source_rules = {
            "techcrunch": "Technology",
            "hacker news": "Technology",
            "hackernews": "Technology",
            "ycombinator": "Technology",
            "tech": "Technology",
            "wired": "Technology",
            "ars technica": "Technology",
            "the verge": "Technology",
            "engadget": "Technology",
            "gizmodo": "Technology",
            "bloomberg": "Business",
            "reuters": "Business",
            "wall street journal": "Business",
            "financial times": "Business",
            "forbes": "Business",
            "cnbc": "Business",
            "marketwatch": "Business",
            "espn": "Sports",
            "sports illustrated": "Sports",
            "nfl": "Sports",
            "nba": "Sports",
            "cnn": "World News",
            "bbc": "World News",
            "associated press": "World News",
            "npr": "World News"
        }

    def categorize_news(self, news_item: Dict) -> str:
        """Categorizes a news item based on its title, content, and source."""

        # Check source-based rules first (highest priority)
        source = news_item.get('source', '').lower()
        for source_pattern, category in self.source_rules.items():
            if source_pattern in source:
                return category

        # Prepare text for analysis
        title = news_item.get('title', '').lower()
        content = news_item.get('full_text', '').lower()
        summary = news_item.get('summary', '').lower()
        description = news_item.get('description', '').lower()

        # Combine all text with title having higher weight
        text_to_categorize = f"{title} {title} {summary} {content} {description}"

        # Score each category
        category_scores = {}

        for category, keywords_dict in self.categories.items():
            if category == "General":
                continue

            score = 0

            # High priority keywords (weight: 10)
            for keyword in keywords_dict.get("high_priority", []):
                if self._keyword_match(keyword, text_to_categorize):
                    score += 10

            # Medium priority keywords (weight: 5)
            for keyword in keywords_dict.get("medium_priority", []):
                if self._keyword_match(keyword, text_to_categorize):
                    score += 5

            # Low priority keywords (weight: 2)
            for keyword in keywords_dict.get("low_priority", []):
                if self._keyword_match(keyword, text_to_categorize):
                    score += 2

            # Bonus for title matches (additional weight)
            for keyword in keywords_dict.get("high_priority", []) + keywords_dict.get("medium_priority", []):
                if self._keyword_match(keyword, title):
                    score += 5

            category_scores[category] = score

        # Find the category with the highest score
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            if category_scores[best_category] > 0:
                return best_category

        return "General"

    def _keyword_match(self, keyword: str, text: str) -> bool:
        """Check if keyword matches in text with word boundaries."""
        # For multi-word keywords, check exact phrase
        if ' ' in keyword:
            return keyword in text

        # For single words, use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(keyword) + r'\b'
        return bool(re.search(pattern, text, re.IGNORECASE))
