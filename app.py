import streamlit as st
import pandas as pd

# Cấu hình trang
st.set_page_config(
    page_title="Tính Lãi Gửi Tiết Kiệm",
    page_icon="💰",
    layout="centered"
)

st.title("💰 Ứng Dụng Tính Lãi Gửi Tiết Kiệm")
st.write("Nhập thông tin khoản tiền gửi để tính toán lợi nhuận dự kiến.")

st.markdown("---")

# 1. NHẬP THÔNG TIN TỪ NGUỜI DÙNG
st.header("📋 Thông tin khoản gửi")

col1, col2 = st.columns(2)

with col1:
    principal = st.number_input(
        "Số tiền gửi (VNĐ):",
        min_value=1_000_000,
        value=100_000_000,
        step=5_000_000,
        format="%d"
    )
    
    term_months = st.number_input(
        "Kỳ hạn gửi (tháng):",
        min_value=1,
        max_value=120,
        value=12,
        step=1
    )
    
    interest_rate = st.number_input(
        "Lãi suất (%/năm):",
        min_value=0.1,
        max_value=30.0,
        value=6.0,
        step=0.1,
        format="%.2f"
    )

with col2:
    interest_type = st.selectbox(
        "Phương pháp tính lãi:",
        ["Lãi đơn", "Lãi kép"]
    )
    
    payout_freq = st.selectbox(
        "Hình thức lãnh lãi:",
        ["Lãnh lãi theo tháng", "Lãnh lãi theo quý", "Lãnh lãi cuối kỳ"]
    )

# 2. XỬ LÝ VÀ TÍNH TOÁN LOGIC
rate_decimal = interest_rate / 100.0

total_interest = 0.0
total_amount = 0.0
periodic_interest = 0.0
freq_label = ""

schedule_data = []

if interest_type == "Lãi đơn":
    # Tính lãi đơn: Lãi = Gốc * Lãi suất năm * (Số tháng / 12)
    total_interest = principal * rate_decimal * (term_months / 12.0)
    total_amount = principal + total_interest

    if payout_freq == "Lãnh lãi theo tháng":
        periodic_interest = principal * rate_decimal / 12.0
        freq_label = "mỗi tháng"
        for m in range(1, term_months + 1):
            schedule_data.append({
                "Kỳ": f"Tháng {m}",
                "Tiền gốc (VNĐ)": principal,
                "Lãi nhận kỳ này (VNĐ)": periodic_interest,
                "Lũy kế tiền lãi (VNĐ)": periodic_interest * m
            })

    elif payout_freq == "Lãnh lãi theo quý":
        periodic_interest = principal * rate_decimal / 4.0
        freq_label = "mỗi quý"
        num_quarters = term_months // 3
        rem_months = term_months % 3
        
        for q in range(1, num_quarters + 1):
            schedule_data.append({
                "Kỳ": f"Quý {q}",
                "Tiền gốc (VNĐ)": principal,
                "Lãi nhận kỳ này (VNĐ)": periodic_interest,
                "Lũy kế tiền lãi (VNĐ)": periodic_interest * q
            })
        if rem_months > 0:
            rem_interest = principal * rate_decimal * (rem_months / 12.0)
            schedule_data.append({
                "Kỳ": f"Lẻ {rem_months} tháng cuối",
                "Tiền gốc (VNĐ)": principal,
                "Lãi nhận kỳ này (VNĐ)": rem_interest,
                "Lũy kế tiền lãi (VNĐ)": total_interest
            })

    else:  # Lãnh lãi cuối kỳ
        periodic_interest = total_interest
        freq_label = "vào cuối kỳ"
        schedule_data.append({
            "Kỳ": "Cuối kỳ",
            "Tiền gốc (VNĐ)": principal,
            "Lãi nhận kỳ này (VNĐ)": total_interest,
            "Lũy kế tiền lãi (VNĐ)": total_interest
        })

else:  # Lãi kép (Compound Interest)
    if payout_freq == "Lãnh lãi theo tháng":
        current_balance = principal
        monthly_rate = rate_decimal / 12.0
        
        for m in range(1, term_months + 1):
            interest_m = current_balance * monthly_rate
            current_balance += interest_m
            schedule_data.append({
                "Kỳ": f"Tháng {m}",
                "Tiền gốc đầu kỳ (VNĐ)": current_balance - interest_m,
                "Lãi nhập gốc (VNĐ)": interest_m,
                "Tổng dư nợ cuối kỳ (VNĐ)": current_balance
            })
            
        total_amount = current_balance
        total_interest = total_amount - principal
        periodic_interest = total_interest / term_months
        freq_label = "trung bình/tháng"

    elif payout_freq == "Lãnh lãi theo quý":
        current_balance = principal
        quarterly_rate = rate_decimal / 4.0
        num_quarters = term_months // 3
        rem_months = term_months % 3

        for q in range(1, num_quarters + 1):
            interest_q = current_balance * quarterly_rate
            current_balance += interest_q
            schedule_data.append({
                "Kỳ": f"Quý {q}",
                "Tiền gốc đầu kỳ (VNĐ)": current_balance - interest_q,
                "Lãi nhập gốc (VNĐ)": interest_q,
                "Tổng dư nợ cuối kỳ (VNĐ)": current_balance
            })

        if rem_months > 0:
            interest_rem = current_balance * rate_decimal * (rem_months / 12.0)
            current_balance += interest_rem
            schedule_data.append({
                "Kỳ": f"Lẻ {rem_months} tháng cuối",
                "Tiền gốc đầu kỳ (VNĐ)": current_balance - interest_rem,
                "Lãi nhập gốc (VNĐ)": interest_rem,
                "Tổng dư nợ cuối kỳ (VNĐ)": current_balance
            })

        total_amount = current_balance
        total_interest = total_amount - principal
        periodic_interest = total_interest / (num_quarters + (1 if rem_months > 0 else 0))
        freq_label = "trung bình/kỳ"

    else:  # Lãnh lãi cuối kỳ (Nhập gốc theo tháng)
        monthly_rate = rate_decimal / 12.0
        total_amount = principal * ((1 + monthly_rate) ** term_months)
        total_interest = total_amount - principal
        periodic_interest = total_interest
        freq_label = "vào cuối kỳ"
        
        schedule_data.append({
            "Kỳ": "Cuối kỳ",
            "Tiền gốc ban đầu (VNĐ)": principal,
            "Lãi cộng dồn (VNĐ)": total_interest,
            "Tổng nhận (VNĐ)": total_amount
        })

# 3. HIỂN THỊ KẾT QUẢ
st.markdown("---")
st.header("📊 Kết quả dự tính")

col_res1, col_res2, col_res3 = st.columns(3)

with col_res1:
    st.metric(
        label=f"Tiền lãi định kỳ ({freq_label})",
        value=f"{periodic_interest:,.0f} VNĐ"
    )

with col_res2:
    st.metric(
        label="Tổng tiền lãi",
        value=f"{total_interest:,.0f} VNĐ"
    )

with col_res3:
    st.metric(
        label="Tổng số tiền (Gốc + Lãi)",
        value=f"{total_amount:,.0f} VNĐ"
    )

# Bảng chi tiết dòng tiền
st.subheader("📅 Bảng chi tiết nhận lãi")
df_schedule = pd.DataFrame(schedule_data)

# Định dạng hiển thị phân cách hàng nghìn cho số tiền trong bảng
for col in df_schedule.columns:
    if "(VNĐ)" in col:
        df_schedule[col] = df_schedule[col].apply(lambda x: f"{x:,.0f}")

st.dataframe(df_schedule, use_container_width=True)
