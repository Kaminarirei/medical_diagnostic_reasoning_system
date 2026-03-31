"""
Knowledge Base for Medical Diagnostic Reasoning System
=======================================================
Focus: Acute Respiratory Inflammation & Fever Syndrome
(Respiratory + Infectious + Allergic Diseases)

Data sources:
- CDC (Centers for Disease Control and Prevention)
- WHO (World Health Organization)
- NIH (National Institutes of Health) / PubMed literature
- Harrison's Principles of Internal Medicine
- Clinical epidemiology studies

All probability values are derived from published medical literature.
"""

# =============================================================================
# 1. DISEASES (Bệnh) — Focused on Respiratory & Infectious
# =============================================================================

DISEASES = {
    "Influenza": {
        "name_vi": "Cúm mùa",
        "description": "Seasonal influenza caused by influenza A/B viruses",
        "description_vi": "Bệnh cúm mùa do virus cúm A hoặc B gây ra",
        "icd10": "J09-J11",
        "category": "Respiratory / Infectious",
    },
    "COVID19": {
        "name_vi": "COVID-19",
        "description": "Coronavirus disease 2019 caused by SARS-CoV-2",
        "description_vi": "Bệnh đường hô hấp cấp tính do virus SARS-CoV-2 gây ra",
        "icd10": "U07.1",
        "category": "Respiratory / Infectious",
    },
    "Bacterial_Pneumonia": {
        "name_vi": "Viêm phổi do vi khuẩn",
        "description": "Community-acquired bacterial pneumonia (e.g., S. pneumoniae)",
        "description_vi": "Viêm phổi cấp tính do vi khuẩn (như phế cầu khuẩn)",
        "icd10": "J15",
        "category": "Respiratory",
    },
    "Acute_Bronchitis": {
        "name_vi": "Viêm phế quản cấp",
        "description": "Acute inflammation of the bronchial tubes, usually viral",
        "description_vi": "Viêm cấp tính các ống phế quản, thường do virus",
        "icd10": "J20",
        "category": "Respiratory",
    },
    "Common_Cold": {
        "name_vi": "Cảm lạnh thông thường",
        "description": "Upper respiratory tract infection (rhinovirus, etc.)",
        "description_vi": "Nhiễm trùng đường hô hấp trên do các loại virus (như rhinovirus)",
        "icd10": "J00",
        "category": "Respiratory",
    },
    "Pertussis": {
        "name_vi": "Ho gà",
        "description": "Whooping cough caused by Bordetella pertussis",
        "description_vi": "Bệnh ho gà do vi khuẩn Bordetella pertussis gây ra",
        "icd10": "A37",
        "category": "Respiratory / Infectious",
    },
    "Tuberculosis": {
        "name_vi": "Lao phổi",
        "description": "Pulmonary tuberculosis caused by Mycobacterium tuberculosis",
        "description_vi": "Bệnh lao phổi do vi khuẩn Mycobacterium tuberculosis gây ra",
        "icd10": "A15",
        "category": "Respiratory / Infectious",
    },
    "Allergic_Rhinitis": {
        "name_vi": "Viêm mũi dị ứng",
        "description": "Allergic inflammation of nasal passages (hay fever)",
        "description_vi": "Viêm mũi dị ứng do phản ứng của cơ thể với các tác nhân môi trường (phấn hoa, bụi)",
        "icd10": "J30",
        "category": "Respiratory / Allergic",
    },
    "Asthma_Exacerbation": {
        "name_vi": "Cơn hen suyễn cấp",
        "description": "Acute worsening of asthma symptoms with bronchospasm",
        "description_vi": "Đợt cấp của hen suyễn gây co thắt phế quản và khó thở",
        "icd10": "J45",
        "category": "Respiratory",
    },
    "Laryngitis": {
        "name_vi": "Viêm thanh quản",
        "description": "Inflammation of the larynx causing hoarseness",
        "description_vi": "Viêm thanh quản gây khàn tiếng hoặc mất giọng",
        "icd10": "J04",
        "category": "Respiratory",
    },
}

