from dotenv import load_dotenv
import os
import requests
import asyncio
import streamlit as st
from crawl4ai import AsyncWebCrawler
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()
GEMINI_API_KEY = "YOUR GEMIN_API_KEY"
GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
GOOGLE_SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID")

# Initialize Gemini AI (LangChain)
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0.7,
    max_tokens=1000
)

def get_short_query(user_input):
    """Prompt for generating a concise search-friendly query using Gemini AI."""
    prompt = f"Rewrite the following user query concisely while retaining its core meaning and ensuring relevance to current market trends: [User Query]. Maintain clarity and industry context, incorporating key market trends where applicable.: {user_input}"
    
    response = llm.invoke(prompt)  # Invoke AI model
    return response.content.strip()

def get_market_analysis(business_idea, scraped_content):
    """Prompt template for generating a structured market research report using Gemini AI."""
    prompt = f"""Based on the following business idea and raw market data, generate a structured market research report.

    **Business Idea:** {business_idea}

    **Raw Data:** 
    {scraped_content}

    --- 
    Format the output as follows:

    1. **Market Overview** - Provide a summary of market trends and growth potential.
    2. **Key Players & Competitors** - List major companies operating in this space.
    3. **Target Audience & Customer Insights** - Define target demographics and their preferences.
    4. **Industry Trends & Innovations** - Highlight current and future trends in this industry.
    5. **Challenges & Risks** - List potential obstacles and concerns.
    6. **Business Opportunities & Gaps** - Suggest areas where new businesses can succeed.
    7. **Investment & Revenue Insights** - Explain possible revenue models and funding opportunities.
    8. **References & Data Sources** - List key sources of information.

    Keep the response well-structured, insightful, and concise.
    """
    
    
    response = llm.invoke(prompt)
    return response.content.strip()  # Ensure we return the structured response

async def main(urls):
    """Crawl given URLs asynchronously and extract useful content."""
    async with AsyncWebCrawler() as crawler:
        extracted_data = []
        for url in urls:
            print(f"\nCrawling: {url}")
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            }
            try:
                res = await crawler.arun(url, headers=headers, page_timeout=120000, wait_until="networkidle")
                extracted_data.append(res.markdown)
            except Exception as e:
                print(f"Error crawling {url}: {e}")
    
    return extracted_data

# Step 1: User inputs a business idea
user_input = input("Enter your business idea: ")

# Step 2: Generate optimized search query
short_query = get_short_query(user_input)
print(f"\nOptimized Search Query: {short_query}")

# Step 3: Search Google API
url = "https://www.googleapis.com/customsearch/v1"
params = {
    "q": short_query,
    "key": GOOGLE_SEARCH_API_KEY,
    "cx": GOOGLE_SEARCH_ENGINE_ID,
    "num": 10,  # Number of results
}
response = requests.get(url, params=params)
dic = response.json()

# Step 4: Extract links
links = [item['link'] for item in dic.get("items", [])]
print("\nExtracted Links:", links)

# Step 5: Crawl the extracted links
if links:
    scraped_content = asyncio.run(main(links))
    
    # Join scraped content into a single text block
    structured_data = "\n\n".join(scraped_content)

    # Generate market research insights
    report = get_market_analysis(user_input, structured_data)

    print("\nMarket Research Report:\n", report)
else:
    print("No valid links found.")
