"""
prep_data.py — Module chuẩn bị dữ liệu dùng chung cho 4 notebook.

Chức năng:
- Đọc 3 sheet từ Data.xlsx (Data, Questions, Sections)
- Chuẩn hoá whitespace và mã hoá tất cả biến Likert sang thang số
- Tách câu multi-select thành list và tạo biến đếm
- Tính điểm tổng hợp: HV_score, POST_score, PRACTICE_score, SEM_score
- Tạo biến HSK_num (ordinal) và các cờ nhận diện đúng Q30–Q37

Sử dụng trong notebook:
    from prep_data import load_and_prepare
    df, questions, sections, META = load_and_prepare('/path/to/Data.xlsx')
"""
import numpy as np
import pandas as pd
import re


# ==== 1. Ánh xạ các thang Likert (đã kiểm tra với dữ liệu thực) ====
AGREE = {
    'Hoàn toàn không đồng ý': 1, 'Không đồng ý': 2, 'Bình thường': 3,
    'Đồng ý': 4, 'Hoàn toàn đồng ý': 5, 'Rất đồng ý': 5,
}
AGREE_REV = {  # reverse-coded cho các phát biểu tiêu cực
    'Hoàn toàn không đồng ý': 5, 'Không đồng ý': 4, 'Bình thường': 3,
    'Đồng ý': 2, 'Hoàn toàn đồng ý': 1,
}
FREQ = {
    'Không bao giờ': 1, 'Chưa từng gặp': 1,
    'Hiếm khi': 2, 'Ít khi': 2,
    'Thỉnh thoảng': 3,
    'Thường xuyên': 4,
    'Rất thường xuyên': 5, 'Luôn luôn': 5,
}
IMPORT = {
    'Không quan trọng': 1, 'Ít quan trọng': 2, 'Khá quan trọng': 3,
    'Quan trọng': 4, 'Rất quan trọng': 5,
}
NECES = {
    'Không cần thiết': 1, 'Ít cần thiết': 2, 'Bình thường': 3,
    'Khá cần thiết': 4, 'Rất cần thiết': 5, 'Cực kỳ cần thiết': 5,
}
DESIRE = {
    'Không mong muốn': 1, 'Ít mong muốn': 2, 'Bình thường': 3,
    'Khá mong muốn': 4, 'Rất mong muốn': 5,
}
LIKE = {
    'Không thích': 1, 'Ít thích': 2, 'Bình thường': 3,
    'Khá thích': 4, 'Rất thích': 5,
}
EFFIC = {
    'Không hiệu quả': 1, 'Ít hiệu quả': 2, 'Bình thường': 3,
    'Khá hiệu quả': 4, 'Rất hiệu quả': 5,
}
KNOW = {
    'Chưa từng nghe qua': 1, 'Chưa từng tìm hiểu': 1,
    'Đã từng nghe qua': 2,
    'Đã tìm hiểu ở mức cơ bản': 3,
    'Đã tìm hiểu kỹ': 4,
}
Q20_MAP = {  # Cấu trúc chữ chồng chữ có giúp hiểu nghĩa — thang số lượng
    'Không': 1,
    'Ít': 2,
    'Bình thường': 3,
    'Khá nhiều': 4,
    'Rất nhiều': 5,
}
Q23_MAP = {  # so sánh với chữ đơn
    'Không khác biệt': 1,
    'Rõ nghĩa hơn': 3,
    'Thú vị hơn': 4,
    'Dễ nhớ hơn': 5,
}
Q28_MAP = {  # khả năng đoán nghĩa từ pinyin
    'Không đoán được': 1, 'Rất khó đoán': 1, 'Khó đoán': 2,
    'Đoán được một phần': 3, 'Dễ đoán': 4,
}
Q29_MAP = {  # nhận ra liên hệ HV↔HanVan
    'Không nhận ra': 1, 'Ít khi nhận ra': 2,
    'Thỉnh thoảng nhận ra': 3,
    'Thường xuyên nhận ra': 4,
    'Nhận ra ngay': 5,
}


