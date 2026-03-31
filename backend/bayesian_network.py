r"""
Bayesian Network for Medical Diagnostic Reasoning System.
==========================================================
Builds a Bayesian Network (DAG) from the Knowledge Base and provides
an interface for probabilistic inference via Variable Elimination.

Network Structure (Noisy-OR model):
    Disease_1  Disease_2  ...  Disease_n
       \         |             /
        \        |            /
         v       v           v
          Symptom (Noisy-OR gate)
"""


from backend.knowledge_base import (
    DISEASES, SYMPTOMS, RISK_FACTORS,
    PRIOR_PROBABILITIES, SENSITIVITY, SPECIFICITY,
    LEAK_PROBABILITIES, _DISEASE_ORDER,
    get_adjusted_priors
)
from backend.factor import (
    Factor, create_prior_factor, create_symptom_factor,
    factor_product, factor_marginalize, factor_reduce, normalize
)


class BayesianNetwork:
    """
    Bayesian Network for medical diagnosis.

    Structure:
        - Disease nodes (root nodes with prior probabilities)
        - Symptom nodes (child nodes with Noisy-OR CPTs)
        - Risk factor nodes optionally modify priors

    The network encodes the causal relationships:
        Disease → Symptom (each disease can independently cause symptoms)
    """

    def __init__(self, risk_factors: list = None):
        """
        Initialize the Bayesian Network with the Knowledge Base data.

        Args:
            risk_factors: Optional list of active risk factor names
                         to adjust prior probabilities
        """
        self.diseases = list(DISEASES.keys())
        self.symptoms = list(SYMPTOMS.keys())
        self.risk_factors = risk_factors or []

        # Get (possibly adjusted) prior probabilities
        self.priors = get_adjusted_priors(self.risk_factors)

        # Build the network structure
        self._build_network()

    def _build_network(self):
        """Build all factors (CPTs) for the network."""
        self.factors = []

        # 1. Prior factors for each disease
        self.prior_factors = {}
        for disease in self.diseases:
            prior = self.priors[disease]
            f = create_prior_factor(disease, prior)
            self.prior_factors[disease] = f
            self.factors.append(f)

        # 2. Symptom CPT factors (Noisy-OR)
        self.symptom_factors = {}
        for symptom in self.symptoms:
            if symptom in SENSITIVITY:
                sens_values = SENSITIVITY[symptom]
                leak = LEAK_PROBABILITIES.get(symptom, 0.01)

                # Parent diseases for this symptom (all diseases)
                f = create_symptom_factor(
                    symptom=symptom,
                    parent_diseases=self.diseases,
                    sensitivity_values=sens_values,
                    leak_prob=leak
                )
                self.symptom_factors[symptom] = f
                self.factors.append(f)

    def get_all_factors(self) -> list:
        """Return all factors in the network."""
        return list(self.factors)

    def get_network_info(self) -> dict:
        """
        Return information about the network structure.

        Returns:
            dict with network statistics and structure info
        """
        return {
            "num_diseases": len(self.diseases),
            "num_symptoms": len(self.symptoms),
            "num_factors": len(self.factors),
            "diseases": self.diseases,
            "symptoms": self.symptoms,
            "risk_factors": self.risk_factors,
            "priors": self.priors,
            "structure": "Noisy-OR Bayesian Network",
            "edges": [
                {"from": d, "to": s}
                for d in self.diseases
                for s in self.symptoms
            ]
        }

    def query(self, query_variables: list, evidence: dict,
              elimination_order: list = None) -> dict:
        """
        Perform probabilistic inference using Variable Elimination.

        Args:
            query_variables: List of variables to query (e.g., disease names)
            evidence: dict mapping variable name -> observed value (0 or 1)
                     Example: {"Fever": 1, "Cough": 1, "Runny_Nose": 0}
            elimination_order: Optional custom elimination order.
                              If None, uses min-neighbors heuristic.

        Returns:
            dict: Results with posterior probabilities for each query variable
        """
        from backend.variable_elimination import variable_elimination

        return variable_elimination(
            factors=self.get_all_factors(),
            query_variables=query_variables,
            evidence=evidence,
            elimination_order=elimination_order
        )

    def diagnose(self, observed_symptoms: dict,
                 risk_factors: list = None) -> dict:
        """
        High-level diagnostic function.

        Args:
            observed_symptoms: dict mapping symptom name -> bool (True/False)
                             Example: {"Fever": True, "Cough": True}
            risk_factors: Optional list of risk factors to consider

        Returns:
            dict with:
                - diagnoses: list of {disease, probability} sorted by probability
                - evidence_used: list of symptoms used as evidence
                - most_likely: name of the most likely disease
                - risk_factors: list of risk factors considered
        """
        # If new risk factors provided, rebuild network
        if risk_factors and set(risk_factors) != set(self.risk_factors):
            self.risk_factors = risk_factors
            self.priors = get_adjusted_priors(self.risk_factors)
            self._build_network()

        # Convert boolean symptoms to evidence format (1=True, 0=False)
        evidence = {}
        for symptom, is_present in observed_symptoms.items():
            if symptom in self.symptoms:
                evidence[symptom] = 1 if is_present else 0

        # Query all diseases given the evidence
        results = []
        for disease in self.diseases:
            try:
                result = self.query(
                    query_variables=[disease],
                    evidence=evidence
                )
                # P(Disease=True | Evidence)
                prob = result.get(disease, {}).get(1, 0.0)
                results.append({
                    "disease": disease,
                    "disease_vi": DISEASES[disease]["name_vi"],
                    "probability": round(prob, 4),
                    "description": DISEASES[disease]["description"],
                    "description_vi": DISEASES[disease].get("description_vi", ""),
                    "icd10": DISEASES[disease]["icd10"],
                    "category": DISEASES[disease]["category"],
                })
            except Exception as e:
                # Fallback: use prior if VE fails
                results.append({
                    "disease": disease,
                    "disease_vi": DISEASES[disease]["name_vi"],
                    "probability": round(self.priors[disease], 4),
                    "description": DISEASES[disease]["description"],
                    "description_vi": DISEASES[disease].get("description_vi", ""),
                    "icd10": DISEASES[disease]["icd10"],
                    "category": DISEASES[disease]["category"],
                    "note": f"Used prior (VE error: {str(e)})"
                })

        # Sort by probability (descending)
        results.sort(key=lambda x: x["probability"], reverse=True)

        # Identify which symptoms were used as evidence
        evidence_used = [s for s, v in observed_symptoms.items() if v and s in self.symptoms]

        return {
            "diagnoses": results,
            "evidence_used": evidence_used,
            "most_likely": results[0]["disease"] if results else None,
            "most_likely_vi": results[0]["disease_vi"] if results else None,
            "risk_factors": self.risk_factors,
            "num_evidence": len(evidence),
            "num_diseases": len(self.diseases),
        }
