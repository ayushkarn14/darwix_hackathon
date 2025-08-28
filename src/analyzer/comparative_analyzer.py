import requests
import re
import os
from urllib.parse import quote
from bs4 import BeautifulSoup
from ..utils.article_fetcher import fetch_article_content
from langchain_google_genai import ChatGoogleGenerativeAI


def extract_search_terms(article_data):
    """Extract key search terms from the article to find related articles."""
    title = article_data.get("title", "")

    # Remove common words and punctuation
    title = re.sub(r"[^\w\s]", " ", title)
    common_words = [
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "is",
        "are",
        "was",
        "were",
        "in",
        "on",
        "at",
        "to",
        "for",
        "with",
        "by",
        "says",
        "said",
    ]

    words = title.lower().split()
    keywords = [word for word in words if word not in common_words and len(word) > 3]

    # Take the most important 3-4 keywords
    return " ".join(keywords[:4])


def find_related_articles(article_data, max_articles=3):
    """Find related articles on the same topic from different sources."""
    search_terms = extract_search_terms(article_data)
    print(f"Searching for related articles about: {search_terms}")

    search_url = f"https://news.google.com/search?q={quote(search_terms)}&hl=en-US"

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        article_links = soup.select("a[href^='./articles/']")

        related_articles = []
        seen_titles = set()  # To avoid duplicates
        current_domain = (
            article_data.get("url", "").split("/")[2] if article_data.get("url") else ""
        )

        for link in article_links:
            if len(related_articles) >= max_articles:
                break

            # Convert relative URL to absolute
            article_path = link.get("href").replace("./articles/", "")
            article_url = f"https://news.google.com/articles/{article_path}"

            # Get the title
            title_elem = link.select_one("h3")
            if not title_elem:
                continue

            title = title_elem.get_text().strip()

            # Skip if we've seen this title or it's from the same source
            if title in seen_titles:
                continue

            # Try to get source name
            source_elem = link.select_one("div[data-n-tid]")
            source = source_elem.get_text().strip() if source_elem else "Unknown"

            # Skip if it's from the same domain as original article
            if current_domain.lower() in source.lower():
                continue

            seen_titles.add(title)
            related_articles.append(
                {"title": title, "url": article_url, "source": source}
            )

        return related_articles

    except Exception as e:
        print(f"Error finding related articles: {e}")
        return []


def compare_article_perspectives(original_article, related_articles):
    """Compare the perspectives between the original and related articles."""
    if not related_articles:
        return {
            "perspective_analysis": "Unable to find related articles for comparison.",
            "related_articles": [],
        }

    # Fetch content from related articles
    articles_with_content = []
    for article in related_articles:
        content = fetch_article_content(article["url"])
        if content:
            articles_with_content.append(
                {
                    "title": article["title"],
                    "source": article["source"],
                    "content": content.get("content", "")[
                        :1000
                    ],  # Limit to first 1000 chars
                }
            )

    if not articles_with_content:
        return {
            "perspective_analysis": "Unable to fetch content from related articles.",
            "related_articles": related_articles,
        }

    # Use LLM to compare perspectives
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return {
            "perspective_analysis": "API key not available for comparative analysis.",
            "related_articles": related_articles,
        }

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2)

    # Create comparison prompt
    prompt = f"""
    I'm going to provide you with an original article and {len(articles_with_content)} related articles on the same topic.
    Please compare how they cover the story and identify unique biases, differences in framing, or details emphasized/omitted.
    
    Original Article Title: {original_article.get('title')}
    Original Article Excerpt: {original_article.get('content', '')[:1000]}
    
    Related Articles:
    """

    for i, article in enumerate(articles_with_content, 1):
        prompt += f"\nArticle {i} ({article['source']}) - {article['title']}:\n{article['content']}\n"

    prompt += """
    Please provide a comparative analysis that highlights:
    1. Key differences in how these articles frame the same story
    2. Important facts mentioned in some articles but omitted in others
    3. Differences in tone and language between the sources
    4. Potential biases revealed through this comparative analysis
    """

    try:
        result = llm.invoke(prompt)
        perspective_analysis = (
            result.content if hasattr(result, "content") else str(result)
        )
    except Exception as e:
        perspective_analysis = f"Error performing comparative analysis: {str(e)}"

    return {
        "perspective_analysis": perspective_analysis,
        "related_articles": related_articles,
    }
