# 🏥 MedDiag AI — Hệ thống Chẩn đoán Y khoa Thông minh

> **Medical Diagnostic Reasoning System** sử dụng **Mạng Bayesian (Bayesian Networks)** và thuật toán **Variable Elimination** để chẩn đoán bệnh viêm đường hô hấp cấp và sốt.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?style=flat-square&logo=fastapi)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

---

## 📋 Mục lục

- [Giới thiệu](#-giới-thiệu)
- [Kiến trúc Hệ thống](#-kiến-trúc-hệ-thống)
- [Cài đặt & Chạy](#-cài-đặt--chạy)
- [Hướng dẫn Sử dụng](#-hướng-dẫn-sử-dụng)
- [Dataset & Mô hình](#-dataset--mô-hình)
- [Kết quả Thử nghiệm](#-kết-quả-thử-nghiệm)
- [Cấu trúc Project](#-cấu-trúc-project)
- [Công nghệ Sử dụng](#-công-nghệ-sử-dụng)

---

## 🎯 Giới thiệu

MedDiag AI là hệ thống chẩn đoán y khoa dựa trên **suy luận xác suất** (Probabilistic Reasoning), giúp xác định bệnh có khả năng cao nhất dựa trên triệu chứng lâm sàng của bệnh nhân.

### Đặc điểm nổi bật

| Tính năng | Mô tả |
|:---|:---|
| 🧠 **Bayesian Network** | Mạng DAG 2 lớp: 7 bệnh → 19 triệu chứng |
| ⚡ **Variable Elimination** | Thuật toán suy luận chính xác (exact inference) |
| 🏥 **Noisy-OR Model** | Xử lý đa nguyên nhân gây triệu chứng |
| 📊 **Dữ liệu Y khoa Thực tế** | Sensitivity/Specificity từ CDC, WHO, NIH |
| 🎨 **Giao diện Chuyên nghiệp** | Dark medical theme với Chart.js |
| ⚠️ **Risk Factors** | Hỗ trợ 6 yếu tố nguy cơ điều chỉnh xác suất |

### Phạm vi Chẩn đoán

**7 bệnh** thuộc nhóm viêm đường hô hấp cấp & sốt:

| Bệnh | ICD-10 | Prior |
|:---|:---:|:---:|
| Influenza (Cúm mùa) | J09-J11 | 15% |
| COVID-19 | U07.1 | 10% |
| Bacterial Pneumonia (Viêm phổi vi khuẩn) | J15 | 5% |
| Acute Bronchitis (Viêm phế quản cấp) | J20 | 20% |
| Common Cold (Cảm lạnh) | J00 | 35% |
| Pertussis (Ho gà) | A37 | 3% |
| Tuberculosis (Lao phổi) | A15 | 2% |

---

## 🏗️ Kiến trúc Hệ thống

```
┌──────────────────────┐     HTTP/REST      ┌──────────────────────┐
│     Frontend         │ ◄──────────────────►│     Backend          │
│  (HTML/CSS/JS)       │    /api/diagnose    │   (FastAPI)          │
│  Chart.js            │    /api/symptoms    │                      │
│  Material Icons      │    /api/diseases    │  ┌────────────────┐  │
└──────────────────────┘                     │  │ Bayesian       │  │
                                             │  │ Network        │  │
                                             │  │   ┌──────────┐ │  │
                                             │  │   │ Variable │ │  │
                                             │  │   │ Elimin.  │ │  │
                                             │  │   └──────────┘ │  │
                                             │  │   ┌──────────┐ │  │
                                             │  │   │ Noisy-OR │ │  │
                                             │  │   │ CPTs     │ │  │
                                             │  │   └──────────┘ │  │
                                             │  └────────────────┘  │
                                             │  ┌────────────────┐  │
                                             │  │ Knowledge Base │  │
                                             │  │ (CDC/WHO/NIH)  │  │
                                             │  └────────────────┘  │
                                             └──────────────────────┘
```

### Thuật toán Variable Elimination

```
Input: Factors F, Query Q, Evidence E

1. Restrict factors theo evidence E
2. Xác định hidden variables H = All \ Q \ E
3. Sắp xếp H theo min-degree heuristic
4. For each h ∈ H:
   a. Collect factors chứa h
   b. Product all collected factors
   c. Marginalize (sum out) h
   d. Add result factor back
5. Product remaining factors
6. Normalize → P(Q | E)
```

### Mô hình Noisy-OR

```
P(Symptom=1 | D₁, ..., Dₙ) = 1 - (1 - p_leak) × ∏ᵢ (1 - pᵢ)^Dᵢ
```

Trong đó:
- `pᵢ` = sensitivity: P(Symptom | Disease_i = True)
- `p_leak` = xác suất triệu chứng do nguyên nhân khác
- `Dᵢ ∈ {0, 1}` = trạng thái bệnh

---

## 🚀 Cài đặt & Chạy

### Yêu cầu
- Python 3.10+
- pip (Python package manager)

### Cài đặt

```bash
# Clone repository
git clone <repo-url>
cd midtermPJ

# Cài đặt dependencies
pip install -r backend/requirements.txt
```

### Chạy ứng dụng

```bash
# Khởi động server
uvicorn backend.main:app --reload --port 8000

# Mở trình duyệt
# http://localhost:8000
```

### Chạy tests

```bash
# Test toàn bộ hệ thống
python tests/test_system.py

# Test chi tiết với báo cáo
python tests/experimental_results.py

# Tạo biểu đồ dataset
python tests/visualize_dataset.py
```

---

## 📖 Hướng dẫn Sử dụng

### Bước 1: Chọn triệu chứng
Nhấp vào các thẻ triệu chứng ở panel bên trái. Triệu chứng được chia theo nhóm:
- **Dấu hiệu sinh tồn**: Sốt, Sốt cao
- **Hô hấp**: Ho, Ho khan, Ho có đờm, Khó thở, Thở khò khè
- **Hô hấp trên**: Đau họng, Chảy mũi, Hắt xì
- **Toàn thân**: Đau đầu, Đau cơ, Mệt mỏi, Ớn lạnh, Đổ mồ hôi đêm, Sụt cân, Ho ra máu
- **Thần kinh**: Mất vị giác/khứu giác

### Bước 2: Chọn yếu tố nguy cơ (tùy chọn)
Nếu bệnh nhân có yếu tố nguy cơ, chọn thêm: Hút thuốc, Cao tuổi, Suy giảm miễn dịch, v.v.

### Bước 3: Nhấn "Chẩn đoán"
Hệ thống sẽ chạy thuật toán Variable Elimination và hiển thị:
- **Chẩn đoán hàng đầu** với xác suất
- **Biểu đồ thanh** phân phối xác suất tất cả 7 bệnh
- **Bảng xếp hạng** chi tiết từng bệnh

---

## 📊 Dataset & Mô hình

### Nguồn dữ liệu

| Nguồn | Loại dữ liệu |
|:---|:---|
| **CDC** (Centers for Disease Control) | Prevalence, Incidence |
| **WHO** (World Health Organization) | Global epidemiology |
| **NIH / PubMed** | Sensitivity, Specificity |
| **Harrison's Principles of Internal Medicine** | Clinical parameters |

### Thống kê Dataset

- **133** giá trị sensitivity (19 symptoms × 7 diseases)
- **133** giá trị specificity (19 symptoms × 7 diseases)
- **19** leak probabilities (Noisy-OR)
- **42** risk factor modifiers (6 factors × 7 diseases)
- **Tổng: ~360 data points**

---

## 🧪 Kết quả Thử nghiệm

### Unit Tests: 7/7 PASSED (100%)

| Test | Kết quả |
|:---|:---:|
| Prior Factor Creation | ✅ |
| Factor Product | ✅ |
| Factor Marginalization | ✅ |
| Factor Reduction (Evidence) | ✅ |
| Factor Normalization | ✅ |
| Noisy-OR Monotonicity | ✅ |
| Probability Range [0,1] | ✅ |

### Clinical Scenarios: 9/10 CORRECT (90%)

| Ca lâm sàng | Chẩn đoán | Xác suất | Confidence Gap |
|:---|:---|:---:|:---:|
| Cúm điển hình | ✅ Influenza | 90.4% | 64.7% |
| COVID-19 (mất khứu giác) | ✅ COVID-19 | 91.0% | 68.7% |
| Viêm phổi vi khuẩn | ✅ Pneumonia | 88.5% | 64.0% |
| Cảm lạnh | ✅ Common Cold | 98.3% | 83.5% |
| Viêm phế quản cấp | ✅ Bronchitis | 77.6% | 59.7% |
| Ho gà | ⚠️ Bronchitis | 44.7% | 8.8% |
| Lao phổi | ✅ TB | 99.7% | 81.6% |
| Ca mơ hồ | ✅ Bronchitis | 53.8% | 31.5% |
| COVID-19 nặng | ✅ COVID-19 | 86.8% | 25.1% |
| Cúm vs Cảm lạnh | ✅ Cold | 93.0% | 67.2% |

---

## 📁 Cấu trúc Project

```
midtermPJ/
├── backend/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app + REST endpoints
│   ├── knowledge_base.py        # Disease/symptom data, Noisy-OR CPTs
│   ├── factor.py                # Factor class for VE operations
│   ├── bayesian_network.py      # Bayesian Network builder
│   ├── variable_elimination.py  # VE algorithm implementation
│   └── requirements.txt
├── frontend/
│   ├── index.html               # Main UI page
│   ├── style.css                # Dark medical theme
│   └── app.js                   # API integration + Chart.js
├── tests/
│   ├── test_system.py           # Unit & integration tests
│   ├── experimental_results.py  # Comprehensive test report
│   └── visualize_dataset.py     # Dataset visualization charts
├── visualizations/              # Generated charts (PNG)
├── knowledgeBase.md             # KB design document
├── finalGuide.md                # Project requirements
└── README.md                    # This file
```

---

## 🛠️ Công nghệ Sử dụng

| Thành phần | Công nghệ |
|:---|:---|
| **Backend** | Python 3.10+, FastAPI, NumPy |
| **Frontend** | HTML5, CSS3, JavaScript (ES6+) |
| **Visualization** | Chart.js 4.4, Matplotlib, Seaborn |
| **Icons** | Google Material Symbols |
| **Fonts** | Inter (Google Fonts) |
| **AI/ML** | Bayesian Networks, Variable Elimination, Noisy-OR |

---

## ⚠️ Lưu ý

> Hệ thống chỉ mang tính chất **demo học thuật** cho môn Advanced AI.
> **Không thay thế** chẩn đoán y khoa chuyên nghiệp từ bác sĩ.

---

## 👤 Tác giả

- **Nhóm trưởng**: Nguyễn Đăng Hùng Dũng
- **Thành viên**: Lưu Thiên Long, Trần Thị Mai Phương
- **Trường**: Open University - Trường Đại Học Mở Thành Phố Hồ Chí Minh
- **Môn học**: Advanced AI — Midterm Project


---

## 📚 Tài liệu Tham khảo

1. Koller, D. & Friedman, N. (2009). *Probabilistic Graphical Models: Principles and Techniques*. MIT Press.
2. Russell, S. & Norvig, P. (2020). *Artificial Intelligence: A Modern Approach*, 4th Ed, Chapter 13-14.
3. CDC. Influenza (Flu) Surveillance Reports. https://www.cdc.gov/flu/
4. WHO. COVID-19 Dashboard. https://covid19.who.int/
5. Harrison's Principles of Internal Medicine, 21st Edition (2022).