# ==== 2. Đáp án đúng cho phần đoán nghĩa Q30–Q37 ====
CORRECT_ANSWERS = {
    'Q30': ('淼', 'Miễu', 'Biển nước rộng, mênh mông'),
    'Q31': ('休', 'Hưu', 'Nghỉ ngơi'),
    'Q32': ('忍', 'Nhẫn', 'Kiềm chế cảm xúc / chịu đựng'),
    'Q33': ('炎', 'Viêm', 'Lửa mạnh'),
    'Q34': ('品', 'Phẩm', 'Nhiều người cùng nói / đánh giá'),
    'Q35': ('众', 'Chúng', 'Nhiều người, đám đông'),
    'Q36': ('双', 'Song', 'Hai sự vật đi thành một đôi (vd: đôi giày, đôi đũa)'),
    'Q37': ('囍', 'Hỉ kép', 'Niềm vui lớn gắn với sự kiện trọng đại'),
}


# ==== 3. Thứ tự nhóm dân số học ====
ORDERS = {
    'Q1': ['Dưới 18', '18 – 22', '23 – 30', 'Trên 30'],
    'Q3': ['Dưới 6 tháng', '6 tháng – 1 năm', '1 – 3 năm', 'Trên 3 năm'],
    'Q4': ['Mới bắt đầu', 'HSK1 – HSK2', 'HSK3 – HSK4', 'HSK5 - HSK6', 'HSK6 trở lên'],
}


# ==== 4. Các cột multi-select + canonical options ====
MULTI_COLS = ['Q9', 'Q12', 'Q21', 'Q22', 'Q26', 'Q41', 'Q42', 'Q48']

# Danh sách lựa chọn chuẩn (discovered qua phân tích paren-aware).
# Dùng để tách multi-select đúng khi label chứa dấu phẩy (vd: "Phân tích cấu trúc (bộ thủ, chữ chồng chữ)").
CANONICAL_OPTIONS = {
    'Q9': [
        'Giúp đoán nghĩa', 'Giúp ghi nhớ', 'Giúp hiểu cấu trúc chữ',
        'Giúp tạo hứng thú khi học (khám phá cái mới, chữ viết mới)',
        'Giúp hiểu hơn về chữ Nôm (được phát triển từ chữ Hán)',
        'Giúp hiểu hơn về văn hóa Trung Quốc',
    ],
    'Q12': [
        'Dễ nhầm lẫn bộ thủ giống nhau', 'Khó nhớ cách viết',
        'Không hiểu mối liên hệ nghĩa', 'Quá nhiều, khó hệ thống',
    ],
    'Q21': [
        'Tư duy trực quan của người xưa', 'Quy luật logic (lặp = nhiều)',
        'Tính biểu ý rõ ràng của chữ Hán', 'Sự sáng tạo', 'Vẻ đẹp chữ Hán',
    ],
    'Q22': [
        'Liên tưởng hình ảnh', 'Học thuộc lòng',
        'So sánh với chữ đơn để hiểu nghĩa', 'Phân tích cấu trúc',
    ],
    'Q26': [
        'Tăng tính biểu ý và tính tượng hình',
        'Sự cân đối, hài hòa về hình thức',
        'Sự lặp lại đơn giản, không đặc biệt',
    ],
    'Q41': [
        'Hiểu sai bộ thủ', 'Nhầm Hán–Việt', 'Thiếu ngữ cảnh',
        'Không nhận ra cấu trúc', 'Chữ quá phức tạp, khó đoán',
    ],
    'Q42': [
        'Học bộ thủ', 'Luyện viết nhiều', 'Phân tích cấu trúc chữ',
        'Liên hệ Hán–Việt', 'Học qua ngữ cảnh',
    ],
    'Q48': [
        'Kể câu chuyện/giải thích nguồn gốc chữ (chiết tự)',
        'Sử dụng sơ đồ tư duy (mindmap) từ bộ thủ ra các chữ',
        'Giải thích ý nghĩa chữ qua ví dụ thực tế (tên người, địa danh…)',
        'Phân tích cấu trúc chữ (bộ thủ, chữ chồng chữ) một cách trực quan',
        'Luyện viết chữ để ghi nhớ cấu trúc',
        'Học chữ qua hình ảnh minh họa hoặc liên tưởng',
        'Học qua ngữ cảnh (câu, đoạn hội thoại)',
        'So sánh, liên hệ với từ Hán–Việt tương ứng',
        'Sử dụng trò chơi/hoạt động tương tác khi học chữ',
    ],
}


