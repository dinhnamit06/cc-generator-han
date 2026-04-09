import streamlit as st
import random
from datetime import datetime, timedelta
import pandas as pd
import io
import json

st.set_page_config(page_title="CC Generator PRO v5 - Thẻ Hàn", page_icon="💳", layout="wide")

BANKS = {
    "All Banks": ["451842", "457972", "425940", "426066", "426271", "457901", "453936", "515594", "532092", "553423", "554481", "557042", "558370"],
    "Shinhan Bank": ["451842", "457972", "426066", "457901", "457905", "418163"],
    "Hana Bank": ["425940", "426271", "426578", "490625", "490678"],
    "KB Kookmin Bank": ["532092", "532105", "553423", "554481", "557042"],
    "Hyundai Card": ["515594", "531408", "558370", "459907"],
    "Woori Bank": ["532147", "538831", "542184", "556659"],
    "BC Card": ["402367", "411904", "457493"],
}

KOREAN_SURNAMES = ["Kim", "Lee", "Park", "Choi", "Jung", "Kang", "Yoo", "Shin", "Han", "Lim", "Song", "Jo", "Yoon"]
KOREAN_FIRST = ["Ji-hoon", "Min-jun", "Seo-yun", "Ji-eun", "Hyun-woo", "Soo-min", "Dong-hyun", "Eun-ji", "Tae-hyuk", "Hye-jin", "Jae-won", "Ye-ji"]
SEOUL_DISTRICTS = ["Gangnam-gu", "Seocho-gu", "Jongno-gu", "Mapo-gu", "Yongsan-gu", "Songpa-gu", "Dongdaemun-gu", "Seongbuk-gu"]
STREET_NAMES = ["Teheran-ro", "Gangnam-daero", "Seolleung-ro", "Yeoksam-ro", "Samseong-ro"]

def generate_fake_name():
    return f"{random.choice(KOREAN_SURNAMES)} {random.choice(KOREAN_FIRST)}"

def generate_fake_phone():
    return f"010-{random.randint(1000,9999)}-{random.randint(1000,9999)}"

def generate_fake_address():
    district = random.choice(SEOUL_DISTRICTS)
    street = random.choice(STREET_NAMES)
    number = random.randint(10, 999)
    return f"{number}, {street}, {district}, Seoul, South Korea"

def luhn_generate(prefix: str):
    ccnumber = list(str(prefix))
    while len(ccnumber) < 15:
        ccnumber.append(str(random.randint(0, 9)))
    sum_ = 0
    reversed_cc = ccnumber[::-1]
    for pos, digit in enumerate(reversed_cc):
        d = int(digit)
        if pos % 2 == 0:
            d *= 2
            if d > 9: d -= 9
        sum_ += d
    check_digit = (10 - (sum_ % 10)) % 10
    ccnumber.append(str(check_digit))
    return ''.join(ccnumber)

def generate_card(bank_name, custom_bin=None):
    if custom_bin:
        prefix = str(custom_bin).strip()
    else:
        prefix = random.choice(BANKS[bank_name])
    number = luhn_generate(prefix)
    today = datetime.now()
    expiry = (today + timedelta(days=random.randint(400, 2555))).strftime('%m/%y')
    cvv = str(random.randint(100, 999))
    name = generate_fake_name()
    return {
        "Tên": name,
        "Ngân hàng": bank_name if bank_name != "All Banks" else "Random Korea",
        "BIN": number[:6],
        "Số thẻ": number,
        "Hạn": expiry,
        "CVV": cvv,
    }

st.title("💳 Credit Card Generator PRO v5 - Thẻ Hàn Quốc 2026")
st.markdown("**Chỉ dùng cho TESTING / TRIAL / DEVELOPMENT**")

with st.sidebar:
    st.header("⚙️ Cài đặt")
    num_cards = st.number_input("Số lượng thẻ", min_value=1, max_value=1000, value=50, step=10)
    bank_option = st.selectbox("Chọn ngân hàng", options=list(BANKS.keys()))
    custom_bin = st.text_input("Custom BIN (tùy chọn)", placeholder="Ví dụ: 451842")
    include_phone = st.toggle("Thêm số điện thoại Hàn", value=True)
    include_address = st.toggle("Thêm địa chỉ Hàn", value=True)
    generate_btn = st.button("🚀 GENERATE THẺ HÀN", type="primary", use_container_width=True)

if generate_btn:
    with st.spinner("Đang sinh thẻ Hàn Quốc..."):
        cards = []
        bin_input = custom_bin.strip() if custom_bin else None
        for _ in range(num_cards):
            card = generate_card(bank_option, bin_input)
            if include_phone:
                card["SĐT Hàn"] = generate_fake_phone()
            if include_address:
                card["Địa chỉ"] = generate_fake_address()
            cards.append(card)
        df = pd.DataFrame(cards)
        st.success(f"✅ Đã generate {num_cards} thẻ Hàn Quốc!")
        st.dataframe(df, use_container_width=True, height=600)

        col1, col2, col3 = st.columns(3)
        with col1:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("💾 Tải CSV", csv, f"the_han_v5_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", "text/csv")
        with col2:
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            st.download_button("📊 Tải Excel", excel_buffer.getvalue(), f"the_han_v5_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        with col3:
            json_str = df.to_json(orient="records", force_ascii=False, indent=2)
            st.download_button("📄 Tải JSON", json_str.encode('utf-8'), f"the_han_v5_{datetime.now().strftime('%Y%m%d_%H%M')}.json", "application/json")

st.caption("💡 Deploy bởi Grok v5 - Dùng thoải mái cho trial!")
