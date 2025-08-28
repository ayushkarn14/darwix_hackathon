import os
import time
import random
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from ..utils.text_processor import extract_section


def analyze_article(article_data, verbose=False):
    """Use LLM to analyze the article content."""

    # Define output schemas
    response_schemas = [
        ResponseSchema(
            name="core_claims",
            description="A bulleted list summarizing the 3-5 main factual claims the article makes.",
        ),
        ResponseSchema(
            name="language_tone",
            description="A brief analysis and classification of the article's language (e.g., neutral, emotional, persuasive, opinion-based).",
        ),
        ResponseSchema(
            name="red_flags",
            description="A bulleted list identifying any detected signs of bias or poor reporting.",
        ),
        ResponseSchema(
            name="verification_questions",
            description="A list of 3-4 insightful, specific questions a reader should ask to independently verify the article's content.",
        ),
        ResponseSchema(
            name="key_entities",
            description="A list of key people, organizations, and locations mentioned in the article, each with a suggestion of what to investigate about them.",
        ),
        ResponseSchema(
            name="counter_argument",
            description="A brief summary of the article from a hypothetical opposing viewpoint to highlight potential biases.",
        ),
    ]

    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()

    template = """
    You are the "Digital Skeptic" AI, a critical thinking assistant. Your job is to analyze news articles 
    and provide a critical analysis without determining what is "true" or "false."
    
    Article Title: {title}
    
    Article Content: {content}
    
    Please provide a critical analysis of this article with the following components:
    
    1. Core Claims: Identify the 3-5 main factual claims the article makes.
    2. Language & Tone Analysis: Analyze the article's language style and tone.
    3. Potential Red Flags: Identify any signs of bias or poor reporting practices.
    4. Verification Questions: Provide 3-4 specific questions readers should ask to verify the content.
    5. Key Entities Analysis: Identify key people, organizations, and locations mentioned in the article and suggest what readers should investigate about each (e.g., "Investigate the author's previous work," "Look into the funding of the institute").
    6. Counter-Argument Simulation: Briefly summarize the article from a hypothetical opposing viewpoint to highlight its potential biases.
    
    {format_instructions}
    """

    prompt = PromptTemplate(
        input_variables=["title", "content"],
        partial_variables={"format_instructions": format_instructions},
        template=template,
    )

    # Initialize the language model with API key
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY environment variable is not set. Please set it in your .env file or environment."
        )

    # Try with different models in case of rate limiting
    models = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.0-flash"]
    result = None

    for model in models:
        try:
            if verbose:
                print(f"Trying with model: {model}")
            else:
                print(f"Analyzing with {model}...")

            llm = ChatGoogleGenerativeAI(model=model, temperature=0.2)

            # Implement retry with exponential backoff
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    formatted_prompt = prompt.format(
                        title=article_data["title"], content=article_data["content"]
                    )
                    result = llm.invoke(formatted_prompt)
                    break  # If successful, break the retry loop
                except Exception as e:
                    if "quota" in str(e).lower() or "429" in str(e):
                        if attempt < max_retries - 1:
                            wait_time = (2**attempt) + random.uniform(0, 1)
                            print(
                                f"Rate limit hit. Retrying in {wait_time:.1f} seconds..."
                            )
                            time.sleep(wait_time)
                        else:
                            print(
                                f"Max retries reached with model {model}. Trying another model if available."
                            )
                            raise
                    else:
                        # Not a rate limit error, re-raise
                        raise

            if result:  # If we got a result, no need to try other models
                break

        except Exception as e:
            print(f"Error with model {model}: {str(e)}")
            # Continue to try the next model
            continue

    # If we have a result, try to parse it
    if result:
        try:
            return output_parser.parse(result.content)
        except Exception as e:
            print(f"Error parsing structured output: {e}")
            # Fall back to manual extraction
            return create_fallback_analysis(
                result.content if hasattr(result, "content") else None
            )
    else:
        # If all models failed, generate a fallback analysis based on simple heuristics
        print("All models failed. Generating fallback analysis...")
        return generate_fallback_analysis(article_data)


def create_fallback_analysis(raw_content):
    """
    Create a structured analysis from raw LLM output when the parser fails.

    Args:
        raw_content: The unparsed text response from the LLM

    Returns:
        dict: A dictionary containing the structured analysis components
    """
    if not raw_content:
        return generate_empty_analysis()

    return {
        "core_claims": extract_section(raw_content, "Core Claims"),
        "language_tone": extract_section(raw_content, "Language & Tone Analysis"),
        "red_flags": extract_section(raw_content, "Potential Red Flags"),
        "verification_questions": extract_section(
            raw_content, "Verification Questions"
        ),
        "key_entities": extract_section(raw_content, "Key Entities Analysis"),
        "counter_argument": extract_section(raw_content, "Counter-Argument Simulation"),
    }


def generate_fallback_analysis(article_data):
    """
    Generate a basic analysis when all LLM calls fail using simple heuristics.

    Args:
        article_data: Dictionary containing article information

    Returns:
        dict: A dictionary containing the fallback analysis components
    """
    title = article_data.get("title", "")
    content = article_data.get("content", "")

    # Extract potential entities (very basic approach)
    entities = []
    if content:
        # Look for capitalized words that might be entities
        words = content.split()
        for i, word in enumerate(words):
            if (
                word[0].isupper()
                and len(word) > 1
                and (i == 0 or words[i - 1].endswith((".", "!", "?", '"', "'")))
            ):
                if word not in entities:
                    entities.append(word)

    # Create basic verification questions
    questions = [
        "What are the primary sources cited in this article?",
        "Is there evidence presented to support the main claims?",
        "What perspectives might be missing from this reporting?",
    ]

    return {
        "core_claims": [f"The article discusses {title}"],
        "language_tone": "Unable to analyze the tone due to technical limitations.",
        "red_flags": ["Analysis unavailable - please read critically"],
        "verification_questions": questions,
        "key_entities": [
            f"{entity} - Consider researching this entity's background"
            for entity in entities[:5]
        ],
        "counter_argument": "Unable to generate a counter-argument due to technical limitations. Consider seeking alternative viewpoints on this topic.",
    }


def generate_empty_analysis():
    """Generate an empty analysis structure when no content is available."""
    return {
        "core_claims": ["No article content available for analysis"],
        "language_tone": "No content to analyze",
        "red_flags": ["No content available for analysis"],
        "verification_questions": [
            "Is the article content actually available?",
            "Is there a technical issue with the content retrieval?",
        ],
        "key_entities": [],
        "counter_argument": "No content to analyze",
    }
