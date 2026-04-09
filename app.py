import streamlit as st
import random
from datetime import datetime, timedelta
import pandas as pd
import io
import json
from faker import Faker

st.set_page_config(page_title="CC Generator PRO v7 - Korea & USA", page_icon="💳", layout="wide")

# ==================== FAKER ====================
fake_kr = Faker('ko_KR')
fake_us = Faker('en_US')

# ==================== BIN DATABASE 2026 ====================
# KOREA (giữ nguyên v6)
KOREA_BANKS = {
    "All Banks": ["451842","457972","425940","426066","426271","426578","457901","453936","515594","532092","553423","554481","557042","558370"],
    "Shinhan Bank": ["451842","457972","426066","457901","418163"],
    "Hana Bank": ["425940","426271","426578","490625"],
    "KB Kookmin Bank": ["532092","553423","554481","557042"],
    "Hyundai Card": ["515594","531408","558370"],
    "Woori Bank": ["532147","538831","542184"],
    "BC Card": ["402367","411904","457493"],
}

# UNITED STATES (chuẩn USA 2026 - Chase, BoA, Amex, Discover...)
USA_BANKS = {
    "All US Banks": ["414720","414740","403116","406045","411432","400906","474480","549191","6011","644","65","34","37","51","52","53","54","55"],
    "Chase": ["414720","414740","403116","406045","411432","401135","402297"],
    "Bank of America": ["414718","400906","474480","549191","4147"],
    "Citi": ["542418","542419","559458","414720"],
    "Capital One": ["414720","414721","434256"],
    "American Express": ["34","37"],
    "Discover": ["6011","644","65"],
    "Wells Fargo": ["401201","401202","414720"],
}

def generate_card(country, bank_name, custom_bin=None):
    if country == "United States":
        fake = fake_us
        banks_dict = USA_BANKS
        is_amex = bank_name == "American Express" or (custom_bin and str(custom_bin).startswith(('34','37')))
        length = 15 if is_amex else 16
    else:
        fake = fake_kr
        banks_dict = KOREA_BANKS
        length = 16

    if custom_bin:
        prefix = str(custom_bin).strip()
    else:
        prefix = random.choice(banks_dict[bank_name])

    # LUHN
    ccnumber = list(prefix)
    while len(ccnumber) < length - 1:
        ccnumber.append(str(random.randint(0, 9)))
    
    sum_ = 0
    for i, digit in enumerate(reversed(ccnumber)):
        d = int(digit)
        if i % 2 == 0:
            d *= 2
            if d > 9: d -= 9
        sum_ += d
    check_digit = (10 - (sum_ % 10)) % 10
    ccnumber.append(str(check_digit))
    number = ''.join(ccnumber)

    expiry = (datetime.now() + timedelta(days=random.randint(400, 2555))).strftime('%m/%y')
    cvv = str(random.randint(1000, 9999)) if length == 15 else str(random.randint(100, 999))
    brand = "AMEX" if length == 15 else ("VISA" if number.startswith('4') else "MASTERCARD" if number.startswith(('5','2')) else "DISCOVER")

    return {
        "Country": country,
        "Tên": fake.name(),
        "Ngân hàng": bank_name if bank_name != "All Banks" and bank_name != "All US Banks" else "Random",
        "Brand": brand,
        "BIN": number[:6],
        "Số thẻ": number,
        "Hạn": expiry,
        "CVV": cvv,
        "SĐT": fake.phone_number(),
        "Địa chỉ": fake.address(),
        "Email": fake.email()
    }

# ==================== GIAO DIỆN V7 ====================
st.title("💳 Credit Card Generator PRO v7 - Korea & USA")
st.caption("🚀 BIN 2026 + Faker en_US/ko_KR | Chỉ dùng TESTING / TRIAL")

tab1, tab2, tab3 = st.tabs(["Generate", "History", "Settings"])

with tab1:
    with st.form("generate_form"):
        col1, col2 = st.columns([1, 1])
        with col1:
            country = st.selectbox("Quốc gia", options=["South Korea", "United States"], index=1)
            num_cards = st.number_input("Số lượng thẻ", min_value=1, max_value=1000, value=100, step=10)
        with col2:
            if country == "United States":
                bank_option = st.selectbox("Ngân hàng Mỹ", options=list(USA_BANKS.keys()))
            else:
                bank_option = st.selectbox("Ngân hàng Hàn", options=list(KOREA_BANKS.keys()))
            custom_bin = st.text_input("Custom BIN (tùy chọn)", placeholder="Ví dụ: 414720 (Chase)")
        
        include_extra = st.toggle("Thêm SĐT + Địa chỉ + Email", value=True)
        generate_btn = st.form_submit_button("🚀 GENERATE", type="primary", use_container_width=True)

    if generate_btn:
        with st.spinner(f"Đang sinh thẻ {country}..."):
            progress_bar = st.progress(0)
            cards = []
            for i in range(num_cards):
                card = generate_card(country, bank_option, custom_bin)
                if not include_extra:
                    card.pop("SĐT", None)
                    card.pop("Địa chỉ", None)
                    card.pop("Email", None)
                cards.append(card)
                progress_bar.progress((i + 1) / num_cards)
            
            df = pd.DataFrame(cards)
            st.success(f"✅ Đã generate {num_cards} thẻ {country}!")
            st.dataframe(df, use_container_width=True, height=650)

            # Download
            col1, col2, col3 = st.columns(3)
            with col1:
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("💾 CSV", csv, f"{country.lower()}_v7_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", "text/csv")
            with col2:
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False)
                st.download_button("📊 Excel", excel_buffer.getvalue(), f"{country.lower()}_v7_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            with col3:
                json_str = df.to_json(orient="records", force_ascii=False, indent=2)
                st.download_button("📄 JSON", json_str.encode('utf-8'), f"{country.lower()}_v7_{datetime.now().strftime('%Y%m%d_%H%M')}.json", "application/json")

            if 'history' not in st.session_state:
                st.session_state.history = []
            st.session_state.history.extend(cards)

with tab2:
    if 'history' in st.session_state and st.session_state.history:
        st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True)
        if st.button("🗑️ Xóa history"):
            st.session_state.history = []
            st.rerun()

with tab3:
    st.info("**Nguồn v7:** BIN Mỹ từ Chase, Bank of America, Amex, Discover… (binlist.io + bintable.com 2026) | Faker en_US chuẩn USA")

st.caption("💡 v7 - Korea + United States | Deploy lại là dùng ngay!")