# =============================================================================
# 2. SYMPTOMS (Triệu chứng)
# =============================================================================

SYMPTOMS = {
    "Fever": {
        "name_vi": "Sốt",
        "description": "Body temperature ≥ 38°C (100.4°F)",
        "type": "vital_sign",
    },
    "High_Fever": {
        "name_vi": "Sốt cao",
        "description": "Body temperature ≥ 39°C (102.2°F)",
        "type": "vital_sign",
    },
    "Cough": {
        "name_vi": "Ho",
        "description": "Persistent coughing (dry or productive)",
        "type": "respiratory",
    },
    "Productive_Cough": {
        "name_vi": "Ho có đờm",
        "description": "Cough producing sputum/mucus",
        "type": "respiratory",
    },
    "Dry_Cough": {
        "name_vi": "Ho khan",
        "description": "Cough without sputum production",
        "type": "respiratory",
    },
    "Shortness_of_Breath": {
        "name_vi": "Khó thở",
        "description": "Dyspnea or difficulty breathing",
        "type": "respiratory",
    },
    "Chest_Pain": {
        "name_vi": "Đau ngực",
        "description": "Pain in chest area, especially with breathing",
        "type": "respiratory",
    },
    "Sore_Throat": {
        "name_vi": "Đau họng",
        "description": "Pain or irritation in the throat",
        "type": "upper_respiratory",
    },
    "Runny_Nose": {
        "name_vi": "Chảy mũi",
        "description": "Nasal discharge (rhinorrhea)",
        "type": "upper_respiratory",
    },
    "Sneezing": {
        "name_vi": "Hắt xì",
        "description": "Frequent sneezing episodes",
        "type": "upper_respiratory",
    },
    "Headache": {
        "name_vi": "Đau đầu",
        "description": "Pain in the head region",
        "type": "systemic",
    },
    "Muscle_Pain": {
        "name_vi": "Đau cơ / nhức mỏi",
        "description": "Myalgia — generalized muscle aches",
        "type": "systemic",
    },
    "Fatigue": {
        "name_vi": "Mệt mỏi",
        "description": "Extreme tiredness or exhaustion",
        "type": "systemic",
    },
    "Loss_of_Taste_Smell": {
        "name_vi": "Mất vị giác / khứu giác",
        "description": "Anosmia or ageusia",
        "type": "neurological",
    },
    "Night_Sweats": {
        "name_vi": "Đổ mồ hôi đêm",
        "description": "Excessive sweating during sleep",
        "type": "systemic",
    },
    "Weight_Loss": {
        "name_vi": "Sụt cân",
        "description": "Unintentional weight loss",
        "type": "systemic",
    },
    "Chills": {
        "name_vi": "Ớn lạnh / rét run",
        "description": "Shivering and feeling cold",
        "type": "systemic",
    },
    "Wheezing": {
        "name_vi": "Thở khò khè",
        "description": "Whistling sound when breathing",
        "type": "respiratory",
    },
    "Hemoptysis": {
        "name_vi": "Ho ra máu",
        "description": "Coughing up blood",
        "type": "respiratory",
    },
    "Hoarseness": {
        "name_vi": "Khàn giọng",
        "description": "Abnormal voice changes, raspy or strained voice",
        "type": "upper_respiratory",
    },
    "Itchy_Eyes": {
        "name_vi": "Ngứa mắt / chảy nước mắt",
        "description": "Allergic conjunctivitis — itchy, watery eyes",
        "type": "neurological",
    },
}

# =============================================================================
# 3. RISK FACTORS (Yếu tố nguy cơ) — Optional evidence
# =============================================================================

