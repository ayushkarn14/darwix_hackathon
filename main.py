import argparse
import os
from dotenv import load_dotenv
from src.utils.article_fetcher import fetch_article_content, read_article_from_file
from src.analyzer.content_analyzer import analyze_article
from src.utils.report_generator import generate_markdown_report, save_report
from src.analyzer.credibility_scorer import analyze_source_credibility
from src.analyzer.headline_analyzer import analyze_headline
from src.analyzer.comparative_analyzer import (
    find_related_articles,
    compare_article_perspectives,
)
from src.utils.html_generator import generate_html_report, save_html_report

load_dotenv()


def main():
    parser = argparse.ArgumentParser(
        description="Digital Skeptic - A critical thinking AI assistant for news articles"
    )
    parser.add_argument("url", help="URL of the news article to analyze")
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path for the analysis report",
    )
    parser.add_argument(
        "--local",
        "-l",
        help="Path to local file containing article text (used if URL scraping fails)",
    )
    parser.add_argument(
        "--html",
        action="store_true",
        help="Generate an interactive HTML report in addition to Markdown",
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Perform comparative analysis with other articles on the same topic",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print detailed debug information during processing",
    )

    args = parser.parse_args()
    verbose = args.verbose

    # Create analysis_reports directory if it doesn't exist
    reports_dir = "analysis_reports"
    os.makedirs(reports_dir, exist_ok=True)

    # Fetch article content
    print("Fetching article content...")
    article_data = fetch_article_content(args.url)

    local_file = args.local or "local.txt"

    if not article_data:
        print(f"Failed to fetch article from URL: {args.url}")

        # Check if the local file exists and has content
        if os.path.exists(local_file) and os.path.getsize(local_file) > 0:
            print(f"Trying to read from existing file: {local_file}")
            article_data = read_article_from_file(local_file)
        else:
            # Prompt the user to enter the article text
            print("\n" + "=" * 80)
            print(f"Please copy-paste the article text into the file '{local_file}'")
            print(
                "Format: First line should be the article title, followed by the content."
            )
            print("Example:")
            print("  Article Title Here")
            print("  First paragraph of content...")
            print("  Second paragraph of content...")
            print("=" * 80 + "\n")

            # Create empty file if it doesn't exist
            if not os.path.exists(local_file):
                with open(local_file, "w", encoding="utf-8") as f:
                    f.write("Article Title\n\nPaste the article content here...")
                print(f"Empty template created at '{local_file}'. Edit this file now.")

            # Wait for user to edit the file
            input("Press Enter after you've saved the article text to continue...")

            # Read from the local file
            article_data = read_article_from_file(local_file)

    if not article_data:
        print("Failed to obtain article content. Exiting.")
        return

    # Add credibility analysis
    print("Analyzing source credibility...")
    credibility_info = analyze_source_credibility(args.url, article_data)

    # Add headline analysis
    print("Analyzing headline...")
    headline_info = analyze_headline(article_data, verbose=verbose)

    # Comparative analysis (optional)
    comparative_info = None
    if args.compare:
        print("Finding related articles for comparison...")
        related_articles = find_related_articles(article_data)
        if related_articles:
            print(
                f"Found {len(related_articles)} related articles. Comparing perspectives..."
            )
            comparative_info = compare_article_perspectives(
                article_data, related_articles
            )
        else:
            print("No related articles found for comparison.")

    # Main article analysis
    print("Analyzing article content...")
    analysis = analyze_article(article_data, verbose=verbose)

    # Add headline analysis to the overall analysis
    analysis["headline_analysis"] = headline_info.get("headline_analysis")
    analysis["sensationalism_score"] = headline_info.get(
        "sensationalism_score", 0
    )  # Default to 0 if not present
    analysis["clickbait_indicators"] = headline_info.get("clickbait_indicators", [])

    # Only print debug info in verbose mode
    if verbose:
        print(f"Sensationalism score: {analysis['sensationalism_score']}/100")
        print(f"Type of sensationalism_score: {type(analysis['sensationalism_score'])}")

    # Add comparative analysis if available
    if comparative_info:
        analysis["comparative_analysis"] = comparative_info.get("perspective_analysis")
        analysis["related_articles"] = comparative_info.get("related_articles")

    # If comparative analysis wasn't requested via arguments, ask the user if they want it now
    if not args.compare and not args.html:
        user_input = (
            input(
                "Would you like to perform a comparative analysis with other articles on the same topic? (y/n): "
            )
            .strip()
            .lower()
        )
        if user_input == "y" or user_input == "yes":
            print("Finding related articles for comparison...")
            related_articles = find_related_articles(article_data)
            if related_articles:
                print(
                    f"Found {len(related_articles)} related articles. Comparing perspectives..."
                )
                comparative_info = compare_article_perspectives(
                    article_data, related_articles
                )
                analysis["comparative_analysis"] = comparative_info.get(
                    "perspective_analysis"
                )
                analysis["related_articles"] = comparative_info.get("related_articles")
                print("Comparative analysis complete!")
            else:
                print("No related articles found for comparison.")

    # Ask about HTML report if not already requested
    if not args.html:
        user_input = (
            input("Would you like to generate an interactive HTML report? (y/n): ")
            .strip()
            .lower()
        )
        if user_input == "y" or user_input == "yes":
            args.html = True

    # Generate filename from article title
    safe_title = "".join(c if c.isalnum() else "_" for c in article_data["title"][:50])

    # Generate the markdown report
    print("Generating report...")
    report = generate_markdown_report(
        article_data, analysis, credibility_info, verbose=verbose
    )

    # Determine output filename for markdown
    if args.output:
        output_path = args.output
    else:
        output_path = os.path.join(reports_dir, f"{safe_title}.md")

    # Save the markdown report
    save_report(report, output_path)
    print(f"Analysis complete! Report saved to {output_path}")

    # Generate HTML report if requested
    if args.html:
        html_path = os.path.splitext(output_path)[0] + ".html"
        print("Generating interactive HTML report...")
        html_report = generate_html_report(article_data, analysis, credibility_info)
        save_html_report(html_report, html_path)
        print(f"HTML report saved to {html_path}")


if __name__ == "__main__":
    main()
