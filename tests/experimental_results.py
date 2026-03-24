"""
Comprehensive Experimental Results Report Generator.
=====================================================
Runs detailed clinical test scenarios and generates a full report
with accuracy metrics, sensitivity analysis, and edge cases.
"""

import sys
import os
import json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from backend.bayesian_network import BayesianNetwork
from backend.knowledge_base import (
    DISEASES, SYMPTOMS, RISK_FACTORS,
    PRIOR_PROBABILITIES, SENSITIVITY, _DISEASE_ORDER,
    compute_noisy_or_probability
)
from backend.factor import Factor, factor_product, factor_marginalize, factor_reduce, normalize

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "visualizations")
os.makedirs(OUT_DIR, exist_ok=True)

DISEASE_SHORT = {
    'Influenza': 'Flu', 'COVID19': 'COVID-19',
    'Bacterial_Pneumonia': 'Pneumonia', 'Acute_Bronchitis': 'Bronchitis',
    'Common_Cold': 'Cold', 'Pertussis': 'Pertussis', 'Tuberculosis': 'TB'
}


# =============================================================================
# TEST CASES: Clinical scenarios with expected diagnoses
# =============================================================================

TEST_CASES = [
    {
        "id": 1,
        "name": "Classic Influenza (Cum mua dien hinh)",
        "description": "Khoi phat dot ngot voi sot cao, dau co, moi met, lanh run, dau dau, ho khan",
        "symptoms": {
            "Fever": True, "High_Fever": True, "Cough": True, "Dry_Cough": True,
            "Headache": True, "Muscle_Pain": True, "Fatigue": True, "Chills": True,
            "Sore_Throat": True, "Runny_Nose": False, "Shortness_of_Breath": False,
            "Loss_of_Taste_Smell": False,
        },
        "expected": "Influenza",
        "risk_factors": [],
    },
    {
        "id": 2,
        "name": "COVID-19 with Anosmia (COVID-19 mat khuu giac)",
        "description": "Sot, ho khan, met moi, mat vi giac/khuu giac - dau hieu dac trung COVID",
        "symptoms": {
            "Fever": True, "Dry_Cough": True, "Fatigue": True,
            "Loss_of_Taste_Smell": True, "Headache": True, "Muscle_Pain": True,
            "Shortness_of_Breath": True, "Runny_Nose": False, "Sneezing": False,
            "Sore_Throat": False,
        },
        "expected": "COVID19",
        "risk_factors": [],
    },
    {
        "id": 3,
        "name": "Bacterial Pneumonia (Viem phoi vi khuan)",
        "description": "Sot cao, ho co dom, kho tho, dau nguc, met moi - benh nhan cao tuoi",
        "symptoms": {
            "Fever": True, "High_Fever": True, "Productive_Cough": True,
            "Shortness_of_Breath": True, "Chest_Pain": True, "Fatigue": True,
            "Chills": True, "Runny_Nose": False, "Sneezing": False,
            "Loss_of_Taste_Smell": False,
        },
        "expected": "Bacterial_Pneumonia",
        "risk_factors": ["Elderly"],
    },
    {
        "id": 4,
        "name": "Common Cold (Cam lanh thong thuong)",
        "description": "Chay mui, hat xi, dau hong, ho nhe - khong sot",
        "symptoms": {
            "Runny_Nose": True, "Sneezing": True, "Sore_Throat": True,
            "Cough": True, "Fever": False, "High_Fever": False,
            "Shortness_of_Breath": False, "Muscle_Pain": False,
            "Loss_of_Taste_Smell": False,
        },
        "expected": "Common_Cold",
        "risk_factors": [],
    },
    {
        "id": 5,
        "name": "Acute Bronchitis (Viem phe quan cap)",
        "description": "Ho keo dai (co dom), tho kho khe, met moi nhe, sot nhe",
        "symptoms": {
            "Cough": True, "Productive_Cough": True, "Wheezing": True,
            "Fatigue": True, "Fever": True, "High_Fever": False,
            "Chest_Pain": False, "Shortness_of_Breath": False,
            "Runny_Nose": False, "Loss_of_Taste_Smell": False,
        },
        "expected": "Acute_Bronchitis",
        "risk_factors": [],
    },
    {
        "id": 6,
        "name": "Pertussis / Whooping Cough (Ho ga)",
        "description": "Ho khan du doi keo dai, khong sot hoac sot nhe",
        "symptoms": {
            "Cough": True, "Dry_Cough": True, "Fever": False,
            "High_Fever": False, "Shortness_of_Breath": False,
            "Runny_Nose": False, "Sneezing": False, "Headache": False,
            "Muscle_Pain": False, "Loss_of_Taste_Smell": False,
            "Night_Sweats": False,
        },
        "expected": "Pertussis",
        "risk_factors": ["Unvaccinated"],
    },
    {
        "id": 7,
        "name": "Pulmonary Tuberculosis (Lao phoi)",
        "description": "Ho keo dai > 2 tuan, do mo hoi dem, sut can, ho ra mau, met moi man tinh",
        "symptoms": {
            "Cough": True, "Productive_Cough": True, "Hemoptysis": True,
            "Night_Sweats": True, "Weight_Loss": True, "Fatigue": True,
            "Fever": True, "High_Fever": False, "Shortness_of_Breath": False,
            "Runny_Nose": False, "Sneezing": False, "Loss_of_Taste_Smell": False,
        },
        "expected": "Tuberculosis",
        "risk_factors": ["Close_Contact_TB"],
    },
    {
        "id": 8,
        "name": "Mild Respiratory (Nhe, kho xac dinh)",
        "description": "Chi ho nhe va met moi - trieu chung mo ho",
        "symptoms": {
            "Cough": True, "Fatigue": True,
            "Fever": False, "Shortness_of_Breath": False,
            "Runny_Nose": False, "Loss_of_Taste_Smell": False,
        },
        "expected": None,  # Ambiguous case
        "risk_factors": [],
    },
    {
        "id": 9,
        "name": "COVID-19 Severe (COVID-19 nang)",
        "description": "Sot cao, kho tho nang, met moi tram trong, mat khuu giac",
        "symptoms": {
            "Fever": True, "High_Fever": True, "Shortness_of_Breath": True,
            "Fatigue": True, "Loss_of_Taste_Smell": True, "Chest_Pain": True,
            "Dry_Cough": True, "Headache": True, "Muscle_Pain": True,
            "Chills": True,
        },
        "expected": "COVID19",
        "risk_factors": ["Elderly", "Immunocompromised"],
    },
    {
        "id": 10,
        "name": "Flu vs Cold (Phan biet Cum vs Cam lanh)",
        "description": "Sot, ho, chay mui, dau hong - ranh gioi giua cum va cam lanh",
        "symptoms": {
            "Fever": True, "Cough": True, "Runny_Nose": True,
            "Sore_Throat": True, "Headache": True,
            "Muscle_Pain": False, "Chills": False, "Fatigue": False,
        },
        "expected": "Common_Cold",  # Without systemic symptoms, more likely cold
        "risk_factors": [],
    },
]


