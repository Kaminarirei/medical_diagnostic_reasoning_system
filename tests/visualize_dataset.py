"""
Dataset Visualization for Medical Diagnostic Reasoning System.
================================================================
Generates comprehensive charts showing the statistical distribution
of the knowledge base dataset.

Output: Saves all charts to the 'visualizations/' directory.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns

from backend.knowledge_base import (
    DISEASES, SYMPTOMS, RISK_FACTORS,
    PRIOR_PROBABILITIES, SENSITIVITY, SPECIFICITY,
    LEAK_PROBABILITIES, _DISEASE_ORDER, RISK_FACTOR_MODIFIERS,
    compute_noisy_or_probability
)

# Output directory
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "visualizations")
os.makedirs(OUT_DIR, exist_ok=True)

# Style settings
plt.style.use('seaborn-v0_8-whitegrid')
DISEASE_COLORS = ['#2196F3', '#F44336', '#FF9800', '#4CAF50', '#9C27B0', '#00BCD4', '#795548']
DISEASE_SHORT = {
    'Influenza': 'Flu',
    'COVID19': 'COVID-19',
    'Bacterial_Pneumonia': 'Pneumonia',
    'Acute_Bronchitis': 'Bronchitis',
    'Common_Cold': 'Cold',
    'Pertussis': 'Pertussis',
    'Tuberculosis': 'TB',
}


def plot_1_prior_probabilities():
    """Chart 1: Prior Probabilities P(Disease) — Bar chart."""
    fig, ax = plt.subplots(figsize=(10, 6))

    diseases = list(PRIOR_PROBABILITIES.keys())
    priors = list(PRIOR_PROBABILITIES.values())
    short_names = [DISEASE_SHORT[d] for d in diseases]
    vi_names = [DISEASES[d]['name_vi'] for d in diseases]

    bars = ax.bar(range(len(diseases)), priors, color=DISEASE_COLORS, edgecolor='white', linewidth=1.5)

    # Add value labels
    for bar, val in zip(bars, priors):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.005,
                f'{val:.0%}', ha='center', va='bottom', fontweight='bold', fontsize=11)

    ax.set_xticks(range(len(diseases)))
    ax.set_xticklabels([f'{s}\n({v})' for s, v in zip(short_names, vi_names)],
                        fontsize=9, ha='center')
    ax.set_ylabel('Prior Probability P(Disease)', fontsize=12)
    ax.set_title('Prior Probabilities of Diseases\n(Xac suat tien nghiem cua benh)', fontsize=14, fontweight='bold')
    ax.set_ylim(0, max(priors) * 1.25)

    # Add annotation
    ax.text(0.98, 0.95, 'Source: CDC, WHO\nEpidemiological Data',
            transform=ax.transAxes, ha='right', va='top',
            fontsize=8, fontstyle='italic', color='gray',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

    plt.tight_layout()
    path = os.path.join(OUT_DIR, '01_prior_probabilities.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {path}")


def plot_2_sensitivity_heatmap():
    """Chart 2: Sensitivity Heatmap P(Symptom | Disease)."""
    fig, ax = plt.subplots(figsize=(14, 10))

    symptoms = list(SENSITIVITY.keys())
    diseases = _DISEASE_ORDER
    short_diseases = [DISEASE_SHORT[d] for d in diseases]

    # Build matrix
    matrix = np.array([SENSITIVITY[s] for s in symptoms])

    # Vietnamese symptom names
    symptom_labels = [f"{s.replace('_', ' ')} ({SYMPTOMS[s]['name_vi']})" for s in symptoms]

    sns.heatmap(matrix, annot=True, fmt='.2f', cmap='YlOrRd',
                xticklabels=short_diseases,
                yticklabels=symptom_labels,
                ax=ax, linewidths=0.5, linecolor='white',
                vmin=0, vmax=1,
                cbar_kws={'label': 'P(Symptom | Disease)', 'shrink': 0.8})

    ax.set_title('Sensitivity Matrix: P(Symptom = True | Disease = True)\nDo nhay: Kha nang benh gay ra trieu chung',
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Diseases', fontsize=12)
    ax.set_ylabel('Symptoms', fontsize=12)

    plt.tight_layout()
    path = os.path.join(OUT_DIR, '02_sensitivity_heatmap.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {path}")


def plot_3_specificity_heatmap():
    """Chart 3: Specificity Heatmap P(~Symptom | ~Disease)."""
    fig, ax = plt.subplots(figsize=(14, 10))

    symptoms = list(SPECIFICITY.keys())
    diseases = _DISEASE_ORDER
    short_diseases = [DISEASE_SHORT[d] for d in diseases]

    matrix = np.array([SPECIFICITY[s] for s in symptoms])

    symptom_labels = [f"{s.replace('_', ' ')} ({SYMPTOMS[s]['name_vi']})" for s in symptoms]

    sns.heatmap(matrix, annot=True, fmt='.2f', cmap='YlGnBu',
                xticklabels=short_diseases,
                yticklabels=symptom_labels,
                ax=ax, linewidths=0.5, linecolor='white',
                vmin=0, vmax=1,
                cbar_kws={'label': 'P(~Symptom | ~Disease)', 'shrink': 0.8})

    ax.set_title('Specificity Matrix: P(Symptom = False | Disease = False)\nDo dac hieu: Kha nang khong co trieu chung khi khong co benh',
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('Diseases', fontsize=12)
    ax.set_ylabel('Symptoms', fontsize=12)

    plt.tight_layout()
    path = os.path.join(OUT_DIR, '03_specificity_heatmap.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {path}")


def plot_4_leak_probabilities():
    """Chart 4: Leak Probabilities — Horizontal bar chart."""
    fig, ax = plt.subplots(figsize=(10, 8))

    symptoms = list(LEAK_PROBABILITIES.keys())
    leaks = list(LEAK_PROBABILITIES.values())

    # Sort by leak probability
    sorted_pairs = sorted(zip(symptoms, leaks), key=lambda x: x[1], reverse=True)
    symptoms_sorted = [p[0] for p in sorted_pairs]
    leaks_sorted = [p[1] for p in sorted_pairs]

    colors = plt.cm.RdYlGn_r(np.array(leaks_sorted) / max(leaks_sorted) * 0.8 + 0.1)

    y_pos = range(len(symptoms_sorted))
    bars = ax.barh(y_pos, leaks_sorted, color=colors, edgecolor='white', height=0.7)

    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, leaks_sorted)):
        ax.text(val + 0.002, i, f'{val:.1%}', va='center', fontsize=9)

    labels = [f"{s.replace('_', ' ')} ({SYMPTOMS[s]['name_vi']})" for s in symptoms_sorted]
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel('Leak Probability (P_leak)', fontsize=12)
    ax.set_title('Noisy-OR Leak Probabilities\nXac suat ro ri (nguyen nhan chua duoc mo hinh hoa)',
                 fontsize=14, fontweight='bold')
    ax.invert_yaxis()

    plt.tight_layout()
    path = os.path.join(OUT_DIR, '04_leak_probabilities.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {path}")


def plot_5_disease_symptom_profiles():
    """Chart 5: Radar/Spider chart — Symptom profiles for each disease."""
    symptoms_for_radar = [
        'Fever', 'Cough', 'Shortness_of_Breath', 'Sore_Throat',
        'Runny_Nose', 'Headache', 'Muscle_Pain', 'Fatigue',
        'Chills', 'Night_Sweats'
    ]

    N = len(symptoms_for_radar)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]  # Close the polygon

    fig, axes = plt.subplots(2, 4, figsize=(20, 10), subplot_kw=dict(polar=True))
    axes = axes.flatten()

    for idx, disease in enumerate(_DISEASE_ORDER):
        ax = axes[idx]
        values = [SENSITIVITY[s][idx] for s in symptoms_for_radar]
        values += values[:1]

        ax.fill(angles, values, alpha=0.25, color=DISEASE_COLORS[idx])
        ax.plot(angles, values, 'o-', color=DISEASE_COLORS[idx], linewidth=2, markersize=4)

        ax.set_xticks(angles[:-1])
        short_labels = [s.replace('_', '\n') for s in symptoms_for_radar]
        ax.set_xticklabels(short_labels, fontsize=7)
        ax.set_ylim(0, 1)
        ax.set_title(f"{DISEASE_SHORT[disease]}\n({DISEASES[disease]['name_vi']})",
                     fontsize=11, fontweight='bold', pad=15)

    # Hide the extra subplot
    axes[7].set_visible(False)

    fig.suptitle('Disease Symptom Profiles (Sensitivity)\nHo so trieu chung cua tung benh',
                 fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    path = os.path.join(OUT_DIR, '05_disease_symptom_profiles.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {path}")


def plot_6_risk_factor_impact():
    """Chart 6: Risk Factor Impact — Grouped bar chart."""
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    axes = axes.flatten()

    risk_factors = list(RISK_FACTOR_MODIFIERS.keys())
    diseases = _DISEASE_ORDER
    short_diseases = [DISEASE_SHORT[d] for d in diseases]

    for idx, rf in enumerate(risk_factors):
        ax = axes[idx]
        modifiers = [RISK_FACTOR_MODIFIERS[rf].get(d, 1.0) for d in diseases]

        bars = ax.bar(range(len(diseases)), modifiers, color=DISEASE_COLORS,
                      edgecolor='white', linewidth=1)

        # Reference line at 1.0 (no effect)
        ax.axhline(y=1.0, color='red', linestyle='--', linewidth=1, alpha=0.7)

        for bar, val in zip(bars, modifiers):
            if val > 1.0:
                ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.05,
                        f'{val:.1f}x', ha='center', va='bottom', fontsize=8, fontweight='bold')

        ax.set_xticks(range(len(diseases)))
        ax.set_xticklabels(short_diseases, fontsize=8, rotation=30)
        ax.set_ylabel('Multiplier', fontsize=10)
        ax.set_title(f"{rf.replace('_', ' ')}\n({RISK_FACTORS[rf]['name_vi']})",
                     fontsize=11, fontweight='bold')
        ax.set_ylim(0, max(modifiers) * 1.3)

    fig.suptitle('Risk Factor Impact on Prior Probabilities\nAnh huong cua yeu to nguy co len xac suat mac benh',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    path = os.path.join(OUT_DIR, '06_risk_factor_impact.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {path}")


def plot_7_symptom_discriminative_power():
    """Chart 7: How well each symptom discriminates between diseases."""
    fig, ax = plt.subplots(figsize=(12, 8))

    symptoms = list(SENSITIVITY.keys())

    # Compute discriminative power = max(sensitivity) - min(sensitivity) across diseases
    discriminative = []
    for s in symptoms:
        vals = SENSITIVITY[s]
        discriminative.append(max(vals) - min(vals))

    # Sort
    sorted_pairs = sorted(zip(symptoms, discriminative), key=lambda x: x[1], reverse=True)
    symptoms_sorted = [p[0] for p in sorted_pairs]
    disc_sorted = [p[1] for p in sorted_pairs]

    colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(symptoms_sorted)))

    y_pos = range(len(symptoms_sorted))
    bars = ax.barh(y_pos, disc_sorted, color=colors, edgecolor='white', height=0.7)

    for i, (bar, val) in enumerate(zip(bars, disc_sorted)):
        ax.text(val + 0.005, i, f'{val:.2f}', va='center', fontsize=9)

    labels = [f"{s.replace('_', ' ')} ({SYMPTOMS[s]['name_vi']})" for s in symptoms_sorted]
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel('Discriminative Power (max - min sensitivity)', fontsize=12)
    ax.set_title('Symptom Discriminative Power\nKha nang phan biet benh cua tung trieu chung\n(Higher = Better at distinguishing diseases)',
                 fontsize=13, fontweight='bold')
    ax.invert_yaxis()

    plt.tight_layout()
    path = os.path.join(OUT_DIR, '07_symptom_discriminative_power.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {path}")


def plot_8_noisy_or_demo():
    """Chart 8: Noisy-OR demonstration — how probabilities combine."""
    fig, ax = plt.subplots(figsize=(12, 7))

    symptom = "Fever"
    diseases_to_add = ["Common_Cold", "Acute_Bronchitis", "COVID19", "Influenza", "Bacterial_Pneumonia"]
    short_names = [DISEASE_SHORT[d] for d in diseases_to_add]

    # Compute cumulative Noisy-OR probabilities
    active = []
    probs = [LEAK_PROBABILITIES[symptom]]  # Start with leak only
    labels = ["Leak only\n(No disease)"]

    for d in diseases_to_add:
        active.append(d)
        prob = compute_noisy_or_probability(symptom, active)
        probs.append(prob)
        labels.append(f"+ {DISEASE_SHORT[d]}")

    x = range(len(probs))
    bars = ax.bar(x, probs, color=['gray'] + DISEASE_COLORS[:len(diseases_to_add)],
                  edgecolor='white', linewidth=1.5)

    for bar, val in zip(bars, probs):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.01,
                f'{val:.1%}', ha='center', va='bottom', fontweight='bold', fontsize=10)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9, rotation=15)
    ax.set_ylabel('P(Fever = True)', fontsize=12)
    ax.set_title('Noisy-OR Model: How Multiple Diseases Combine\nMo hinh Noisy-OR: Xac suat sot khi cong don nhieu benh',
                 fontsize=14, fontweight='bold')
    ax.set_ylim(0, 1.1)

    # Add formula annotation
    ax.text(0.5, 0.02,
            r'$P(S|D_1,...,D_n) = 1 - (1-p_{leak}) \times \prod_{D_i=True} (1-p_i)$',
            transform=ax.transAxes, ha='center', va='bottom',
            fontsize=12, fontstyle='italic',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9))

    plt.tight_layout()
    path = os.path.join(OUT_DIR, '08_noisy_or_demo.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {path}")


def plot_9_dataset_summary_table():
    """Chart 9: Summary statistics table as a figure."""
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.axis('off')

    # Build summary data
    rows = []
    for d in _DISEASE_ORDER:
        idx = _DISEASE_ORDER.index(d)
        sens_vals = [SENSITIVITY[s][idx] for s in SENSITIVITY]
        spec_vals = [SPECIFICITY[s][idx] for s in SPECIFICITY]

        rows.append([
            DISEASE_SHORT[d],
            DISEASES[d]['name_vi'],
            f"{PRIOR_PROBABILITIES[d]:.0%}",
            f"{np.mean(sens_vals):.2f}",
            f"{np.median(sens_vals):.2f}",
            f"{np.std(sens_vals):.2f}",
            f"{np.mean(spec_vals):.2f}",
            f"{np.median(spec_vals):.2f}",
            f"{np.std(spec_vals):.2f}",
        ])

    headers = ['Disease', 'Ten benh', 'Prior',
               'Sens Mean', 'Sens Med', 'Sens Std',
               'Spec Mean', 'Spec Med', 'Spec Std']

    table = ax.table(
        cellText=rows,
        colLabels=headers,
        cellLoc='center',
        loc='center',
        colColours=['#E3F2FD'] * len(headers),
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.0, 1.8)

    # Style header
    for j in range(len(headers)):
        table[0, j].set_text_props(fontweight='bold')
        table[0, j].set_facecolor('#1976D2')
        table[0, j].set_text_props(color='white', fontweight='bold')

    # Alternate row colors
    for i in range(len(rows)):
        color = '#F5F5F5' if i % 2 == 0 else 'white'
        for j in range(len(headers)):
            table[i+1, j].set_facecolor(color)

    ax.set_title('Dataset Statistical Summary\nTom tat thong ke dataset',
                 fontsize=16, fontweight='bold', pad=30)

    plt.tight_layout()
    path = os.path.join(OUT_DIR, '09_dataset_summary.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {path}")


def plot_10_bayesian_network_structure():
    """Chart 10: Network structure visualization."""
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_xlim(-1, 11)
    ax.set_ylim(-1, 8)
    ax.axis('off')

    # Disease positions (top row)
    disease_x = np.linspace(1, 9, 7)
    disease_y = 7.0

    # Symptom positions (bottom row, spread out)
    symptom_keys = list(SYMPTOMS.keys())
    n_symptoms = len(symptom_keys)
    symptom_x = np.linspace(0.5, 9.5, n_symptoms)
    symptom_y = 1.0

    # Draw edges (connections)
    for i, disease in enumerate(_DISEASE_ORDER):
        for j, symptom in enumerate(symptom_keys):
            sens = SENSITIVITY[symptom][i]
            if sens >= 0.3:  # Only draw significant connections
                alpha = min(sens * 0.8, 0.6)
                width = sens * 2
                ax.plot([disease_x[i], symptom_x[j]],
                        [disease_y - 0.4, symptom_y + 0.3],
                        color=DISEASE_COLORS[i], alpha=alpha,
                        linewidth=width, zorder=1)

    # Draw disease nodes
    for i, disease in enumerate(_DISEASE_ORDER):
        circle = plt.Circle((disease_x[i], disease_y), 0.35,
                            color=DISEASE_COLORS[i], zorder=3, ec='white', linewidth=2)
        ax.add_patch(circle)
        ax.text(disease_x[i], disease_y, DISEASE_SHORT[disease],
                ha='center', va='center', fontsize=8, fontweight='bold',
                color='white', zorder=4)
        ax.text(disease_x[i], disease_y + 0.55,
                f'P={PRIOR_PROBABILITIES[disease]:.0%}',
                ha='center', va='bottom', fontsize=7, color='gray')

    # Draw symptom nodes
    for j, symptom in enumerate(symptom_keys):
        rect = plt.Rectangle((symptom_x[j] - 0.25, symptom_y - 0.2), 0.5, 0.4,
                             color='#E8EAF6', zorder=3, ec='#3F51B5', linewidth=1.5,
                             joinstyle='round')
        ax.add_patch(rect)
        short_s = symptom.replace('_', '\n')[:12]
        ax.text(symptom_x[j], symptom_y, short_s,
                ha='center', va='center', fontsize=5.5, zorder=4)

    # Labels
    ax.text(5, 7.8, 'DISEASE NODES (Nut benh)', ha='center', fontsize=13,
            fontweight='bold', color='#1565C0')
    ax.text(5, 0.3, 'SYMPTOM NODES (Nut trieu chung)', ha='center', fontsize=13,
            fontweight='bold', color='#3F51B5')
    ax.text(5, -0.3, 'Line thickness = Sensitivity P(S|D). Only connections with P >= 0.3 are shown.',
            ha='center', fontsize=9, fontstyle='italic', color='gray')

    ax.set_title('Bayesian Network Structure (DAG)\nCau truc Mang Bayesian',
                 fontsize=16, fontweight='bold', pad=15)

    plt.tight_layout()
    path = os.path.join(OUT_DIR, '10_network_structure.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {path}")


if __name__ == "__main__":
    print("=" * 60)
    print("Generating Dataset Visualizations...")
    print("=" * 60)

    plot_1_prior_probabilities()
    plot_2_sensitivity_heatmap()
    plot_3_specificity_heatmap()
    plot_4_leak_probabilities()
    plot_5_disease_symptom_profiles()
    plot_6_risk_factor_impact()
    plot_7_symptom_discriminative_power()
    plot_8_noisy_or_demo()
    plot_9_dataset_summary_table()
    plot_10_bayesian_network_structure()

    print(f"\nAll 10 charts saved to: {OUT_DIR}")
    print("Done!")
