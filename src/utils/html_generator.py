import os
import json
import re


def convert_markdown_to_html(text):
    """Convert basic Markdown syntax to HTML"""
    if not text:
        return ""

    # Convert bold (**text**) to <strong>text</strong>
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)

    # Convert numbered lists (1. item) to ordered lists
    # First, detect if we have a numbered list
    if re.search(r"^\d+\.\s", text, re.MULTILINE):
        # Split by lines
        lines = text.split("\n")
        list_started = False
        result = []

        for line in lines:
            # Check if this is a list item (starts with number and period)
            list_item = re.match(r"^\s*(\d+)\.\s+(.*)", line)

            if list_item:
                if not list_started:
                    # Start a new list if we're not already in one
                    result.append("<ol>")
                    list_started = True

                # Add the list item
                result.append(f"<li>{list_item.group(2)}</li>")
            else:
                # If we're ending a list, close it
                if list_started:
                    result.append("</ol>")
                    list_started = False

                # Add the regular line if it's not empty
                if line.strip():
                    result.append(f"<p>{line}</p>")

        # If we ended while still in a list, close it
        if list_started:
            result.append("</ol>")

        return "\n".join(result)

    # Convert bullet lists (* item) to unordered lists
    if re.search(r"^\s*\*\s", text, re.MULTILINE):
        lines = text.split("\n")
        list_started = False
        result = []

        for line in lines:
            # Check if this is a list item (starts with *)
            list_item = re.match(r"^\s*\*\s+(.*)", line)

            if list_item:
                if not list_started:
                    # Start a new list if we're not already in one
                    result.append("<ul>")
                    list_started = True

                # Add the list item
                result.append(f"<li>{list_item.group(1)}</li>")
            else:
                # If we're ending a list, close it
                if list_started:
                    result.append("</ul>")
                    list_started = False

                # Add the regular line if it's not empty
                if line.strip():
                    result.append(f"<p>{line}</p>")

        # If we ended while still in a list, close it
        if list_started:
            result.append("</ul>")

        return "\n".join(result)

    # Split paragraphs and wrap them in <p> tags
    paragraphs = text.split("\n\n")
    formatted = []

    for para in paragraphs:
        if para.strip():
            formatted.append(f"<p>{para}</p>")

    return "\n".join(formatted)


def generate_html_report(article_data, analysis, credibility_info=None):
    """Generate an interactive HTML version of the analysis report."""

    # Initialize entities_json as an empty array string at the beginning of the function
    entities_json = "[]"

    # Base HTML structure with Bootstrap for styling
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analysis: {article_data['title']}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .highlight {{
            background-color: #ffffd0;
            padding: 2px;
        }}
        .entity {{
            cursor: pointer;
            text-decoration: underline;
            color: #0d6efd;
        }}
        .collapse-toggle {{
            cursor: pointer;
        }}
        .red-flag {{
            background-color: #ffebee;
            border-left: 3px solid #f44336;
            padding-left: 15px;
            margin: 5px 0;
        }}
        .counter-argument {{
            background-color: #e8f5e9;
            border-left: 3px solid #4caf50;
            padding: 15px;
            margin-top: 10px;
        }}
    </style>
</head>
<body>
    <div class="container mt-4 mb-5">
        <div class="card shadow">
            <div class="card-header bg-primary text-white">
                <h2>{article_data['title']}</h2>
                <p class="mb-0">Source: <a href="{article_data['url']}" class="text-white" target="_blank">{article_data['url']}</a></p>
            </div>
            <div class="card-body">
