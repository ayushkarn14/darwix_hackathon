import re
from urllib.parse import urlparse


def analyze_source_credibility(url, article_data):
    """
    Analyze the credibility of the news source.

    Args:
        url: The URL of the article
        article_data: Dictionary containing article information

    Returns:
        dict: A dictionary containing credibility analysis
    """
    domain = urlparse(url).netloc

    # Simple indicators for analysis
    indicators = {
        "has_author": article_data.get("author") is not None,
        "has_date": article_data.get("date") is not None,
        "has_internal_links": "href" in article_data.get("content", ""),
        "has_external_links": "http" in article_data.get("content", ""),
        "content_length": len(article_data.get("content", "")),
    }

    # Look for citation patterns
    citation_patterns = [
        r"according to [A-Z][a-z]+",
        r"cited [A-Z][a-z]+",
        r"reported by",
        r"study (by|from|in)",
        r"research (by|from|in)",
        r"source[s]?:",
    ]

    content = article_data.get("content", "")
    citation_count = sum(
        1 for pattern in citation_patterns if re.search(pattern, content, re.IGNORECASE)
    )

    # Simple credibility factors analysis
    credibility_factors = []

    if indicators["has_author"]:
        credibility_factors.append("Article identifies its author")
    else:
        credibility_factors.append("Article does not identify an author")

    if indicators["has_date"]:
        credibility_factors.append("Article includes a publication date")
    else:
        credibility_factors.append("Article does not include a publication date")

    if citation_count > 3:
        credibility_factors.append("Article cites multiple sources")
    elif citation_count > 0:
        credibility_factors.append("Article includes some citations")
    else:
        credibility_factors.append("Article does not appear to cite sources")

    if indicators["content_length"] < 1000:
        credibility_factors.append(
            "Article is very brief, which may limit comprehensive coverage"
        )

    # Domain credibility could be expanded with a database of known news sources

    return {
        "credibility_factors": credibility_factors,
        "citation_count": citation_count,
        "domain": domain,
    }