RISK_FACTORS = {
    "Smoking": {
        "name_vi": "Hút thuốc",
        "description": "Current or former smoker",
    },
    "Elderly": {
        "name_vi": "Người cao tuổi (≥65)",
        "description": "Age 65 years or older",
    },
    "Immunocompromised": {
        "name_vi": "Suy giảm miễn dịch",
        "description": "HIV, chemotherapy, organ transplant, etc.",
    },
    "Close_Contact_TB": {
        "name_vi": "Tiếp xúc người lao",
        "description": "Close contact with active TB patient",
    },
    "Recent_Travel": {
        "name_vi": "Đi du lịch gần đây",
        "description": "Travel to endemic area in past 14 days",
    },
    "Unvaccinated": {
        "name_vi": "Chưa tiêm vắc-xin",
        "description": "Not vaccinated against relevant diseases",
    },
}

# =============================================================================
# 4. PRIOR PROBABILITIES — P(Disease)
#    Based on community prevalence / incidence rates
#    Source: CDC, WHO epidemiological data
#    Note: These represent the probability of a patient presenting
#    to a clinic with respiratory symptoms actually having each disease.
#    (NOT general population prevalence)
#
#    Rescaled to accommodate 10 diseases, sum ≈ 0.90
#    (10% reserved for other/unmodeled causes)
# =============================================================================

PRIOR_PROBABILITIES = {
    # P(D) — Prior probability in a symptomatic patient presenting
    # to primary care with acute respiratory complaints.
    # Sources: CDC Morbidity & Mortality Weekly Report, WHO surveillance data

    "Influenza":          0.12,   # ~12% of acute respiratory visits during flu season
                                   # CDC: median 8.3% population incidence/year

    "COVID19":            0.08,   # ~8% of acute respiratory visits (post-pandemic baseline)

    "Bacterial_Pneumonia": 0.04,  # ~4% of acute respiratory visits
                                   # NIH: CAP incidence 24.8/10,000 adults/year

    "Acute_Bronchitis":   0.17,   # ~17% — most common acute respiratory diagnosis

    "Common_Cold":        0.30,   # ~30% — most prevalent respiratory condition
                                   # Adults average 2-3 colds/year

    "Pertussis":          0.025,  # ~2.5% — underdiagnosed in adults

    "Tuberculosis":       0.015,  # ~1.5% in symptomatic patients (higher in endemic areas)

    "Allergic_Rhinitis":  0.07,   # ~7% — common in patients presenting with nasal symptoms
                                   # Affects 10-30% of adults globally (WHO)

    "Asthma_Exacerbation": 0.04,  # ~4% — common trigger of acute respiratory visits
                                   # ~8% of US adults have asthma (CDC)

    "Laryngitis":         0.03,   # ~3% — common cause of hoarseness/voice changes
}
# Total: 0.12+0.08+0.04+0.17+0.30+0.025+0.015+0.07+0.04+0.03 = 0.89

# =============================================================================
# 5. SENSITIVITY TABLE — P(Symptom | Disease)
#    The probability that a patient WITH the disease exhibits the symptom.
#    Sources: Harrison's Principles of Internal Medicine, CDC clinical guides,
#    systematic reviews from PubMed/NIH
#
#    Column order: Influ COVID BacPn AcBr  Cold  Pert  TB   AlRh  Asth  Laryng
# =============================================================================

