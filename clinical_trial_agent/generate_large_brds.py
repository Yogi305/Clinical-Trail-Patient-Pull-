import os
import random

# Realistic Clinical Trial boilerplate paragraphs (NO delimiters, NO markers)
boilerplate_sections = {
    "regulatory": [
        """All participating clinical sites must maintain full compliance with the International Council for Harmonisation of Technical Requirements for Pharmaceuticals for Human Use Good Clinical Practice guidelines, specifically the E6(R2) consolidated guideline as amended in November 2016 and subsequent addenda. Principal investigators bear ultimate responsibility for ensuring that all study procedures are conducted in accordance with the approved protocol, applicable regulatory requirements, and institutional policies governing the protection of human research subjects. Any deviation from the protocol, whether classified as major or minor under the sponsor's deviation management framework, must be documented within 72 hours of discovery using the standardized Protocol Deviation Report Form and submitted to both the institutional review board and the sponsor's clinical operations team for review and determination of corrective and preventive action requirements.""",
        """The sponsor maintains a comprehensive pharmacovigilance system in accordance with European Union Good Pharmacovigilance Practices Module VI and the International Conference on Harmonisation E2B(R3) electronic transmission standards for individual case safety reports. All serious adverse events must be reported to the sponsor's global safety database within 24 hours of the investigator becoming aware of the event, regardless of the investigator's assessment of causality. Suspected unexpected serious adverse reactions require expedited reporting to all relevant regulatory authorities within the timelines specified by applicable national legislation, which in most jurisdictions requires initial notification within 7 calendar days for fatal or life-threatening events and 15 calendar days for all other serious unexpected reactions.""",
        """Data integrity and subject privacy are ensured through a multi-layered security architecture that includes AES-256 encryption for data at rest, TLS 1.3 for data in transit, and role-based access controls implementing the principle of least privilege across all electronic data capture systems. The electronic case report form system has been validated in accordance with 21 CFR Part 11 requirements for electronic records and electronic signatures, with complete audit trail functionality that captures all data creation, modification, and deletion events with timestamps and user identification. Regular vulnerability assessments and penetration testing are conducted by an independent cybersecurity firm to ensure ongoing compliance with HIPAA Security Rule administrative, physical, and technical safeguard requirements.""",
        """Quality management activities are governed by the sponsor's Integrated Quality Management Plan, which implements a risk-based approach to clinical trial oversight consistent with ICH E6(R2) Section 5.0 requirements. The plan identifies critical data and processes, establishes risk indicators and thresholds for key quality parameters, and defines escalation pathways for quality events that may impact subject safety or data integrity. Centralized statistical monitoring is performed on an ongoing basis using validated algorithms that detect unusual data patterns, protocol deviations, and potential fraud indicators across all participating sites simultaneously."""
    ],
    "methodology": [
        """The biostatistical analysis plan specifies a modified intention-to-treat population as the primary analysis set, defined as all randomized subjects who receive at least one dose of study medication and have at least one post-baseline efficacy assessment. Sensitivity analyses will be conducted using the per-protocol population, which excludes subjects with major protocol deviations that could materially impact the interpretability of their efficacy data. Missing data will be handled using a pattern mixture model framework with multiple imputation under the missing-at-random assumption, with sensitivity analyses conducted under missing-not-at-random scenarios using tipping point analyses to assess the robustness of primary conclusions.""",
        """Randomization will be performed using a validated interactive web response system with a computer-generated randomization schedule prepared by an independent biostatistician who is not otherwise involved in the conduct or analysis of the study. The randomization scheme employs permuted blocks of varying size to prevent prediction of future treatment assignments while maintaining approximate balance across treatment groups within each stratification factor combination. Stratification factors include study site, baseline disease severity classification, and prior treatment history as defined in the statistical analysis plan.""",
        """Interim analyses will be conducted by an independent Data Safety Monitoring Board comprising at least three members with relevant clinical expertise, one biostatistician, and one ethicist. The DSMB will review unblinded safety data at pre-specified intervals and has the authority to recommend study termination for safety concerns, overwhelming efficacy, or futility based on pre-defined stopping boundaries calculated using the Lan-DeMets alpha-spending function with O'Brien-Fleming-type boundaries to preserve the overall Type I error rate at the two-sided 0.05 significance level.""",
        """Sample size calculations are based on the primary endpoint analysis assuming a two-sided test at the 0.05 significance level with 80 percent statistical power to detect a clinically meaningful difference between the investigational and control arms. The assumed effect size is derived from the pooled estimate of prior Phase II studies in similar populations, adjusted for expected variability based on the range of baseline disease severity in the target population. An additional 15 percent inflation factor has been applied to account for anticipated dropout rates based on historical data from comparable clinical programs in this therapeutic area."""
    ],
    "operations": [
        """Site initiation visits will be conducted by qualified clinical research associates prior to the enrollment of the first subject at each participating institution. The initiation visit agenda includes comprehensive protocol training for all site personnel involved in study conduct, review of informed consent procedures and documentation requirements, verification of regulatory document completeness, confirmation of investigational product storage and accountability procedures, and hands-on training for all study-specific equipment and electronic data capture systems. Sites must demonstrate competency in all critical study procedures before receiving authorization to begin screening activities.""",
        """Investigational product supply chain management follows the sponsor's validated cold-chain logistics framework, which maintains continuous temperature monitoring from the manufacturing facility through regional distribution centers to individual clinical sites. Temperature excursion management procedures specify acceptable deviation ranges, documentation requirements, and disposition decision pathways that involve both the sponsor's quality assurance unit and the qualified person responsible for batch certification. All investigational product shipments are accompanied by validated temperature monitoring devices that record ambient temperature at five-minute intervals throughout the distribution process.""",
        """Clinical monitoring activities follow a risk-proportionate approach with a combination of on-site monitoring visits, remote monitoring activities, and centralized data review. On-site monitoring visits occur at minimum quarterly frequency, with additional visits triggered by enrollment milestones, safety signals, or quality indicators exceeding pre-defined thresholds. Source document verification is performed for all primary endpoint data, all serious adverse events, and a random sample of secondary endpoint data sufficient to provide 95 percent confidence in overall data accuracy within a three percent margin of error.""",
        """The clinical operations team maintains a comprehensive communication plan that includes monthly investigator newsletters, quarterly investigator teleconferences, and an annual investigator meeting. A dedicated medical monitor is available around the clock for consultation on eligibility questions, adverse event management guidance, and protocol interpretation issues. The sponsor's medical information department provides a toll-free hotline for subjects and healthcare providers seeking information about the investigational product or the clinical trial program."""
    ],
    "scientific": [
        """The pathophysiological basis for the proposed therapeutic intervention rests on converging evidence from molecular biology, pharmacology, and clinical observation spanning approximately two decades of systematic investigation. At the cellular level, the target pathway mediates a cascade of inflammatory and metabolic signaling events that have been implicated in disease progression across multiple organ systems. Preclinical studies using both in vitro cell-based assays and in vivo animal models have demonstrated dose-dependent modulation of key biomarkers, with therapeutic concentrations achievable within the predicted human pharmacokinetic profile based on allometric scaling from non-human primate data.""",
        """A comprehensive literature review conducted using systematic search methodology across PubMed, EMBASE, the Cochrane Library, and ClinicalTrials.gov identified 847 potentially relevant publications, of which 127 met pre-specified inclusion criteria for detailed analysis. The resulting evidence synthesis revealed consistent support for the proposed mechanism of action, though the quality of evidence varies substantially across studies, with particular limitations in the domains of allocation concealment, blinding adequacy, and completeness of outcome reporting. These methodological limitations in the existing evidence base provide strong justification for the rigorous controlled trial design proposed in this protocol.""",
        """Biomarker analyses will employ validated liquid chromatography-tandem mass spectrometry methods for pharmacokinetic assessments and commercially available immunoassay platforms for pharmacodynamic biomarkers. All bioanalytical methods have been validated in accordance with FDA Guidance for Industry on Bioanalytical Method Validation (2018), with demonstrated accuracy, precision, selectivity, sensitivity, reproducibility, and stability within pre-defined acceptance criteria. Quality control samples spanning the calibration range are included in each analytical run, with acceptance criteria requiring that at least two-thirds of quality control samples fall within 15 percent of nominal concentration."""
    ]
}

