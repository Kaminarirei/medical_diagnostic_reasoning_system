"""
Factor class for Bayesian Network inference.
=============================================
A Factor is a function from a set of random variables to real numbers.
It is the fundamental data structure used in Variable Elimination.

Each factor stores:
- variables: list of variable names
- cardinalities: dict mapping variable -> number of possible values
- values: flat numpy array of factor values (row-major order)
"""

import numpy as np
from itertools import product as iter_product
from copy import deepcopy


class Factor:
    """
    Represents a factor (potential function) in a Bayesian Network.

    For binary variables (which is our case: True/False for each disease/symptom),
    cardinality = 2 for all variables.

    Example:
        Factor(["Flu", "Fever"], [2, 2], [0.17, 0.83, 0.40, 0.60])
        represents:
            Flu=0, Fever=0: 0.17
            Flu=0, Fever=1: 0.83
            Flu=1, Fever=0: 0.40
            Flu=1, Fever=1: 0.60
    """

    def __init__(self, variables: list, cardinalities: list, values: np.ndarray = None):
        """
        Initialize a Factor.

        Args:
            variables: List of variable names (strings)
            cardinalities: List of cardinalities for each variable
            values: Flat array of factor values. If None, initialized to zeros.
        """
        self.variables = list(variables)
        self.cardinalities = list(cardinalities)
        self.card_dict = dict(zip(self.variables, self.cardinalities))

        total_size = int(np.prod(cardinalities)) if cardinalities else 1

        if values is not None:
            self.values = np.array(values, dtype=np.float64).flatten()
            if len(self.values) != total_size:
                raise ValueError(
                    f"Expected {total_size} values for variables {variables} "
                    f"with cardinalities {cardinalities}, got {len(self.values)}"
                )
        else:
            self.values = np.zeros(total_size, dtype=np.float64)

    def __repr__(self):
        return (
            f"Factor(variables={self.variables}, "
            f"cardinalities={self.cardinalities}, "
            f"values={self.values})"
        )

    def _get_index(self, assignment: dict) -> int:
        """
        Convert a variable assignment dict to a flat array index.

        Args:
            assignment: dict mapping variable name -> value (0 or 1 for binary)

        Returns:
            int: Index into self.values
        """
        index = 0
        multiplier = 1
        for var, card in reversed(list(zip(self.variables, self.cardinalities))):
            val = assignment.get(var, 0)
            index += val * multiplier
            multiplier *= card
        return index

    def get_value(self, assignment: dict) -> float:
        """Get the factor value for a specific assignment."""
        return self.values[self._get_index(assignment)]

    def set_value(self, assignment: dict, value: float):
        """Set the factor value for a specific assignment."""
        self.values[self._get_index(assignment)] = value

    def get_all_assignments(self):
        """
        Generate all possible assignments for this factor's variables.

        Yields:
            dict mapping variable name -> value
        """
        ranges = [range(c) for c in self.cardinalities]
        for combo in iter_product(*ranges):
            yield dict(zip(self.variables, combo))

    def copy(self):
        """Return a deep copy of this factor."""
        return Factor(
            list(self.variables),
            list(self.cardinalities),
            self.values.copy()
        )


def factor_product(f1: Factor, f2: Factor) -> Factor:
    """
    Compute the product of two factors.

    The resulting factor has variables = union(f1.variables, f2.variables).
    For each assignment to these variables, the value is f1(assignment) * f2(assignment).

    Args:
        f1: First factor
        f2: Second factor

    Returns:
        Factor: Product factor
    """
    # Determine variables and cardinalities for the result
    result_vars = list(f1.variables)
    result_cards = list(f1.cardinalities)

    for var, card in zip(f2.variables, f2.cardinalities):
        if var not in result_vars:
            result_vars.append(var)
            result_cards.append(card)

    result = Factor(result_vars, result_cards)

    # Compute product values
    for assignment in result.get_all_assignments():
        val1 = f1.get_value(assignment)
        val2 = f2.get_value(assignment)
        result.set_value(assignment, val1 * val2)

    return result


