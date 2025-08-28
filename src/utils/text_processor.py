def extract_section(text, section_name):
    """Helper function to extract sections from a raw text response."""
    if not text:
        return []

    sections = text.split("###")
    for section in sections:
        if section_name.lower() in section.lower():
            lines = [line.strip() for line in section.split("\n") if line.strip()]
            if len(lines) > 1:  # Skip the section title
                if section_name in [
                    "Core Claims",
                    "Potential Red Flags",
                    "Key Entities Analysis",
                ]:
                    return [
                        item[2:].strip() for item in lines[1:] if item.startswith("* ")
                    ]
                elif section_name == "Verification Questions":
                    return [
                        item[item.find(".") + 1 :].strip() if "." in item else item
                        for item in lines[1:]
                    ]
                else:
                    return "\n".join(lines[1:])
    return []
