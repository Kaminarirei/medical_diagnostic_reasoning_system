/**
 * MedDiag AI — Frontend Application Logic
 * ==========================================
 * Features:
 *   - Symptom selection with search & staggered animations
 *   - Diagnosis with severity badges & expandable details
 *   - Toast notifications
 *   - Diagnosis history (localStorage, max 10)
 *   - Side-by-side comparison
 *   - Bayesian Network visualization (Canvas)
 *   - PDF export (html2pdf.js)
 *   - Keyboard shortcuts
 *   - Floating action bar
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
let lastDiagnosisResult = null;
let networkData = null;

// Disease color palette (10 diseases)
const DISEASE_COLORS = {
    'Influenza':           { bg: 'rgba(33, 150, 243, 0.7)',  border: '#2196F3' },
    'COVID19':             { bg: 'rgba(244, 67, 54, 0.7)',   border: '#F44336' },
    'Bacterial_Pneumonia': { bg: 'rgba(255, 152, 0, 0.7)',   border: '#FF9800' },
    'Acute_Bronchitis':    { bg: 'rgba(76, 175, 80, 0.7)',   border: '#4CAF50' },
    'Common_Cold':         { bg: 'rgba(156, 39, 176, 0.7)',  border: '#9C27B0' },
    'Pertussis':           { bg: 'rgba(0, 188, 212, 0.7)',   border: '#00BCD4' },
    'Tuberculosis':        { bg: 'rgba(121, 85, 72, 0.7)',   border: '#795548' },
    'Allergic_Rhinitis':   { bg: 'rgba(0, 150, 136, 0.7)',   border: '#009688' },
    'Asthma_Exacerbation': { bg: 'rgba(63, 81, 181, 0.7)',   border: '#3F51B5' },
    'Laryngitis':          { bg: 'rgba(233, 30, 99, 0.7)',   border: '#E91E63' },
};

// ============================================================================
// INITIALIZATION
// ============================================================================
document.addEventListener('DOMContentLoaded', async () => {
    try {
        // Show skeleton loading
        showSkeletonLoading();

        await Promise.all([
            loadSymptoms(),
            loadRiskFactors(),
        ]);
        renderSymptoms();
        renderRiskFactors();
        updateHistoryBadge();
        setupKeyboardShortcuts();
        setupSearchBar();
    } catch (error) {
        console.error('Failed to initialize:', error);
        showToast('Không thể kết nối đến server. Hãy đảm bảo backend đang chạy.', 'error');
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
// SKELETON LOADING
// ============================================================================
function showSkeletonLoading() {
    const categories = ['vital_sign', 'respiratory', 'upper_respiratory', 'systemic', 'neurological'];
    categories.forEach(cat => {
        const grid = document.getElementById(`symptoms-${cat}`);
        if (grid) {
            grid.innerHTML = Array(4).fill(0).map(() =>
                '<div class="skeleton skeleton-card"></div>'
            ).join('');
        }
    });
}

// ============================================================================
// RENDER SYMPTOM UI (with staggered animations)
// ============================================================================
function renderSymptoms() {
    const categories = {};
    symptomsData.forEach(symptom => {
        if (!categories[symptom.type]) {
            categories[symptom.type] = [];
        }
        categories[symptom.type].push(symptom);
    });

    let globalIndex = 0;
    for (const [type, symptoms] of Object.entries(categories)) {
        const grid = document.getElementById(`symptoms-${type}`);
        if (!grid) continue;

        grid.innerHTML = '';
        symptoms.forEach(symptom => {
            const card = createSymptomCard(symptom, globalIndex);
            grid.appendChild(card);
            globalIndex++;
        });
    }
}

function createSymptomCard(symptom, index) {
    const card = document.createElement('div');
    card.className = 'symptom-card';
    card.dataset.symptom = symptom.name;
    card.dataset.searchText = `${symptom.name_vi} ${symptom.name} ${symptom.description}`.toLowerCase();
    card.style.animationDelay = `${index * 0.03}s`;
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
    updateFloatingBar();
}

// ============================================================================
// SEARCH BAR
// ============================================================================
function setupSearchBar() {
    const input = document.getElementById('symptom-search');
    if (!input) return;

    input.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase().trim();
        filterSymptoms(query);
    });
}

function filterSymptoms(query) {
    const cards = document.querySelectorAll('.symptom-card:not(.risk-card)');
    const categories = document.querySelectorAll('.symptom-category');

    cards.forEach(card => {
        const text = card.dataset.searchText || '';
        if (!query || text.includes(query)) {
            card.classList.remove('no-match');
        } else {
            card.classList.add('no-match');
        }
    });

    // Hide empty categories
    categories.forEach(cat => {
        const visibleCards = cat.querySelectorAll('.symptom-card:not(.no-match)');
        cat.classList.toggle('hidden', visibleCards.length === 0);
    });
}

// ============================================================================
// RENDER RISK FACTORS
// ============================================================================
function renderRiskFactors() {
    const grid = document.getElementById('risk-factors-grid');
    grid.innerHTML = '';

    riskFactorsData.forEach((rf, index) => {
        const card = document.createElement('div');
        card.className = 'symptom-card risk-card';
        card.dataset.riskfactor = rf.name;
        card.style.animationDelay = `${(symptomsData.length + index) * 0.03}s`;
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
// SELECTED COUNT & FLOATING BAR
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

function updateFloatingBar() {
    const count = Object.keys(selectedSymptoms).length;
    const total = symptomsData.length;
    const bar = document.getElementById('floating-bar');
    const floatCount = document.getElementById('float-count');
    const floatBtn = document.getElementById('float-diagnose');

    floatCount.textContent = `${count}/${total} triệu chứng`;
    floatBtn.disabled = count === 0;

    // Show floating bar when scrolled down
    if (count > 0) {
        bar.classList.add('visible');
    } else {
        bar.classList.remove('visible');
    }
}

// ============================================================================
// KEYBOARD SHORTCUTS
// ============================================================================
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Don't trigger when typing in input
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
            if (e.key === 'Escape') {
                e.target.blur();
                filterSymptoms('');
                document.getElementById('symptom-search').value = '';
            }
            return;
        }

        switch (e.key) {
            case 'Enter':
                e.preventDefault();
                runDiagnosis();
                break;
            case 'Escape':
                e.preventDefault();
                // Close any open modals first
                if (document.getElementById('network-modal').style.display !== 'none') {
                    closeNetworkModal();
                } else if (document.getElementById('compare-modal').style.display !== 'none') {
                    closeCompareModal();
                } else if (document.getElementById('history-drawer').classList.contains('open')) {
                    toggleHistoryDrawer();
                } else {
                    resetForm();
                }
                break;
            case '/':
                e.preventDefault();
                document.getElementById('symptom-search').focus();
                break;
        }
    });
}

// ============================================================================
// DIAGNOSIS
// ============================================================================
async function runDiagnosis() {
    const symptomCount = Object.keys(selectedSymptoms).length;
    if (symptomCount === 0) return;

    // Build full symptom map
    const symptomMap = {};
    symptomsData.forEach(s => {
        if (selectedSymptoms[s.name]) {
            symptomMap[s.name] = true;
        }
    });

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
        lastDiagnosisResult = result;
        displayResults(result);

        // Save to history
        saveToHistory(result);

        // Show success toast
        const top = result.diagnoses[0];
        showToast(
            `Chuẩn đoán hoàn tất: ${top.disease_vi} (${(top.probability * 100).toFixed(1)}%)`,
            'success'
        );

    } catch (error) {
        console.error('Diagnosis error:', error);
        showToast(`Lỗi chuẩn đoán: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

// ============================================================================
// DISPLAY RESULTS (enhanced with severity badges)
// ============================================================================
function displayResults(result) {
    document.getElementById('results-placeholder').style.display = 'none';
    document.getElementById('results-content').style.display = 'block';

    // Top diagnosis
    const top = result.diagnoses[0];
    document.getElementById('top-disease-name').textContent = top.disease.replace(/_/g, ' ');
    document.getElementById('top-disease-vi').textContent = top.disease_vi;

    // Probability ring animation with gradient
    const prob = top.probability;
    const circumference = 2 * Math.PI * 52;
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

    // Dynamic gradient color based on probability
    const grad = document.getElementById('prob-gradient');
    if (prob >= 0.7) {
        grad.querySelector('stop:first-child').style.stopColor = '#10b981';
        grad.querySelector('stop:last-child').style.stopColor = '#3b82f6';
    } else if (prob >= 0.4) {
        grad.querySelector('stop:first-child').style.stopColor = '#f59e0b';
        grad.querySelector('stop:last-child').style.stopColor = '#ef4444';
    } else {
        grad.querySelector('stop:first-child').style.stopColor = '#ef4444';
        grad.querySelector('stop:last-child').style.stopColor = '#94a3b8';
    }

    const ringColor = prob >= 0.7 ? '#10b981' : prob >= 0.4 ? '#f59e0b' : '#ef4444';
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

    // Evidence count & disease count
    document.getElementById('evidence-count').textContent = result.num_evidence;
    const dcDisplay = document.getElementById('disease-count-display');
    if (dcDisplay) dcDisplay.textContent = result.num_diseases || 10;

    // Chart
    renderProbabilityChart(result.diagnoses);

    // Disease list with severity badges and expandable details
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

    const isLight = document.body.classList.contains('light-theme');
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
                    backgroundColor: isLight ? '#ffffff' : '#1a2035',
                    borderColor: '#3b82f6',
                    borderWidth: 1,
                    titleColor: isLight ? '#0f172a' : '#f1f5f9',
                    bodyColor: isLight ? '#475569' : '#94a3b8',
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
                    grid: { color: isLight ? 'rgba(15,23,42,0.06)' : 'rgba(148,163,184,0.08)' },
                    ticks: {
                        color: isLight ? '#475569' : '#94a3b8',
                        font: { family: 'Inter', size: 11 },
                        callback: val => val + '%',
                    }
                },
                y: {
                    grid: { display: false },
                    ticks: {
                        color: isLight ? '#0f172a' : '#f1f5f9',
                        font: { family: 'Inter', size: 11, weight: '500' },
                    }
                }
            }
        }
    });
}

// ============================================================================
// DISEASE LIST (with severity badges + expandable details)
// ============================================================================
function renderDiseaseList(diagnoses) {
    const container = document.getElementById('diseases-list');
    container.innerHTML = '';

    diagnoses.forEach((d, index) => {
        const color = DISEASE_COLORS[d.disease]?.border || '#666';
        const prob = (d.probability * 100).toFixed(1);
        const rankClass = index < 3 ? `top-${index + 1}` : '';

        // Severity badge
        let severityClass, severityText;
        if (d.probability >= 0.5) {
            severityClass = 'severity-high';
            severityText = 'Cao';
        } else if (d.probability >= 0.2) {
            severityClass = 'severity-medium';
            severityText = 'TB';
        } else {
            severityClass = 'severity-low';
            severityText = 'Thấp';
        }

        // Row
        const row = document.createElement('div');
        row.className = 'disease-row animate-in';
        row.style.animationDelay = `${index * 0.08}s`;
        row.onclick = () => toggleDiseaseDetails(row, `details-${index}`);
        row.innerHTML = `
            <div class="disease-rank ${rankClass}">${index + 1}</div>
            <div class="disease-info">
                <div class="name">
                    ${d.disease.replace(/_/g, ' ')}
                    <span class="severity-badge ${severityClass}">${severityText}</span>
                </div>
                <div class="name-vi">${d.disease_vi}</div>
            </div>
            <div class="disease-prob">
                <div class="bar-wrap">
                    <div class="bar-fill" style="width: ${prob}%; background: ${color};"></div>
                </div>
                <span class="prob-text">${prob}%</span>
            </div>
            <span class="material-symbols-rounded expand-arrow">expand_more</span>
        `;
        container.appendChild(row);

        // Expandable details
        const details = document.createElement('div');
        details.className = 'disease-details';
        details.id = `details-${index}`;
        details.innerHTML = `
            <div class="detail-grid">
                <div class="detail-item">
                    <span class="detail-label">Mã ICD-10</span>
                    <span class="detail-value">${d.icd10 || 'N/A'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Phân loại</span>
                    <span class="detail-value">${d.category || 'N/A'}</span>
                </div>
                <div class="detail-item" style="grid-column: 1 / -1;">
                    <span class="detail-label">Mô tả</span>
                    <span class="detail-value">
                        <div>${d.description_vi || ''}</div>
                        <div style="font-size: 0.9em; opacity: 0.8; margin-top: 4px;">${d.description || ''}</div>
                    </span>
                </div>
                <div class="detail-item" style="grid-column: 1 / -1;">
                    <span class="detail-label">Khuyến nghị</span>
                    <span class="detail-value">${getRecommendation(d.probability)}</span>
                </div>
            </div>
        `;
        container.appendChild(details);
    });
}

function toggleDiseaseDetails(row, detailsId) {
    const details = document.getElementById(detailsId);
    const isExpanded = row.classList.contains('expanded');

    // Close all others
    document.querySelectorAll('.disease-row.expanded').forEach(r => r.classList.remove('expanded'));
    document.querySelectorAll('.disease-details.show').forEach(d => d.classList.remove('show'));

    if (!isExpanded) {
        row.classList.add('expanded');
        details.classList.add('show');
    }
}

function getRecommendation(probability) {
    if (probability >= 0.7) return 'Xác suất cao — Nên thăm khám bác sĩ chuyên khoa ngay';
    if (probability >= 0.4) return 'Xác suất trung bình — Nên theo dõi và tham khảo ý kiến bác sĩ';
    if (probability >= 0.1) return 'Xác suất thấp — Theo dõi tại nhà, tái khám nếu triệu chứng nặng hơn';
    return 'Xác suất rất thấp — Khả năng mắc bệnh này không đáng kể';
}

// ============================================================================
// TOAST NOTIFICATIONS
// ============================================================================
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    const icons = {
        success: 'check_circle',
        error: 'error',
        info: 'info',
    };

    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <span class="material-symbols-rounded">${icons[type] || 'info'}</span>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    // Remove after animation
    setTimeout(() => {
        if (toast.parentNode) toast.remove();
    }, 4200);
}


// ============================================================================
// DIAGNOSIS HISTORY (localStorage)
// ============================================================================
const HISTORY_KEY = 'meddiag-history';
const MAX_HISTORY = 10;

function getHistory() {
    try {
        return JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]');
    } catch {
        return [];
    }
}

function saveToHistory(result) {
    const history = getHistory();
    const entry = {
        id: Date.now(),
        timestamp: new Date().toISOString(),
        result: result,
        symptoms: { ...selectedSymptoms },
        riskFactors: [...selectedRiskFactors],
    };

    history.unshift(entry);
    if (history.length > MAX_HISTORY) history.pop();

    localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
    updateHistoryBadge();
}

function updateHistoryBadge() {
    const history = getHistory();
    const badge = document.getElementById('history-badge');
    if (history.length > 0) {
        badge.style.display = 'flex';
        badge.textContent = history.length;
    } else {
        badge.style.display = 'none';
    }
}

function toggleHistoryDrawer() {
    const drawer = document.getElementById('history-drawer');
    const overlay = document.getElementById('history-overlay');
    const isOpen = drawer.classList.contains('open');

    if (isOpen) {
        drawer.classList.remove('open');
        overlay.classList.remove('open');
    } else {
        drawer.classList.add('open');
        overlay.classList.add('open');
        renderHistoryList();
    }
}

function renderHistoryList() {
    const container = document.getElementById('history-list');
    const history = getHistory();

    if (history.length === 0) {
        container.innerHTML = '<p class="empty-history">Chưa có lịch sử chuẩn đoán</p>';
        return;
    }

    container.innerHTML = history.map((entry, idx) => {
        const top = entry.result.diagnoses[0];
        const time = new Date(entry.timestamp);
        const timeStr = time.toLocaleDateString('vi-VN') + ' ' + time.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
        const symptomTags = entry.result.evidence_used.slice(0, 4).map(s => {
            const sym = symptomsData.find(sd => sd.name === s);
            return `<span class="history-symptom-tag">${sym ? sym.name_vi : s}</span>`;
        }).join('') + (entry.result.evidence_used.length > 4 ? `<span class="history-symptom-tag">+${entry.result.evidence_used.length - 4}</span>` : '');

        return `
            <div class="history-item">
                <div class="history-time">
                    <span class="material-symbols-rounded" style="font-size:14px;">schedule</span>
                    ${timeStr}
                </div>
                <div class="history-result">${top.disease_vi}</div>
                <div class="history-prob">${(top.probability * 100).toFixed(1)}%</div>
                <div class="history-symptoms">${symptomTags}</div>
                <div class="history-actions">
                    <button class="history-btn" onclick="loadHistoryEntry(${idx})">
                        <span class="material-symbols-rounded">visibility</span>Xem
                    </button>
                    <button class="history-btn" onclick="compareWithCurrent(${idx})">
                        <span class="material-symbols-rounded">compare</span>So sánh
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

function loadHistoryEntry(index) {
    const history = getHistory();
    if (index >= history.length) return;

    const entry = history[index];
    lastDiagnosisResult = entry.result;
    displayResults(entry.result);
    toggleHistoryDrawer();
    showToast('Đã tải lại kết quả chuẩn đoán từ lịch sử', 'info');
}

function clearHistory() {
    localStorage.removeItem(HISTORY_KEY);
    updateHistoryBadge();
    renderHistoryList();
    showToast('Đã xóa toàn bộ lịch sử', 'info');
}

// ============================================================================
// COMPARISON
// ============================================================================
function compareWithCurrent(historyIndex) {
    const history = getHistory();
    if (historyIndex >= history.length) return;

    const historyEntry = history[historyIndex];

    if (!lastDiagnosisResult) {
        showToast('Chưa có kết quả hiện tại để so sánh. Hãy chạy chuẩn đoán trước.', 'error');
        return;
    }

    toggleHistoryDrawer();
    openCompareModal(lastDiagnosisResult, historyEntry.result, historyEntry.timestamp);
}

function openCompareModal(current, historical, historicalTime) {
    const modal = document.getElementById('compare-modal');
    const grid = document.getElementById('compare-grid');
    const timeStr = new Date(historicalTime).toLocaleDateString('vi-VN') + ' ' + new Date(historicalTime).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });

    // Get symptom names for both sessions
    const currentSymptoms = current.evidence_used || [];
    const historicalSymptoms = historical.evidence_used || [];
    const currentRisks = current.risk_factors || [];
    const historicalRisks = historical.risk_factors || [];

    grid.innerHTML = `
        <div class="compare-column">
            <h3>🔵 Kết quả Hiện tại</h3>
            ${current.diagnoses.map(d => `
                <div class="compare-disease-item">
                    <span>${d.disease_vi}</span>
                    <span style="font-weight:600;color:${DISEASE_COLORS[d.disease]?.border || '#666'}">${(d.probability * 100).toFixed(1)}%</span>
                </div>
            `).join('')}
        </div>
        <div class="compare-column">
            <h3>📋 Lịch sử (${timeStr})</h3>
            ${historical.diagnoses.map(d => `
                <div class="compare-disease-item">
                    <span>${d.disease_vi}</span>
                    <span style="font-weight:600;color:${DISEASE_COLORS[d.disease]?.border || '#666'}">${(d.probability * 100).toFixed(1)}%</span>
                </div>
            `).join('')}
        </div>

        <!-- Symptoms Detail Section -->
        <div class="compare-symptoms-section" style="grid-column: 1 / -1;">
            <button class="compare-symptoms-toggle" onclick="toggleCompareSymptoms(this)">
                <h4>
                    <span class="material-symbols-rounded">symptoms</span>
                    Chi tiết Triệu chứng đã chọn
                </h4>
                <span class="material-symbols-rounded toggle-icon">expand_more</span>
            </button>
            <div class="compare-symptoms-content" id="compare-symptoms-content">
                <div class="compare-symptoms-grid">
                    <div class="compare-symptom-column">
                        <h5>🔵 Hiện tại (${currentSymptoms.length} triệu chứng)</h5>
                        <div class="compare-symptom-tags">
                            ${currentSymptoms.map(s => {
                                const sym = symptomsData.find(sd => sd.name === s);
                                return `<span class="compare-symptom-tag">
                                    <span class="material-symbols-rounded">check_circle</span>
                                    ${sym ? sym.name_vi : s.replace(/_/g, ' ')}
                                </span>`;
                            }).join('')}
                        </div>
                        ${currentRisks.length > 0 ? `
                            <h5 style="margin-top:12px;">⚠️ Yếu tố nguy cơ</h5>
                            <div class="compare-symptom-tags">
                                ${currentRisks.map(rf => {
                                    const factor = riskFactorsData.find(r => r.name === rf);
                                    return `<span class="compare-symptom-tag compare-risk-tag">
                                        <span class="material-symbols-rounded">warning</span>
                                        ${factor ? factor.name_vi : rf}
                                    </span>`;
                                }).join('')}
                            </div>
                        ` : ''}
                    </div>
                    <div class="compare-symptom-column">
                        <h5>📋 Lịch sử (${historicalSymptoms.length} triệu chứng)</h5>
                        <div class="compare-symptom-tags">
                            ${historicalSymptoms.map(s => {
                                const sym = symptomsData.find(sd => sd.name === s);
                                return `<span class="compare-symptom-tag">
                                    <span class="material-symbols-rounded">check_circle</span>
                                    ${sym ? sym.name_vi : s.replace(/_/g, ' ')}
                                </span>`;
                            }).join('')}
                        </div>
                        ${historicalRisks.length > 0 ? `
                            <h5 style="margin-top:12px;">⚠️ Yếu tố nguy cơ</h5>
                            <div class="compare-symptom-tags">
                                ${historicalRisks.map(rf => {
                                    const factor = riskFactorsData.find(r => r.name === rf);
                                    return `<span class="compare-symptom-tag compare-risk-tag">
                                        <span class="material-symbols-rounded">warning</span>
                                        ${factor ? factor.name_vi : rf}
                                    </span>`;
                                }).join('')}
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        </div>
    `;

    modal.style.display = 'flex';
}

function toggleCompareSymptoms(btn) {
    btn.classList.toggle('expanded');
    const content = document.getElementById('compare-symptoms-content');
    content.classList.toggle('show');
}

function closeCompareModal() {
    document.getElementById('compare-modal').style.display = 'none';
}

// ============================================================================
// BAYESIAN NETWORK VISUALIZATION (Canvas)
// ============================================================================
async function openNetworkModal() {
    const modal = document.getElementById('network-modal');
    modal.style.display = 'flex';

    if (!networkData) {
        try {
            const res = await fetch(`${API_BASE}/api/network`);
            networkData = await res.json();
        } catch (e) {
            showToast('Không thể tải dữ liệu mạng', 'error');
            return;
        }
    }

    // Wait for modal to render, then draw
    requestAnimationFrame(() => {
        drawBayesianNetwork();
    });
}

function closeNetworkModal() {
    document.getElementById('network-modal').style.display = 'none';
}

function drawBayesianNetwork() {
    const canvas = document.getElementById('network-canvas');
    const ctx = canvas.getContext('2d');
    const rect = canvas.parentElement.getBoundingClientRect();

    canvas.width = rect.width - 56;
    canvas.height = 700;

    const W = canvas.width;
    const H = canvas.height;
    const diseases = networkData.diseases || [];
    const symptoms = networkData.symptoms || [];
    const sensitivity = networkData.sensitivity_matrix || {};

    const isLight = document.body.classList.contains('light-theme');
    const bgColor = isLight ? '#f1f5f9' : '#232b42';
    const textColor = isLight ? '#0f172a' : '#f1f5f9';
    const mutedColor = isLight ? '#64748b' : '#94a3b8';

    // Clear
    ctx.fillStyle = bgColor;
    ctx.fillRect(0, 0, W, H);

    // Layout: Disease row at top, 2 symptom rows at bottom
    const diseaseY = 80;
    const symptomRow1Y = H - 200;
    const symptomRow2Y = H - 80;
    const diseaseSpacing = W / (diseases.length + 1);

    // Split symptoms into 2 rows for better spacing
    const half = Math.ceil(symptoms.length / 2);
    const row1Symptoms = symptoms.slice(0, half);
    const row2Symptoms = symptoms.slice(half);
    const row1Spacing = W / (row1Symptoms.length + 1);
    const row2Spacing = W / (row2Symptoms.length + 1);

    const nodePositions = {};
    const diseaseRadius = 24;
    const symptomRadius = 16;

    // Pre-calculate all positions
    diseases.forEach((d, i) => {
        nodePositions[d] = { x: diseaseSpacing * (i + 1), y: diseaseY, type: 'disease' };
    });
    row1Symptoms.forEach((s, i) => {
        nodePositions[s] = { x: row1Spacing * (i + 1), y: symptomRow1Y, type: 'symptom' };
    });
    row2Symptoms.forEach((s, i) => {
        nodePositions[s] = { x: row2Spacing * (i + 1), y: symptomRow2Y, type: 'symptom' };
    });

    const observed = lastDiagnosisResult ? (lastDiagnosisResult.evidence_used || []) : [];

    // Draw background edges (faint, bezier curves)
    diseases.forEach((d, di) => {
        const dx = nodePositions[d].x;
        const dy = nodePositions[d].y;
        symptoms.forEach(s => {
            const sens = sensitivity[s]?.[d] || 0;
            if (sens <= 0.15) return; // Skip weak connections
            if (observed.includes(s)) return; // Draw highlighted separately

            const sp = nodePositions[s];
            const alpha = Math.min(sens * 0.4, 0.2);
            ctx.strokeStyle = isLight ? `rgba(100, 116, 139, ${alpha})` : `rgba(148, 163, 184, ${alpha})`;
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(dx, dy + diseaseRadius);
            const midY = (dy + diseaseRadius + sp.y - symptomRadius) / 2;
            ctx.bezierCurveTo(dx, midY, sp.x, midY, sp.x, sp.y - symptomRadius);
            ctx.stroke();
        });
    });

    // Draw highlighted edges (for observed symptoms — thicker, colored)
    if (observed.length > 0) {
        diseases.forEach((d, di) => {
            const dx = nodePositions[d].x;
            const dy = nodePositions[d].y;
            const diseaseColor = DISEASE_COLORS[d]?.border || '#3b82f6';

            observed.forEach(s => {
                const sens = sensitivity[s]?.[d] || 0;
                if (sens <= 0.1) return;

                const sp = nodePositions[s];
                const alpha = Math.min(sens * 0.9, 0.7);
                ctx.strokeStyle = diseaseColor;
                ctx.globalAlpha = alpha;
                ctx.lineWidth = sens > 0.5 ? 2.5 : 1.5;
                ctx.beginPath();
                ctx.moveTo(dx, dy + diseaseRadius);
                const midY = (dy + diseaseRadius + sp.y - symptomRadius) / 2;
                ctx.bezierCurveTo(dx, midY, sp.x, midY, sp.x, sp.y - symptomRadius);
                ctx.stroke();
                ctx.globalAlpha = 1;
            });
        });
    }

    // Draw disease nodes
    diseases.forEach(d => {
        const pos = nodePositions[d];
        const isTopResult = lastDiagnosisResult && lastDiagnosisResult.most_likely === d;
        const diseaseColor = DISEASE_COLORS[d]?.border || '#3b82f6';

        // Glow for top result
        if (isTopResult) {
            ctx.shadowColor = '#fbbf24';
            ctx.shadowBlur = 15;
        }

        // Node circle
        const grad = ctx.createRadialGradient(pos.x, pos.y, 4, pos.x, pos.y, diseaseRadius);
        if (isTopResult) {
            grad.addColorStop(0, '#fbbf24');
            grad.addColorStop(1, '#d97706');
        } else {
            grad.addColorStop(0, diseaseColor);
            grad.addColorStop(1, adjustColor(diseaseColor, -30));
        }
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, diseaseRadius, 0, Math.PI * 2);
        ctx.fill();

        // Reset shadow
        ctx.shadowColor = 'transparent';
        ctx.shadowBlur = 0;

        // Border
        ctx.strokeStyle = isTopResult ? '#fbbf24' : 'rgba(255,255,255,0.15)';
        ctx.lineWidth = isTopResult ? 2.5 : 1;
        ctx.stroke();

        // Disease label below node
        ctx.fillStyle = textColor;
        ctx.font = '600 11px Inter';
        ctx.textAlign = 'center';
        const label = d.replace(/_/g, ' ');
        ctx.fillText(label.length > 14 ? label.substring(0, 14) + '…' : label, pos.x, pos.y + diseaseRadius + 16);

        // Show probability if diagnosis exists
        if (lastDiagnosisResult) {
            const diag = lastDiagnosisResult.diagnoses.find(dd => dd.disease === d);
            if (diag) {
                ctx.fillStyle = mutedColor;
                ctx.font = '500 9px Inter';
                ctx.fillText(`${(diag.probability * 100).toFixed(1)}%`, pos.x, pos.y + diseaseRadius + 28);
            }
        }
    });

    // Draw symptom nodes
    symptoms.forEach(s => {
        const pos = nodePositions[s];
        const isObserved = observed.includes(s);
        const sym = symptomsData.find(sd => sd.name === s);

        // Glow for observed
        if (isObserved) {
            ctx.shadowColor = '#f59e0b';
            ctx.shadowBlur = 12;
        }

        const grad = ctx.createRadialGradient(pos.x, pos.y, 2, pos.x, pos.y, symptomRadius);
        if (isObserved) {
            grad.addColorStop(0, '#fbbf24');
            grad.addColorStop(1, '#d97706');
        } else {
            grad.addColorStop(0, '#34d399');
            grad.addColorStop(1, '#059669');
        }
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, symptomRadius, 0, Math.PI * 2);
        ctx.fill();

        ctx.shadowColor = 'transparent';
        ctx.shadowBlur = 0;

        // Border
        ctx.strokeStyle = isObserved ? '#fbbf24' : 'rgba(255,255,255,0.1)';
        ctx.lineWidth = isObserved ? 2 : 0.5;
        ctx.stroke();

        // Label above node (rotated for readability)
        ctx.save();
        ctx.translate(pos.x, pos.y - symptomRadius - 6);
        ctx.rotate(-Math.PI / 5);
        ctx.fillStyle = isObserved ? textColor : mutedColor;
        ctx.font = isObserved ? '600 10px Inter' : '400 9px Inter';
        ctx.textAlign = 'right';
        const symLabel = sym ? sym.name_vi : s.replace(/_/g, ' ');
        ctx.fillText(symLabel.length > 12 ? symLabel.substring(0, 12) + '…' : symLabel, 0, 0);
        ctx.restore();
    });

    // Tooltip on hover
    canvas.onmousemove = (e) => {
        const crect = canvas.getBoundingClientRect();
        const mx = e.clientX - crect.left;
        const my = e.clientY - crect.top;

        let found = null;
        for (const [name, pos] of Object.entries(nodePositions)) {
            const r = pos.type === 'disease' ? diseaseRadius : symptomRadius;
            const dist = Math.sqrt((mx - pos.x) ** 2 + (my - pos.y) ** 2);
            if (dist < r + 4) {
                found = { name, ...pos };
                break;
            }
        }

        const tooltip = document.getElementById('network-tooltip');
        if (found) {
            canvas.style.cursor = 'pointer';
            let html = '';
            if (found.type === 'disease') {
                const prior = networkData.priors?.[found.name] || 0;
                const diag = lastDiagnosisResult?.diagnoses?.find(d => d.disease === found.name);
                html = `
                    <div class="tt-title">${found.name.replace(/_/g, ' ')}</div>
                    <div class="tt-subtitle">Disease Node</div>
                    <div class="tt-value">Prior: P(D) = ${(prior * 100).toFixed(1)}%</div>
                    ${diag ? `<div class="tt-value">Posterior: ${(diag.probability * 100).toFixed(1)}%</div>` : ''}
                `;
            } else {
                const sym = symptomsData.find(s => s.name === found.name);
                html = `
                    <div class="tt-title">${sym ? sym.name_vi : found.name}</div>
                    <div class="tt-subtitle">${sym ? sym.description : 'Symptom Node'}</div>
                `;
                const sData = sensitivity[found.name];
                if (sData) {
                    const entries = Object.entries(sData)
                        .sort((a, b) => b[1] - a[1])
                        .slice(0, 3);
                    html += '<div style="margin-top:4px;border-top:1px solid rgba(148,163,184,0.15);padding-top:4px;">';
                    html += entries.map(([d, v]) =>
                        `<div class="tt-value">${d.replace(/_/g, ' ')}: ${(v * 100).toFixed(0)}%</div>`
                    ).join('');
                    html += '</div>';
                }
            }
            tooltip.innerHTML = html;
            tooltip.style.display = 'block';

            // Position tooltip, keeping it in viewport
            let tx = found.x + 24;
            let ty = found.y - 10;
            if (tx + 200 > W) tx = found.x - 220;
            if (ty < 0) ty = 10;
            tooltip.style.left = tx + 'px';
            tooltip.style.top = ty + 'px';
        } else {
            canvas.style.cursor = 'default';
            tooltip.style.display = 'none';
        }
    };

    canvas.onmouseleave = () => {
        document.getElementById('network-tooltip').style.display = 'none';
    };
}

// Helper: darken/lighten a hex color
function adjustColor(hex, amount) {
    const num = parseInt(hex.replace('#', ''), 16);
    const r = Math.min(255, Math.max(0, (num >> 16) + amount));
    const g = Math.min(255, Math.max(0, ((num >> 8) & 0x00FF) + amount));
    const b = Math.min(255, Math.max(0, (num & 0x0000FF) + amount));
    return `#${(1 << 24 | r << 16 | g << 8 | b).toString(16).slice(1)}`;
}

// ============================================================================
// PDF EXPORT (html2pdf.js)
// ============================================================================
function exportPDF() {
    if (!lastDiagnosisResult) {
        showToast('Chưa có kết quả để xuất', 'error');
        return;
    }

    showToast('Đang tạo PDF...', 'info');

    const result = lastDiagnosisResult;
    const top = result.diagnoses[0];
    const now = new Date();
    const dateStr = now.toLocaleDateString('vi-VN');
    const timeStr = now.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
    const fileName = `MedDiag_Report_${dateStr.replace(/\//g, '-')}.pdf`;

    // Build PDF content
    const reportHTML = `
    <div style="font-family: Inter, Arial, sans-serif; color: #1a1a1a; padding: 40px; max-width: 700px; margin: 0 auto;">
        <!-- Header -->
        <div style="text-align: center; margin-bottom: 32px; border-bottom: 3px solid #3b82f6; padding-bottom: 20px;">
            <h1 style="font-size: 24px; color: #1e40af; margin: 0 0 4px;">MedDiag AI — Báo cáo Chuẩn đoán</h1>
            <p style="font-size: 12px; color: #6b7280; margin: 0;">Hệ thống Chuẩn đoán Y khoa Thông minh | Bayesian Network</p>
            <p style="font-size: 12px; color: #9ca3af; margin: 4px 0 0;">Ngày: ${dateStr} | Giờ: ${timeStr}</p>
        </div>

        <!-- Top Diagnosis -->
        <div style="background: #f0fdf4; border: 2px solid #10b981; border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 24px;">
            <p style="font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: #059669; margin: 0 0 8px;">Chuẩn đoán hàng đầu</p>
            <h2 style="font-size: 22px; color: #065f46; margin: 0 0 4px;">${top.disease_vi}</h2>
            <p style="font-size: 14px; color: #6b7280; margin: 0 0 8px;">${top.disease.replace(/_/g, ' ')} (${top.icd10 || ''})</p>
            <p style="font-size: 28px; font-weight: 800; color: #10b981; margin: 0;">${(top.probability * 100).toFixed(1)}%</p>
        </div>

        <!-- Evidence Used -->
        <div style="margin-bottom: 24px;">
            <h3 style="font-size: 14px; color: #374151; border-bottom: 1px solid #e5e7eb; padding-bottom: 8px; margin-bottom: 12px;">
                Triệu chứng đã chọn (${result.evidence_used.length})
            </h3>
            <div style="display: flex; flex-wrap: wrap; gap: 6px;">
                ${result.evidence_used.map(s => {
                    const sym = symptomsData.find(sd => sd.name === s);
                    return `<span style="background: #e0f2fe; color: #0369a1; padding: 4px 10px; border-radius: 6px; font-size: 12px;">${sym ? sym.name_vi : s}</span>`;
                }).join('')}
            </div>
        </div>

        ${result.risk_factors && result.risk_factors.length > 0 ? `
        <div style="margin-bottom: 24px;">
            <h3 style="font-size: 14px; color: #374151; border-bottom: 1px solid #e5e7eb; padding-bottom: 8px; margin-bottom: 12px;">
                Yếu tố nguy cơ
            </h3>
            <div style="display: flex; flex-wrap: wrap; gap: 6px;">
                ${result.risk_factors.map(rf => {
                    const factor = riskFactorsData.find(r => r.name === rf);
                    return `<span style="background: #fef3c7; color: #92400e; padding: 4px 10px; border-radius: 6px; font-size: 12px;">${factor ? factor.name_vi : rf}</span>`;
                }).join('')}
            </div>
        </div>
        ` : ''}

        <!-- All Diagnoses -->
        <div style="margin-bottom: 24px;">
            <h3 style="font-size: 14px; color: #374151; border-bottom: 1px solid #e5e7eb; padding-bottom: 8px; margin-bottom: 12px;">
                Phân phối Xác suất Tất cả Bệnh
            </h3>
            <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                <thead>
                    <tr style="background: #f9fafb;">
                        <th style="text-align: left; padding: 8px 12px; border-bottom: 2px solid #e5e7eb;">#</th>
                        <th style="text-align: left; padding: 8px 12px; border-bottom: 2px solid #e5e7eb;">Bệnh</th>
                        <th style="text-align: left; padding: 8px 12px; border-bottom: 2px solid #e5e7eb;">ICD-10</th>
                        <th style="text-align: right; padding: 8px 12px; border-bottom: 2px solid #e5e7eb;">Xác suất</th>
                        <th style="text-align: center; padding: 8px 12px; border-bottom: 2px solid #e5e7eb;">Mức độ</th>
                    </tr>
                </thead>
                <tbody>
                    ${result.diagnoses.map((d, i) => {
                        const prob = (d.probability * 100).toFixed(1);
                        let level, levelColor;
                        if (d.probability >= 0.5) { level = 'Cao'; levelColor = '#dc2626'; }
                        else if (d.probability >= 0.2) { level = 'Trung bình'; levelColor = '#d97706'; }
                        else { level = 'Thấp'; levelColor = '#6b7280'; }
                        return `
                        <tr style="border-bottom: 1px solid #f3f4f6;">
                            <td style="padding: 8px 12px; font-weight: 600; color: #6b7280;">${i + 1}</td>
                            <td style="padding: 8px 12px;">
                                <div style="font-weight: 600;">${d.disease_vi}</div>
                                <div style="font-size: 11px; color: #9ca3af;">${d.disease.replace(/_/g, ' ')}</div>
                            </td>
                            <td style="padding: 8px 12px; color: #6b7280;">${d.icd10 || ''}</td>
                            <td style="padding: 8px 12px; text-align: right; font-weight: 700;">${prob}%</td>
                            <td style="padding: 8px 12px; text-align: center; color: ${levelColor}; font-weight: 600;">${level}</td>
                        </tr>`;
                    }).join('')}
                </tbody>
            </table>
        </div>

        <!-- Footer -->
        <div style="border-top: 2px solid #e5e7eb; padding-top: 16px; margin-top: 32px; text-align: center;">
            <p style="font-size: 11px; color: #9ca3af; margin: 0;">
                Thuật toán: Variable Elimination | Mô hình: Noisy-OR Bayesian Network | ${result.num_diseases || 10} bệnh x ${symptomsData.length} triệu chứng
            </p>
            <p style="font-size: 10px; color: #d1d5db; margin: 8px 0 0;">
                Hệ thống chỉ mang tính chất tham khảo. Vui lòng tham vấn bác sĩ chuyên khoa để có chuẩn đoán chính xác.
            </p>
            <p style="font-size: 10px; color: #d1d5db; margin: 4px 0 0;">
                Advanced AI Midterm Project — OU University
            </p>
        </div>
    </div>
    `;

    const pdfContainer = document.getElementById('pdf-report');
    pdfContainer.innerHTML = reportHTML;
    pdfContainer.style.display = 'block';

    const opt = {
        margin: [10, 10, 10, 10],
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true, logging: false },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };

    html2pdf().set(opt).from(pdfContainer).toPdf().get('pdf').then(function(pdf) {
        // Step 1: Download file with correct name using jsPDF's native save
        pdf.save(fileName);

        // Step 2: Open preview in new tab
        const blobUrl = pdf.output('bloburl');
        window.open(blobUrl, '_blank');

        showToast('PDF đã tải xuống và mở preview!', 'success');
        pdfContainer.innerHTML = '';
        pdfContainer.style.display = 'none';
    }).catch(err => {
        showToast('Lỗi tạo PDF: ' + err.message, 'error');
        pdfContainer.innerHTML = '';
        pdfContainer.style.display = 'none';
    });
}

// ============================================================================
// RESET
// ============================================================================
function resetForm() {
    selectedSymptoms = {};
    selectedRiskFactors = [];

    document.querySelectorAll('.symptom-card').forEach(card => {
        card.classList.remove('active');
    });

    document.getElementById('results-placeholder').style.display = 'flex';
    document.getElementById('results-content').style.display = 'none';

    if (probabilityChart) {
        probabilityChart.destroy();
        probabilityChart = null;
    }

    // Clear search
    const searchInput = document.getElementById('symptom-search');
    if (searchInput) {
        searchInput.value = '';
        filterSymptoms('');
    }

    updateSelectedCount();
    updateFloatingBar();
}

// ============================================================================
// UTILITIES
// ============================================================================
function showLoading(show) {
    document.getElementById('loading-overlay').style.display = show ? 'flex' : 'none';
}

function showError(message) {
    showToast(message, 'error');
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

    // Redraw network if open
    if (document.getElementById('network-modal').style.display !== 'none' && networkData) {
        drawBayesianNetwork();
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
