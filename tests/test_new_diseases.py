"""Quick test for new diseases."""
from backend.bayesian_network import BayesianNetwork

bn = BayesianNetwork()

# Test 1: Allergic Rhinitis typical symptoms
print("=== Test 1: Allergic Rhinitis symptoms ===")
r = bn.diagnose({"Runny_Nose": True, "Sneezing": True, "Itchy_Eyes": True})
print(f"Top: {r['most_likely']} ({r['most_likely_vi']})")
for d in r["diagnoses"][:5]:
    print(f"  {d['disease_vi']:25s} {d['probability']*100:6.2f}%")

# Test 2: Asthma Exacerbation typical symptoms
print("\n=== Test 2: Asthma Exacerbation symptoms ===")
r = bn.diagnose({"Wheezing": True, "Shortness_of_Breath": True, "Dry_Cough": True, "Chest_Pain": True})
print(f"Top: {r['most_likely']} ({r['most_likely_vi']})")
for d in r["diagnoses"][:5]:
    print(f"  {d['disease_vi']:25s} {d['probability']*100:6.2f}%")

# Test 3: Laryngitis typical symptoms
print("\n=== Test 3: Laryngitis symptoms ===")
r = bn.diagnose({"Hoarseness": True, "Sore_Throat": True, "Dry_Cough": True})
print(f"Top: {r['most_likely']} ({r['most_likely_vi']})")
for d in r["diagnoses"][:5]:
    print(f"  {d['disease_vi']:25s} {d['probability']*100:6.2f}%")

# Test 4: Original Influenza test still works
print("\n=== Test 4: Influenza (regression) ===")
r = bn.diagnose({"Fever": True, "High_Fever": True, "Muscle_Pain": True, "Fatigue": True, "Chills": True, "Headache": True})
print(f"Top: {r['most_likely']} ({r['most_likely_vi']})")
for d in r["diagnoses"][:5]:
    print(f"  {d['disease_vi']:25s} {d['probability']*100:6.2f}%")

# Test 5: COVID-19 (regression)
print("\n=== Test 5: COVID-19 (regression) ===")
r = bn.diagnose({"Fever": True, "Dry_Cough": True, "Loss_of_Taste_Smell": True, "Fatigue": True})
print(f"Top: {r['most_likely']} ({r['most_likely_vi']})")
for d in r["diagnoses"][:5]:
    print(f"  {d['disease_vi']:25s} {d['probability']*100:6.2f}%")

# Test 6: Common Cold (regression)
print("\n=== Test 6: Common Cold (regression) ===")
r = bn.diagnose({"Runny_Nose": True, "Sneezing": True, "Sore_Throat": True, "Cough": True})
print(f"Top: {r['most_likely']} ({r['most_likely_vi']})")
for d in r["diagnoses"][:5]:
    print(f"  {d['disease_vi']:25s} {d['probability']*100:6.2f}%")

# Test 7: TB (regression)
print("\n=== Test 7: TB (regression) ===")
r = bn.diagnose({"Cough": True, "Night_Sweats": True, "Weight_Loss": True, "Hemoptysis": True, "Fatigue": True})
print(f"Top: {r['most_likely']} ({r['most_likely_vi']})")
for d in r["diagnoses"][:5]:
    print(f"  {d['disease_vi']:25s} {d['probability']*100:6.2f}%")
