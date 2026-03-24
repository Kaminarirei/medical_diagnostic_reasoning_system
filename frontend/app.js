/**
 * MedDiag AI — Frontend Application Logic
 * ==========================================
 * Handles symptom selection, API communication,
 * and result visualization with Chart.js
 */

const API_BASE = '';  // Same origin

// ============================================================================
// STATE
// ============================================================================
let selectedSymptoms = {};
let selectedRiskFactors = [];
let probabilityChart = null;
let symptomsData = [];
let diseasesData = [];
let riskFactorsData = [];

// Disease color palette
const DISEASE_COLORS = {
    'Influenza':          { bg: 'rgba(33, 150, 243, 0.7)',  border: '#2196F3' },
    'COVID19':            { bg: 'rgba(244, 67, 54, 0.7)',   border: '#F44336' },
    'Bacterial_Pneumonia':{ bg: 'rgba(255, 152, 0, 0.7)',   border: '#FF9800' },
    'Acute_Bronchitis':   { bg: 'rgba(76, 175, 80, 0.7)',   border: '#4CAF50' },
    'Common_Cold':        { bg: 'rgba(156, 39, 176, 0.7)',  border: '#9C27B0' },
    'Pertussis':          { bg: 'rgba(0, 188, 212, 0.7)',   border: '#00BCD4' },
    'Tuberculosis':       { bg: 'rgba(121, 85, 72, 0.7)',   border: '#795548' },
};

// ============================================================================
// INITIALIZATION
// ============================================================================
document.addEventListener('DOMContentLoaded', async () => {
    try {
        await Promise.all([
            loadSymptoms(),
            loadRiskFactors(),
        ]);
        renderSymptoms();
        renderRiskFactors();
    } catch (error) {
        console.error('Failed to initialize:', error);
        showError('Không thể kết nối đến server. Hãy đảm bảo backend đang chạy.');
    }
});

async function loadSymptoms() {
    const response = await fetch(`${API_BASE}/api/symptoms`);
    symptomsData = await response.json();
}

async function loadRiskFactors() {
    const response = await fetch(`${API_BASE}/api/risk-factors`);
    riskFactorsData = await response.json();
}

// ============================================================================
// RENDER SYMPTOM UI
// ============================================================================
function renderSymptoms() {
    const categories = {};
    symptomsData.forEach(symptom => {
        if (!categories[symptom.type]) {
            categories[symptom.type] = [];
        }
        categories[symptom.type].push(symptom);
    });

    for (const [type, symptoms] of Object.entries(categories)) {
        const grid = document.getElementById(`symptoms-${type}`);
        if (!grid) continue;

        grid.innerHTML = '';
        symptoms.forEach(symptom => {
            const card = createSymptomCard(symptom);
            grid.appendChild(card);
        });
    }
}

function createSymptomCard(symptom) {
    const card = document.createElement('div');
    card.className = 'symptom-card';
    card.dataset.symptom = symptom.name;
    card.innerHTML = `
        <div class="toggle-dot"></div>
        <div class="symptom-label">
            <span class="name-vi">${symptom.name_vi}</span>
            <span class="name-en">${symptom.name.replace(/_/g, ' ')}</span>
        </div>
    `;

    card.addEventListener('click', () => toggleSymptom(card, symptom.name));
    return card;
}

function toggleSymptom(card, symptomName) {
    card.classList.toggle('active');

    if (card.classList.contains('active')) {
        selectedSymptoms[symptomName] = true;
    } else {
        delete selectedSymptoms[symptomName];
    }

    updateSelectedCount();
}

// ============================================================================
// RENDER RISK FACTORS
// ============================================================================
function renderRiskFactors() {
    const grid = document.getElementById('risk-factors-grid');
    grid.innerHTML = '';

    riskFactorsData.forEach(rf => {
        const card = document.createElement('div');
        card.className = 'symptom-card risk-card';
        card.dataset.riskfactor = rf.name;
        card.innerHTML = `
            <div class="toggle-dot"></div>
            <div class="symptom-label">
                <span class="name-vi">${rf.name_vi}</span>
                <span class="name-en">${rf.name.replace(/_/g, ' ')}</span>
            </div>
        `;

        card.addEventListener('click', () => toggleRiskFactor(card, rf.name));
        grid.appendChild(card);
    });
}

