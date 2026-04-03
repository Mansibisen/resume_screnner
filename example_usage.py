#!/usr/bin/env python
"""
Example usage script for the Resume Screener LangGraph application.
Run this script to test the resume screening system with a LinkedIn job URL.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to import resume_screener
sys.path.insert(0, str(Path(__file__).parent.parent))

from resume_screener.app import screen_resume
import json


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def display_results(result: dict):
    """Display the screening results in a formatted way"""
    
    print_section("FIT SCORE ANALYSIS")
    print(f"\n🎯 Overall Fit Score: {result['fit_score']['overall_score']}/100")
    
    if result['fit_score']['requirement_scores']:
        print("\n📋 Requirement Breakdown:")
        for req, score in result['fit_score']['requirement_scores'].items():
            bar = "█" * (score // 10) + "░" * (10 - score // 10)
            print(f"   {req[:30]:<30} │{bar}│ {score}/100")
    
    print_section("SKILL ANALYSIS")
    print(f"\n✅ Matched Skills ({len(result['fit_score'].get('matched_skills', []))}):")
    for skill in result['fit_score'].get('matched_skills', []):
        print(f"   • {skill}")
    
    print(f"\n❌ Missing Skills ({len(result['fit_score'].get('missing_skills', []))}):")
    for skill in result['fit_score'].get('missing_skills', []):
        print(f"   • {skill}")
    
    print(f"\n💼 Experience Fit: {result['fit_score'].get('experience_fit', 'N/A')}")
    
    print_section("IMPROVEMENT SUGGESTIONS")
    suggestions = result['improvement_suggestions']
    if suggestions:
        for i, suggestion in enumerate(suggestions, 1):
            print(f"\n{i}. {suggestion.get('suggestion', 'N/A')}")
            print(f"   📌 Why: {suggestion.get('why_important', 'N/A')}")
            print(f"   📈 Impact: {suggestion.get('expected_impact', 'N/A')}")
    else:
        print("\n   No suggestions available")
    
    print_section("COMPREHENSIVE REPORT")
    print(f"\n{result['final_report']}")
    
    print_section("ANALYSIS COMPLETE")
    print("\n✨ Resume screening analysis completed successfully!")
    print(f"   Fit Score: {result['fit_score']['overall_score']}/100")
    if result['fit_score']['overall_score'] >= 75:
        print("   Status: 🟢 STRONG CANDIDATE - Highly recommended to apply!")
    elif result['fit_score']['overall_score'] >= 60:
        print("   Status: 🟡 MODERATE CANDIDATE - Consider applying with improvements")
    else:
        print("   Status: 🔴 WEAK CANDIDATE - Focus on improvements first")
    print()


def main():
    """Main entry point for the resume screener"""
    print("\n" + "="*70)
    print("  🚀 RESUME SCREENER - LinkedIn Job Analysis")
    print("="*70)
    print("\nThis tool analyzes your resume against LinkedIn job postings and")
    print("provides a fit score with actionable improvement suggestions.\n")
    
    # Get job URL from user
    while True:
        job_url = input("Enter LinkedIn job URL (or 'quit' to exit): ").strip()
        
        if job_url.lower() in ['quit', 'exit', 'q']:
            print("\nThank you for using Resume Screener! 👋")
            break
        
        if not job_url:
            print("⚠️  Please enter a valid URL\n")
            continue
        
        if "linkedin.com" not in job_url:
            print("⚠️  Please enter a LinkedIn job URL\n")
            continue
        
        try:
            print("\n🔄 Processing your request...\n")
            result = screen_resume(job_url)
            display_results(result)
            
            # Option to save results
            save_results = input("\nWould you like to save these results? (yes/no): ").strip().lower()
            if save_results in ['yes', 'y']:
                filename = f"screening_result_{result['fit_score']['overall_score']}.json"
                with open(filename, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"✅ Results saved to: {filename}")
            
            another = input("\nAnalyze another job? (yes/no): ").strip().lower()
            if another not in ['yes', 'y']:
                print("\nThank you for using Resume Screener! 👋")
                break
        
        except Exception as e:
            print(f"\n❌ Error during analysis: {str(e)}")
            print("Please check your job URL and try again.\n")


if __name__ == "__main__":
    main()
