import re
from langchain_google_genai import ChatGoogleGenerativeAI
import os


def analyze_headline(article_data, verbose=False):
    """Analyze the headline for sensationalism, clickbait, and framing."""

    title = article_data.get("title", "")
    if not title:
        return {
            "headline_analysis": "No headline available for analysis",
            "sensationalism_score": 0,
            "clickbait_indicators": [],
        }

    # Simple rule-based analysis
    clickbait_phrases = [
        "you won't believe",
        "shocking",
        "mind blowing",
        "amazing",
        "jaw-dropping",
        "unbelievable",
        "incredible",
        "insane",
        "stunning",
        "never seen before",
        "secret",
        "hack",
        "trick",
        "they don't want you to know",
        "this one trick",
        "miracle",
        "breakthrough",
        "life changing",
        "game changing",
        "must see",
        "warning",
        "attention",
    ]

    emotional_words = [
        "shocking",
        "explosive",
        "incredible",
        "devastating",
        "terrifying",
        "catastrophic",
        "horrifying",
        "amazing",
        "unbelievable",
        "extraordinary",
        "outrageous",
        "sensational",
        "scandalous",
        "bombshell",
        "staggering",
        "dramatic",
        "alarming",
        "jaw-dropping",
    ]

    question_pattern = (
        r"\?$|^(who|what|when|where|why|how|is|are|can|will|should|would|could|do|does)"
    )
    number_pattern = r"^\d+|^\d+ "  # Headlines starting with numbers
    superlative_pattern = (
        r"(best|worst|most|biggest|greatest|easiest|deadliest|highest|lowest)"
    )

    # Calculate simple scores
    clickbait_count = sum(
        1 for phrase in clickbait_phrases if phrase.lower() in title.lower()
    )
    emotional_count = sum(
        1 for word in emotional_words if word.lower() in title.lower().split()
    )
    has_question = bool(re.search(question_pattern, title.lower(), re.IGNORECASE))
    has_number = bool(re.search(number_pattern, title))
    has_superlative = bool(re.search(superlative_pattern, title.lower()))

    # Create a simple score (0-100)
    base_score = 0
    if clickbait_count > 0:
        base_score += 20 * min(clickbait_count, 3)
    if emotional_count > 0:
        base_score += 15 * min(emotional_count, 3)
    if has_question:
        base_score += 10
    if has_number:
        base_score += 10
    if has_superlative:
        base_score += 15

    # Add a small base score for any headline from news sources
    if "news" in title.lower() or any(
        word in title.lower() for word in ["breaking", "report", "exclusive"]
    ):
        base_score += 5

    # Check title length - longer titles tend to be more sensationalist
    if len(title) > 70:
        base_score += 5

    # Check for all caps segments which can indicate sensationalism
    if any(word.isupper() and len(word) > 2 for word in title.split()):
        base_score += 5

    # Add some score for "serial killer" type content - clearly sensational
    if any(
        term in title.lower()
        for term in ["serial killer", "murder", "kill", "dead", "death"]
    ):
        base_score += 25

    # Add score for specific clickbaity content that isn't caught by above patterns
    if (
        "mom" in title.lower() and not "moment" in title.lower()
    ):  # "Mom" is often used in clickbait
        base_score += 15

    # Cap at 100
    sensationalism_score = min(base_score, 100)

    # Force to integer type
    sensationalism_score = int(sensationalism_score)

    # Debug information - only print in verbose mode
    if verbose:
        print(f"Title: {title}")
        print(f"Calculated sensationalism score: {sensationalism_score}")
        print(f"Clickbait count: {clickbait_count}, Emotional count: {emotional_count}")
        print(
            f"Has question: {has_question}, Has number: {has_number}, Has superlative: {has_superlative}"
        )

    # Collect detected patterns
    clickbait_indicators = []
    if clickbait_count > 0:
        detected_phrases = [
            phrase for phrase in clickbait_phrases if phrase.lower() in title.lower()
        ]
        clickbait_indicators.append(
            f"Uses clickbait phrases: {', '.join(detected_phrases)}"
        )
    if emotional_count > 0:
        detected_words = [
            word for word in emotional_words if word.lower() in title.lower().split()
        ]
        clickbait_indicators.append(
            f"Uses emotional language: {', '.join(detected_words)}"
        )
    if has_question:
        clickbait_indicators.append(
            "Headline poses a question (often used to create curiosity)"
        )
    if has_number:
        clickbait_indicators.append(
            "Headline starts with a number (common clickbait format)"
        )
    if has_superlative:
        clickbait_indicators.append("Uses superlatives like 'best', 'worst', 'most'")

    # Add indicator for "mom" and "serial killer" content
    if "mom" in title.lower() and not "moment" in title.lower():
        clickbait_indicators.append(
            "Uses 'mom' in headline (common clickbait approach to create relatability)"
        )
    if any(
        term in title.lower()
        for term in ["serial killer", "murder", "kill", "dead", "death"]
    ):
        clickbait_indicators.append(
            "Uses morbid/shocking terminology (e.g., 'serial killer', 'murder') to grab attention"
        )

    # Use LLM for deeper analysis if available
    headline_analysis = ""
    try:
        api_key = os.environ.get("GOOGLE_API_KEY")
        if api_key:
            llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2)
            prompt = f"""
            Analyze this news headline for sensationalism, clickbait tactics, and framing choices:
            
            "{title}"
            
            Please provide:
            1. An objective assessment of whether the headline appears sensationalist or clickbaity
            2. Analysis of specific language choices and framing
            3. How the headline might set reader expectations
            4. Suggestions for a more neutral version of the headline
            
            Keep your analysis concise but insightful.
            """

            result = llm.invoke(prompt)
            headline_analysis = (
                result.content if hasattr(result, "content") else str(result)
            )
        else:
            headline_analysis = "LLM analysis unavailable: API key not configured."
    except Exception as e:
        headline_analysis = f"LLM analysis error: {str(e)}"

    # Final check to ensure sensationalism_score is an integer
    if not isinstance(sensationalism_score, int):
        sensationalism_score = int(sensationalism_score) if sensationalism_score else 0

    return {
        "headline_analysis": headline_analysis,
        "sensationalism_score": sensationalism_score,
        "clickbait_indicators": clickbait_indicators,
    }
