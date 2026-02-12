import streamlit as st
import pandas as pd
from datetime import date

# 設定頁面標題
st.set_page_config(page_title="我的卡路里追蹤器", page_icon="🏃")

st.title("🏃‍♂️ 個人卡路里與減肥助手")

# --- 側邊欄：個人資料設定 ---
st.sidebar.header("1. 個人資料設定")
gender = st.sidebar.radio("性別", ["男", "女"])
age = st.sidebar.number_input("年齡", 18, 100, 22)
height = st.sidebar.number_input("身高 (cm)", 100, 250, 175)
weight = st.sidebar.number_input("體重 (kg)", 40, 200, 70)
activity_level = st.sidebar.selectbox("日常活動量", 
    ["久坐 (辦公室/讀書)", "輕度活動 (每週運動1-3天)", "中度活動 (每週運動3-5天)", "高度活動 (每週運動6-7天)"])

# BMR & TDEE 計算 (Mifflin-St Jeor 公式)
if gender == "男":
    bmr = 10 * weight + 6.25 * height - 5 * age + 5
else:
    bmr = 10 * weight + 6.25 * height - 5 * age - 161

activity_multiplier = {
    "久坐 (辦公室/讀書)": 1.2,
    "輕度活動 (每週運動1-3天)": 1.375,
    "中度活動 (每週運動3-5天)": 1.55,
    "高度活動 (每週運動6-7天)": 1.725
}
tdee = bmr * activity_multiplier[activity_level]

st.sidebar.markdown("---")
st.sidebar.header("2. 減肥目標")
deficit = st.sidebar.slider("每日熱量赤字 (建議 300-500 kcal)", 0, 1000, 500)
target_calories = tdee - deficit

st.sidebar.info(f"🔥 你的每日維持熱量 (TDEE): {int(tdee)} kcal")
st.sidebar.success(f"🎯 減肥目標攝取量: {int(target_calories)} kcal")

# --- 主頁面：記錄區 ---

# 初始化 Session State 來暫存資料
if 'food_log' not in st.session_state:
    st.session_state.food_log = []
if 'exercise_log' not in st.session_state:
    st.session_state.exercise_log = []

col1, col2 = st.columns(2)

with col1:
    st.subheader("🍔 新增飲食")
    food_name = st.text_input("食物名稱 (例如: 雞胸肉飯)")
    food_cal = st.number_input("卡路里 (kcal)", 0, 2000, 0, key="food_input")
    if st.button("記錄食物"):
        if food_name and food_cal > 0:
            st.session_state.food_log.append({"項目": food_name, "熱量": food_cal, "類型": "攝取"})
            st.success(f"已記錄: {food_name}")

with col2:
    st.subheader("🏃 新增運動")
    # 預設一些常見運動方便選擇
    ex_name = st.text_input("運動名稱", value="跑步") 
    ex_cal = st.number_input("消耗卡路里 (kcal)", 0, 2000, 0, key="ex_input")
    if st.button("記錄運動"):
        if ex_name and ex_cal > 0:
            st.session_state.exercise_log.append({"項目": ex_name, "熱量": ex_cal, "類型": "消耗"})
            st.success(f"已記錄: {ex_name}")

# --- 數據總結 ---
st.markdown("---")
st.header("📊 今日摘要")

total_food = sum([item['熱量'] for item in st.session_state.food_log])
total_exercise = sum([item['熱量'] for item in st.session_state.exercise_log])
net_calories = total_food - total_exercise
remaining = target_calories - net_calories

# 顯示指標
m1, m2, m3 = st.columns(3)
m1.metric("已攝取", f"{total_food} kcal", delta_color="inverse")
m2.metric("運動消耗", f"{total_exercise} kcal", delta_color="normal")
m3.metric("剩餘額度", f"{int(remaining)} kcal", delta=f"{int(remaining)}", delta_color="normal")

# 進度條
if target_calories > 0:
    progress = min(max(net_calories / target_calories, 0.0), 1.0)
    st.progress(progress)
    if net_calories > target_calories:
        st.warning("⚠️ 注意：你今天的淨攝取已超過減肥目標！")
    else:
        st.caption(f"目前使用了 {int(progress*100)}% 的熱量預算")

# 顯示詳細清單
if st.checkbox("顯示詳細記錄清單"):
    all_logs = st.session_state.food_log + st.session_state.exercise_log
    if all_logs:
        df = pd.DataFrame(all_logs)
        st.table(df)
    else:
        st.text("目前沒有記錄。")
