import re
import json
import os


def parse_eligibility(text: str) -> dict:
    """
    Extracts structured rules from free-text eligibility criteria
    using regex patterns. Fast and transparent, handles common cases.
    """
    rules = {
        "min_age": None,
        "max_age": None,
        "ecog_max": None,
        "lab_thresholds": [],  # list of (lab_name, operator, value)
        "exclusions": [],
    }

    if not text:
        return rules

    # Split into inclusion vs exclusion sections
    sections = re.split(r"Exclusion Criteria:?", text, flags=re.IGNORECASE)
    inclusion_text = sections[0]
    exclusion_text = sections[1] if len(sections) > 1 else ""

    # Age range: "Age 18-75" or "18 Years to 75 Years"
    age_match = re.search(r"(\d{1,3})\s*(?:-|to)\s*(\d{1,3})", inclusion_text)
    if age_match:
        rules["min_age"] = int(age_match.group(1))
        rules["max_age"] = int(age_match.group(2))

    # ECOG status: "ECOG performance status 0-1"
    ecog_match = re.search(r"ECOG.*?(\d)\s*-\s*(\d)", inclusion_text, re.IGNORECASE)
    if ecog_match:
        rules["ecog_max"] = int(ecog_match.group(2))

    # Lab thresholds: "ANC >= 1500" or "Creatinine > 1.5"
    lab_pattern = re.findall(r"([A-Za-z\s]+?)\s*(>=|<=|>|<)\s*([\d.]+)", text)
    for lab_name, op, value in lab_pattern:
        rules["lab_thresholds"].append((lab_name.strip(), op, float(value)))

    # Exclusion keywords (prior treatment, pregnancy, etc.)
    exclusion_keywords = ["prior chemotherapy", "pregnant", "active infection", "renal failure"]
    for kw in exclusion_keywords:
        if kw.lower() in exclusion_text.lower():
            rules["exclusions"].append(kw)

    return rules


def parse_eligibility_llm(text: str) -> dict:
    """
    Uses an LLM (Anthropic API) to extract structured eligibility rules as JSON
    when regex parsing isn't confident enough (e.g. found 0 rules on messy text).

    Requires ANTHROPIC_API_KEY environment variable to be set.
    """
    try:
        import anthropic
    except ImportError:
        raise RuntimeError("Install the anthropic package: pip install anthropic")

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    prompt = f"""Extract structured eligibility rules from this clinical trial text.
Return ONLY valid JSON, no preamble, no markdown fences, with keys:
min_age, max_age, ecog_max, lab_thresholds (list of [name, operator, value]), exclusions (list of strings).

Text:
{text}
"""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.content[0].text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


def parse_eligibility_hybrid(text: str) -> dict:
    """
    Tries regex first; falls back to LLM parsing if regex found nothing useful.
    """
    rules = parse_eligibility(text)
    found_anything = any([
        rules["min_age"], rules["max_age"], rules["ecog_max"],
        rules["lab_thresholds"], rules["exclusions"]
    ])
    if not found_anything and os.environ.get("ANTHROPIC_API_KEY"):
        try:
            return parse_eligibility_llm(text)
        except Exception:
            return rules
    return rules


if __name__ == "__main__":
    sample = """
    Inclusion Criteria:
    - Age 18-75
    - ECOG performance status 0-1
    - ANC >= 1500/mcL
    Exclusion Criteria:
    - Prior chemotherapy within 4 weeks
    - Creatinine > 1.5 mg/dL
    """
    print(parse_eligibility(sample))
