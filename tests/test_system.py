"""
Verification script for the Medical Diagnostic Reasoning System.
Tests the knowledge base, factor operations, and Variable Elimination.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.knowledge_base import (
    print_knowledge_base_summary,
    get_sensitivity_for_symptom,
    compute_noisy_or_probability,
    get_adjusted_priors,
    DISEASES, SYMPTOMS, RISK_FACTORS,
    PRIOR_PROBABILITIES, SENSITIVITY, SPECIFICITY, LEAK_PROBABILITIES,
)
from backend.factor import (
    Factor, factor_product, factor_marginalize, factor_reduce,
    normalize, create_prior_factor, create_symptom_factor
)
from backend.bayesian_network import BayesianNetwork


def test_knowledge_base():
    """Test that the knowledge base has consistent data."""
    print("=" * 60)
    print("TEST 1: Knowledge Base Consistency")
    print("=" * 60)

    # Check all diseases have priors
    for d in DISEASES:
        assert d in PRIOR_PROBABILITIES, f"Missing prior for {d}"
    print(" All diseases have prior probabilities")

    # Check sensitivity table has correct shape
    for symptom, values in SENSITIVITY.items():
        assert len(values) == len(DISEASES), (
            f"Sensitivity for {symptom}: expected {len(DISEASES)} values, got {len(values)}"
        )
    print(" Sensitivity table has correct shape")

    # Check specificity table has correct shape
    for symptom, values in SPECIFICITY.items():
        assert len(values) == len(DISEASES), (
            f"Specificity for {symptom}: expected {len(DISEASES)} values, got {len(values)}"
        )
    print(" Specificity table has correct shape")

    # Check all values are in [0, 1]
    for symptom, values in SENSITIVITY.items():
        for v in values:
            assert 0.0 <= v <= 1.0, f"Invalid sensitivity value for {symptom}: {v}"
    for symptom, values in SPECIFICITY.items():
        for v in values:
            assert 0.0 <= v <= 1.0, f"Invalid specificity value for {symptom}: {v}"
    print(" All probability values are in [0, 1]")

    # Check leak probabilities
    for symptom, leak in LEAK_PROBABILITIES.items():
        assert 0.0 <= leak <= 1.0, f"Invalid leak probability for {symptom}: {leak}"
    print(" All leak probabilities are valid")

    # Print summary
    print_knowledge_base_summary()


def test_factor_operations():
    """Test basic factor operations."""
    print("=" * 60)
    print("TEST 2: Factor Operations")
    print("=" * 60)

    # Test prior factor
    f_flu = create_prior_factor("Flu", 0.15)
    assert abs(f_flu.get_value({"Flu": 0}) - 0.85) < 1e-10
    assert abs(f_flu.get_value({"Flu": 1}) - 0.15) < 1e-10
    print(" Prior factor creation works")

    # Test factor product
    f_a = Factor(["A"], [2], [0.6, 0.4])
    f_b = Factor(["A", "B"], [2, 2], [0.3, 0.7, 0.8, 0.2])
    product = factor_product(f_a, f_b)
    assert "A" in product.variables and "B" in product.variables
    print(" Factor product works")

    # Test factor marginalize
    marginal = factor_marginalize(product, "B")
    assert "B" not in marginal.variables
    assert "A" in marginal.variables
    print(" Factor marginalization works")

    # Test factor reduce
    reduced = factor_reduce(f_b, "A", 1)
    assert "A" not in reduced.variables
    assert abs(reduced.get_value({"B": 0}) - 0.8) < 1e-10
    print(" Factor reduction (evidence) works")

    # Test normalize
    f_unnorm = Factor(["X"], [2], [3.0, 7.0])
    f_norm = normalize(f_unnorm)
    assert abs(f_norm.get_value({"X": 0}) - 0.3) < 1e-10
    assert abs(f_norm.get_value({"X": 1}) - 0.7) < 1e-10
    print(" Factor normalization works")


def test_noisy_or():
    """Test the Noisy-OR computation."""
    print("=" * 60)
    print("TEST 3: Noisy-OR Model")
    print("=" * 60)

    # No active diseases: should return leak probability
    prob = compute_noisy_or_probability("Fever", [])
    print(f"   P(Fever | no diseases) = {prob:.4f} (expected ~leak={LEAK_PROBABILITIES['Fever']})")
    assert abs(prob - LEAK_PROBABILITIES["Fever"]) < 1e-10
    print(" Noisy-OR with no diseases returns leak probability")

    # Single disease active
    prob_flu = compute_noisy_or_probability("Fever", ["Influenza"])
    print(f"   P(Fever | Influenza) = {prob_flu:.4f}")
    assert prob_flu > LEAK_PROBABILITIES["Fever"]
    print(" Noisy-OR with one disease increases probability")

    # Multiple diseases: should be higher
    prob_multi = compute_noisy_or_probability("Fever", ["Influenza", "COVID19"])
    print(f"   P(Fever | Influenza, COVID19) = {prob_multi:.4f}")
    assert prob_multi > prob_flu
    print(" Noisy-OR: multiple diseases increase probability further")


def test_bayesian_network_diagnosis():
    """Test the full Bayesian Network diagnosis pipeline."""
    print("=" * 60)
    print("TEST 4: Bayesian Network Diagnosis")
    print("=" * 60)

    bn = BayesianNetwork()

    # Test Case 1: Classic flu symptoms
    print("\n Case 1: Fever + Cough + Headache + Muscle Pain + Fatigue + Chills")
    result = bn.diagnose({
        "Fever": True,
        "Cough": True,
        "Headache": True,
        "Muscle_Pain": True,
        "Fatigue": True,
        "Chills": True,
        "Runny_Nose": False,
        "Sneezing": False,
    })
    print(f"   Most likely: {result['most_likely']} ({result['most_likely_vi']})")
    for d in result["diagnoses"]:
        print(f"   • {d['disease']:25s} P={d['probability']:.4f}")
    print(" Case 1 completed")

    # Test Case 2: COVID-19 signature (loss of taste/smell)
    print("\n Case 2: Fever + Cough + Loss of Taste/Smell + Fatigue")
    result2 = bn.diagnose({
        "Fever": True,
        "Cough": True,
        "Loss_of_Taste_Smell": True,
        "Fatigue": True,
        "Dry_Cough": True,
    })
    print(f"   Most likely: {result2['most_likely']} ({result2['most_likely_vi']})")
    for d in result2["diagnoses"]:
        print(f"   • {d['disease']:25s} P={d['probability']:.4f}")
    print(" Case 2 completed")

    # Test Case 3: Common cold symptoms
    print("\n Case 3: Runny Nose + Sneezing + Sore Throat + mild Cough")
    result3 = bn.diagnose({
        "Runny_Nose": True,
        "Sneezing": True,
        "Sore_Throat": True,
        "Cough": True,
        "Fever": False,
        "Shortness_of_Breath": False,
    })
    print(f"   Most likely: {result3['most_likely']} ({result3['most_likely_vi']})")
    for d in result3["diagnoses"]:
        print(f"   • {d['disease']:25s} P={d['probability']:.4f}")
    print(" Case 3 completed")

    # Test Case 4: TB suspicion (chronic cough, night sweats, weight loss)
    print("\n Case 4: Cough + Night Sweats + Weight Loss + Hemoptysis + Fatigue")
    result4 = bn.diagnose({
        "Cough": True,
        "Night_Sweats": True,
        "Weight_Loss": True,
        "Hemoptysis": True,
        "Fatigue": True,
        "Fever": True,
    })
    print(f"   Most likely: {result4['most_likely']} ({result4['most_likely_vi']})")
    for d in result4["diagnoses"]:
        print(f"   • {d['disease']:25s} P={d['probability']:.4f}")
    print(" Case 4 completed")


def test_risk_factors():
    """Test risk factor adjustments."""
    print("=" * 60)
    print("TEST 5: Risk Factor Adjustments")
    print("=" * 60)

    base_priors = get_adjusted_priors()
    smoker_priors = get_adjusted_priors(["Smoking"])
    elderly_priors = get_adjusted_priors(["Elderly"])
    tb_contact_priors = get_adjusted_priors(["Close_Contact_TB"])

    print("   Base priors:")
    for d, p in base_priors.items():
        print(f"      {d:25s} {p:.4f}")

    print("\n   Smoker priors:")
    for d, p in smoker_priors.items():
        print(f"      {d:25s} {p:.4f}")

    print("\n   TB contact priors:")
    for d, p in tb_contact_priors.items():
        print(f"      {d:25s} {p:.4f}")

    # TB should be much higher with close contact
    assert tb_contact_priors["Tuberculosis"] > base_priors["Tuberculosis"]
    print("\n Risk factors correctly modify priors")


if __name__ == "__main__":
    test_knowledge_base()
    print()
    test_factor_operations()
    print()
    test_noisy_or()
    print()
    test_risk_factors()
    print()
    test_bayesian_network_diagnosis()
    print()
    print("=" * 60)
    print(" ALL TESTS PASSED!")
    print("=" * 60)
