"""
Variable Elimination Algorithm for Bayesian Network Inference.
================================================================
Implements the Variable Elimination (VE) algorithm to compute
posterior probabilities P(Query | Evidence) in a Bayesian Network.

Algorithm Steps:
1. Collect all factors from the Bayesian Network
2. Restrict factors based on observed evidence
3. Determine elimination ordering for hidden variables
4. For each hidden variable (in order):
   a. Collect all factors containing that variable
   b. Compute the product of these factors
   c. Marginalize (sum out) the hidden variable
   d. Add the resulting factor back to the pool
5. Multiply remaining factors and normalize

Reference: Koller & Friedman, "Probabilistic Graphical Models" (2009)
"""

from backend.factor import (
    Factor, factor_product, factor_marginalize, factor_reduce, normalize
)


def variable_elimination(factors: list, query_variables: list,
                         evidence: dict,
                         elimination_order: list = None) -> dict:
    """
    Perform Variable Elimination to compute P(Query | Evidence).

    Args:
        factors: List of Factor objects representing the Bayesian Network
        query_variables: Variables to compute posterior for
        evidence: dict mapping observed variable -> value (0 or 1)
        elimination_order: Optional order for eliminating hidden variables.
                          If None, uses min-degree heuristic.

    Returns:
        dict mapping each query variable -> {value: probability}
        Example: {"Flu": {0: 0.3, 1: 0.7}}
    """
    # Step 1: Deep copy factors to avoid modifying originals
    working_factors = [f.copy() for f in factors]

    # Step 2: Restrict factors based on evidence
    restricted_factors = []
    for factor in working_factors:
        restricted = factor
        for var, val in evidence.items():
            if var in restricted.variables:
                restricted = factor_reduce(restricted, var, val)
        restricted_factors.append(restricted)

    # Remove trivial factors (no variables, scalar)
    # Keep them as they contribute to the product
    working_factors = restricted_factors

    # Step 3: Determine hidden variables (not query, not evidence)
    all_vars = set()
    for f in working_factors:
        all_vars.update(f.variables)

    evidence_vars = set(evidence.keys())
    query_vars = set(query_variables)
    hidden_vars = all_vars - query_vars - evidence_vars

    # Step 4: Determine elimination ordering
    if elimination_order is None:
        elimination_order = _min_degree_order(working_factors, hidden_vars)
    else:
        elimination_order = [v for v in elimination_order if v in hidden_vars]

    # Step 5: Eliminate hidden variables one by one
    for var in elimination_order:
        # Collect factors containing this variable
        relevant = [f for f in working_factors if var in f.variables]
        remaining = [f for f in working_factors if var not in f.variables]

        if not relevant:
            continue

        # Product of all relevant factors
        product = relevant[0]
        for f in relevant[1:]:
            product = factor_product(product, f)

        # Marginalize the variable
        new_factor = factor_marginalize(product, var)

        # Update factor pool
        working_factors = remaining + [new_factor]

    # Step 6: Multiply all remaining factors
    if not working_factors:
        return {qv: {0: 0.5, 1: 0.5} for qv in query_variables}

    result_factor = working_factors[0]
    for f in working_factors[1:]:
        result_factor = factor_product(result_factor, f)

    # Step 7: Normalize and extract results
    result_factor = normalize(result_factor)

    # Extract posterior probabilities for each query variable
    results = {}
    for qv in query_variables:
        if qv in result_factor.variables:
            # Marginalize out other query variables if multiple
            temp_factor = result_factor
            for other_qv in query_variables:
                if other_qv != qv and other_qv in temp_factor.variables:
                    temp_factor = factor_marginalize(temp_factor, other_qv)

            temp_factor = normalize(temp_factor)
            results[qv] = {}
            for assignment in temp_factor.get_all_assignments():
                val = assignment[qv]
                results[qv][val] = temp_factor.get_value(assignment)
        else:
            # Variable was fully eliminated by evidence
            results[qv] = {0: 0.5, 1: 0.5}

    return results


def _min_degree_order(factors: list, variables: set) -> list:
    """
    Determine elimination order using the min-degree heuristic.

    The variable appearing in the fewest factors is eliminated first.
    This is a greedy heuristic that tends to minimize the size of
    intermediate factors, improving computational efficiency.

    Args:
        factors: List of current factors
        variables: Set of variables to order

    Returns:
        list: Elimination ordering (list of variable names)
    """
    order = []
    remaining_vars = set(variables)
    current_factors = list(factors)

    while remaining_vars:
        # Count factor appearances for each variable
        var_counts = {}
        for var in remaining_vars:
            count = sum(1 for f in current_factors if var in f.variables)
            var_counts[var] = count

        # Choose variable with minimum degree (fewest factors)
        min_var = min(var_counts, key=var_counts.get)
        order.append(min_var)
        remaining_vars.remove(min_var)

        # Simulate elimination to update factor counts
        relevant = [f for f in current_factors if min_var in f.variables]
        other = [f for f in current_factors if min_var not in f.variables]

        if relevant:
            # Compute the "result" variables (union minus eliminated var)
            result_vars = set()
            for f in relevant:
                result_vars.update(f.variables)
            result_vars.discard(min_var)

            # Create a placeholder factor for the simulated result
            if result_vars:
                placeholder = Factor(
                    list(result_vars),
                    [2] * len(result_vars)
                )
                current_factors = other + [placeholder]
            else:
                current_factors = other

    return order


def compute_marginal(factors: list, query_variable: str,
                     evidence: dict) -> dict:
    """
    Convenience function to compute the marginal posterior P(query | evidence).

    Args:
        factors: List of Factor objects
        query_variable: Single variable to query
        evidence: dict of observed evidence

    Returns:
        dict mapping value -> probability, e.g., {0: 0.3, 1: 0.7}
    """
    result = variable_elimination(
        factors=factors,
        query_variables=[query_variable],
        evidence=evidence
    )
    return result.get(query_variable, {0: 0.5, 1: 0.5})
