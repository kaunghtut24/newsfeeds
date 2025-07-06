#!/usr/bin/env python3
"""
Test script to verify the improved fallback summary method
"""

import sys
import os
sys.path.insert(0, 'src')

from core.multi_llm_summarizer import MultiLLMSummarizer

def test_fallback_summary_with_numbers():
    """Test the improved fallback summary with financial data"""
    print("🧪 Testing Improved Fallback Summary (Numbers Filtering)...")
    
    summarizer = MultiLLMSummarizer()
    
    # Test article with financial data (like the problematic ones)
    test_article = {
        'title': 'Over 3/4th of capped allocation of first half for Rural Employment Guarantee Scheme spent in 3 months of FY26',
        'source': 'Businessline',
        'full_text': """-452.44 -120.75 -40.00 + 478.00 + 94.00 -452.44 -120.75 -120.75 -40.00 -40.00 + 478.00      The Rural Development Department allowed to spend up to 60 per cent of the annual allocation for MGNREGS during the first half of the financial year. However, the actual expenditure has exceeded this limit, with over three-fourths of the capped allocation already spent in just three months. This rapid spending pattern indicates high demand for rural employment under the scheme. The government may need to reassess budget allocations to meet the growing demand for rural employment opportunities."""
    }
    
    # Test the fallback summary function
    fallback_summary = summarizer._create_fallback_summary(test_article)
    
    print(f"📄 Original title: {test_article['title']}")
    print(f"📝 Original text (first 100 chars): {test_article['full_text'][:100]}...")
    print(f"✨ Improved fallback summary: {fallback_summary}")
    
    # Check if the random numbers are filtered out
    has_random_numbers = any(num in fallback_summary for num in ['-452.44', '-120.75', '+478.00', '+94.00'])
    
    if not has_random_numbers and len(fallback_summary) > 50:
        print("✅ PASS: Random numbers filtered out successfully!")
        print("✅ PASS: Summary is meaningful and readable")
    else:
        print("❌ FAIL: Random numbers still present or summary too short")
        print(f"   Has random numbers: {has_random_numbers}")
        print(f"   Summary length: {len(fallback_summary)}")
    
    return not has_random_numbers

def test_normal_article():
    """Test with a normal article without financial data"""
    print("\n🧪 Testing Normal Article (No Financial Data)...")
    
    summarizer = MultiLLMSummarizer()
    
    test_article = {
        'title': 'New AI Technology Revolutionizes Healthcare',
        'source': 'TechNews',
        'full_text': """Artificial intelligence is transforming healthcare delivery across the globe. Researchers have developed new machine learning algorithms that can detect diseases earlier than traditional methods. The technology shows promising results in cancer detection and treatment planning. Medical professionals are embracing these tools to improve patient outcomes and reduce diagnostic errors."""
    }
    
    fallback_summary = summarizer._create_fallback_summary(test_article)
    
    print(f"📄 Title: {test_article['title']}")
    print(f"✨ Fallback summary: {fallback_summary}")
    
    # Check if summary is meaningful
    if len(fallback_summary) > 50 and "Artificial intelligence" in fallback_summary:
        print("✅ PASS: Normal article summary generated correctly")
        return True
    else:
        print("❌ FAIL: Normal article summary generation failed")
        return False

if __name__ == "__main__":
    print("🔧 Testing Improved Fallback Summary Method\n")
    
    test1_passed = test_fallback_summary_with_numbers()
    test2_passed = test_normal_article()
    
    print(f"\n📊 Test Results:")
    print(f"   Financial Data Filtering: {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"   Normal Article Processing: {'✅ PASS' if test2_passed else '❌ FAIL'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! The improved fallback summary method is working correctly.")
    else:
        print("\n⚠️  Some tests failed. The fallback summary method needs further improvement.")
