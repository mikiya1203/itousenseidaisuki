import streamlit as st
import time
import datetime

# ポモドーロタイマーの設定
POMODORO_DURATION = 25 * 60  # 25分
BREAK_DURATION = 5 * 60  # 5分
LONG_BREAK_DURATION = 15 * 60  # 15分

# 学習進捗の設定
learning_progress = {}

# ページのタイトル
st.title("ポモドーロタイマーと学習管理")

# タイマーのセクション
st.header("ポモドーロタイマー")
timer_type = st.selectbox("タイマーの選択", ["ポモドーロ", "短い休憩", "長い休憩"])

# タイマー開始ボタン
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
    end_time = time.time() + duration
    while time.time() < end_time:
        remaining_time = int(end_time - time.time())
        minutes, seconds = divmod(remaining_time, 60)
        st.text(f"残り時間: {minutes:02d}:{seconds:02d}")
        time.sleep(1)
        st.experimental_rerun()
    
    st.success(f"{timer_type}が完了しました！")


    