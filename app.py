import streamlit as st
from trial_fetcher import fetch_trials
from criteria_parser import parse_eligibility
from patient_schema import Patient
from matcher import evaluate_patient
from explainer import explain_match

st.title("AI Clinical Trial Matcher")
st.caption("Matches a patient profile against live trials from ClinicalTrials.gov")

st.sidebar.header("Patient Profile")
age = st.sidebar.number_input("Age", 1, 100, 55)
sex = st.sidebar.selectbox("Sex", ["MALE", "FEMALE"])
diagnosis = st.sidebar.text_input("Diagnosis / Condition", "breast cancer")
ecog = st.sidebar.slider("ECOG Status", 0, 5, 1)
prior_chemo = st.sidebar.checkbox("Prior Chemotherapy")
creatinine = st.sidebar.number_input("Creatinine (mg/dL)", 0.0, 5.0, 1.0)
anc = st.sidebar.number_input("ANC (/mcL)", 0, 10000, 2000)
max_results = st.sidebar.slider("Number of trials to fetch", 5, 30, 10)

if st.sidebar.button("Find Matching Trials"):
    patient = Patient(
        age=age, sex=sex, diagnosis=diagnosis,
        ecog_status=ecog, prior_chemo=prior_chemo,
        labs={"creatinine": creatinine, "anc": anc}
    )

    with st.spinner("Fetching live trials from ClinicalTrials.gov..."):
        try:
            trials = fetch_trials(diagnosis, max_results=max_results)
        except Exception as e:
            st.error(f"Failed to fetch trials: {e}")
            trials = []

    st.write(f"Found {len(trials)} trials for '{diagnosis}'")

    results = []
    for trial in trials:
        rules = parse_eligibility(trial["eligibility_text"])
        result = evaluate_patient(patient, rules)
        results.append((trial, result))

    results.sort(key=lambda x: x[1]["score"], reverse=True)

    for trial, result in results:
        icon = "✅" if result["eligible"] else "❌"
        with st.expander(f"{icon} {trial['title']}"):
            st.markdown(explain_match(trial, result))
            st.caption(f"Status: {trial['status']} | NCT ID: {trial['nct_id']}")
else:
    st.info("Fill in the patient profile on the left and click 'Find Matching Trials'.")
