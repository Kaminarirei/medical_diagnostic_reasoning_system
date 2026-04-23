### 1. Thành phần cốt lõi của Knowledge Base (KB)
Để xây dựng KB, bạn cần xác định các thành phần chính cấu thành nên Mạng Bayesian cho chuẩn đoán y khoa:

*   **Các biến số (Nodes):**
    *   **Bệnh (Diseases - D):** Các nút đại diện cho trạng thái của bệnh nhân (có bệnh hoặc không).
    *   **Triệu chứng/Phát hiện lâm sàng (Symptoms/Findings - S/F):** Các biểu hiện cụ thể quan sát được.
    *   **Các yếu tố nguy cơ (Risk Factors - R):** Các tiền sử bệnh lý, di truyền hoặc lối sống ảnh hưởng đến xác suất mắc bệnh.
*   **Các liên kết phụ thuộc (Arcs/Edges):** Các mũi tên hướng từ nguyên nhân (bệnh/yếu tố nguy cơ) đến kết quả (triệu chứng) để thể hiện quan hệ nhân quả.
*   **Bảng xác suất có điều kiện (CPT):** Đây là "linh hồn" của KB, định lượng mức độ tác động của các nút cha lên nút con.

### 2. Xây dựng Cơ sở tri thức từ số liệu thống kê không đầy đủ
Thách thức lớn nhất trong y khoa là bạn thường chỉ có dữ liệu về độ nhạy và độ đặc hiệu của từng bệnh riêng lẻ thay vì xác suất chung của nhiều bệnh kết hợp.

*   **Sử dụng mô hình Noisy-OR:** Đây là kỹ thuật quan trọng nhất để xây dựng KB khi một triệu chứng (F) có thể do nhiều bệnh ($D_1, D_2, \dots, D_n$) gây ra một cách độc lập.
    *   Xác định **Xác suất liên kết ($p_i$):** Khả năng bệnh $D_i$ đứng đơn lẻ gây ra triệu chứng F.
    *   Xác định **Xác suất rò rỉ ($p_L$ - Leak probability):** Đại diện cho các nguyên nhân chưa được mô hình hóa hoặc sai số đo lường gây ra triệu chứng.
    *   KB sẽ tính toán xác suất tổng hợp triệu chứng xuất hiện khi có nhiều bệnh là: $P(F|D_1, \dots, D_n) = 1 - [(1-p_L) \times \prod_{D_i \in Positive} (1-p_i)]$.
*   **Chuyển đổi Độ nhạy/Độ đặc hiệu:** Bạn có thể tính toán $p_i$ từ các chỉ số y khoa thông thường theo công thức: $p_i = \frac{P(F|D_i) - P(F|\neg D_i)}{1 - P(F|\neg D_i)}$.

### 3. Tối ưu hóa cấu trúc KB để tránh "Quá tự tin" (Overconfidence)
Hệ thống có thể đưa ra kết luận quá mức nếu các triệu chứng không hoàn toàn độc lập.

*   **Sử dụng Cụm Boolean (Boolean Clusters):** Nếu nhiều phát hiện lâm sàng cùng phụ thuộc vào một trạng thái bệnh lý trung gian, hãy thêm một nút trung gian (Intermediate node) sử dụng các cổng logic như **AND, OR, NOT**.
*   **Kiểm soát sự phụ thuộc có điều kiện:** Khi hai triệu chứng liên quan chặt chẽ với nhau (ví dụ: khó thở và thở nhanh), KB cần thêm các liên kết trực tiếp giữa các triệu chứng để phản ánh đúng thực tế lâm sàng.

### 4. Cơ chế suy luận trong hệ thống
Mặc dù bạn sử dụng **Variable Elimination**, KB cần cung cấp dữ liệu đầu vào phù hợp cho thuật toán này:

*   **Xác suất tiên nghiệm (Prior Probability):** Tỷ lệ hiện mắc của bệnh trong cộng đồng ($P(D)$).
*   **Xác suất hậu nghiệm (Posterior Probability):** Khi người dùng nhập triệu chứng (Evidence - E), thuật toán Variable Elimination sẽ tính $P(D|E)$ bằng cách triệt tiêu các biến không liên quan để tìm ra xác suất bệnh.
*   **Lập luận loại trừ (Reasoning and Elimination):** Hệ thống sẽ cập nhật niềm tin dựa trên từng bằng chứng mới, các bệnh không giải thích được triệu chứng sẽ dần có xác suất thấp đi.

### 5. Nâng cao độ chính xác bằng Lập luận Phản thực (Counterfactual Reasoning)
Để đạt độ chính xác tương đương chuyên gia, KB của bạn không chỉ nên dựa trên sự tương quan (associative) mà còn phải dựa trên nguyên nhân thực sự.

*   **Xác định trách nhiệm nhân quả:** Thay vì chỉ tìm bệnh có tương quan cao nhất, hãy lập luận xem triệu chứng có biến mất không nếu bệnh đó được "chữa khỏi" (Intervention: $do(D=False)$).
*   **Hai chỉ số đo lường:**
    1.  **Expected Disablement:** Số triệu chứng hiện có dự kiến sẽ biến mất nếu bệnh D được loại bỏ.
    2.  **Expected Sufficiency:** Số triệu chứng hiện có dự kiến sẽ vẫn tồn tại nếu loại bỏ mọi nguyên nhân khác ngoại trừ bệnh D.

### Cấu trúc tóm tắt của Knowledge Base:

| Thành phần | Nguồn dữ liệu/Công thức | Vai trò trong dự án |
| :--- | :--- | :--- |
| **Priors** | Dữ liệu dịch tễ học (Prevalence) | Xác suất ban đầu khi chưa có triệu chứng. |
| **Sensitivity** | $P(S|D)$ từ y văn | Khả năng bệnh gây ra triệu chứng. |
| **Specificity** | $P(\neg S|\neg D)$ từ y văn | Khả năng không có triệu chứng khi không có bệnh. |
| **Noisy-OR Logic** | Công thức rò rỉ và liên kết | Kết hợp nhiều nguyên nhân gây một triệu chứng. |
| **Boolean Gates** | Cổng logic AND/OR trung gian | Xử lý sự phụ thuộc giữa các triệu chứng. |
| **Causal Weights** | Counterfactual probabilities | Tăng độ chính xác cho các bệnh hiếm. |