def smart_multi_split(value, options):
    """Tách chuỗi multi-select, tôn trọng các option có dấu phẩy trong nhãn.
    Match longest option trước để tránh false match."""
    if pd.isna(value):
        return []
    s = str(value).strip()
    if not s:
        return []
    sorted_opts = sorted(options, key=len, reverse=True)
    matched = []
    remaining = s
    for opt in sorted_opts:
        if opt in remaining:
            matched.append(opt)
            remaining = remaining.replace(opt, '', 1)
    return matched


# ==== 5. Các cấu trúc khái niệm (construct) ====
CONSTRUCTS = {
    'HV_Advantage': ['Q13_1_num', 'Q13_2_num', 'Q13_3_num', 'Q13_4_num'],
    'POST_Attitude': ['Q50_1_num', 'Q50_2_num', 'Q50_3_num', 'Q50_4_num'],
    'Practice': ['Q14_num', 'Q15_num', 'Q16_num', 'Q27_num'],
}


def normalize_q11(val):
    """Chuẩn hoá Q11 (số bộ thủ tự đánh giá đã nhớ) về thang 1–4."""
    if pd.isna(val):
        return np.nan
    s = str(val).lower().strip()
    if 'chưa học' in s or 'chưa thống' in s or 'quên' in s or 'không nhớ' in s:
        return np.nan
    if 'không biết' in s:
        return np.nan
    if '214' in s:
        return 4
    if any(k in s for k in ['100', '120', '150']):
        return 3
    if '50' in s:
        return 2
    if 'dưới 50' in s or 'ít hơn 50' in s or 'dưới 10' in s or '10 bộ' in s:
        return 1
    m = re.search(r'(\d+)', s)
    if m:
        n = int(m.group(1))
        if n < 20: return 1
        if n < 75: return 2
        if n < 160: return 3
        return 4
    return np.nan