def run_all_tests():
    """Run all test cases and collect results."""
    results = []
    
    for tc in TEST_CASES:
        bn = BayesianNetwork(risk_factors=tc["risk_factors"] if tc["risk_factors"] else None)
        result = bn.diagnose(
            observed_symptoms=tc["symptoms"],
            risk_factors=tc["risk_factors"] if tc["risk_factors"] else None
        )
        
        # Determine correctness
        top_disease = result["most_likely"]
        is_correct = (tc["expected"] is None) or (top_disease == tc["expected"])
        
        results.append({
            "test_case": tc,
            "result": result,
            "is_correct": is_correct,
            "top_disease": top_disease,
            "top_prob": result["diagnoses"][0]["probability"],
            "confidence_gap": (
                result["diagnoses"][0]["probability"] - result["diagnoses"][1]["probability"]
                if len(result["diagnoses"]) > 1 else result["diagnoses"][0]["probability"]
            ),
        })
    
    return results


def run_factor_unit_tests():
    """Run unit tests on Factor operations and return results."""
    tests = []
    
    # Test 1: Prior factor
    from backend.factor import create_prior_factor
    f = create_prior_factor("Flu", 0.15)
    t1_pass = abs(f.get_value({"Flu": 0}) - 0.85) < 1e-10 and abs(f.get_value({"Flu": 1}) - 0.15) < 1e-10
    tests.append(("Prior Factor Creation", t1_pass, "P(Flu=0)=0.85, P(Flu=1)=0.15"))
    
    # Test 2: Factor product
    f_a = Factor(["A"], [2], [0.6, 0.4])
    f_b = Factor(["A", "B"], [2, 2], [0.3, 0.7, 0.8, 0.2])
    product = factor_product(f_a, f_b)
    t2_pass = "A" in product.variables and "B" in product.variables
    expected_val = 0.6 * 0.3  # A=0, B=0
    t2_pass = t2_pass and abs(product.get_value({"A": 0, "B": 0}) - expected_val) < 1e-10
    tests.append(("Factor Product", t2_pass, f"phi(A=0,B=0) = 0.6*0.3 = {expected_val}"))
    
    # Test 3: Marginalization
    marginal = factor_marginalize(product, "B")
    t3_pass = "B" not in marginal.variables and "A" in marginal.variables
    # sum over B: A=0: 0.6*0.3 + 0.6*0.7 = 0.6
    t3_pass = t3_pass and abs(marginal.get_value({"A": 0}) - 0.6) < 1e-10
    tests.append(("Factor Marginalization", t3_pass, "Sum_B phi(A=0,B) = 0.6*0.3 + 0.6*0.7 = 0.6"))
    
    # Test 4: Evidence reduction
    reduced = factor_reduce(f_b, "A", 1)
    t4_pass = "A" not in reduced.variables
    t4_pass = t4_pass and abs(reduced.get_value({"B": 0}) - 0.8) < 1e-10
    tests.append(("Factor Reduction (Evidence)", t4_pass, "phi(B|A=1): B=0 -> 0.8"))
    
    # Test 5: Normalization
    f_unnorm = Factor(["X"], [2], [3.0, 7.0])
    f_norm = normalize(f_unnorm)
    t5_pass = abs(f_norm.get_value({"X": 0}) - 0.3) < 1e-10
    t5_pass = t5_pass and abs(f_norm.get_value({"X": 1}) - 0.7) < 1e-10
    t5_pass = t5_pass and abs(sum(f_norm.values) - 1.0) < 1e-10
    tests.append(("Factor Normalization", t5_pass, "Normalize [3,7] -> [0.3, 0.7], sum=1.0"))
    
    # Test 6: Noisy-OR symmetry
    p_no = compute_noisy_or_probability("Fever", [])
    p_one = compute_noisy_or_probability("Fever", ["Influenza"])
    p_two = compute_noisy_or_probability("Fever", ["Influenza", "COVID19"])
    t6_pass = p_no < p_one < p_two
    tests.append(("Noisy-OR Monotonicity", t6_pass, 
                  f"P(F|none)={p_no:.3f} < P(F|Flu)={p_one:.3f} < P(F|Flu,COVID)={p_two:.3f}"))
    
    # Test 7: Probabilities in valid range
    bn = BayesianNetwork()
    res = bn.diagnose({"Fever": True, "Cough": True})
    all_valid = all(0.0 <= d["probability"] <= 1.0 for d in res["diagnoses"])
    tests.append(("Probability Range [0,1]", all_valid, "All posterior probs in valid range"))
    
    return tests


