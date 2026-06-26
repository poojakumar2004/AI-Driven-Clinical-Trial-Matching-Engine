import requests


def fetch_trials(condition: str, max_results: int = 20):
    """
    Pulls trials from ClinicalTrials.gov API v2 for a given condition.
    Returns list of trial dicts with id, title, eligibility text, etc.
    """
    url = "https://clinicaltrials.gov/api/v2/studies"
    params = {
        "query.cond": condition,
        "pageSize": max_results,
        "fields": "NCTId,BriefTitle,EligibilityCriteria,OverallStatus,Condition,MinimumAge,MaximumAge,Sex"
    }
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    trials = []
    for study in data.get("studies", []):
        protocol = study.get("protocolSection", {})
        identification = protocol.get("identificationModule", {})
        eligibility = protocol.get("eligibilityModule", {})

        trials.append({
            "nct_id": identification.get("nctId"),
            "title": identification.get("briefTitle"),
            "status": protocol.get("statusModule", {}).get("overallStatus"),
            "eligibility_text": eligibility.get("eligibilityCriteria", ""),
            "min_age": eligibility.get("minimumAge", "N/A"),
            "max_age": eligibility.get("maximumAge", "N/A"),
            "sex": eligibility.get("sex", "ALL"),
        })
    return trials


if __name__ == "__main__":
    trials = fetch_trials("breast cancer", max_results=5)
    for t in trials:
        print(t["nct_id"], "-", t["title"])
