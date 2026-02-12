import streamlit as st
import pandas as pd
from datetime import date

# --- 頁面設定 ---
st.set_page_config(page_title="智能卡路里計算機", page_icon="🍱")
st.title("🍱 智能卡路里 & 減肥助手")

# --- 1. 側邊欄：個人資料與 BMR ---
st.sidebar.header("1. 設定你的檔案")
gender = st.sidebar.radio("性別", ["男", "女"])
age = st.sidebar.number_input("年齡", 18, 100, 22)
height = st.sidebar.number_input("身高 (cm)", 100, 250, 175)
weight = st.sidebar.number_input("體重 (kg)", 40, 200, 70)
activity_level = st.sidebar.selectbox("日常活動量", 
    ["久坐 (辦公室/讀書)", "輕度 (每週運動1-3天)", "中度 (每週運動3-5天)", "高度 (每週運動6-7天)"])

# BMR 計算 (Mifflin-St Jeor 公式)
if gender == "男":
    bmr = 10 * weight + 6.25 * height - 5 * age + 5
else:
    bmr = 10 * weight + 6.25 * height - 5 * age - 161

activity_multiplier = {
    "久坐 (辦公室/讀書)": 1.2,
    "輕度 (每週運動1-3天)": 1.375,
    "中度 (每週運動3-5天)": 1.55,
    "高度 (每週運動6-7天)": 1.725
}
tdee = bmr * activity_multiplier[activity_level]

st.sidebar.markdown("---")
st.sidebar.header("2. 減肥目標")
deficit = st.sidebar.slider("每日熱量赤字", 0, 1000, 500)
target_calories = tdee - deficit

st.sidebar.info(f"🔥 每日消耗 (TDEE): {int(tdee)}")
st.sidebar.success(f"🎯 每日目標攝取: {int(target_calories)}")

# --- Session State 初始化 ---
if 'food_log' not in st.session_state:
    st.session_state.food_log = []
if 'exercise_log' not in st.session_state:
    st.session_state.exercise_log = []

# --- 2. 主功能區 ---
tab1, tab2 = st.tabs(["🍽️ 記錄飲食 (自動計算)", "🏃 記錄運動"])

with tab1:
    st.subheader("輸入食物重量 (Gram)")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        carbs_g = st.number_input("🍚 飯/麵/澱粉 (g)", 0, 1000, 0, step=10, help="煮熟後的重量")
        meat_g = st.number_input("🥩 肉類/蛋白質 (g)", 0, 1000, 0, step=10, help="煮熟後的重量")
    
    with col_b:
        veg_g = st.number_input("🥦 蔬菜 (g)", 0, 1000, 0, step=10)
        oil_spoon = st.number_input("🥄 油/醬汁 (湯匙)", 0.0, 10.0, 0.0, step=0.5, help="1湯匙約15ml")

    # --- 自動計算核心邏輯 ---
    # 估算標準：飯 1.3kcal/g, 肉 2.0kcal/g, 菜 0.3kcal/g, 油 120kcal/湯匙
    estimated_cal = (carbs_g * 1.3) + (meat_g * 2.0) + (veg_g * 0.3) + (oil_spoon * 100)
    
    st.info(f"🧮 系統估算熱量: **{int(estimated_cal)} kcal**")

    # 確認按鈕
    meal_name = st.text_input("餐點名稱 (選填，例如: 午餐便當)", value="我的餐點")
    
    if st.button("➕ 加入飲食記錄"):
        if estimated_cal > 0:
            st.session_state.food_log.append({
                "名稱": meal_name,
                "澱粉": f"{carbs_g}g",
                "肉類": f"{meat_g}g",
                "蔬菜": f"{veg_g}g",
                "熱量": int(estimated_cal)
            })
            st.success(f"已新增！總計 {int(estimated_cal)} kcal")
        else:
            st.warning("請輸入至少一項食物的重量")

with tab2:
    st.subheader("新增運動")
    ex_name = st.text_input("運動項目", value="跑步")
    ex_cal = st.number_input("消耗卡路里 (kcal)", 0, 2000, 0)
    if st.button("➕ 加入運動記錄"):
        st.session_state.exercise_log.append({"名稱": ex_name, "熱量": ex_cal})
        st.success("運動已記錄！")

# --- 3. 儀表板 ---
st.markdown("---")
st.subheader("📊 今日進度")

total_food = sum([item['熱量'] for item in st.session_state.food_log])
total_exercise = sum([item['熱量'] for item in st.session_state.exercise_log])
net = total_food - total_exercise
remaining = target_calories - net

c1, c2, c3 = st.columns(3)
c1.metric("已攝取", f"{int(total_food)}", delta_color="inverse")
c2.metric("運動消耗", f"{int(total_exercise)}", delta_color="normal")
c3.metric("剩餘額度", f"{int(remaining)}", delta=f"{int(remaining)}", delta_color="normal")

if target_calories > 0:
    prog = min(max(net / target_calories, 0.0), 1.0)
    st.progress(prog)

# --- 4. 詳細清單 ---
if st.checkbox("查看詳細記錄"):
    st.write("🍽️ 飲食清單")
    if st.session_state.food_log:
        st.table(pd.DataFrame(st.session_state.food_log))
    
    st.write("🏃 運動清單")
    if st.session_state.exercise_log:
        st.table(pd.DataFrame(st.session_state.exercise_log))
