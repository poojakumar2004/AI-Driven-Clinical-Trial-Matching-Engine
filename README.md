# AI-Driven Clinical Trial Matching Engine

Matches a patient profile against live clinical trials pulled from
ClinicalTrials.gov, parses free-text eligibility criteria into structured
rules, scores the match, and explains the result.

## Setup

```bash
pip install -r requirements.txt
```

(Optional, for LLM-based criteria parsing fallback)
```bash
export ANTHROPIC_API_KEY=your_key_here
```

## Run the dashboard

```bash
streamlit run app.py
```

This opens a browser window where you can enter a patient profile
(age, diagnosis, labs, ECOG status, etc.) and see ranked, explained
matches against real, currently-recruiting trials.

## Project Files

- `trial_fetcher.py` — pulls live trial data from the ClinicalTrials.gov API
- `patient_schema.py` — patient data model
- `criteria_parser.py` — regex-based (+ optional LLM fallback) parser that
  converts free-text eligibility criteria into structured rules
- `matcher.py` — scores a patient against a trial's parsed rules
- `explainer.py` — turns match results into human-readable explanations
- `app.py` — Streamlit web dashboard tying it all together

## Quick test of individual modules

```bash
python trial_fetcher.py      # prints 5 sample breast cancer trials
python criteria_parser.py    # parses a sample eligibility text block
```

## Next steps (for a 6-month project scope)

1. Replace structured patient input with NLP extraction from real clinical
   notes (e.g. MIMIC-III/IV, after credentialed access).
2. Fine-tune a ClinicalBERT model on labeled eligibility criteria instead of
   relying purely on regex/LLM calls.
3. Add semantic similarity matching (sentence embeddings) for non-numeric
   criteria (e.g. "no history of autoimmune disease").
4. Validate against a clinician's manual review of 20-30 cases for your
   evaluation/results chapter.
