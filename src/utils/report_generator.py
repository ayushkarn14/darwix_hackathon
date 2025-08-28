import os


def generate_markdown_report(article_data, analysis, credibility_info=None):
    """Generate a markdown report from the analysis."""

    markdown = f"# Critical Analysis Report for: {article_data['title']}\n\n"
    markdown += f"Source: {article_data['url']}\n\n"

    if article_data.get("author"):
        markdown += f"Author: {article_data['author']}\n\n"

    if article_data.get("date"):
        markdown += f"Date: {article_data['date']}\n\n"

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
