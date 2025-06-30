#!/usr/bin/env python3
"""
Test script to verify the fixes for:
1. Summary unavailable issue
2. Incorrect cryptocurrency categorization
"""

import sys
import os
sys.path.insert(0, 'src')

from core.categorizer import Categorizer
from core.multi_llm_summarizer import MultiLLMSummarizer

def test_categorization():
    """Test the improved categorization logic"""
    print("🧪 Testing Categorization Fixes...")
    
    categorizer = Categorizer()
    
    # Test cases that should NOT be categorized as Cryptocurrency
    test_cases = [
        {
            "title": "Ex-Meta engineers have built an AI tool to plan every detail of your trip",
            "full_text": "The travel industry has gathered extensive data about trips and transportation...",
            "expected": "Technology"  # Should be Technology, not Cryptocurrency
        },
        {
            "title": "Google embraces AI in the classroom with new Gemini tools",
            "full_text": "Google announced a series of updates intended to bring its Gemini AI...",
            "expected": "Education"  # Should be Education, not Cryptocurrency
        },
        {
            "title": "Mexican drug cartel hacker spied on FBI official's phone",
            "full_text": "In 2018, a hacker hired by the Mexican Sinaloa drug cartel...",
            "expected": "Technology"  # Should be Technology, not Cryptocurrency
        },
        {
            "title": "India refuses to give in to US demand on agriculture in trade talks",
            "full_text": "India has refused to give in to the US demand for market access...",
            "expected": "Politics"  # Should be Politics, not Cryptocurrency
        }
    ]
    
    # Test cases that SHOULD be categorized as Cryptocurrency
    crypto_cases = [
        {
            "title": "Bitcoin reaches new all-time high as institutional adoption grows",
            "full_text": "Bitcoin cryptocurrency has reached a new all-time high as more institutions adopt digital currency...",
            "expected": "Cryptocurrency"
        },
        {
            "title": "Ethereum blockchain technology enables new DeFi protocols",
            "full_text": "Ethereum blockchain technology is enabling new decentralized finance (DeFi) protocols...",
            "expected": "Cryptocurrency"
        }
    ]
    
    print("\n📊 Testing non-crypto articles (should NOT be Cryptocurrency):")
    for i, case in enumerate(test_cases, 1):
        category = categorizer.categorize_news(case)
        status = "✅ PASS" if category != "Cryptocurrency" else "❌ FAIL"
        print(f"  {i}. {case['title'][:50]}...")
        print(f"     Expected: {case['expected']}, Got: {category} {status}")
    
    print("\n📊 Testing crypto articles (should BE Cryptocurrency):")
    for i, case in enumerate(crypto_cases, 1):
        category = categorizer.categorize_news(case)
        status = "✅ PASS" if category == "Cryptocurrency" else "❌ FAIL"
        print(f"  {i}. {case['title'][:50]}...")
        print(f"     Expected: {case['expected']}, Got: {category} {status}")

def test_fallback_summary():
    """Test the fallback summary generation"""
    print("\n🧪 Testing Fallback Summary Generation...")
    
    summarizer = MultiLLMSummarizer()
    
    test_article = {
        "title": "BRICS nations' interest in national currency trade is not de-dollarisation",
        "source": "Businessline",
        "full_text": """Get businessline apps on
Connect with us
TO ENJOY ADDITIONAL BENEFITS
Connect With Us
Get BusinessLine apps on
The US dollar will continue to exist in the global trade, said the official
BRICS nations will work on increasing their understanding of the importance of having an alternative mechanism to do trade in national currencies to protect against geopolitical vulnerabilities, but the process is not the same as de-dollarisation, a senior MEA official has said.
"The dollar (US) will continue to exist in the global trade. It's the most dominant currency. I don't think there's a competition there. It's just that countries will look for alternatives and we have to appreciate their effort in the direction," Dammu Ravi, MEA Secretary (ER), said."""
    }
    
    # Test the fallback summary function
    fallback_summary = summarizer._create_fallback_summary(test_article)
    
    print(f"📄 Original title: {test_article['title']}")
    print(f"📝 Fallback summary: {fallback_summary}")
    
    # Check if summary is meaningful
    if len(fallback_summary) > 50 and "Summary unavailable" not in fallback_summary:
        print("✅ PASS: Fallback summary generated successfully")
    else:
        print("❌ FAIL: Fallback summary is too short or contains 'Summary unavailable'")

if __name__ == "__main__":
    print("🔧 Testing News Feed Pro Fixes")
    print("=" * 50)
    
    test_categorization()
    test_fallback_summary()
    
    print("\n" + "=" * 50)
    print("✅ Test completed! Check results above.")
