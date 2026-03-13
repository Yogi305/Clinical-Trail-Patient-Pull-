$brd_1_core = @"
=========================================
CLINICAL TRIAL PROTOCOL SUMMARY: DXT-2026-001
=========================================
Document Version: 1.0 (Final)
Sponsor: Agilisium Life Sciences Research Division 
Date: March 1, 2026
Title: Efficacy of Novel Therapeutics in Older Diabetic Patients (Phase III) 

[1] RATIONALE
The prevalence of unstable Type 2 Diabetes Mellitus in geriatric populations presents a significant clinical challenge. Current standard-of-care treatments often result in adverse interactions with cardiovascular medications, specifically statins. This Phase III clinical trial is designed to evaluate the safety, tolerability, and glycemic efficacy of an investigational novel therapeutic compound (NTC-884) tailored specifically for older demographics.

[2] OBJECTIVES
Primary: To evaluate the efficacy of NTC-884 in stabilizing glycemic variability in older patients with unstable diabetes over a 12-month period.
Secondary: To assess the cardiovascular safety profile of the therapeutic and monitor patient adherence to the protocol.

[3] PATIENT ELIGIBILITY PARAMETERS
Candidates must pass the following screening matrix:

>>> REQUIRED FOR ENROLLMENT (INCLUSIONS) <<<
- Documented explicit Medical Condition of "Diabetes" in EHR.
- Patient Age strictly 60 years or older at the time of initial screening.
- Recent Test Results classified as "Abnormal" reflecting elevated HbA1c or erratic fasting glucose.

>>> DISQUALIFYING CONDITIONS (EXCLUSIONS) <<<
- Actively taking or prescribed "Lipitor" (atorvastatin) as a Medication due to severe drug-drug interactions.
- Known history of severe hepatic impairment or acute liver failure.

[4] METHODOLOGY
This is a randomized, double-blind, placebo-controlled, multi-center trial. Eligible candidates will be matched via the Agilisium AI Patient Matching system and enrolled into a 52-week observation and treatment phase, requiring bi-weekly outpatient monitoring.

[5] APPROVALS
Principal Investigator: Dr. Sarah Jenkins, MD, PhD. 
IRB Status: Approved.
"@

$brd_2_core = @"
MEMORANDUM OF STUDY DESIGN: ORT-2026-002
Date: March 1, 2026
Prepared for: Agilisium Life Sciences Orthopedics Division
Subject: Post-Operative Recovery Rates in Female Arthritis Patients (Phase II)

BACKGROUND
Joint intervention recovery rates heavily vary based on demographic factors and underlying chronic conditions. This trial seeks to monitor the recovery velocity and quality of life improvements in female patients diagnosed with arthritis following planned surgical interventions. 

STUDY GOALS
To establish a baseline recovery timeline for arthritis patients and isolate gender-specific recovery anomalies in standard elective procedures.

SUBJECT SELECTION CRITERIA
Below are the bounds for patient enrollment in the observation trial. Note that there are no automated exclusion criteria required for data mining at this phase. Manual EHR audits will follow.

*Inclusion Bounds:*
Gender: Must be listed as "Female".
Diagnosis: Must carry a formal Medical Condition of "Arthritis".
Age Bracket: The candidate's Age must be between 40 and 70 years old, inclusive.
Encounter Setting: The hospital Admission Type must be strictly "Elective" (planned interventions only).

STUDY DESIGN OVERVIEW
This is a real-world evidence (RWE) observational study. Patients will report subjective pain scores and objective mobility metrics over a 16-week postoperative period.

COMPLIANCE NOTICES
HIPAA and GDPR compliance is governed by the Agilisium AI extraction layer. 

INVESTIGATOR
Dr. Marcus Vance, MD.
Status: IRB Approved.
"@

$brd_3_core = @"
Emergency Protocol Brief: HKT-2026-003
"Emergency Blood Transfusion Efficacy in A-Negative Patients"
Agilisium Acute Care Research Team -- March 1, 2026

------------------------------------------------------
SECTION I: ELIGIBILITY CHECKLIST FOR RAPID RESPONSE
------------------------------------------------------
Given the rapid nature of emergency trauma studies, data pipelines must instantly isolate candidates matching these profiles:

[ ACCEPTANCE TRIGGERS ]
* Blood Type must be conclusively "A-".
* Trial restricts age to rule out geriatric frailty (Patient Age must be under 50).
* Admission Type must be strictly "Urgent".

[ REJECTION TRIGGERS ]
* The patient cannot be clinically stable. Those with Test Results marked as "Normal" are rejected from the data pull (Wait for manual override).

------------------------------------------------------
SECTION II: CLINICAL CONTEXT
------------------------------------------------------
There is a statistically significant rate of adverse hemolytic reactions in A-Negative populations during trauma and emergency response transfusions. This rapid-response study evaluates patient outcomes in these high-stress admission environments with the goal to track and mitigate adverse reactions.

