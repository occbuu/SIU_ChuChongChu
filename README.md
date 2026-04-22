# 📚 Pipeline phân tích dữ liệu khảo sát: Bộ thủ & Chữ chồng chữ

**Đề tài:** *Bộ thủ và cấu trúc chữ chồng chữ trong chữ Hán từ góc nhìn của người Việt: Đặc điểm, giá trị văn hóa và ứng dụng trong dạy học*

**Mẫu:** N = 548 người Việt đang học tiếng Trung, khảo sát 59 câu hỏi qua 6 phần (S1–S6)

---

## 🗂 Cấu trúc thư mục

```
/
├── Data.xlsx                           # Dữ liệu gốc (3 sheet: Data, Questions, Sections)
├── prep_data.py                        # Module chuẩn bị dữ liệu (dùng chung cho 4 notebook)
├── 01_DataPreparation_EDA.ipynb        # Notebook 1: Chuẩn bị dữ liệu + EDA
├── 02_Quantitative_Analysis.ipynb      # Notebook 2: Phân tích định lượng
├── 03_Qualitative_Analysis.ipynb       # Notebook 3: Phân tích định tính
└── 04_Advanced_Analysis.ipynb          # Notebook 4: Phân tích nâng cao (Q1 level)
```

## ⚙️ Cài đặt môi trường

```bash
pip install pandas numpy matplotlib seaborn scipy scikit-learn==1.5.* \
    statsmodels pingouin factor_analyzer wordcloud openpyxl pyarrow \
    prince kmodes networkx
```

**Lưu ý:** `factor_analyzer 0.5.1` cần `scikit-learn < 1.6` (vì API `force_all_finite` đã đổi).

## ▶️ Cách sử dụng

1. **Đặt** `Data.xlsx` cùng thư mục với các notebook (hoặc sửa `DATA_PATH` trong từng notebook).
2. **Chạy theo thứ tự 01 → 02 → 03 → 04** (notebook 01 lưu `df_clean.parquet` để các notebook sau đọc nhanh hơn).
3. **Module `prep_data.py`** phải nằm cùng thư mục với các notebook.

## 📊 Nội dung chính mỗi notebook

### Notebook 01 — Data Preparation & EDA
- Đọc 3 sheet từ Excel (Data, Questions, Sections)
- Chuẩn hoá 32 biến Likert (8 thang đo khác nhau) với 2 reverse-coded items
- Smart-parser cho 8 câu multi-select (xử lý dấu phẩy trong nhãn lựa chọn)
- Mô tả mẫu (demographics), missing values audit
- Tính 4 điểm tổng hợp: HV_score, POST_score, PRACTICE_score, SEM_score
- **Hình 1-2:** Demographics overview, composite distributions

### Notebook 02 — Quantitative Analysis
- **Cronbach's α** (với 95% CI + item-total + α-if-deleted)
  - HV_Advantage: α = 0.928 (Excellent)
  - POST_Attitude: α = 0.967 (Excellent)
  - Practice: α = 0.288 (formative scale, không áp dụng)
- **Chi-square + Cramér's V** (Bergsma 2013 corrected) với FDR Benjamini-Hochberg
- **Kruskal-Wallis + ε²** so sánh theo HSK (SEM_score có ε²=0.15 — large)
- **Dunn's post-hoc** với Bonferroni
- **Spearman's ρ** matrix
- **Mann-Whitney U + rank-biserial** cho so sánh 2 nhóm
- **Bảng 2.1–2.7 + Hình 3–7**

### Notebook 03 — Qualitative Analysis
- Multi-select frequencies cho 8 câu (Q9, Q12, Q21, Q22, Q26, Q41, Q42, Q48)
- **Co-occurrence matrix + Jaccard similarity** cho Q48 (phương pháp mong muốn)
- **NetworkX graph** của phương pháp đồng xuất hiện
- Phân tích chi tiết Q30–Q37 (nhận diện nghĩa 8 chữ chồng chữ)
- **IRT-style difficulty ranking** (logit)
- **Thematic coding** Q60 (8 chủ đề)
- **Word cloud** + top 25 từ
- Cross-tab Q12 × Q46 (khó khăn × mong muốn)
- **Bảng 3.1–3.11 + Hình 8–17**

