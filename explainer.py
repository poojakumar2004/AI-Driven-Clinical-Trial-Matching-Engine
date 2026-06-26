def explain_match(trial: dict, result: dict) -> str:
    """
    Produces a human-readable explanation of why a patient matched
    or did not match a given trial.
    """
    lines = [f"**{trial['title']}** ({trial['nct_id']}) — Score: {result['score']*100:.0f}%"]
    if result["reasons_pass"]:
        lines.append("✅ " + "; ".join(result["reasons_pass"]))
    if result["reasons_fail"]:
        lines.append("❌ " + "; ".join(result["reasons_fail"]))
    return "\n".join(lines)