def generate_report_charts(results):
    """Generate result visualization charts."""
    
    # Chart 1: Accuracy by test case (bar chart)
    fig, ax = plt.subplots(figsize=(14, 6))
    
    case_names = [f"Case {r['test_case']['id']}" for r in results]
    top_probs = [r['top_prob'] for r in results]
    correctness = [r['is_correct'] for r in results]
    colors = ['#4CAF50' if c else '#F44336' for c in correctness]
    
    bars = ax.bar(range(len(results)), top_probs, color=colors, edgecolor='white', linewidth=1.5)
    
    for i, (bar, r) in enumerate(zip(bars, results)):
        label = DISEASE_SHORT.get(r['top_disease'], r['top_disease'])
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.01,
                f'{label}\n{r["top_prob"]:.1%}', ha='center', va='bottom', fontsize=8, fontweight='bold')
    
    ax.set_xticks(range(len(results)))
    ax.set_xticklabels([f"#{r['test_case']['id']}" for r in results], fontsize=10)
    ax.set_ylabel('Top Diagnosis Probability', fontsize=12)
    ax.set_title('Diagnostic Accuracy Across 10 Clinical Scenarios\nDo chinh xac chan doan qua 10 ca lam sang',
                 fontsize=14, fontweight='bold')
    ax.set_ylim(0, 1.15)
    
    green_patch = mpatches.Patch(color='#4CAF50', label='Correct')
    red_patch = mpatches.Patch(color='#F44336', label='Incorrect / Ambiguous')
    ax.legend(handles=[green_patch, red_patch], loc='upper right')
    
    plt.tight_layout()
    path = os.path.join(OUT_DIR, '11_diagnostic_accuracy.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {path}")
    
    # Chart 2: Confidence gap (how much the top diagnosis beats the 2nd)
    fig, ax = plt.subplots(figsize=(14, 6))
    
    gaps = [r['confidence_gap'] for r in results]
    colors_gap = ['#2196F3' if g > 0.1 else '#FF9800' if g > 0.05 else '#F44336' for g in gaps]
    
    bars = ax.bar(range(len(results)), gaps, color=colors_gap, edgecolor='white', linewidth=1.5)
    
    for bar, gap in zip(bars, gaps):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.005,
                f'{gap:.1%}', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    ax.set_xticks(range(len(results)))
    ax.set_xticklabels([f"#{r['test_case']['id']}" for r in results], fontsize=10)
    ax.set_ylabel('Confidence Gap (P1 - P2)', fontsize=12)
    ax.set_title('Diagnostic Confidence Gap\nDo tin cay chan doan (chenh lech giua benh #1 va #2)',
                 fontsize=14, fontweight='bold')
    
    blue_patch = mpatches.Patch(color='#2196F3', label='High confidence (>10%)')
    orange_patch = mpatches.Patch(color='#FF9800', label='Medium (5-10%)')
    red_patch = mpatches.Patch(color='#F44336', label='Low (<5%)')
    ax.legend(handles=[blue_patch, orange_patch, red_patch], loc='upper right')
    
    plt.tight_layout()
    path = os.path.join(OUT_DIR, '12_confidence_gap.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {path}")
    
    # Chart 3: Full probability distribution for each case (stacked)
    fig, axes = plt.subplots(2, 5, figsize=(22, 8))
    axes = axes.flatten()
    
    disease_colors_map = dict(zip(_DISEASE_ORDER, 
        ['#2196F3', '#F44336', '#FF9800', '#4CAF50', '#9C27B0', '#00BCD4', '#795548']))
    
    for idx, r in enumerate(results):
        ax = axes[idx]
        diagnoses = r['result']['diagnoses']
        names = [DISEASE_SHORT[d['disease']] for d in diagnoses]
        probs = [d['probability'] for d in diagnoses]
        colors = [disease_colors_map[d['disease']] for d in diagnoses]
        
        bars = ax.barh(range(len(names)), probs, color=colors, edgecolor='white')
        
        for bar, prob in zip(bars, probs):
            if prob > 0.03:
                ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2.,
                        f'{prob:.0%}', va='center', fontsize=7)
        
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names, fontsize=7)
        ax.set_xlim(0, 1.1)
        ax.set_title(f"Case #{r['test_case']['id']}", fontsize=10, fontweight='bold')
        
        status = "OK" if r['is_correct'] else "?"
        status_color = '#4CAF50' if r['is_correct'] else '#F44336'
        ax.text(0.95, 0.05, status, transform=ax.transAxes, ha='right', va='bottom',
                fontsize=14, fontweight='bold', color=status_color)
    
    fig.suptitle('Posterior Probability Distribution for Each Clinical Case\nPhan phoi xac suat hau nghiem cua tung ca lam sang',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    path = os.path.join(OUT_DIR, '13_posterior_distributions.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {path}")


def run_sensitivity_analysis():
    """Run sensitivity analysis: how does adding/removing symptoms affect diagnosis."""
    bn = BayesianNetwork()
    
    # Start with Fever + Cough (ambiguous) and progressively add discriminating symptoms
    base_symptoms = {"Fever": True, "Cough": True}
    
    progressive_symptoms = [
        ("Fever + Cough", {}),
        ("+ Headache", {"Headache": True}),
        ("+ Muscle Pain", {"Muscle_Pain": True}),
        ("+ Chills", {"Chills": True}),
        ("+ High Fever", {"High_Fever": True}),
        ("+ Dry Cough", {"Dry_Cough": True}),
    ]
    
    progression_results = []
    accumulated = dict(base_symptoms)
    
    for label, new_symptoms in progressive_symptoms:
        accumulated.update(new_symptoms)
        result = bn.diagnose(dict(accumulated))
        top3 = [(d["disease"], d["probability"]) for d in result["diagnoses"][:3]]
        progression_results.append((label, top3, result["most_likely"]))
    
    # Chart
    fig, ax = plt.subplots(figsize=(14, 7))
    
    diseases_to_track = ["Influenza", "COVID19", "Bacterial_Pneumonia", "Common_Cold", "Acute_Bronchitis"]
    colors = ['#2196F3', '#F44336', '#FF9800', '#9C27B0', '#4CAF50']
    
    x_labels = [pr[0] for pr in progression_results]
    x = range(len(x_labels))
    
    for disease, color in zip(diseases_to_track, colors):
        probs = []
        for label, top3, _ in progression_results:
            prob = next((p for d, p in top3 if d == disease), 0.0)
            # Need the full result, let me recalculate
            probs.append(prob)
        
        # Recalculate properly
        accumulated2 = dict(base_symptoms)
        probs2 = []
        for lbl, new_symptoms in progressive_symptoms:
            accumulated2.update(new_symptoms)
            result2 = bn.diagnose(dict(accumulated2))
            p = next((d["probability"] for d in result2["diagnoses"] if d["disease"] == disease), 0.0)
            probs2.append(p)
        
        ax.plot(x, probs2, 'o-', color=color, linewidth=2, markersize=8,
                label=DISEASE_SHORT[disease])
    
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, fontsize=9, rotation=15)
    ax.set_ylabel('Posterior Probability', fontsize=12)
    ax.set_title('Sensitivity Analysis: Progressive Symptom Addition\nPhan tich do nhay: them dan trieu chung (huong toi Influenza)',
                 fontsize=14, fontweight='bold')
    ax.legend(loc='upper left', fontsize=10)
    ax.set_ylim(0, 1.0)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    path = os.path.join(OUT_DIR, '14_sensitivity_analysis.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {path}")
    
    return progression_results


def run_risk_factor_comparison():
    """Compare diagnosis with and without risk factors."""
    symptoms_tb = {
        "Cough": True, "Fatigue": True, "Fever": True,
        "Night_Sweats": True, "Weight_Loss": True,
    }
    
    bn_no_rf = BayesianNetwork()
    bn_smoker = BayesianNetwork(risk_factors=["Smoking"])
    bn_tb_contact = BayesianNetwork(risk_factors=["Close_Contact_TB"])
    bn_immuno = BayesianNetwork(risk_factors=["Immunocompromised"])
    
    results = {
        "No Risk Factors": bn_no_rf.diagnose(symptoms_tb),
        "Smoker": bn_smoker.diagnose(symptoms_tb, risk_factors=["Smoking"]),
        "TB Contact": bn_tb_contact.diagnose(symptoms_tb, risk_factors=["Close_Contact_TB"]),
        "Immunocompromised": bn_immuno.diagnose(symptoms_tb, risk_factors=["Immunocompromised"]),
    }
    
    # Chart
    fig, ax = plt.subplots(figsize=(14, 7))
    
    scenarios = list(results.keys())
    width = 0.12
    x = np.arange(len(scenarios))
    
    disease_colors_map = dict(zip(_DISEASE_ORDER, 
        ['#2196F3', '#F44336', '#FF9800', '#4CAF50', '#9C27B0', '#00BCD4', '#795548']))
    
    for i, disease in enumerate(_DISEASE_ORDER):
        probs = []
        for scenario in scenarios:
            p = next((d["probability"] for d in results[scenario]["diagnoses"] if d["disease"] == disease), 0.0)
            probs.append(p)
        
        offset = (i - len(_DISEASE_ORDER)/2) * width + width/2
        bars = ax.bar(x + offset, probs, width, label=DISEASE_SHORT[disease],
                      color=disease_colors_map[disease], edgecolor='white')
    
    ax.set_xticks(x)
    ax.set_xticklabels(scenarios, fontsize=10)
    ax.set_ylabel('Posterior Probability', fontsize=12)
    ax.set_title('Risk Factor Impact on Diagnosis\nAnh huong cua yeu to nguy co den ket qua chan doan\n(Symptoms: Cough + Fatigue + Fever + Night Sweats + Weight Loss)',
                 fontsize=13, fontweight='bold')
    ax.legend(loc='upper left', fontsize=8, ncol=4)
    ax.set_ylim(0, 1.0)
    
    plt.tight_layout()
    path = os.path.join(OUT_DIR, '15_risk_factor_comparison.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {path}")
    
    return results


if __name__ == "__main__":
    print("=" * 60)
    print("RUNNING COMPREHENSIVE EXPERIMENTAL TESTS")
    print("=" * 60)
    
    # 1. Unit tests
    print("\n--- Unit Tests ---")
    unit_results = run_factor_unit_tests()
    for name, passed, detail in unit_results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {name}: {detail}")
    
    unit_passed = sum(1 for _, p, _ in unit_results if p)
    unit_total = len(unit_results)
    print(f"\n  Unit Tests: {unit_passed}/{unit_total} passed")
    
    # 2. Clinical test cases
    print("\n--- Clinical Test Cases ---")
    clinical_results = run_all_tests()
    
    for r in clinical_results:
        tc = r['test_case']
        status = "PASS" if r['is_correct'] else "CHECK"
        expected = tc['expected'] or "Ambiguous"
        got = r['top_disease']
        print(f"  [{status}] Case #{tc['id']}: {tc['name']}")
        print(f"         Expected: {expected} | Got: {got} ({r['top_prob']:.1%})")
        print(f"         Confidence gap: {r['confidence_gap']:.1%}")
    
    correct = sum(1 for r in clinical_results if r['is_correct'])
    total = len(clinical_results)
    print(f"\n  Clinical Tests: {correct}/{total} correct")
    
    # 3. Generate charts
    print("\n--- Generating Charts ---")
    generate_report_charts(clinical_results)
    
    # 4. Sensitivity analysis
    print("\n--- Sensitivity Analysis ---")
    sensitivity_results = run_sensitivity_analysis()
    for label, top3, most_likely in sensitivity_results:
        print(f"  {label:25s} -> {DISEASE_SHORT.get(most_likely, most_likely):10s} | Top 3: ", end="")
        print(", ".join(f"{DISEASE_SHORT.get(d,d)}={p:.1%}" for d, p in top3))
    
    # 5. Risk factor comparison
    print("\n--- Risk Factor Comparison ---")
    rf_results = run_risk_factor_comparison()
    for scenario, result in rf_results.items():
        top = result['diagnoses'][0]
        print(f"  {scenario:25s} -> {DISEASE_SHORT.get(top['disease'], top['disease'])} ({top['probability']:.1%})")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Unit Tests:     {unit_passed}/{unit_total} passed")
    print(f"  Clinical Tests: {correct}/{total} correct ({correct/total:.0%} accuracy)")
    print(f"  Charts generated: 5 new charts in visualizations/")
    print("=" * 60)