"""

    # Add article metadata
    if article_data.get("author") or article_data.get("date"):
        html += '<div class="row mb-4">'
        if article_data.get("author"):
            html += f'<div class="col"><strong>Author:</strong> {article_data["author"]}</div>'
        if article_data.get("date"):
            html += (
                f'<div class="col"><strong>Date:</strong> {article_data["date"]}</div>'
            )
        html += "</div>"

    # Add headline analysis if available
    if analysis.get("headline_analysis"):
        html += f"""
                <div class="card mb-4">
                    <div class="card-header bg-light">
                        <h3 class="mb-0">Headline Analysis</h3>
                    </div>
                    <div class="card-body">
                        {convert_markdown_to_html(analysis.get("headline_analysis"))}
        """

        # Add sensationalism score if available
        if "sensationalism_score" in analysis:
            score = analysis.get("sensationalism_score", 0)
            html += f"""
                        <div class="d-flex align-items-center mb-3">
                            <strong class="me-2">Sensationalism Score: </strong>
                            <div class="progress flex-grow-1" style="height: 20px;">
                                <div class="progress-bar bg-warning" role="progressbar" 
                                     style="width: {score}%;" 
                                     aria-valuenow="{score}" 
                                     aria-valuemin="0" aria-valuemax="100">
                                    {score}/100
                                </div>
                            </div>
                        </div>
            """

        # Add clickbait indicators if available
        if analysis.get("clickbait_indicators"):
            html += """
                        <div class="mt-3">
                            <strong>Clickbait Indicators:</strong>
                            <ul class="list-group mt-2">
            """
            for indicator in analysis.get("clickbait_indicators", []):
                html += f'<li class="list-group-item">{indicator}</li>'
            html += """
                            </ul>
                        </div>
            """

        html += """
                    </div>
                </div>
        """

    # Add Core Claims section
    html += """
                <div class="card mb-4">
                    <div class="card-header bg-light">
                        <h3 class="mb-0">Core Claims</h3>
                    </div>
                    <div class="card-body">
                        <ul class="list-group list-group-flush">
    """

    if isinstance(analysis.get("core_claims"), list):
        for claim in analysis.get("core_claims", []):
            html += f'<li class="list-group-item">{claim}</li>'
    else:
        content = analysis.get("core_claims", "No core claims identified.")
        # Add check to ensure content is a string
        if isinstance(content, str) and content.startswith(
            "- "
        ):  # Check if content has bullet points
            html += "<ul>"
            for line in content.split("\n"):
                if line.startswith("- "):
                    html += f"<li>{line[2:]}</li>"
            html += "</ul>"
        else:
            html += f'<li class="list-group-item">{content}</li>'

    html += """
                        </ul>
                    </div>
                </div>
    """

    # Add Language & Tone Analysis section
    html += """
                <div class="card mb-4">
                    <div class="card-header bg-light">
                        <h3 class="mb-0">Language & Tone Analysis</h3>
                    </div>
                    <div class="card-body">
    """

    lang_tone = analysis.get("language_tone", "No language analysis available.")
    if isinstance(lang_tone, list):
        html += f'<p>{" ".join(lang_tone)}</p>'
    else:
        html += convert_markdown_to_html(lang_tone)

    html += """
                    </div>
                </div>
    """

    # Add Potential Red Flags section
    html += """
                <div class="card mb-4">
                    <div class="card-header bg-light">
                        <h3 class="mb-0">Potential Red Flags</h3>
                    </div>
                    <div class="card-body">
    """

    if isinstance(analysis.get("red_flags"), list):
        html += "<ul>"
        for flag in analysis.get("red_flags", []):
            html += f'<li class="red-flag mb-2">{flag}</li>'
        html += "</ul>"
    else:
        content = analysis.get("red_flags", "No red flags identified.")
        # Add check to ensure content is a string
        if isinstance(content, str) and content.startswith(
            "- "
        ):  # Check if content has bullet points
            html += "<ul>"
            for line in content.split("\n"):
                if line.startswith("- "):
                    html += f'<li class="red-flag mb-2">{line[2:]}</li>'
            html += "</ul>"
        else:
            html += convert_markdown_to_html(content)

    html += """
                    </div>
                </div>
    """

    # Add interactive sections with JavaScript
    html += """
                <div class="card mb-4">
                    <div class="card-header bg-light">
                        <h3 class="mb-0">Key Entities to Investigate</h3>
                    </div>
                    <div class="card-body">
                        <div class="row">
    """

    if isinstance(analysis.get("key_entities"), list) and analysis.get("key_entities"):
        entities_json = json.dumps(analysis.get("key_entities", []))
        html += f"""
            <div class="col-md-8">
                <ul class="list-group" id="entity-list">
        """

        for i, entity in enumerate(analysis.get("key_entities", [])):
            html += (
                f'<li class="list-group-item entity" data-entity-id="{i}">{entity}</li>'
            )

        html += """
                </ul>
            </div>
            <div class="col-md-4">
                <div class="card" id="entity-info-card">
                    <div class="card-header">Entity Information</div>
                    <div class="card-body" id="entity-info">
                        <p class="text-muted">Click on an entity to see research suggestions</p>
                    </div>
                </div>
            </div>
        """
    else:
        content = analysis.get("key_entities", "No key entities identified.")
        # Add check to ensure content is a string
        if isinstance(content, str) and content.startswith(
            "- "
        ):  # Check if content has bullet points
            html += "<ul>"
            for line in content.split("\n"):
                if line.startswith("- "):
                    html += f"<li>{line[2:]}</li>"
            html += "</ul>"
        else:
            html += convert_markdown_to_html(content)

    html += """
                        </div>
                    </div>
                </div>
    """

    # Add Verification Questions section
    html += """
                <div class="card mb-4">
                    <div class="card-header bg-light">
                        <h3 class="mb-0">Verification Questions</h3>
                    </div>
                    <div class="card-body">
                        <div class="accordion" id="verificationQuestions">
    """

    if isinstance(analysis.get("verification_questions"), list):
        for i, question in enumerate(analysis.get("verification_questions", []), 1):
            html += f"""
                <div class="accordion-item">
                    <h2 class="accordion-header" id="question-heading-{i}">
                        <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#question-collapse-{i}" aria-expanded="false" aria-controls="question-collapse-{i}">
                            {i}. {question}
                        </button>
                    </h2>
                    <div id="question-collapse-{i}" class="accordion-collapse collapse" aria-labelledby="question-heading-{i}" data-bs-parent="#verificationQuestions">
                        <div class="accordion-body">
                            <p>To answer this question, you might want to:</p>
                            <ul>
                                <li>Check reliable sources like academic papers or official statistics</li>
                                <li>Look for primary sources mentioned in the article</li>
                                <li>Search for alternative perspectives from other experts</li>
                            </ul>
                        </div>
                    </div>
                </div>
            """
    else:
        content = analysis.get(
            "verification_questions", "No verification questions generated."
        )
        # Fixed: Check if content is a string before trying to use startswith()
        if isinstance(content, str) and content.startswith(
            "- "
        ):  # Check if content has bullet points
            html += "<ol>"
            for line in content.split("\n"):
                if line.startswith("- "):
                    html += f"<li>{line[2:]}</li>"
            html += "</ol>"
        else:
            html += convert_markdown_to_html(content)

    html += """
                        </div>
                    </div>
                </div>
    """

    # Add Counter-Argument section
    html += """
                <div class="card mb-4">
                    <div class="card-header bg-light">
                        <div class="d-flex justify-content-between align-items-center">
                            <h3 class="mb-0">Counter-Argument Perspective</h3>
                            <button class="btn btn-sm btn-outline-primary" id="toggle-counter">Show/Hide</button>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="counter-argument" id="counter-argument-content">
    """

    counter_arg = analysis.get("counter_argument")
    if counter_arg:
        if isinstance(counter_arg, list):
            html += f'<p>{" ".join(counter_arg)}</p>'
        else:
            html += convert_markdown_to_html(counter_arg)
    else:
        html += "<p>No counter-argument perspective generated.</p>"

    html += """
                        </div>
                    </div>
                </div>
    """

    # Add credibility section if available
    if credibility_info:
        html += """
                <div class="card mb-4">
                    <div class="card-header bg-light">
                        <h3 class="mb-0">Source Credibility Factors</h3>
                    </div>
                    <div class="card-body">
                        <ul class="list-group list-group-flush">
        """

        for factor in credibility_info.get("credibility_factors", []):
            html += f'<li class="list-group-item">{factor}</li>'

        html += """
                        </ul>
                    </div>
                </div>
        """

    # Add JavaScript for interactivity
    html += f"""
            </div>
            <div class="card-footer text-center text-muted">
                Generated by Digital Skeptic
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Entity click handler
        document.querySelectorAll('.entity').forEach(entity => {{
            entity.addEventListener('click', function() {{
                const entityId = this.getAttribute('data-entity-id');
                const entities = {entities_json};
                const entityInfo = document.getElementById('entity-info');
                
                // Add active class
                document.querySelectorAll('.entity').forEach(e => e.classList.remove('active'));
                this.classList.add('active');
                
                // Extract entity name (usually before the first dash or colon)
                const entityText = entities[entityId];
                const entityName = entityText.split(/[-:]/)[0].trim();
                
                // Generate research suggestions
                entityInfo.innerHTML = `
                    <h5>${{entityName}}</h5>
                    <p>${{entityText}}</p>
                    <h6>Research Suggestions:</h6>
                    <ul>
                        <li>Search for "${{entityName}}" in reliable news sources</li>
                        <li>Look for "${{entityName}}" background and affiliations</li>
                        <li>Check for potential conflicts of interest</li>
                    </ul>
                `;
            }});
        }});
        
        // Counter argument toggle
        document.getElementById('toggle-counter').addEventListener('click', function() {{
            const counterContent = document.getElementById('counter-argument-content');
            if (counterContent.style.display === 'none') {{
                counterContent.style.display = 'block';
                this.textContent = 'Hide';
            }} else {{
                counterContent.style.display = 'none';
                this.textContent = 'Show';
            }}
        }});
    </script>
</body>
</html>
    """

    return html


def save_html_report(html, output_path="analysis_report.html"):
    """Save the HTML report to a file."""
    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML report saved to {output_path}")