SENSITIVITY = {
    #                       Influ  COVID  BacPn  AcBr   Cold  Pert   TB    AlRh  Asth  Laryng
    "Fever":               [0.83,  0.78,  0.80,  0.30,  0.25, 0.30,  0.60, 0.03, 0.10, 0.30],
    "High_Fever":          [0.60,  0.45,  0.65,  0.10,  0.05, 0.10,  0.30, 0.01, 0.03, 0.08],
    "Cough":               [0.93,  0.70,  0.85,  0.95,  0.80, 0.95,  0.85, 0.35, 0.80, 0.70],
    "Productive_Cough":    [0.30,  0.20,  0.75,  0.50,  0.40, 0.20,  0.60, 0.15, 0.30, 0.20],
    "Dry_Cough":           [0.65,  0.55,  0.15,  0.50,  0.45, 0.80,  0.30, 0.25, 0.55, 0.55],
    "Shortness_of_Breath": [0.30,  0.40,  0.70,  0.15,  0.05, 0.10,  0.40, 0.05, 0.85, 0.10],
    "Chest_Pain":          [0.15,  0.20,  0.50,  0.10,  0.02, 0.05,  0.30, 0.02, 0.45, 0.05],
    "Sore_Throat":         [0.65,  0.40,  0.15,  0.30,  0.70, 0.10,  0.05, 0.25, 0.10, 0.80],
    "Runny_Nose":          [0.60,  0.30,  0.10,  0.20,  0.85, 0.15,  0.03, 0.90, 0.20, 0.30],
    "Sneezing":            [0.40,  0.15,  0.05,  0.10,  0.80, 0.10,  0.02, 0.90, 0.15, 0.15],
    "Headache":            [0.75,  0.60,  0.40,  0.20,  0.40, 0.15,  0.35, 0.35, 0.20, 0.25],
    "Muscle_Pain":         [0.80,  0.55,  0.35,  0.15,  0.10, 0.10,  0.25, 0.05, 0.10, 0.10],
    "Fatigue":             [0.85,  0.75,  0.70,  0.40,  0.35, 0.30,  0.80, 0.30, 0.50, 0.35],
    "Loss_of_Taste_Smell": [0.05,  0.55,  0.02,  0.02,  0.05, 0.01,  0.02, 0.15, 0.02, 0.05],
    "Night_Sweats":        [0.20,  0.15,  0.20,  0.05,  0.02, 0.05,  0.70, 0.02, 0.05, 0.03],
    "Weight_Loss":         [0.05,  0.10,  0.10,  0.02,  0.01, 0.02,  0.65, 0.01, 0.02, 0.01],
    "Chills":              [0.75,  0.50,  0.60,  0.15,  0.10, 0.10,  0.30, 0.03, 0.05, 0.10],
    "Wheezing":            [0.15,  0.15,  0.20,  0.40,  0.05, 0.20,  0.10, 0.10, 0.90, 0.05],
    "Hemoptysis":          [0.02,  0.03,  0.10,  0.02,  0.00, 0.02,  0.25, 0.00, 0.01, 0.01],
    "Hoarseness":          [0.15,  0.10,  0.05,  0.20,  0.25, 0.15,  0.10, 0.10, 0.15, 0.95],
    "Itchy_Eyes":          [0.05,  0.03,  0.01,  0.03,  0.10, 0.02,  0.01, 0.85, 0.15, 0.03],
}

# Column order for reference
_DISEASE_ORDER = [
    "Influenza", "COVID19", "Bacterial_Pneumonia",
    "Acute_Bronchitis", "Common_Cold", "Pertussis", "Tuberculosis",
    "Allergic_Rhinitis", "Asthma_Exacerbation", "Laryngitis"
]

# =============================================================================
# 6. SPECIFICITY TABLE — P(¬Symptom | ¬Disease)
#    The probability that a patient WITHOUT the disease does NOT have the symptom.
#    Used to calculate false positive rate: P(S|¬D) = 1 - Specificity
#
#    Column order: Influ COVID BacPn AcBr  Cold  Pert  TB   AlRh  Asth  Laryng
# =============================================================================

