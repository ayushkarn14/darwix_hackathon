import os


def generate_markdown_report(
    article_data, analysis, credibility_info=None, verbose=False
):
    """Generate a markdown report from the analysis."""

    markdown = f"# Critical Analysis Report for: {article_data['title']}\n\n"
    markdown += f"Source: {article_data['url']}\n\n"

    if article_data.get("author"):
        markdown += f"Author: {article_data['author']}\n\n"

    if article_data.get("date"):
        markdown += f"Date: {article_data['date']}\n\n"

    # Add headline analysis section if available
    if analysis.get("headline_analysis"):
        markdown += "## Headline Analysis\n"
        markdown += analysis.get("headline_analysis") + "\n\n"

        # Debug information - only print in verbose mode
        if verbose:
            print(
                f"Sensationalism score in report generator: {analysis.get('sensationalism_score')}"
            )
            print(
                f"Type of sensationalism score: {type(analysis.get('sensationalism_score'))}"
            )

        # Add sensationalism score if available
        if "sensationalism_score" in analysis:
            # Make sure sensationalism_score is an integer
            score = analysis.get("sensationalism_score", 0)
            if not isinstance(score, (int, float)):
                try:
                    score = int(score)
                except (ValueError, TypeError):
                    score = 0
            markdown += f"**Sensationalism Score**: {score}/100\n\n"

        # Add clickbait indicators if available
        if analysis.get("clickbait_indicators"):
            markdown += "**Clickbait Indicators**:\n"
            for indicator in analysis.get("clickbait_indicators", []):
                markdown += f"* {indicator}\n"
            markdown += "\n"

    markdown += "## Core Claims\n"
    if isinstance(analysis.get("core_claims"), list):
        for claim in analysis.get("core_claims", []):
            markdown += f"* {claim}\n"
    else:
        markdown += analysis.get("core_claims", "No core claims identified.")

    markdown += "\n## Language & Tone Analysis\n"
    # Handle language_tone whether it's a string or list
    lang_tone = analysis.get("language_tone", "No language analysis available.")
    if isinstance(lang_tone, list):
        markdown += "\n".join(lang_tone)
    else:
        markdown += lang_tone

    markdown += "\n\n## Potential Red Flags\n"
    if isinstance(analysis.get("red_flags"), list):
        for flag in analysis.get("red_flags", []):
            markdown += f"* {flag}\n"
    else:
        markdown += analysis.get("red_flags", "No red flags identified.")

    markdown += "\n## Verification Questions\n"
    if isinstance(analysis.get("verification_questions"), list):
        for i, question in enumerate(analysis.get("verification_questions", []), 1):
            markdown += f"{i}. {question}\n"
    else:
        markdown += analysis.get(
            "verification_questions", "No verification questions generated."
        )

    # Add Key Entities section
    markdown += "\n## Key Entities to Investigate\n"
    if isinstance(analysis.get("key_entities"), list):
        for entity in analysis.get("key_entities", []):
            markdown += f"* {entity}\n"
    else:
        markdown += analysis.get("key_entities", "No key entities identified.")

    # Add Counter-Argument section
    markdown += "\n## Counter-Argument Perspective\n"
    counter_arg = analysis.get("counter_argument")
    if counter_arg:
        if isinstance(counter_arg, list):
            markdown += "\n".join(counter_arg)
        else:
            markdown += counter_arg
    else:
        markdown += "No counter-argument perspective generated."

    # Add comparative analysis section if available
    if analysis.get("comparative_analysis"):
        markdown += "\n## Comparative Analysis\n"
        markdown += analysis.get("comparative_analysis") + "\n\n"

        if analysis.get("related_articles"):
            markdown += "### Related Articles Analyzed\n"
            for i, article in enumerate(analysis.get("related_articles", []), 1):
                markdown += f"{i}. [{article.get('title')}]({article.get('url')}) - {article.get('source')}\n"
            markdown += "\n"

    # Add credibility section if available
    if credibility_info:
        markdown += "\n## Source Credibility Factors\n"
        for factor in credibility_info.get("credibility_factors", []):
            markdown += f"* {factor}\n"

    return markdown


def save_report(report, output_path="analysis_report.md"):
    """Save the analysis report to a file."""
    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Report saved to {output_path}")
