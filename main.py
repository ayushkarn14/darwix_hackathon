import argparse
import os
from dotenv import load_dotenv
from src.utils.article_fetcher import fetch_article_content, read_article_from_file
from src.analyzer.content_analyzer import analyze_article
from src.utils.report_generator import generate_markdown_report, save_report
from src.analyzer.credibility_scorer import analyze_source_credibility

# Load environment variables from .env file
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

    args = parser.parse_args()

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
    credibility_info = analyze_source_credibility(args.url, article_data)

    # Analyze the article
    print("Analyzing article...")
    analysis = analyze_article(article_data)

    # Generate the report
    print("Generating report...")
    report = generate_markdown_report(article_data, analysis, credibility_info)

    # Determine output filename
    if args.output:
        # If user specified an output path, use it directly
        output_path = args.output
    else:
        # Generate a filename based on the article title
        safe_title = "".join(
            c if c.isalnum() else "_" for c in article_data["title"][:50]
        )
        output_path = os.path.join(reports_dir, f"{safe_title}.md")

    # Save the report
    save_report(report, output_path)

    print(f"Analysis complete! Report saved to {output_path}")


if __name__ == "__main__":
    main()