------------------------------------------------------
SECTION III: EXECUTION
------------------------------------------------------
Methodology: Retrospective chart review isolating urgent admissions requiring blood products. Data automated extraction governed by standard internal protocols.

Approving Officer: Dr. Elena Rostova, MD, FACS.
Authority: Approved under Emergency Provisions.
"@

$brd_4_core = @"
** OBSERVATIONAL COHORT PROPOSAL **
Protocol ID #CVX-2026-004
Project Title: Long-term Lipitor Tolerance in Senior Populations
Sponsor Branch: Agilisium Cardiovascular Division
Effective Date: March 1, 2026

1.0 INTRODUCTION 
Statins remain the premier standard of care for dyslipidemia, but longitudinal studies in purely senior, asymptomatic populations remain sparse. This study observes baseline health metrics. Primary Objective: Observing baseline health metrics in elderly patients on active statin regimens.

2.0 DESIGN
Observational cohort spanning 24 months. Data management adhering to Good Clinical Practice (GCP) guidelines. Sign-off executed by Dr. William Thorne, MD, PhD (IRB Approved). 

3.0 COHORT PARAMETERS (ELIGIBILITY)
This study explicitly targets asymptomatic elderly males on specific cholesterol management routines. Any patient failing the below parameters is inherently excluded from the data pool (no explicit exclusionary rules needed).

Candidate must meet all 4 conditions exactly:
1. Patient Age > 75
2. Patient Gender == "Male"
3. Current Medication regimen actively lists "Lipitor"
4. Patient Test Results == "Normal" (Must be asymptomatic/stable)
"@

$boilerplate_chunks = @(
    "Agilisium Life Sciences is dedicated to the robust pursuit of physiological advancements and pharmacological breakthroughs that span across the diverse and ever-evolving landscape of global healthcare infrastructure. ",
    "The historical context of standard of care dictates a longitudinal assessment of confounding variables extending through socio-economic, environmental, and genetically predisposed metabolic pathways. ",
    "Regulatory frameworks heavily stipulate that all principal investigators strictly adhere to the updated ICH-GCP (International Council for Harmonisation of Technical Requirements for Pharmaceuticals for Human Use - Good Clinical Practice) E6(R2) guidelines. ",
    "Phase matching protocols necessitate robust multi-variate analysis wherein biostatisticians leverage redundant stratification to minimize p-value inflation and alpha-risk accumulation over extended longitudinal milestones. ",
    "Pre-clinical murine model extrapolations suggested a dose-dependent kinetic absorption profile, significantly altered by hepatic first-pass metabolism, which necessitated phase one reassessments of bioavailability matrices. ",
    "Compliance with local institutional review board edicts requires continuous auditing of electronic health record security, specifically ensuring AES-256 encryption standards for data at rest and TLS 1.3 for data in transit. ",
    "Furthermore, the company narrative revolves around stakeholder value generation via rigorous, compliant, and transformative double-blind methodologies that secure FDA, EMA, and PMDA multi-regional approvals. ",
    "A comprehensive literature review dating back two decades highlights the persistent gap in real-world evidence tracking long-term symptomatic remission versus acute intervention suppression. ",
    "Pharmacovigilance operations strictly monitor for Suspected Unexpected Serious Adverse Reactions (SUSARs), requiring unblinded reporting to the Data Safety Monitoring Board (DSMB) within 72 hours of clinical detection. ",
    "The operational footprint of our clinical logistics division ensures that cold-chain supply dependencies are maintained down to strict temperature tolerances of minus eighty degrees Celsius. "
)

function Get-Noise {
    param([int]$WordCount)
    $noise = [System.Text.StringBuilder]::new()
    $current_words = 0
    $rand = New-Object System.Random
    while ($current_words -lt $WordCount) {
        $chunk = $boilerplate_chunks[$rand.Next(0, $boilerplate_chunks.Length)]
        [void]$noise.Append($chunk)
        $current_words += ($chunk.Trim() -split '\s+').Count
    }
    return $noise.ToString()
}

function Create-MassiveBRD {
    param([string]$Filename, [string]$CoreContent)
    
    $prefix_noise = Get-Noise -WordCount 1000
    $suffix_noise = Get-Noise -WordCount 1000
    
    $document = "$prefix_noise`n`n======================================================`n$CoreContent`n======================================================`n`n$suffix_noise"
    
    $path = Join-Path $PSScriptRoot "sample_protocols\$Filename"
    Set-Content -Path $path -Value $document -Encoding UTF8
    Write-Host "Generated $Filename"
}

Create-MassiveBRD "brd_1_diabetes_geriatric.txt" $brd_1_core
Create-MassiveBRD "brd_2_arthritis_elective.txt" $brd_2_core
Create-MassiveBRD "brd_3_urgent_blood.txt" $brd_3_core
Create-MassiveBRD "brd_4_statin_efficacy.txt" $brd_4_core

