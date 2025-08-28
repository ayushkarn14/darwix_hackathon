# Digital Skeptic

Digital Skeptic is an AI-powered tool that helps users critically analyze news articles by highlighting claims, analyzing language tone, identifying potential red flags, and suggesting verification questions. It serves as a critical thinking partner to help readers navigate our complex information landscape.

## Problem Statement

In an age of information overload, we are constantly exposed to a firehose of information online. The mundane yet essential task of vetting every article for bias, spin, or logical fallacies is mentally exhausting. Digital Skeptic automates the initial analysis, freeing up our mental energy to make informed judgments.

## Features

- Fetches article content from URLs or local text files
- Analyzes the main claims made in the article
- Evaluates the language tone and style
- Identifies potential signs of bias or poor reporting
- Suggests verification questions for readers
- **Headline Analysis**: Evaluates headlines for sensationalism and clickbait tactics with a numeric score
- **Entity Recognition**: Identifies key people, organizations, and locations mentioned in the article with suggestions for what to investigate about them
- **Counter-Argument Simulation**: Provides a summary of the article from a hypothetical opposing viewpoint to highlight potential biases
- **Comparative Analysis**: Finds and compares related articles on the same topic to identify differences in coverage
- **Interactive HTML Reports**: Generates interactive HTML reports with collapsible sections and visual elements
- **Source Credibility Assessment**: Evaluates the credibility of the article source based on various factors
- Robust error handling with multiple model fallbacks
- Exponential backoff for API rate limits

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set your Google API key as an environment variable or in a .env file:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

## Usage

### Analyzing an article from a URL:

```
python main.py https://example.com/news-article --output report.md
```

### Using a local file when web scraping is blocked:

```
python main.py https://example.com/news-article --local ./article_text.txt
```

### Generating an interactive HTML report:

```
python main.py https://example.com/news-article --html
```

### Performing comparative analysis with other articles:

```
python main.py https://example.com/news-article --compare
```

### Sample usage with detailed debugging:

```
python main.py https://www.indiatoday.in/elections/assembly/story/pm-narendra-modi-mother-abused-rahul-gandhi-bihar-rally-bjp-apology-2778056-2025-08-28 --html --compare --verbose
```

### Command-line options:

- `url`: The URL of the article to analyze (required)
- `--output`, `-o`: Output file path for the analysis report (default: analysis_report.md)
- `--local`, `-l`: Path to a local file containing article text (used if URL scraping fails)
- `--html`: Generate an interactive HTML report in addition to Markdown
- `--compare`: Perform comparative analysis with other articles on the same topic
- `--verbose`, `-v`: Print detailed debug information during processing

## Architecture

The project follows a modular architecture with the following components:

- `main.py`: Entry point that coordinates the workflow
- `src/utils/article_fetcher.py`: Handles fetching article content from URLs or files
- `src/analyzer/content_analyzer.py`: Uses LLM to analyze article content
- `src/analyzer/headline_analyzer.py`: Analyzes headlines for sensationalism and clickbait
- `src/analyzer/comparative_analyzer.py`: Finds and compares related articles
- `src/analyzer/credibility_scorer.py`: Evaluates source credibility
- `src/utils/text_processor.py`: Helper functions for text processing
- `src/utils/report_generator.py`: Generates the markdown report
- `src/utils/html_generator.py`: Creates interactive HTML reports

## Web Scraping Approach

This tool uses the `requests` library to fetch article content and `BeautifulSoup` for HTML parsing. It attempts to identify the main article content by looking for common article containers and paragraph elements. For websites that block scraping, you can save the article text manually to a file and use the `--local` option.

## Sample Output

The analysis report includes the following sections:
- Headline Analysis: Evaluation of the headline's sensationalism and clickbait tactics
- Core Claims: A bulleted list of 3-5 main factual claims the article makes
- Language & Tone Analysis: Classification and analysis of the article's language
- Potential Red Flags: Signs of bias or poor reporting practices
- Verification Questions: Specific questions readers should ask to verify content
- Key Entities to Investigate: Important people, organizations, and locations mentioned
- Counter-Argument Perspective: Summary from an opposing viewpoint
- Source Credibility Factors: Assessment of the article source's credibility
- Comparative Analysis (optional): Comparison with other articles on the same topic

## Interactive HTML Reports

The HTML reports include the following features:
- Responsive, mobile-friendly design
- Collapsible sections for better organization
- Visual indicators for red flags and sensationalism score
- Interactive entity exploration
- Toggle for counter-argument visibility
- Bootstrap styling for a clean, modern look
