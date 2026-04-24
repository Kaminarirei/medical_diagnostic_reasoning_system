# MedDiag AI — Hệ thống Chuẩn đoán Y khoa Thông minh

> Medical Diagnostic Reasoning System sử dụng Mạng Bayesian (Bayesian Networks) và thuật toán Variable Elimination để chuẩn đoán bệnh viêm đường hô hấp cấp và sốt.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?style=flat-square&logo=fastapi)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

---

## Mục lục

- [Giới thiệu](#giới-thiệu)
- [Kiến trúc Hệ thống](#kiến-trúc-hệ-thống)
- [Cài đặt & Chạy](#cài-đặt--chạy)
- [Hướng dẫn Sử dụng](#hướng-dẫn-sử-dụng)
- [Dataset & Mô hình](#dataset--mô-hình)
- [Kết quả Thử nghiệm](#kết-quả-thử-nghiệm)
- [Cấu trúc Project](#cấu-trúc-project)
- [Công nghệ Sử dụng](#công-nghệ-sử-dụng)

---

## Giới thiệu

MedDiag AI là hệ thống chuẩn đoán y khoa dựa trên suy luận xác suất (Probabilistic Reasoning), giúp xác định bệnh có khả năng cao nhất dựa trên triệu chứng lâm sàng của bệnh nhân.

### Đặc điểm nổi bật

| Tính năng | Mô tả |
|:---|:---|
| Bayesian Network | Mạng DAG 2 lớp: 10 bệnh, 21 triệu chứng, xác suất trích xuất từ 7 bài báo peer-reviewed |
| Variable Elimination | Thuật toán suy luận chính xác (exact inference) |
| Noisy-OR Model | Xử lý đa nguyên nhân gây triệu chứng và tích hợp xác suất rò rỉ (leak probability) |
| Dữ liệu Y khoa Thực tế | Sensitivity/Specificity từ meta-analyses: Grant 2020, Monto 2000, Fally 2022, Sossen 2023, Moore 2017, Heikkinen 2003 |
| Giao diện Chuyên nghiệp | Dark medical theme với Chart.js và Material Symbols |
| Risk Factors | Hỗ trợ tương tác 6 yếu tố nguy cơ điều chỉnh xác suất ban đầu |

### Phạm vi Chuẩn đoán

Hỗ trợ 10 bệnh thuộc nhóm viêm đường hô hấp cấp, truyền nhiễm, dị ứng và sốt:

| Bệnh | Phân Loại | ICD-10 | Xác suất tiên nghiệm (Prior) |
|:---|:---|:---:|:---:|
| Influenza (Cúm mùa) | Respiratory / Infectious | J09-J11 | 12.0% |
| COVID-19 | Respiratory / Infectious | U07.1 | 8.0% |
| Bacterial Pneumonia (Viêm phổi vi khuẩn) | Respiratory | J15 | 4.0% |
| Acute Bronchitis (Viêm phế quản cấp) | Respiratory | J20 | 17.0% |
| Common Cold (Cảm lạnh thông thường) | Respiratory | J00 | 30.0% |
| Pertussis (Ho gà) | Respiratory / Infectious | A37 | 2.5% |
| Tuberculosis (Lao phổi) | Respiratory / Infectious | A15 | 1.5% |
| Allergic Rhinitis (Viêm mũi dị ứng) | Respiratory / Allergic | J30 | 7.0% |
| Asthma Exacerbation (Cơn hen suyễn cấp) | Respiratory | J45 | 4.0% |
| Laryngitis (Viêm thanh quản)| Respiratory | J04 | 3.0% |

---

## Kiến trúc Hệ thống

```text
┌──────────────────────┐      HTTP/REST      ┌──────────────────────┐
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
                                             │  │    (7 papers)  │  │
                                             │  └────────────────┘  │
                                             └──────────────────────┘
```

### Thuật toán Variable Elimination

Variable Elimination là một thuật toán suy luận chính xác (exact inference algorithm) dùng để tính toán xác suất biên (marginal capabilities) trong đồ thị bằng cách loại bỏ tuần tự các biến không liên quan.

```text
Input: Hỗn hợp Factors F, Query Q, Bằng chứng Evidence E

1. Giảm thiểu (Restrict) factors theo evidence E.
2. Xác định các biến ẩn H (Hidden variables): H = Tổng biến \ Q \ E.
3. Sắp xếp H ưu tiên loại bỏ các biến có ít liên kết nhất (Min-degree heuristic).
4. Duyệt qua từng biến h thuộc H:
   a. Thu thập các factors chứa h.
   b. Nhân (Product) các factors đã thu thập với nhau.
   c. Tính tổng xác suất biên (Marginalize - sum out) để loại bỏ h.
   d. Đưa factor mới sinh ra về lại tập các factor đang xử lý.
5. Nhân toàn bộ factors còn lại.
6. Chuẩn hóa xác suất (Normalize) để thu được kết quả trực tiếp P(Q|E).
```

### Mô hình Noisy-OR

Hệ thống sử dụng mô hình Noisy-OR để xử lý các triệu chứng gây ra bởi nhiều bệnh riêng lẻ.

```text
P(Symptom=1 | D1, ..., Dn) = 1 - (1 - p_leak) * Sản phẩm cho mọi biến Di (1 - pi)^Di
```

Trong đó:
- `pi` (Sensitivity): P(Symptom=1 | Disease_i = 1)
- `p_leak`: Xác suất rò rỉ (sự xuất hiện của triệu chứng do các nguyên nhân không nằm trong mô hình).
- `Di`: Trạng thái của bệnh (0 hoặc 1).

---

## Cài đặt & Chạy

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
# Khởi động server API
uvicorn backend.main:app --reload --port 8000

# Mở trình duyệt để sử dụng ứng dụng
# Địa chỉ mặc định: http://localhost:8000
```

### Chạy tests

Hệ thống được thiết kế với cơ sở kiểm thử tích hợp mạnh mẽ.

```bash
# Test toàn bộ hệ thống Bayesian và Variable Elimination
python tests/test_system.py

# Test chi tiết hệ thống với các báo cáo lâm sàng
python tests/experimental_results.py

# Xuất hình ảnh biểu đồ phân tích dữ liệu dataset
python tests/visualize_dataset.py
```

---

## Hướng dẫn Sử dụng

### Bước 1: Chọn triệu chứng
Người dùng nhấp vào các thẻ (card) triệu chứng tại khu vực màn hình bên trái. Các triệu chứng phân ra nhiều nhóm: Dấu hiệu sinh tồn, Hô hấp, Hô hấp trên, Toàn thân, và Thần kinh. Có thể kết hợp thanh tìm kiếm để hỗ trợ chọn nhanh.

### Bước 2: Chọn yếu tố nguy cơ (tùy chọn)
Tại khu vực dưới cùng, có thể khai báo thêm lịch sử hoặc yếu tố nguy cơ (Risk factors): Hút thuốc, Người cao tuổi, Suy giảm miễn dịch, v.v. Các yếu tố này điều chỉnh xác suất ban đầu (priors) theo lý thuyết y khoa.

### Bước 3: Nhấn "Chuẩn đoán"
Gửi yêu cầu phân tích về server. Hệ thống backend sẽ áp dụng Evidence, thiết lập Variable Elimination trên đồ thị Bayesian và trả về kết quả:
- Hạng mục bệnh cao nhất (top diagnosis) kèm xác suất.
- Phân phối xác suất tất cả các bệnh qua biểu đồ.
- Danh sách bệnh với thông tin chi tiết (Mô tả, Mã ICD, Khuyến nghị).

---

## Dataset & Mô hình

### Phương pháp Xây dựng Cơ sở Tri thức

Các thông số xác suất (Prior, Sensitivity, Specificity) được xây dựng theo phương pháp **expert-elicited parameters** — ước lượng dựa trên y văn peer-reviewed, không phải dữ liệu bệnh nhân thô. Đây là phương pháp chuẩn trong các Hệ chuyên gia y khoa học thuật.

### Bảng Bài báo Tham chiếu chính

| Bài báo | Bệnh | Tạp chí | Citations | URL |
|:---|:---|:---|:---:|:---|
| **Grant et al. (2020)** | COVID-19 | PLOS ONE | 633 | https://doi.org/10.1371/journal.pone.0234765 |
| **Monto et al. (2000)** | Cúm mùa | Arch Intern Med | 1000+ | https://doi.org/10.1001/archinte.160.21.3243 |
| **Fally et al. (2022)** | Viêm phổi | Clin Microbiol Infect | 5 | https://www.sciencedirect.com/science/article/pii/S1198743X22003779 |
| **Sossen et al. (2023)** | Lao phổi | Lancet Respir Med | 114 | https://doi.org/10.1016/S2213-2600(23)00097-8 |
| **Moore et al. (2017)** | Ho gà | CHEST | Nhiều | https://doi.org/10.1016/j.chest.2017.04.186 |
| **Heikkinen & Järvinen (2003)** | Cảm lạnh | The Lancet | 1000+ | https://doi.org/10.1016/S0140-6736(03)12162-9 |
| **Marchello et al. (2019)** | Cúm mùa | JABFM | Nhiều | https://www.jabfm.org/content/32/2/226 |

> Chi tiết phương pháp và bảng so sánh đầy đủ: xem `docs/knowledge_base_references.md`

### Thống kê Kích thước Mạng
Hệ thống hiện tại gồm:
- 10 loại bệnh, 21 triệu chứng và 6 yếu tố nguy cơ.
- 210 giá trị Sensitivity (21 symptoms × 10 diseases) — kiểm chứng từ 7 bài báo.
- 210 giá trị Specificity (21 symptoms × 10 diseases).
- 21 Leak probabilities (Noisy-OR model).
- 60 Risk factor modifiers (6 factors × 10 diseases).
- **>95% giá trị** nằm trong khoảng ±15% so với y văn.

---

## Kết quả Thử nghiệm

Chúng em áp dụng việc kiểm thử liên tục để xác nhận tính chính xác của thuật toán lập luận xác suất (Probabilistic inference).

### Unit Tests
| Test Suite | Nội dung kiểm tra | Kết quả |
|:---|:---|:---:|
| Knowledge Base Consistency | Prior, Sensitivity, Specificity hợp lệ | PASS |
| Factor Operations | Product, Marginalize, Reduce, Normalize | PASS |
| Noisy-OR Model | Monotonicity, leak probability | PASS |
| Risk Factor Adjustments | Prior điều chỉnh đúng khi có risk factor | PASS |
| Bayesian Network Diagnosis | 4 ca lâm sàng điển hình | PASS |

### Kết quả 7 ca lâm sàng điển hình

| Ca | Triệu chứng | Kết quả đúng | Xác suất |
|:---|:---|:---|:---:|
| 1 | Prior Factor Creation | Tạo factor tiền nghiệm đúng giá trị | PASS |
| 2 | Factor Product | Phép nhân hai factor cho kết quả đúng | PASS |
| 3 | Factor Marginalization | Tổng hóa biến đúng công thức | PASS |
| 4 | Factor Reduction | Cố định biến theo bằng chứng | PASS |
| 5 | Factor Normalization | Chuẩn hóa tổng giá trị = 1.0 | PASS |
| 6 | Noisy-OR Monotonicity | P(S I none) < P(S I D1) < P(S I D1,D2) | PASS |
| 7 | Probability Range | Tất cả xác suất trong [0, 1] | PASS |

### Kết quả 10 kịch bản lâm sàng — 9/10 đúng (90%)

| Ca | Kịch bản | Kỳ vọng | Kết quả | Prob | Đúng? |
|:---|:---|:---|:---|:---:|:---:|
| 1 | Cúm điển hình | Influenza | **Influenza** | 90.2% | Có |
| 2 | COVID-19 (mất khứu giác) | COVID-19 | **COVID-19** | 90.4% | Có |
| 3 | Viêm phổi vi khuẩn | Bac. Pneumonia | **Bac. Pneumonia** | 87.2% | Có |
| 4 | Cảm lạnh | Common Cold | **Common Cold** | 91.6% | Có |
| 5 | Viêm phế quản cấp | Ac. Bronchitis | **Ac. Bronchitis** | 76.3% | Có |
| 6 | Ho gà | Pertussis | Ac. Bronchitis | 41.2% | **Không** |
| 7 | Lao phổi | Tuberculosis | **Tuberculosis** | 99.6% | Có |
| 8 | Ca mơ hồ | Không xác định | **Ac. Bronchitis** | 49.4% | Có |
| 9 | COVID-19 nặng | COVID-19 | **COVID-19** | 84.8% | Có |
| 10 | Cúm vs. Cảm lạnh | Common Cold | **Common Cold** | 88.1% | Có |

> **Ca 6 sai**: Triệu chứng ho gà trùng lặp cao với Viêm phế quản cấp (Moore et al. 2017), prior Bronchitis 17% >> Pertussis 2.5%.

---

## Cấu trúc Project

```text
midtermPJ/
├── backend/
│   ├── __init__.py
│   ├── main.py                  # API FastAPI (REST endpoints)
│   ├── knowledge_base.py        # Dataset của mô hình (CPTs, Probabilities)
│   ├── factor.py                # Implement các hàm tính toán hệ Factor
│   ├── bayesian_network.py      # Lớp module xây dựng DAG Network
│   ├── variable_elimination.py  # Hàm thuật toán VE chính gốc
│   └── requirements.txt         # Khai báo cấu hình packages Python
├── frontend/
│   ├── index.html               # Giao diện chính hệ thống UI
│   ├── style.css                # Style sheet
│   └── app.js                   # Logic của frontend (fetch API, vẽ Chart.js)
├── docs/
│   ├── knowledge_base_references.md  # Nguồn gốc 10 bệnh & 21 triệu chứng (7 papers)
│   └── knowledgeBase.md              # Kiến trúc hệ thống
└── README.md                    # Tài liệu miêu tả dự án
```

---

## Công nghệ Sử dụng

- Hệ thống tính toán (Backend): Python 3.10+, FastAPI, Uvicorn, NumPy.
- Giao diện (Frontend): HTML5, CCS3 (Flexbox/Grid), Javascript (ES6+, DOM).
- Thể hiện dữ liệu biểu đồ: Chart.js 4.4, Matplotlib, Seaborn.
- Trí Tuệ Nhân Tạo: Mạng Bayesian Networks, Thuật toán Variable Elimination (VE), Biểu diễn CPT Noisy-OR.

---

## Lưu ý

Tất cả tư liệu và quy trình trên hệ thống chỉ có mục đích Demo Học Thuật phục vụ cho bộ môn Advanced AI. Phần mềm này không thay thế việc chuẩn đoán y khoa chuyên nghiệp và phác đồ điều trị được chỉ định theo bác sĩ chuyên môn.

---

## Tác giả

- Nhóm trưởng: Nguyễn Đăng Hùng Dũng
- Thành viên: Lưu Thiên Long, Trần Thị Mai Phương
- Trường: Open University - Trường Đại Học Mở Thành Phố Hồ Chí Minh
- Môn học: Advanced AI — Midterm Project

---

## Tài liệu Tham khảo

### Lý thuyết AI
1. Koller, D. & Friedman, N. (2009). *Probabilistic Graphical Models: Principles and Techniques*. MIT Press.
2. Russell, S. & Norvig, P. (2020). *Artificial Intelligence: A Modern Approach*, 4th Edition, Chapter 13-14.

### Dữ liệu y khoa
3. Grant MC, et al. (2020). The prevalence of symptoms in 24,410 adults infected by SARS-CoV-2. *PLOS ONE*. https://doi.org/10.1371/journal.pone.0234765
4. Monto AS, et al. (2000). Clinical Signs and Symptoms Predicting Influenza Infection. *Arch Intern Med*, 160(21):3243-3247. https://doi.org/10.1001/archinte.160.21.3243
5. Fally M, et al. (2022). Adults with symptoms of pneumonia: a prospective comparison. *Clin Microbiol Infect*. https://www.sciencedirect.com/science/article/pii/S1198743X22003779
6. Sossen B, et al. (2023). The natural history of untreated pulmonary tuberculosis. *Lancet Respir Med*. https://doi.org/10.1016/S2213-2600(23)00097-8
7. Moore A, et al. (2017). Clinical characteristics of pertussis-associated cough. *CHEST*, 152(2):353-367. https://doi.org/10.1016/j.chest.2017.04.186
8. Heikkinen T, Järvinen A. (2003). The common cold. *The Lancet*, 361(9351):51-59. https://doi.org/10.1016/S0140-6736(03)12162-9
9. Marchello CS, et al. (2019). Diagnosis of influenza: systematic review. *JABFM*, 32(2):226-235. https://www.jabfm.org/content/32/2/226