### Notebook 04 — Advanced Analysis (Q1-publication level)
- **Exploratory Factor Analysis (EFA)**
  - KMO = 0.856 (Meritorious), Bartlett p < 0.001
  - Kaiser + Parallel Analysis → 6 nhân tố
  - **65.6% variance explained** (chuẩn Q1: ≥60%)
  - 6 nhân tố: Động cơ học / Cảm nhận sau KS / HV Advantage / Nhận diện HV↔Hán / Chú ý bộ thủ / Khó khăn
- **Ordinal Logistic Regression**
  - N=548, Pseudo R² = 0.202, LR χ²(7) = 260.37 ***
  - Predictor mạnh nhất: **Yêu thích (OR = 3.49)**, SEM (OR=1.55), HV (OR=1.45)
  - Kiểm tra Proportional Odds assumption (SD < 0.3 cho các predictor chính → thoả mãn)
- **Correspondence Analysis (CA)** — HSK × Top 5 phương pháp mong muốn
- **K-modes Cluster Analysis** (K=4):
  - **C0 (43%)**: Enthusiastic beginners
  - **C1 (25%)**: Casual learners
  - **C2 (20%)**: Advanced enthusiasts
  - **C3 (12%)**: Mature steady
- **Item Response Theory**:
  - Rasch-style difficulty + point-biserial discrimination
  - Item Characteristic Curves (ICC)
  - Test Information Function (TIF)
- **Bảng 4.1–4.7 + Hình 18–25**

## 🏆 Phát hiện chính cho công bố Q1

1. **Thang HV_Advantage có độ tin cậy xuất sắc** (α=0.928, 95% CI [0.918, 0.938])
2. **Nhận thức giá trị Hán-Việt cao và phổ quát**: M=4.12/5, không khác theo HSK (ns)
3. **Năng lực nhận diện nghĩa tăng mạnh theo HSK**: ε²=0.15 (large effect)
4. **Yêu thích là động cơ số 1**: OR=3.49 trong ordinal logit
5. **Môi trường học × HSK**: V=0.40 (strong) — người học trung tâm đạt HSK cao hơn
6. **4 persona người học** qua K-modes clustering — framework đầu tiên cho thiết kế giáo trình phân tầng
7. **Bài test IRT 8 items** cho nhận diện chữ chồng chữ — công cụ chuẩn hoá có thể tái sử dụng
8. **Cấu trúc 6 nhân tố** lần đầu tiên được xác thực ở quần thể người Việt học tiếng Trung

## ⚠️ Hạn chế cần thảo luận trong báo cáo

- **Cross-sectional**: không thể kết luận nhân quả
- **Sampling**: mẫu có thể không đại diện toàn quốc (stratification theo vùng)
- **Bài test IRT**: cần thêm item khó để đo chính xác người HSK5+
- **Practice scale α thấp (0.29)**: là formative scale, không phải reflective — cần thiết kế items mới nếu muốn xây dựng thang đo thực hành

## 📝 Trình tự đề xuất khi viết bài Q1

1. **Literature review** dựa trên:
   - Lý thuyết bộ thủ (214 bộ) + lục thư + Thuyết văn giải tự
   - Lý thuyết hội ý trùng điệp (字重字)
   - Han-Viet pronunciation advantage trong ngôn ngữ học
2. **Methods**: Trích từ Notebook 01 (demographics, instruments)
3. **Results**: 
   - Cronbach + descriptives (Notebook 02)
   - Multi-select + SEM patterns (Notebook 03)
   - EFA + Ordinal Logit + Clusters (Notebook 04)
4. **Discussion**:
   - 6-factor structure → đóng góp lý thuyết
   - OR=3.49 của yêu thích → implication cho giáo học pháp
   - 4 personae → khung phân tầng giảng dạy
5. **Conclusion + Limitations**

---

**Pipeline được xây dựng với chuẩn Q1:**
- ✅ Effect sizes đi kèm mọi p-value
- ✅ Multiple comparison correction (Benjamini-Hochberg FDR, Bonferroni)
- ✅ Assumption checks (KMO, Bartlett, Proportional Odds)
- ✅ Validation của model choices (scree plot, parallel analysis, elbow)
- ✅ Reproducible (random seeds, saved parquet, shared module)
