

import subprocess
from typing import List, Dict
import re

class Summarizer:
    def __init__(self, model: str = "llama3:8b"):
        self.model = model

    def check_ollama_available(self) -> bool:
        """Check if Ollama is available"""
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False

    def summarize_with_ollama(self, text: str) -> str:
        """Summarize text using Ollama"""
        try:
            # Prepare the prompt
            prompt = f"""Please provide a brief, informative summary of the following news article in 4-5 sentences. Focus only on the summary, do not include any conversational filler or extra text:

{text}

Summary:"""
            
            # Call Ollama
            result = subprocess.run([
                'ollama', 'run', self.model, prompt
            ], capture_output=True, text=True, timeout=60) # Increased timeout
            
            if result.returncode == 0:
                summary = result.stdout.strip()
                
                # Aggressively clean the response
                # Remove common conversational intros/outros
                summary = re.sub(r'^.*Summary:\s*' , '', summary, flags=re.DOTALL | re.IGNORECASE)
                summary = re.sub(r"^Here's a brief summary(?: of the article)?:\s*" , '', summary, flags=re.DOTALL | re.IGNORECASE)
                summary = re.sub(r'^This article summarizes:\s*' , '', summary, flags=re.DOTALL | re.IGNORECASE)
                summary = re.sub(r'^The article discusses:\s*' , '', summary, flags=re.DOTALL | re.IGNORECASE)
                summary = re.sub(r'^Based on the provided text:\s*' , '', summary, flags=re.DOTALL | re.IGNORECASE)
                summary = re.sub(r'^Here is a 2-3 sentence summary of the provided text:\s*' , '', summary, flags=re.DOTALL | re.IGNORECASE)
                summary = re.sub(r"^Here's a summary of the provided text:\s*" , '', summary, flags=re.DOTALL | re.IGNORECASE)
                summary = re.sub(r"^Here's a summary of the article:\s*" , '', summary, flags=re.DOTALL | re.IGNORECASE)
                summary = re.sub(r'^Here\'s a summary:\s*' , '', summary, flags=re.DOTALL | re.IGNORECASE)
                summary = re.sub(r'^Summary: Here is a 4-5 sentence summary of the news article:\s*' , '', summary, flags=re.DOTALL | re.IGNORECASE)
                summary = re.sub(r'^Summary: Here is a brief summary of the article in 4-5 sentences:\s*' , '', summary, flags=re.DOTALL | re.IGNORECASE)
                summary = re.sub(r'^Summary:\s*' , '', summary, flags=re.DOTALL | re.IGNORECASE)
                
                # Remove any trailing conversational text or incomplete sentences
                summary = re.sub(r'\n\n.*$', '', summary, flags=re.DOTALL)
                summary = re.sub(r'\n.*$', '', summary, flags=re.DOTALL)
                summary = summary.split('\n')[0] # Take only the first line after cleaning

                return summary.strip()
            else:
                return f"Error: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return "Error: Ollama request timed out"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def summarize_news_items(self, news_items: List[Dict]) -> List[Dict]:
        """Summarize all news items"""
        if not self.check_ollama_available():
            print("⚠️  Ollama not available. Using placeholder summaries.")
            for item in news_items:
                item['summary'] = f"Summary of: {item['title']}"
            return news_items
        
        print("🤖 Summarizing news with Ollama...")
        summarized_items = []
        
        for i, item in enumerate(news_items):
            print(f"Summarizing {i+1}/{len(news_items)}: {item['title'][:50]}...")
            
            # Prioritize full_text for summarization, fallback to title and source
            text_to_summarize = item.get('full_text') or f"Title: {item['title']}\nSource: {item['source']}"
            
            summary = self.summarize_with_ollama(text_to_summarize)
            item['summary'] = summary
            summarized_items.append(item)
            
        return summarized_items