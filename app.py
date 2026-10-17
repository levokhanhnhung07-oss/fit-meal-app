import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CẤU HÌNH TRANG VÀ SESSION STATE (GIỎ HÀNG)
st.set_page_config(page_title="Fit-Meal AI", page_icon="🥗", layout="wide")

if 'cart' not in st.session_state:
    st.session_state.cart = []

# Hàm thêm vào giỏ hàng
def add_to_cart(item_name, price):
    st.session_state.cart.append({"Tên": item_name, "Giá": price})
    st.toast(f"Đã thêm {item_name} vào giỏ hàng!", icon="🛒")

# 2. GIAO DIỆN HEADER CÓ ẢNH BANNER
st.image("https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=1200&h=300&fit=crop", use_container_width=True)
st.title("🥗 Fit-Meal AI - Trợ lý Dinh dưỡng & Đặt bữa ăn")
st.markdown("*Giải pháp cá nhân hóa đánh bay mệt mỏi, cải thiện vóc dáng và sức khỏe dạ dày.*")
st.divider()

# 3. SIDEBAR: THU THẬP DỮ LIỆU NGƯỜI DÙNG
st.sidebar.header("📊 Hồ Sơ Sức Khỏe")
gender = st.sidebar.selectbox("Giới tính", ["Nam", "Nữ"])
age = st.sidebar.number_input("Tuổi", min_value=15, max_value=100, value=25)
weight = st.sidebar.number_input("Cân nặng (kg)", min_value=30.0, max_value=200.0, value=60.0)
height = st.sidebar.number_input("Chiều cao (cm)", min_value=100.0, max_value=250.0, value=165.0)

activity_level = st.sidebar.selectbox(
    "Mức độ vận động", 
    ["Ít vận động (Văn phòng)", "Vận động nhẹ", "Vận động vừa", "Vận động nhiều"]
)

goal = st.sidebar.radio("Mục tiêu hình thể", ["Giảm mỡ", "Giữ dáng", "Tăng cơ"])
health_issue = st.sidebar.selectbox("Tình trạng tiêu hóa (Tùy chọn)", ["Bình thường", "Hay đau dạ dày", "Khó tiêu, đầy bụng"])

# 4. TÍNH TOÁN LOGIC
def calculate_metrics(gender, age, weight, height, activity_level, goal):
    # Tính BMR (Mifflin-St Jeor)
    if gender == "Nam":
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
        
    activity_multipliers = {"Ít vận động (Văn phòng)": 1.2, "Vận động nhẹ": 1.375, "Vận động vừa": 1.55, "Vận động nhiều": 1.725}
    tdee = bmr * activity_multipliers[activity_level]
    
    # Tính Calo mục tiêu
    target_calories = tdee - 500 if goal == "Giảm mỡ" else (tdee + 500 if goal == "Tăng cơ" else tdee)
    
    # Tính Macro (Tỷ lệ phân bổ)
    if goal == "Giảm mỡ":
        macros = {"Protein": 0.4, "Carbs": 0.3, "Fat": 0.3}
    elif goal == "Tăng cơ":
        macros = {"Protein": 0.3, "Carbs": 0.5, "Fat": 0.2}
    else:
        macros = {"Protein": 0.3, "Carbs": 0.4, "Fat": 0.3}
        
    protein_g = (target_calories * macros["Protein"]) / 4
    carbs_g = (target_calories * macros["Carbs"]) / 4
    fat_g = (target_calories * macros["Fat"]) / 9
    
    return int(tdee), int(target_calories), int(protein_g), int(carbs_g), int(fat_g)

tdee, target_cal, protein, carbs, fat = calculate_metrics(gender, age, weight, height, activity_level, goal)

# 5. HIỂN THỊ DỮ LIỆU THEO TABS
tab1, tab2, tab3 = st.tabs(["📈 Chỉ số & Macro", "🍱 Đề xuất Thực đơn", f"🛒 Giỏ hàng ({len(st.session_state.cart)})"])

