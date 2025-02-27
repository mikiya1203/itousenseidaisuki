import streamlit as st
import time
import sqlite3
from datetime import datetime
import pandas as pd

# ポモドーロタイマーの設定
POMODORO_DURATION = 25 * 60  # 25分
BREAK_DURATION = 5 * 60  # 5分
LONG_BREAK_DURATION = 15 * 60  # 15分

# SQLite データベースファイルのパス
DB_NAME = "learning_progress.db"

# SQLite データベースに接続する関数
def connect_db():
    conn = sqlite3.connect(DB_NAME)
    return conn

# 学習進捗テーブルを作成する関数
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

# 学習データをデータベースに保存する関数
def save_learning_data(subject, study_time):
    conn = connect_db()
    cursor = conn.cursor()

    # 現在の日付と曜日を取得
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    day_of_week = now.strftime("%A")

    # データベースに保存
    cursor.execute("""
        INSERT INTO progress (subject, date, day_of_week, study_time)
        VALUES (?, ?, ?, ?)
    """, (subject, date_str, day_of_week, study_time))
    conn.commit()
    conn.close()

# 学習データをデータベースから取得する関数
def get_learning_data():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM progress")
    data = cursor.fetchall()
    conn.close()
    return data

# ポモドーロサイクルのカウント
pomodoro_cycles = 0

# ページのタイトル
st.title("ポモドーロタイマーと学習管理")

# 初回実行時にテーブルを作成
create_table()

# タイマーのセクション
st.header("ポモドーロタイマー")
timer_type = st.selectbox("タイマーの選択", ["ポモドーロ", "短い休憩", "長い休憩"])

# タイマー開始ボタン
if st.button("タイマー開始"):
    if timer_type == "ポモドーロ":
        duration = POMODORO_DURATION
        st.info("ポモドーロタイマーが開始されました。25分間集中しましょう！")
        pomodoro_cycles += 1  # ポモドーロサイクル数を増加
    elif timer_type == "短い休憩":
        duration = BREAK_DURATION
        st.info("短い休憩タイマーが開始されました。5分間休憩しましょう！")
    elif timer_type == "長い休憩":
        duration = LONG_BREAK_DURATION
        st.info("長い休憩タイマーが開始されました。15分間休憩しましょう！")
    
    # タイマーのカウントダウン
    progress_bar = st.progress(0)  # 進捗バーを作成
    end_time = time.time() + duration
    
    # タイマーの進行をリセットして、表示を毎回更新
    timer_display = st.empty()  # タイマーの残り時間を表示するための空のコンテナ

    while time.time() < end_time:
        remaining_time = int(end_time - time.time())
        minutes, seconds = divmod(remaining_time, 60)
        progress_bar.progress((time.time() - (end_time - duration)) / duration)  # 進捗の更新
        
        # 残り時間を大きなフォントで表示
        timer_display.markdown(f"<h1 style='font-size: 72px; text-align: center;'>残り時間: {minutes:02d}:{seconds:02d}</h1>", unsafe_allow_html=True)
        
        time.sleep(1)  # 1秒ごとに進捗更新
    
    st.success(f"{timer_type}が完了しました！")

# 学習管理セクション
st.header("学習管理")

# 学習する科目の選択肢
subjects = ["数学", "英語", "国語", "物理", "生物", "プログラミング"]
selected_subject = st.selectbox("学習する科目を選択", subjects)

# 学習進捗を記録する
if selected_subject:
    study_time = st.number_input(f"{selected_subject}の学習時間 (分)", min_value=0, step=1)

    # 学習時間を記録するボタン
    if st.button("学習時間を追加"):
        # データベースに学習時間を保存
        save_learning_data(selected_subject, study_time)
        st.success(f"{study_time}分の学習時間が記録されました！")

# 学習進捗の表示
st.header("学習進捗")

# 学習時間の表を作成
data = get_learning_data()

# 表を作成
df = pd.DataFrame(data, columns=["ID", "科目", "学習日", "曜日", "学習時間 (分)"])
st.table(df)  # 学習進捗を表形式で表示

# 完了したポモドーロサイクル数を表示
st.write(f"完了したポモドーロサイクル数: {pomodoro_cycles}")