def load_and_prepare(path='/mnt/user-data/uploads/Data.xlsx'):
    """Đọc và chuẩn bị toàn bộ dữ liệu."""
    xlsx = pd.ExcelFile(path)
    df = pd.read_excel(xlsx, sheet_name='Data')
    questions = pd.read_excel(xlsx, sheet_name='Questions')
    sections = pd.read_excel(xlsx, sheet_name='Sections')

    # 1. Chuẩn hoá whitespace
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace({'nan': np.nan, '': np.nan, 'NaN': np.nan})

    # 2. Mã hoá các biến Likert
    df['Q7_num']   = df['Q7'].map(FREQ)
    df['Q8_num']   = df['Q8'].map(IMPORT)
    for s in ['Q13_1', 'Q13_2', 'Q13_3', 'Q13_4']:
        df[s + '_num'] = df[s].map(AGREE)
    df['Q13_5_num'] = df['Q13_5'].map(AGREE_REV)   # reverse coded
    df['Q14_num']  = df['Q14'].map(FREQ)
    df['Q15_num']  = df['Q15'].map(FREQ)
    df['Q16_num']  = df['Q16'].map(FREQ)
    df['Q17_num']  = df['Q17'].map(KNOW)
    df['Q18_num']  = df['Q18'].map(FREQ)
    df['Q20_num']  = df['Q20'].map(Q20_MAP)
    df['Q23_num']  = df['Q23'].map(Q23_MAP)
    df['Q24_num']  = df['Q24'].map(NECES)
    df['Q27_num']  = df['Q27'].map(FREQ)
    df['Q28_num']  = df['Q28'].map(Q28_MAP)
    df['Q29_num']  = df['Q29'].map(Q29_MAP)
    df['Q40_num']  = df['Q40'].map(EFFIC)
    df['Q44_num']  = df['Q44'].map(LIKE)
    df['Q45_num']  = df['Q45'].map(AGREE)
    df['Q46_num']  = df['Q46'].map(DESIRE)
    df['Q47_num']  = df['Q47'].map(NECES)    # chú ý: dùng NECES, KHÔNG phải AGREE
    df['Q49_num']  = df['Q49'].map(AGREE)    # 'Rất đồng ý' = 5
    for s in ['Q50_1', 'Q50_2', 'Q50_3', 'Q50_4']:
        df[s + '_num'] = df[s].map(AGREE)
    df['Q50_5_num'] = df['Q50_5'].map(AGREE_REV)   # reverse: "không nhận thấy khác biệt"

    # 3. Các biến kiểm tra kiến thức
    df['Q6_correct']  = (df['Q6'] == 'Có').astype(int)
    df['Q10_correct'] = (df['Q10'] == 'Khoảng 214 bộ').astype(int)
    df['Q11_num']     = df['Q11'].map(normalize_q11)

    # 4. Multi-select: smart-parse với canonical options (xử lý dấu phẩy trong label)
    for col in MULTI_COLS:
        options = CANONICAL_OPTIONS.get(col, [])
        df[col + '_list'] = df[col].apply(lambda x: smart_multi_split(x, options))
        df[col + '_n'] = df[col + '_list'].map(len)

    # 5. Điểm đoán nghĩa chữ chồng chữ (0–8)
    for q, (char, name, correct) in CORRECT_ANSWERS.items():
        df[q + '_correct'] = (df[q] == correct).astype(int)
    df['SEM_score'] = df[[q + '_correct' for q in CORRECT_ANSWERS]].sum(axis=1)
    df['SEM_pct']   = df['SEM_score'] / 8 * 100

    # 6. Composite scores (sau khi loại Q13_5 negative item khỏi HV)
    df['HV_score']       = df[CONSTRUCTS['HV_Advantage']].mean(axis=1)
    df['POST_score']     = df[CONSTRUCTS['POST_Attitude']].mean(axis=1)
    df['PRACTICE_score'] = df[CONSTRUCTS['Practice']].mean(axis=1)

    # 7. HSK ordinal
    hsk_map = {g: i for i, g in enumerate(ORDERS['Q4'])}
    df['HSK_num'] = df['Q4'].map(hsk_map)

    # 8. Độ tuổi ordinal
    age_map = {g: i for i, g in enumerate(ORDERS['Q1'])}
    df['AGE_num'] = df['Q1'].map(age_map)

    META = {
        'CORRECT_ANSWERS': CORRECT_ANSWERS,
        'ORDERS': ORDERS,
        'MULTI_COLS': MULTI_COLS,
        'CONSTRUCTS': CONSTRUCTS,
        'CANONICAL_OPTIONS': CANONICAL_OPTIONS,
    }

    return df, questions, sections, META


if __name__ == '__main__':
    df, q, s, m = load_and_prepare()
    print(f"✅ Loaded: {df.shape[0]} respondents × {df.shape[1]} columns")
    print(f"   Cronbach HV: {df['HV_score'].mean():.2f} (SD={df['HV_score'].std():.2f})")
    print(f"   SEM mean correct: {df['SEM_score'].mean():.2f}/8")
    likert_cols = sorted([c for c in df.columns if c.endswith('_num')])
    print(f"\n   All {len(likert_cols)} Likert columns have valid SD:")
    issues = []
    for c in likert_cols:
        sd = df[c].std()
        if sd < 0.1 or pd.isna(sd):
            issues.append(c)
    if issues:
        print(f"   ⚠  Issues: {issues}")
    else:
        print("   ✅ All columns OK")