with tab1:
    st.subheader("Báo cáo Dinh dưỡng Cá nhân hóa")
    col1, col2, col3 = st.columns(3)
    col1.metric("TDEE (Năng lượng duy trì)", f"{tdee} kcal")
    col2.metric("Năng lượng Mục tiêu", f"{target_cal} kcal", delta="-500 kcal" if goal=="Giảm mỡ" else ("+500 kcal" if goal=="Tăng cơ" else "0"))
    col3.metric("Lượng nước gợi ý", f"{round(weight * 0.04, 1)} Lít")
    
    # Biểu đồ Tròn (Pie chart) cho Macro
    st.write("### Phân bổ Đa lượng chất (Macronutrients)")
    macro_data = pd.DataFrame({
        "Chất": ["Protein (Đạm)", "Carbs (Tinh bột)", "Fat (Chất béo)"],
        "Khối lượng (g)": [protein, carbs, fat]
    })
    fig = px.pie(macro_data, values='Khối lượng (g)', names='Chất', 
                 color_discrete_sequence=['#ff9999','#66b3ff','#99ff99'],
                 hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader(f"Thực đơn tối ưu cho mục tiêu: {goal}")
    if health_issue != "Bình thường":
        st.warning(f"💡 Hệ thống đã ưu tiên các nguyên liệu mềm, dễ tiêu hóa vì bạn có dấu hiệu: {health_issue}")
    
    # Database thực đơn (có kèm link ảnh)
    menu_db = {
        "Giảm mỡ": [
            {"Tên": "Salad Ức Gà Áp Chảo", "Calo": 350, "Giá": 65000, "Img": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=500&h=300&fit=crop"},
            {"Tên": "Cá Hồi Nướng Măng Tây", "Calo": 420, "Giá": 120000, "Img": "https://images.unsplash.com/photo-1467003909585-2f8a72700288?w=500&h=300&fit=crop"}
        ],
        "Giữ dáng": [
            {"Tên": "Cơm Gà Teriyaki Gạo Lứt", "Calo": 550, "Giá": 75000, "Img": "https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?w=500&h=300&fit=crop"},
            {"Tên": "Mì Ý Nguyên Cám Bò Băm", "Calo": 600, "Giá": 85000, "Img": "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=500&h=300&fit=crop"}
        ],
        "Tăng cơ": [
            {"Tên": "Steak Bò Khoai Tây Nghiền", "Calo": 750, "Giá": 150000, "Img": "https://images.unsplash.com/photo-1544025162-8317e3e7f4c3?w=500&h=300&fit=crop"},
            {"Tên": "Nửa Con Gà Quay & Salad", "Calo": 850, "Giá": 110000, "Img": "https://images.unsplash.com/photo-1598514982205-f36b96d1e8d4?w=500&h=300&fit=crop"}
        ]
    }
    
    # Hiển thị món ăn dạng Grid (cột)
    meals = menu_db[goal]
    cols = st.columns(2)
    
    for i, meal in enumerate(meals):
        with cols[i]:
            st.image(meal["Img"], use_container_width=True, caption="Ảnh minh họa thực tế")
            st.markdown(f"### {meal['Tên']}")
            st.write(f"🔥 Năng lượng: **{meal['Calo']} kcal**")
            st.write(f"💰 Giá: **{meal['Giá']:,} VNĐ**")
            st.button("Thêm vào giỏ", key=f"btn_{i}", on_click=add_to_cart, args=(meal['Tên'], meal['Giá']))

with tab3:
    st.subheader("Giỏ hàng của bạn")
    if len(st.session_state.cart) == 0:
        st.info("Giỏ hàng đang trống. Hãy qua tab 'Đề xuất Thực đơn' để chọn món nhé!")
    else:
        total_price = 0
        for item in st.session_state.cart:
            st.write(f"- {item['Tên']} : **{item['Giá']:,} VNĐ**")
            total_price += item['Giá']
        
        st.divider()
        st.write(f"### Tổng cộng: {total_price:,} VNĐ")
        
        if st.button("💳 Tiến hành thanh toán (Demo)", type="primary"):
            st.success("Cảm ơn bạn! Đơn hàng đang được nhà hàng chuẩn bị và giao đến bạn sớm nhất.")
            st.session_state.cart = [] # Reset giỏ hàng sau khi thanh toán
