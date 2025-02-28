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
    hashed_password = bcrypt.hash(password)
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
        stored_password = user[2]
        if bcrypt.verify(password, stored_password):
            return True
    return False

# 学習進捗テーブルを作成する関数
def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            subject TEXT,
            date TEXT,
            day_of_week TEXT,
            study_time INTEGER,
            FOREIGN KEY (username) REFERENCES users (username)
        )
    """)
    conn.commit()
    conn.close()

# 学習データをデータベースに保存する関数
def save_learning_data(username, subject, study_time):
    conn = connect_db()
    cursor = conn.cursor()
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    day_of_week = now.strftime("%A")
    
    # 既存のデータをチェックし、同じ日・科目があれば更新
    cursor.execute("SELECT study_time FROM progress WHERE username = ? AND subject = ? AND date = ?", (username, subject, date_str))
    existing = cursor.fetchone()
    if existing:
        new_study_time = existing[0] + study_time
        cursor.execute("UPDATE progress SET study_time = ? WHERE username = ? AND subject = ? AND date = ?", (new_study_time, username, subject, date_str))
    else:
        cursor.execute("""
            INSERT INTO progress (username, subject, date, day_of_week, study_time)
            VALUES (?, ?, ?, ?, ?)
        """, (username, subject, date_str, day_of_week, study_time))
    
    conn.commit()
    conn.close()

# 学習データをデータベースから取得する関数
def get_learning_data(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT subject, date, day_of_week, study_time FROM progress WHERE username = ? ORDER BY date DESC", (username,))
    data = cursor.fetchall()
    conn.close()
    return data

# 日ごとの合計学習時間を取得する関数
def get_daily_totals(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT date, SUM(study_time) FROM progress WHERE username = ? GROUP BY date ORDER BY date DESC", (username,))
    data = cursor.fetchall()
    conn.close()
    return data

# ページのタイトル
st.title("学習管理アプリ")
create_table()
create_user_table()

auth_choice = st.sidebar.radio("ログインまたは登録", ("ログイン", "新規登録"))
username = None
if auth_choice == "ログイン":
    username = st.text_input("ユーザー名")
    password = st.text_input("パスワード", type="password")
    if st.button("ログイン") and authenticate_user(username, password):
        st.session_state.username = username
elif auth_choice == "新規登録":
    new_username = st.text_input("新規ユーザー名")
    new_password = st.text_input("新規パスワード", type="password")
    if st.button("登録") and new_username and new_password:
        save_user(new_username, new_password)
        st.success("ユーザー登録が完了しました！")

if 'username' in st.session_state:
    username = st.session_state.username
    st.subheader("学習管理")
    subjects = ["数学", "英語", "国語", "物理", "生物", "情報"]
    selected_subject = st.selectbox("学習する科目を選択", subjects)
    study_time = st.number_input(f"{selected_subject}の学習時間 (分)", min_value=0, step=1)
    if st.button("学習時間を追加"):
        save_learning_data(username, selected_subject, study_time)
        st.success(f"{study_time}分の学習時間が記録されました！")

    # 📊 学習進捗の表示（見やすく）
    st.subheader("📊 学習進捗")
    data = get_learning_data(username)
    df = pd.DataFrame(data, columns=["科目", "学習日", "曜日", "学習時間 (分)"])
    st.table(df)
    
    # 📅 日ごとの合計学習時間の表示
    st.subheader("📅 日ごとの合計学習時間")
    daily_data = get_daily_totals(username)
    daily_df = pd.DataFrame(daily_data, columns=["学習日", "合計学習時間 (分)"])
    st.table(daily_df)
