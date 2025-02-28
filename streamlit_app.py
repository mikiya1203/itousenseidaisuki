import time
import streamlit as st
import sqlite3
import bcrypt
from datetime import datetime
import pandas as pd

# SQLite データベースのパス
DB_NAME = "learning_progress.db"

# SQLite データベースに接続する関数
def connect_db():
    conn = sqlite3.connect(DB_NAME)
    return conn

# ユーザー情報のテーブルを作成する関数
def create_user_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

# ユーザー情報をデータベースに保存する関数
def save_user(username, password):
    conn = connect_db()
    cursor = conn.cursor()
    
    # パスワードをハッシュ化
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    try:
        cursor.execute("""
            INSERT INTO users (username, password)
            VALUES (?, ?)
        """, (username, hashed_password))
        conn.commit()
    except sqlite3.IntegrityError:
        st.error("このユーザー名は既に使用されています")
    conn.close()

# ユーザーの認証を行う関数
def authenticate_user(username, password):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user:
        stored_password = user[2]  # パスワードはハッシュ化されている
        if bcrypt.checkpw(password.encode('utf-8'), stored_password):
            return True
    return False

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

# ページのタイトル
st.title("ポモドーロタイマーと学習管理")

# ユーザー登録とログインのセクション
create_user_table()  # 初回実行時にユーザー情報テーブルを作成

# ログインフォーム
def login_form():
    st.header("ログイン")
    username = st.text_input("ユーザー名")
    password = st.text_input("パスワード", type="password")
    if st.button("ログイン"):
        if authenticate_user(username, password):
            st.success(f"{username}さん、ようこそ！")
            st.session_state.username = username
        else:
            st.error("ユーザー名またはパスワードが間違っています。")

# ユーザー登録フォーム
def register_form():
    st.header("ユーザー登録")
    username = st.text_input("新規ユーザー名")
    password = st.text_input("新規パスワード", type="password")
    if st.button("登録"):
        if username and password:
            save_user(username, password)
            st.success("ユーザー登録が完了しました！")
        else:
            st.error("ユーザー名とパスワードを入力してください！")

# ログイン画面または登録画面を選択
auth_choice = st.sidebar.radio("ログインまたは登録", ("ログイン", "新規登録"))

if auth_choice == "ログイン":
    login_form()
elif auth_choice == "新規登録":
    register_form()

# ログインが成功した場合、学習進捗を管理する
if "username" in st.session_state:
    username = st.session_state.username
    
    # タイマーの設定と学習管理セクション
    POMODORO_DURATION = 25 * 60  # 25分
    BREAK_DURATION = 5 * 60  # 5分
    LONG_BREAK_DURATION = 15 * 60  # 15分

    # タイマー開始ボタン
    timer_type = st.selectbox("タイマーの選択", ["ポモドーロ", "短い休憩", "長い休憩"])

    if st.button("タイマー開始"):
        if timer_type == "ポモドーロ":
            duration = POMODORO_DURATION
            st.info("ポモドーロタイマーが開始されました。25分間集中しましょう！")
        elif timer_type == "短い休憩":
            duration = BREAK_DURATION
            st.info("短い休憩タイマーが開始されました。5分間休憩しましょう！")
        elif timer_type == "長い休憩":
            duration = LONG_BREAK_DURATION
            st.info("長い休憩タイマーが開始されました。15分間休憩しましょう！")
        
        # タイマーのカウントダウン
        progress_bar = st.progress(0)  # 進捗バーを作成
        end_time = time.time() + duration
        
        while time.time() < end_time:
            remaining_time = int(end_time - time.time())
            minutes, seconds = divmod(remaining_time, 60)
            progress_bar.progress((time.time() - (end_time - duration)) / duration)  # 進捗の更新
            st.text(f"残り時間: {minutes:02d}:{seconds:02d}")
            time.sleep(1)  # 1秒ごとに進捗更新
        
        st.success(f"{timer_type}が完了しました！")

    # 学習管理セクション
    st.header("学習管理")
    subjects = ["数学", "英語", "国語", "物理", "生物", "情報"]
    selected_subject = st.selectbox("学習する科目を選択", subjects)
    
    study_time = st.number_input(f"{selected_subject}の学習時間 (分)", min_value=0, step=1)
    
    if st.button("学習時間を追加"):
        # データベースに学習時間を保存
        save_learning_data(selected_subject, study_time)
        st.success(f"{study_time}分の学習時間が記録されました！")

    # 学習進捗の表示
    st.header("学習進捗")
    data = get_learning_data()
    df = pd.DataFrame(data, columns=["ID", "科目", "学習日", "曜日", "学習時間 (分)"])
    st.table(df)