function toggleRiskFactor(card, rfName) {
    card.classList.toggle('active');

    if (card.classList.contains('active')) {
        selectedRiskFactors.push(rfName);
    } else {
        selectedRiskFactors = selectedRiskFactors.filter(r => r !== rfName);
    }
}

// ============================================================================
// SELECTED COUNT
// ============================================================================
function updateSelectedCount() {
    const count = Object.keys(selectedSymptoms).length;
    const countText = document.getElementById('count-text');

    if (count === 0) {
        countText.textContent = 'Chưa chọn triệu chứng nào';
    } else {
        countText.textContent = `Đã chọn ${count} triệu chứng`;
    }

    // Enable/disable diagnose button
    const btn = document.getElementById('btn-diagnose');
    btn.disabled = count === 0;
}

// ============================================================================
// DIAGNOSIS
// ============================================================================
async function runDiagnosis() {
    const symptomCount = Object.keys(selectedSymptoms).length;
    if (symptomCount === 0) return;

    // Build full symptom map (selected = true, unselected that we want to mark = false)
    const symptomMap = {};

    // Only send symptoms that the user explicitly toggled
    symptomsData.forEach(s => {
        if (selectedSymptoms[s.name]) {
            symptomMap[s.name] = true;
        }
    });

    // Show loading
    showLoading(true);

    try {
        const response = await fetch(`${API_BASE}/api/diagnose`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                symptoms: symptomMap,
                risk_factors: selectedRiskFactors.length > 0 ? selectedRiskFactors : null,
            }),
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Diagnosis failed');
        }

        const result = await response.json();
        displayResults(result);
    } catch (error) {
        console.error('Diagnosis error:', error);
        showError(`Lỗi chẩn đoán: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

// ============================================================================
// DISPLAY RESULTS
// ============================================================================
function displayResults(result) {
    // Hide placeholder, show results
    document.getElementById('results-placeholder').style.display = 'none';
    document.getElementById('results-content').style.display = 'block';

    // Top diagnosis
    const top = result.diagnoses[0];
    document.getElementById('top-disease-name').textContent = top.disease.replace(/_/g, ' ');
    document.getElementById('top-disease-vi').textContent = top.disease_vi;

    // Probability ring animation
    const prob = top.probability;
    const circumference = 2 * Math.PI * 52; // r=52
    const offset = circumference * (1 - prob);
    const ring = document.getElementById('prob-ring');
    ring.style.strokeDasharray = circumference;

    // Reset and animate
    ring.style.strokeDashoffset = circumference;
    requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            ring.style.strokeDashoffset = offset;
        });
    });

    // Color based on probability
    const ringColor = prob >= 0.7 ? '#10b981' : prob >= 0.4 ? '#f59e0b' : '#ef4444';
    ring.style.stroke = ringColor;
    document.getElementById('top-prob-text').textContent = `${(prob * 100).toFixed(1)}%`;
    document.getElementById('top-prob-text').style.color = ringColor;

    // Evidence tags
    const tagsContainer = document.getElementById('evidence-tags');
    tagsContainer.innerHTML = '';
    result.evidence_used.forEach(ev => {
        const symptom = symptomsData.find(s => s.name === ev);
        const tag = document.createElement('span');
        tag.className = 'evidence-tag';
        tag.textContent = symptom ? symptom.name_vi : ev.replace(/_/g, ' ');
        tagsContainer.appendChild(tag);
    });

    // Evidence count
    document.getElementById('evidence-count').textContent = result.num_evidence;

    // Chart
    renderProbabilityChart(result.diagnoses);

    // Disease list
    renderDiseaseList(result.diagnoses);

    // Scroll to results on mobile
    if (window.innerWidth <= 1024) {
        document.getElementById('results-panel').scrollIntoView({ behavior: 'smooth' });
    }
}

// ============================================================================
// CHART
// ============================================================================
function renderProbabilityChart(diagnoses) {
    const ctx = document.getElementById('probability-chart').getContext('2d');

    if (probabilityChart) {
        probabilityChart.destroy();
    }

    const labels = diagnoses.map(d => d.disease_vi);
    const data = diagnoses.map(d => (d.probability * 100).toFixed(1));
    const bgColors = diagnoses.map(d => DISEASE_COLORS[d.disease]?.bg || 'rgba(100,100,100,0.5)');
    const borderColors = diagnoses.map(d => DISEASE_COLORS[d.disease]?.border || '#666');

    probabilityChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Xác suất (%)',
                data: data,
                backgroundColor: bgColors,
                borderColor: borderColors,
                borderWidth: 2,
                borderRadius: 6,
                borderSkipped: false,
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 1000,
                easing: 'easeOutQuart',
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#1a2035',
                    borderColor: '#3b82f6',
                    borderWidth: 1,
                    titleFont: { family: 'Inter', weight: '600' },
                    bodyFont: { family: 'Inter' },
                    callbacks: {
                        label: ctx => `P(Disease|Evidence) = ${ctx.parsed.x}%`,
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    max: 100,
                    grid: { color: 'rgba(148,163,184,0.08)' },
                    ticks: {
                        color: '#94a3b8',
                        font: { family: 'Inter', size: 11 },
                        callback: val => val + '%',
                    }
                },
                y: {
                    grid: { display: false },
                    ticks: {
                        color: '#f1f5f9',
                        font: { family: 'Inter', size: 12, weight: '500' },
                    }
                }
            }
        }
    });
}

// ============================================================================
// DISEASE LIST
// ============================================================================
function renderDiseaseList(diagnoses) {
    const container = document.getElementById('diseases-list');
    container.innerHTML = '';

    diagnoses.forEach((d, index) => {
        const color = DISEASE_COLORS[d.disease]?.border || '#666';
        const prob = (d.probability * 100).toFixed(1);
        const rankClass = index < 3 ? `top-${index + 1}` : '';

        const row = document.createElement('div');
        row.className = 'disease-row animate-in';
        row.style.animationDelay = `${index * 0.08}s`;
        row.innerHTML = `
            <div class="disease-rank ${rankClass}">${index + 1}</div>
            <div class="disease-info">
                <div class="name">${d.disease.replace(/_/g, ' ')}</div>
                <div class="name-vi">${d.disease_vi}</div>
            </div>
            <div class="disease-prob">
                <div class="bar-wrap">
                    <div class="bar-fill" style="width: ${prob}%; background: ${color};"></div>
                </div>
                <span class="prob-text">${prob}%</span>
            </div>
        `;
        container.appendChild(row);
    });
}

// ============================================================================
// RESET
// ============================================================================
function resetForm() {
    // Clear selections
    selectedSymptoms = {};
    selectedRiskFactors = [];

    // Reset all cards
    document.querySelectorAll('.symptom-card').forEach(card => {
        card.classList.remove('active');
    });

    // Reset results
    document.getElementById('results-placeholder').style.display = 'flex';
    document.getElementById('results-content').style.display = 'none';

    if (probabilityChart) {
        probabilityChart.destroy();
        probabilityChart = null;
    }

    updateSelectedCount();
}

// ============================================================================
// UTILITIES
// ============================================================================
function showLoading(show) {
    document.getElementById('loading-overlay').style.display = show ? 'flex' : 'none';
}

function showError(message) {
    alert(message);  // Simple error for now
}

// ============================================================================
// THEME TOGGLE
// ============================================================================
function toggleTheme() {
    const body = document.body;
    const icon = document.getElementById('theme-icon');
    const isLight = body.classList.toggle('light-theme');

    icon.textContent = isLight ? 'dark_mode' : 'light_mode';
    localStorage.setItem('meddiag-theme', isLight ? 'light' : 'dark');

    // Update chart colors if chart exists
    if (probabilityChart) {
        const tickColor = isLight ? '#475569' : '#94a3b8';
        const labelColor = isLight ? '#0f172a' : '#f1f5f9';
        const gridColor = isLight ? 'rgba(15,23,42,0.06)' : 'rgba(148,163,184,0.08)';

        probabilityChart.options.scales.x.ticks.color = tickColor;
        probabilityChart.options.scales.y.ticks.color = labelColor;
        probabilityChart.options.scales.x.grid.color = gridColor;
        probabilityChart.update();
    }
}

// Restore saved theme on load
(function initTheme() {
    const saved = localStorage.getItem('meddiag-theme');
    if (saved === 'light') {
        document.body.classList.add('light-theme');
        const icon = document.getElementById('theme-icon');
        if (icon) icon.textContent = 'dark_mode';
    }
})();