def factor_marginalize(factor: Factor, variable: str) -> Factor:
    """
    Sum out (marginalize) a variable from the factor.

    P(X) = Σ_Y P(X, Y) — sums over all values of Y.

    Args:
        factor: The factor to marginalize
        variable: The variable to sum out

    Returns:
        Factor: New factor with the variable removed

    Raises:
        ValueError: If the variable is not in the factor
    """
    if variable not in factor.variables:
        raise ValueError(f"Variable '{variable}' not found in factor {factor.variables}")

    var_idx = factor.variables.index(variable)
    new_vars = [v for v in factor.variables if v != variable]
    new_cards = [c for v, c in zip(factor.variables, factor.cardinalities) if v != variable]

    if not new_vars:
        # Marginalizing the last variable -> scalar
        return Factor([], [], np.array([np.sum(factor.values)]))

    result = Factor(new_vars, new_cards)

    # Sum over all values of the marginalized variable
    for assignment in result.get_all_assignments():
        total = 0.0
        for val in range(factor.cardinalities[var_idx]):
            full_assignment = dict(assignment)
            full_assignment[variable] = val
            total += factor.get_value(full_assignment)
        result.set_value(assignment, total)

    return result


def factor_reduce(factor: Factor, variable: str, value: int) -> Factor:
    """
    Reduce (observe/condition on) a factor by setting a variable to a specific value.

    This removes the variable from the factor and keeps only the entries
    consistent with the observed value.

    Args:
        factor: The factor to reduce
        variable: The observed variable
        value: The observed value (0 = False, 1 = True for binary)

    Returns:
        Factor: Reduced factor without the observed variable
    """
    if variable not in factor.variables:
        # Variable not in this factor, return copy
        return factor.copy()

    new_vars = [v for v in factor.variables if v != variable]
    new_cards = [c for v, c in zip(factor.variables, factor.cardinalities) if v != variable]

    if not new_vars:
        # All variables observed -> scalar
        assignment = {variable: value}
        return Factor([], [], np.array([factor.get_value(assignment)]))

    result = Factor(new_vars, new_cards)

    for assignment in result.get_all_assignments():
        full_assignment = dict(assignment)
        full_assignment[variable] = value
        result.set_value(assignment, factor.get_value(full_assignment))

    return result


def normalize(factor: Factor) -> Factor:
    """
    Normalize a factor so that its values sum to 1.
    Returns a probability distribution.

    Args:
        factor: The factor to normalize

    Returns:
        Factor: Normalized factor (probability distribution)
    """
    result = factor.copy()
    total = np.sum(result.values)

    if total > 0:
        result.values = result.values / total
    else:
        # Uniform distribution if all zeros
        result.values = np.ones_like(result.values) / len(result.values)

    return result


# =============================================================================
# Convenience functions for building CPT factors from knowledge base
# =============================================================================

def create_prior_factor(disease: str, prior_prob: float) -> Factor:
    """
    Create a prior probability factor for a disease.
    P(Disease=0) = 1 - prior_prob
    P(Disease=1) = prior_prob

    Args:
        disease: Disease variable name
        prior_prob: Prior probability P(Disease=True)

    Returns:
        Factor representing the prior distribution
    """
    return Factor(
        [disease],
        [2],
        np.array([1.0 - prior_prob, prior_prob])
    )


def create_symptom_factor(symptom: str, parent_diseases: list,
                          sensitivity_values: list,
                          leak_prob: float) -> Factor:
    """
    Create a CPT factor for a symptom using the Noisy-OR model.

    P(S=1 | D1, ..., Dn) = 1 - (1 - p_leak) * Π_i (1 - p_i)^Di

    Where p_i is the sensitivity of disease i for this symptom,
    and Di ∈ {0, 1} indicates whether disease i is active.

    Args:
        symptom: Symptom variable name
        parent_diseases: List of disease variable names
        sensitivity_values: List of P(S|Di=1) for each parent disease
        leak_prob: Leak probability for unmodeled causes

    Returns:
        Factor representing the Noisy-OR CPT
    """
    all_vars = parent_diseases + [symptom]
    all_cards = [2] * len(all_vars)
    factor = Factor(all_vars, all_cards)

    # For each combination of parent disease states
    parent_ranges = [range(2)] * len(parent_diseases)
    for parent_combo in iter_product(*parent_ranges):
        parent_assignment = dict(zip(parent_diseases, parent_combo))

        # Compute Noisy-OR probability
        prob_not_symptom = 1.0 - leak_prob
        for disease, is_active, sensitivity in zip(
            parent_diseases, parent_combo, sensitivity_values
        ):
            if is_active == 1:
                prob_not_symptom *= (1.0 - sensitivity)

        prob_symptom = 1.0 - prob_not_symptom

        # Clamp to valid range
        prob_symptom = max(0.0, min(1.0, prob_symptom))

        # Set P(Symptom=0 | parents) and P(Symptom=1 | parents)
        assignment_false = dict(parent_assignment)
        assignment_false[symptom] = 0
        factor.set_value(assignment_false, 1.0 - prob_symptom)

        assignment_true = dict(parent_assignment)
        assignment_true[symptom] = 1
        factor.set_value(assignment_true, prob_symptom)

    return factor
