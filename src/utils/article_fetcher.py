import requests
from bs4 import BeautifulSoup
import os


def fetch_article_content(url):
    """Fetch the content of an article from a given URL."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        # Remove script, style elements and comments
        for element in soup(["script", "style"]):
            element.decompose()

        # Extract article title
        title = soup.title.string if soup.title else "Unknown Title"

        # Try to extract the author's name if available
        author = None
        author_elements = soup.select(
            '.author, .byline, [rel="author"], [name="author"]'
        )
        if author_elements:
            author = author_elements[0].get_text().strip()

        # Try to extract the publication date if available
        date = None
        date_elements = soup.select(
            'time, [datetime], .date, .published, [property="article:published_time"]'
        )
        if date_elements:
            date = date_elements[0].get_text().strip()
            if not date and date_elements[0].has_attr("datetime"):
                date = date_elements[0]["datetime"]

        # Try to find article content - this is a simplified approach
        # In real-world scenario, you'd need more sophisticated content extraction
        article_text = ""

        # Look for common article containers
        article_containers = soup.select("article, .article, .content, .post, main")
        if article_containers:
            # Use the first article container found
            content_container = article_containers[0]
            # Get all paragraphs from the article container
            paragraphs = content_container.find_all("p")
            article_text = " ".join([p.get_text().strip() for p in paragraphs])
        else:
            # Fallback: get all paragraphs from the body
            paragraphs = soup.find_all("p")
            article_text = " ".join([p.get_text().strip() for p in paragraphs])

        return {
            "title": title.strip(),
            "content": article_text,
            "url": url,
            "author": author,
            "date": date,
        }
    except Exception as e:
        print(f"Error fetching article: {e}")
        return None


def read_article_from_file(file_path):
    """Read article content from a local file when web scraping fails."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        # Try to parse title from first line or use filename
        title = os.path.basename(file_path)
        lines = content.split("\n")
        if lines and lines[0].strip():
            title = lines[0].strip()
            content = "\n".join(lines[1:])

        return {
            "title": title,
            "content": content,
            "url": f"local://{file_path}",
            "author": None,
            "date": None,
        }
    except Exception as e:
        print(f"Error reading local file: {e}")
        return None