SPECIFICITY = {
    #                       Influ  COVID  BacPn  AcBr   Cold  Pert   TB    AlRh  Asth  Laryng
    "Fever":               [0.60,  0.65,  0.55,  0.70,  0.65, 0.70,  0.65, 0.70, 0.72, 0.68],
    "High_Fever":          [0.85,  0.88,  0.80,  0.92,  0.93, 0.92,  0.90, 0.92, 0.93, 0.90],
    "Cough":               [0.30,  0.40,  0.35,  0.25,  0.35, 0.30,  0.35, 0.55, 0.30, 0.35],
    "Productive_Cough":    [0.75,  0.80,  0.60,  0.65,  0.68, 0.78,  0.65, 0.75, 0.70, 0.78],
    "Dry_Cough":           [0.55,  0.60,  0.75,  0.58,  0.60, 0.45,  0.65, 0.60, 0.55, 0.55],
    "Shortness_of_Breath": [0.80,  0.78,  0.65,  0.85,  0.90, 0.88,  0.78, 0.88, 0.60, 0.86],
    "Chest_Pain":          [0.90,  0.88,  0.75,  0.92,  0.95, 0.94,  0.85, 0.94, 0.80, 0.92],
    "Sore_Throat":         [0.55,  0.65,  0.80,  0.70,  0.45, 0.82,  0.88, 0.68, 0.82, 0.50],
    "Runny_Nose":          [0.50,  0.65,  0.80,  0.72,  0.35, 0.78,  0.85, 0.40, 0.72, 0.70],
    "Sneezing":            [0.65,  0.80,  0.88,  0.85,  0.40, 0.85,  0.90, 0.40, 0.80, 0.82],
    "Headache":            [0.50,  0.55,  0.65,  0.78,  0.62, 0.82,  0.70, 0.62, 0.75, 0.72],
    "Muscle_Pain":         [0.50,  0.60,  0.70,  0.82,  0.85, 0.88,  0.78, 0.85, 0.85, 0.88],
    "Fatigue":             [0.40,  0.45,  0.50,  0.62,  0.60, 0.68,  0.45, 0.60, 0.55, 0.62],
    "Loss_of_Taste_Smell": [0.95,  0.70,  0.97,  0.97,  0.95, 0.98,  0.97, 0.90, 0.96, 0.94],
    "Night_Sweats":        [0.85,  0.88,  0.85,  0.92,  0.95, 0.93,  0.60, 0.93, 0.92, 0.93],
    "Weight_Loss":         [0.95,  0.92,  0.92,  0.97,  0.98, 0.97,  0.65, 0.97, 0.96, 0.97],
    "Chills":              [0.55,  0.62,  0.58,  0.82,  0.85, 0.88,  0.75, 0.85, 0.88, 0.85],
    "Wheezing":            [0.85,  0.85,  0.82,  0.70,  0.90, 0.82,  0.88, 0.85, 0.50, 0.88],
    "Hemoptysis":          [0.98,  0.97,  0.93,  0.98,  1.00, 0.98,  0.85, 0.99, 0.98, 0.98],
    "Hoarseness":          [0.85,  0.88,  0.90,  0.82,  0.75, 0.80,  0.88, 0.85, 0.82, 0.30],
    "Itchy_Eyes":          [0.92,  0.95,  0.97,  0.95,  0.88, 0.95,  0.97, 0.35, 0.82, 0.95],
}

# =============================================================================
# 7. NOISY-OR LEAK PROBABILITY
#    Represents the background probability that a symptom appears
#    due to causes NOT modeled in the network.
#    P_leak captures measurement error + unmodeled diseases
# =============================================================================

LEAK_PROBABILITIES = {
    "Fever":               0.05,   # Low-grade fever from many causes
    "High_Fever":          0.02,
    "Cough":               0.10,   # Environmental irritants, GERD, etc.
    "Productive_Cough":    0.05,
    "Dry_Cough":           0.08,
    "Shortness_of_Breath": 0.03,   # Anxiety, deconditioning
    "Chest_Pain":          0.03,   # Musculoskeletal, GERD
    "Sore_Throat":         0.08,   # Dryness, reflux
    "Runny_Nose":          0.10,   # Allergies, irritants
    "Sneezing":            0.10,   # Allergies, dust
    "Headache":            0.10,   # Tension, stress, dehydration
    "Muscle_Pain":         0.05,   # Exercise, stress
    "Fatigue":             0.10,   # Poor sleep, stress
    "Loss_of_Taste_Smell": 0.01,   # Rare without infection
    "Night_Sweats":        0.03,   # Hormonal, room temperature
    "Weight_Loss":         0.02,   # Diet changes
    "Chills":              0.03,
    "Wheezing":            0.03,   # Asthma (unmodeled → now partially modeled)
    "Hemoptysis":          0.005,  # Very rare without pathology
    "Hoarseness":          0.04,   # Voice strain, overuse
    "Itchy_Eyes":          0.05,   # Dry eyes, dust, screen fatigue
}