def generate_boilerplate(target_words):
    """Generate realistic clinical trial boilerplate text."""
    text_parts = []
    current_words = 0
    categories = list(boilerplate_sections.keys())
    
    while current_words < target_words:
        cat = random.choice(categories)
        paragraph = random.choice(boilerplate_sections[cat])
        text_parts.append(paragraph)
        current_words += len(paragraph.split())
    
    return "\n\n".join(text_parts)


# Core criteria for each BRD (same as before)
brd_1_core = """
3.0 PATIENT ELIGIBILITY PARAMETERS

Candidates must pass the following screening matrix before randomization:

REQUIRED FOR ENROLLMENT (INCLUSION CRITERIA):
- The patient must have a documented Medical Condition of "Asthma" in their Electronic Health Record.
- Patient Age must be strictly 60 years or older at the time of initial screening visit.
- Patient Gender must be explicitly "Female".
- Recent laboratory Test Results must be classified as "Abnormal", reflecting compromised pulmonary function markers.

DISQUALIFYING CONDITIONS (EXCLUSION CRITERIA):
- Any patient actively taking or prescribed "Lipitor" (atorvastatin) as a current Medication is excluded due to confirmed CYP3A4 drug-drug interaction with the investigational compound.
- Patients whose hospital Admission Type is recorded as "Emergency" are excluded, as emergency presentations confound baseline pulmonary assessments.
"""

