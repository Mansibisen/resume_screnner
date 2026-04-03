import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import json

def scrape_linkedin_job(url: str) -> str:
    """Scrapes the job description and requirements from a LinkedIn URL or returns structured data."""
    try:
        # Check if it's a LinkedIn URL
        parsed_url = urlparse(url)
        if "linkedin.com" not in parsed_url.netloc:
            return "⚠️ Please provide a valid LinkedIn job URL"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try multiple selectors for job description
        job_description_selectors = [
            "div.description__text",
            "div.show-more-less-html__markup",
            "div.descriptions__text",
            "article"
        ]
        
        job_description = ""
        for selector in job_description_selectors:
            element = soup.find("div", {"class": selector})
            if element:
                job_description = element.get_text(strip=True)
                break
        
        if not job_description:
            # Fallback: get all text from main content
            main_content = soup.find("main")
            if main_content:
                job_description = main_content.get_text(strip=True)
        
        return job_description if job_description else "Could not retrieve job description"
        
    except requests.exceptions.RequestException as e:
        return f"Error fetching URL: {str(e)}"
    except Exception as e:
        return f"Error parsing job description: {str(e)}"