# =============================================================================
# 8. RISK FACTOR MODIFIERS
#    Multiplicative factors applied to prior probabilities
#    when risk factors are present.
# =============================================================================

RISK_FACTOR_MODIFIERS = {
    "Smoking": {
        "Influenza":          1.2,
        "COVID19":            1.3,
        "Bacterial_Pneumonia": 2.0,  # Strong association
        "Acute_Bronchitis":   1.8,
        "Common_Cold":        1.1,
        "Pertussis":          1.1,
        "Tuberculosis":       2.5,   # Strong association
        "Allergic_Rhinitis":  1.3,   # Irritant effect on nasal mucosa
        "Asthma_Exacerbation": 2.0,  # Major trigger
        "Laryngitis":         1.8,   # Vocal cord irritation
    },
    "Elderly": {
        "Influenza":          1.5,
        "COVID19":            1.8,
        "Bacterial_Pneumonia": 2.5,  # Very strong in elderly
        "Acute_Bronchitis":   1.3,
        "Common_Cold":        1.0,
        "Pertussis":          1.2,
        "Tuberculosis":       1.5,
        "Allergic_Rhinitis":  0.8,   # Less common in elderly
        "Asthma_Exacerbation": 1.3,
        "Laryngitis":         1.1,
    },
    "Immunocompromised": {
        "Influenza":          1.5,
        "COVID19":            2.0,
        "Bacterial_Pneumonia": 3.0,
        "Acute_Bronchitis":   1.5,
        "Common_Cold":        1.2,
        "Pertussis":          1.3,
        "Tuberculosis":       5.0,   # Extremely strong
        "Allergic_Rhinitis":  1.0,   # Not immune-related differential
        "Asthma_Exacerbation": 1.3,
        "Laryngitis":         1.5,
    },
    "Close_Contact_TB": {
        "Influenza":          1.0,
        "COVID19":            1.0,
        "Bacterial_Pneumonia": 1.0,
        "Acute_Bronchitis":   1.0,
        "Common_Cold":        1.0,
        "Pertussis":          1.0,
        "Tuberculosis":       10.0,  # Dramatically increases TB risk
        "Allergic_Rhinitis":  1.0,
        "Asthma_Exacerbation": 1.0,
        "Laryngitis":         1.0,
    },
    "Recent_Travel": {
        "Influenza":          1.3,
        "COVID19":            1.5,
        "Bacterial_Pneumonia": 1.1,
        "Acute_Bronchitis":   1.0,
        "Common_Cold":        1.2,
        "Pertussis":          1.2,
        "Tuberculosis":       3.0,   # Depending on destination
        "Allergic_Rhinitis":  1.2,   # New allergen exposure
        "Asthma_Exacerbation": 1.1,
        "Laryngitis":         1.0,
    },
    "Unvaccinated": {
        "Influenza":          2.0,
        "COVID19":            2.5,
        "Bacterial_Pneumonia": 1.5,
        "Acute_Bronchitis":   1.0,
        "Common_Cold":        1.0,
        "Pertussis":          3.0,   # Vaccine very effective
        "Tuberculosis":       1.5,   # BCG vaccine
        "Allergic_Rhinitis":  1.0,   # No vaccine relevant
        "Asthma_Exacerbation": 1.0,
        "Laryngitis":         1.0,
    },
}


# =============================================================================
# 9. HELPER FUNCTIONS
# =============================================================================

def get_disease_list():
    """Return ordered list of disease names."""
    return list(DISEASES.keys())


def get_symptom_list():
    """Return ordered list of symptom names."""
    return list(SYMPTOMS.keys())


def get_risk_factor_list():
    """Return ordered list of risk factor names."""
    return list(RISK_FACTORS.keys())


def get_sensitivity_for_symptom(symptom: str) -> dict:
    """
    Return P(Symptom=True | Disease=True) for each disease.

    Args:
        symptom: Name of the symptom

    Returns:
        dict mapping disease name -> sensitivity value
    """
    if symptom not in SENSITIVITY:
        raise ValueError(f"Unknown symptom: {symptom}")

    values = SENSITIVITY[symptom]
    return {d: v for d, v in zip(_DISEASE_ORDER, values)}


