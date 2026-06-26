def evaluate_patient(patient, rules: dict) -> dict:
    """
    Compares a patient against parsed trial rules.
    Returns match result with eligibility, score, and pass/fail reasons.
    """
    reasons_pass = []
    reasons_fail = []

    # Age check
    if rules.get("min_age") and patient.age < rules["min_age"]:
        reasons_fail.append(f"Age {patient.age} below minimum {rules['min_age']}")
    elif rules.get("max_age") and patient.age > rules["max_age"]:
        reasons_fail.append(f"Age {patient.age} above maximum {rules['max_age']}")
    else:
        reasons_pass.append("Age within range")

    # ECOG check
    if rules.get("ecog_max") is not None and patient.ecog_status is not None:
        if patient.ecog_status > rules["ecog_max"]:
            reasons_fail.append(f"ECOG {patient.ecog_status} exceeds max {rules['ecog_max']}")
        else:
            reasons_pass.append("ECOG status acceptable")

    # Lab thresholds
    for lab_name, op, value in rules.get("lab_thresholds", []):
        patient_value = patient.labs.get(lab_name.lower())
        if patient_value is None:
            reasons_fail.append(f"Missing lab data: {lab_name} (cannot confirm)")
            continue
        ok = {
            ">=": patient_value >= value,
            "<=": patient_value <= value,
            ">": patient_value > value,
            "<": patient_value < value,
        }[op]
        if ok:
            reasons_pass.append(f"{lab_name} {op} {value} satisfied")
        else:
            reasons_fail.append(f"{lab_name}={patient_value} fails threshold {op}{value}")

    # Exclusions
    if "prior chemotherapy" in rules.get("exclusions", []) and patient.prior_chemo:
        reasons_fail.append("Excluded: patient has prior chemotherapy")

    hard_fail = any("Age" in r or "Excluded" in r for r in reasons_fail)
    total_checks = len(reasons_pass) + len(reasons_fail)
    score = len(reasons_pass) / total_checks if total_checks else 0.5

    return {
        "eligible": not hard_fail,
        "score": round(score, 2),
        "reasons_pass": reasons_pass,
        "reasons_fail": reasons_fail,
    }