brd_2_core = """
SUBJECT SELECTION CRITERIA

Below are the bounds for patient enrollment in this observation trial. Candidates identified through EHR data mining must satisfy all listed inclusion parameters. There are no protocol-mandated exclusion criteria at this phase; manual chart audits will follow automated screening.

Inclusion Bounds:
Diagnosis: The candidate must suffer from chronically elevated systemic arterial pressure, with documented values consistently exceeding 140/90 mmHg across at least three clinic visits within the preceding 12 months.
Age Bracket: The candidate's Age must be between 50 and 70 years old, inclusive. This range is selected to minimize confounding from age-related arterial stiffening while capturing the peak incidence window for treatment-responsive hypertension.
Pharmacology: The patient must be currently managed on a daily regimen of atorvastatin calcium (commonly branded as Lipitor), as concomitant statin therapy is a protocol requirement for cardiovascular risk stratification in this cohort.
"""

brd_3_core = """
DATA SELECTION PARAMETERS

ACCEPTANCE TRIGGERS (INCLUSION CRITERIA):
- Trial restricts age to rule out geriatric frailty syndromes that confound metabolic assessments. Patient Age must be strictly under 50 years at time of screening.
- The hospital Admission Type must be strictly "Urgent" — only urgent presentations capture the acute decompensation phenotype of interest.
- Clinical Diagnosis: Patient must be presenting with a complex metabolic disorder that heavily impacts both body weight regulation and blood sugar homeostasis. This is the primary diagnostic criterion and must be clearly documented in the attending physician's assessment notes.

REJECTION TRIGGERS (EXCLUSION CRITERIA):
- The patient cannot be clinically stable for purposes of this trial. Those with Test Results marked as "Normal" across all metabolic panels are rejected from the data pull, as they do not represent the target population of active metabolic decompensation. Manual override by the principal investigator is required for any borderline cases.
"""

brd_4_core = """
3.0 COHORT PARAMETERS (ELIGIBILITY)

This study explicitly targets asymptomatic elderly males on specific pain management routines. Any patient failing the below parameters is inherently excluded from the data pool. No additional explicit exclusionary rules are required beyond the inclusion criteria themselves.

Candidate must meet ALL 4 conditions exactly:
1. Patient Age must be 75 years or older, to capture the geriatric risk population identified in prior VA studies.
2. Patient Gender must be "Male", as this study specifically addresses the undercharacterized male GI safety profile.
3. Current Medication regimen must actively list standard over-the-counter NSAID therapy prescribed for chronic inflammation management. The specific NSAID formulation will be identified from the EHR medication reconciliation record.
4. Patient Test Results must be "Normal" — candidates must be asymptomatic and clinically stable at baseline to establish a clean prospective observation window.
"""


