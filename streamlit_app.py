import time
import streamlit as st
import sqlite3
from passlib.hash import bcrypt
from datetime import datetime
import pandas as pd

# SQLite データベースのパス
DB_NAME = "learning_progress.db"

# SQLite データベースに接続する関数
def connect_db():
    return sqlite3.connect(DB_NAME)

# 学習進捗テーブルを作成
def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT,
            date TEXT,
            day_of_week TEXT,
            study_time INTEGER
        )
    """)
    conn.commit()
    conn.close()

# 学習データを保存
def save_learning_data(subject, study_time):
    conn = connect_db()
    cursor = conn.cursor()
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    day_of_week = now.strftime("%A")
    
    cursor.execute("""
        INSERT INTO progress (subject, date, day_of_week, study_time)
        VALUES (?, ?, ?, ?)
    """, (subject, date_str, day_of_week, study_time))
    conn.commit()
    conn.close()

# 学習データを取得
def get_learning_data():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM progress")
    data = cursor.fetchall()
    conn.close()
    return data

# ページのタイトル
st.title("📚 学習管理＆ポモドーロタイマー")

# テーブルを作成
create_table()

# **🔹 タイマーと学習管理を並行して実行**
col1, col2 = st.columns(2)  # 画面を2分割

# **📌 タイマー機能（左側）**
with col1:
    st.header("⏳ タイマー")
    
    POMODORO_DURATION = 25 * 60  # 25分
    BREAK_DURATION = 5 * 60  # 5分
    LONG_BREAK_DURATION = 15 * 60  # 15分
    
    timer_type = st.selectbox("タイマーを選択", ["ポモドーロ", "短い休憩", "長い休憩"])
    timer_button = st.button("⏰ タイマー開始")
    
    if timer_button:
        if timer_type == "ポモドーロ":
            duration = POMODORO_DURATION
            st.info("🔥 25分間集中しましょう！")
        elif timer_type == "短い休憩":
            duration = BREAK_DURATION
            st.info("☕ 5分間休憩しましょう！")
        else:
            duration = LONG_BREAK_DURATION
            st.info("🌿 15分間リラックスしましょう！")
        
        progress_bar = st.progress(0)
        time_display = st.empty()
        start_time = time.time()
        end_time = start_time + duration
        
        while time.time() < end_time:
            remaining_time = int(end_time - time.time())
            minutes, seconds = divmod(remaining_time, 60)
            progress_bar.progress((time.time() - start_time) / duration)
            time_display.text(f"⏳ 残り時間: {minutes:02d}:{seconds:02d}")
            time.sleep(1)

        time_display.text(f"✅ {timer_type}が完了しました！")

# **📌 学習管理（右側）**
with col2:
    st.header("📖 学習管理")

    subjects = ["数学", "英語", "国語", "物理", "生物", "情報"]
    selected_subject = st.selectbox("学習する科目を選択", subjects)
    study_time = st.number_input(f"{selected_subject}の学習時間 (分)", min_value=0, step=1)
    
    if st.button("📝 学習時間を追加"):
        save_learning_data(selected_subject, study_time)
        st.success(f"✅ {study_time}分の学習時間を記録しました！")

    # 学習進捗の表示
    st.subheader("📊 学習進捗")
    data = get_learning_data()
    df = pd.DataFrame(data, columns=["ID", "科目", "学習日", "曜日", "学習時間 (分)"])
    st.table(df)