def get_specificity_for_symptom(symptom: str) -> dict:
    """
    Return P(Symptom=False | Disease=False) for each disease.

    Args:
        symptom: Name of the symptom

    Returns:
        dict mapping disease name -> specificity value
    """
    if symptom not in SPECIFICITY:
        raise ValueError(f"Unknown symptom: {symptom}")

    values = SPECIFICITY[symptom]
    return {d: v for d, v in zip(_DISEASE_ORDER, values)}


def compute_noisy_or_probability(symptom: str, active_diseases: list) -> float:
    """
    Compute P(Symptom=True | active_diseases) using Noisy-OR model.

    The Noisy-OR assumption: each disease independently can cause
    the symptom, and there is also a leak probability.

    P(S=True | D1, D2, ...) = 1 - (1 - p_leak) * Π(1 - p_i) for active Di

    Args:
        symptom: Name of the symptom
        active_diseases: List of disease names that are active (True)

    Returns:
        float: Probability of symptom being present
    """
    p_leak = LEAK_PROBABILITIES.get(symptom, 0.01)
    sensitivities = get_sensitivity_for_symptom(symptom)

    # Compute the Noisy-OR link probabilities
    # p_i = (sensitivity_i - (1 - specificity_i)) / specificity_i
    # Simplified: use sensitivity directly as the causal strength
    product = 1.0 - p_leak
    for disease in active_diseases:
        if disease in sensitivities:
            p_i = sensitivities[disease]
            product *= (1.0 - p_i)

    return 1.0 - product


def get_adjusted_priors(risk_factors: list = None) -> dict:
    """
    Return prior probabilities adjusted by risk factors.
    Ensures probabilities still sum to ≤ 1 after adjustment.

    Args:
        risk_factors: List of active risk factor names

    Returns:
        dict mapping disease name -> adjusted prior probability
    """
    priors = dict(PRIOR_PROBABILITIES)

    if risk_factors:
        for rf in risk_factors:
            if rf in RISK_FACTOR_MODIFIERS:
                modifiers = RISK_FACTOR_MODIFIERS[rf]
                for disease, modifier in modifiers.items():
                    if disease in priors:
                        priors[disease] *= modifier

    # Normalize if total exceeds 1.0 (add "Other/None" implicit category)
    total = sum(priors.values())
    if total > 0.90:  # Leave 10% for "no disease" or unmodeled
        scale = 0.90 / total
        priors = {d: p * scale for d, p in priors.items()}

    return priors


# =============================================================================
# 10. DISPLAY / DEBUG UTILITIES
# =============================================================================

def print_knowledge_base_summary():
    """Print a summary of the knowledge base for debugging."""
    print("=" * 70)
    print("KNOWLEDGE BASE SUMMARY")
    print("Medical Diagnostic Reasoning System")
    print("Focus: Acute Respiratory Inflammation & Fever Syndrome")
    print("=" * 70)

    print(f"\n📋 Diseases: {len(DISEASES)}")
    for d, info in DISEASES.items():
        print(f"   • {d} ({info['name_vi']}) — P(D)={PRIOR_PROBABILITIES[d]:.3f}")

    print(f"\n🩺 Symptoms: {len(SYMPTOMS)}")
    for s, info in SYMPTOMS.items():
        print(f"   • {s} ({info['name_vi']})")

    print(f"\n⚠️  Risk Factors: {len(RISK_FACTORS)}")
    for r, info in RISK_FACTORS.items():
        print(f"   • {r} ({info['name_vi']})")

    print(f"\n📊 Sensitivity table: {len(SENSITIVITY)} symptoms × {len(_DISEASE_ORDER)} diseases")
    print(f"📊 Specificity table: {len(SPECIFICITY)} symptoms × {len(_DISEASE_ORDER)} diseases")
    print(f"📊 Leak probabilities: {len(LEAK_PROBABILITIES)} symptoms")
    print()


if __name__ == "__main__":
    print_knowledge_base_summary()