def create_brd(filename, title, core_content, target_words=1000):
    """Create a realistic BRD with boilerplate surrounding the core criteria."""
    
    # Calculate how much boilerplate we need (total - core - title)
    core_words = len(core_content.split())
    title_words = len(title.split())
    boilerplate_needed = target_words - core_words - title_words
    
    # Split boilerplate roughly 60/40 before and after the criteria
    prefix_target = int(boilerplate_needed * 0.6)
    suffix_target = boilerplate_needed - prefix_target
    
    prefix = generate_boilerplate(prefix_target)
    suffix = generate_boilerplate(suffix_target)
    
    document = f"""{title}

{prefix}

{core_content}

{suffix}"""
    
    filepath = os.path.join(os.path.dirname(__file__), "sample_protocols", filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(document)
    
    word_count = len(document.split())
    print(f"Generated {filename} with approx {word_count} words.")


if __name__ == "__main__":
    create_brd(
        "brd_1_straightforward.txt",
        """CLINICAL TRIAL PROTOCOL SUMMARY: DXT-2026-001
Title: Efficacy of Novel Therapeutics in Older Asthmatic Females (Phase III)
Sponsor: Agilisium Life Sciences Division
Principal Investigator: Dr. Meera Krishnan, MD, FCCP

1.0 BACKGROUND AND RATIONALE

Asthma remains one of the most prevalent chronic respiratory conditions affecting the global population, with a particularly underrepresented demographic in clinical research: elderly females. Historical analyses of Phase I-III respiratory trials from the past decade reveal a systematic underenrollment of women aged 60 and above. This cohort frequently presents with complex comorbidity profiles that standard bronchodilator regimens fail to address adequately. The pharmacokinetic profile of the investigational compound DXT-4071 has demonstrated dose-dependent bronchodilation in murine models, with a favorable safety index across hepatic and renal clearance pathways.

2.0 STUDY OBJECTIVES

Primary: Evaluate reduction in acute exacerbation frequency over 24 weeks.
Secondary: Assess improvement in FEV1/FVC ratio at 12-week interim analysis.
Exploratory: Correlate treatment response with baseline inflammatory biomarker panels.""",
        brd_1_core
    )
    
    create_brd(
        "brd_2_llm_rerank.txt",
        """MEMORANDUM OF STUDY DESIGN: ORT-2026-002
Subject: Cardiovascular Risk Reduction in Middle-Aged Hypertensive Cohorts (Phase II)
Date: March 2026
Classification: Internal — Restricted Distribution

EXECUTIVE SUMMARY

The global burden of cardiovascular morbidity attributable to poorly managed systemic arterial hypertension continues to escalate despite the availability of multiple pharmacological classes. Recent meta-analyses published in The Lancet Cardiology (2025) estimate that fewer than 40 percent of diagnosed hypertensive patients achieve sustained target blood pressure under current standard-of-care regimens. Agilisium Life Sciences proposes a Phase II observation trial to evaluate a novel angiotensin receptor-neprilysin inhibitor combination in a tightly defined cohort.""",
        brd_2_core
    )
    
    create_brd(
        "brd_3_hitl_ambiguous_condition.txt",
        """EMERGENCY PROTOCOL BRIEF: HKT-2026-003
Title: Emergency Response Assessment in Complex Metabolic Syndromes
Priority Classification: HIGH — Requires Expedited IRB Review
Prepared by: Clinical Operations, Agilisium Life Sciences

BACKGROUND

Metabolic syndrome represents a constellation of interrelated physiological abnormalities that dramatically increase cardiovascular risk. The clinical presentation varies widely, encompassing insulin resistance, dyslipidemia, central adiposity, and chronic inflammatory states. This protocol establishes a rapid-deployment observational framework for evaluating treatment response in patients presenting with acute metabolic decompensation.""",
        brd_3_core
    )
    
    create_brd(
        "brd_4_hitl_ambiguous_medication.txt",
        """OBSERVATIONAL COHORT PROPOSAL #CVX-2026-004
Project Title: Long-term NSAID Tolerance and Gastrointestinal Outcomes in Senior Male Populations
Submitted to: Agilisium Institutional Review Board
Version: 2.1 (Revised March 2026)

1. SCIENTIFIC RATIONALE

Non-steroidal anti-inflammatory drugs remain among the most widely prescribed medication classes globally, with particular prevalence in geriatric populations managing chronic musculoskeletal pain and inflammatory conditions. Despite their therapeutic ubiquity, the long-term gastrointestinal safety profile of chronic NSAID use in males over 75 remains poorly characterized in real-world evidence databases. This observational cohort study proposes to leverage a large, multi-institutional electronic health record dataset to characterize GI event rates in elderly males receiving chronic NSAID therapy.""",
        brd_4_core
    )
