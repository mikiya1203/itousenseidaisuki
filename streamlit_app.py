import streamlit as st
import time
import json
import os

# ポモドーロタイマーの設定
POMODORO_DURATION = 25 * 60  # 25分
BREAK_DURATION = 5 * 60  # 5分
LONG_BREAK_DURATION = 15 * 60  # 15分

# 学習進捗を保存するファイルのパス
data_file = "learning_progress.json"

# 学習データをロードする関数
def load_learning_data():
    if os.path.exists(data_file):
        with open(data_file, "r") as file:
            return json.load(file)
    else:
        return {}

# 学習データを保存する関数
def save_learning_data(data):
    with open(data_file, "w") as file:
        json.dump(data, file)

# 学習進捗の設定
learning_progress = load_learning_data()

# ポモドーロサイクルのカウント
pomodoro_cycles = learning_progress.get("pomodoro_cycles", 0)

# 音声通知を再生する関数
def play_notification_sound():
    sound_file = 'notification_sound.mp3'  # 音声ファイルのパス
    audio_data = open(sound_file, 'rb').read()  # 音声データを読み込む
    st.audio(audio_data, format="audio/mp3")  # 音声を再生

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
        pomodoro_cycles += 1  # ポモドーロサイクル数を増加
        save_learning_data({"pomodoro_cycles": pomodoro_cycles})  # サイクル数を保存
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
    play_notification_sound()  # タイマー終了時に音を鳴らす

# 学習管理セクション
st.header("学習管理")
subject = st.text_input("学習する科目またはトピック")

# 学習進捗を記録する
if subject:
    if subject not in learning_progress:
        learning_progress[subject] = {"total_time": 0, "sessions": 0}

    study_time = st.number_input(f"{subject}の学習時間 (分)", min_value=0, step=1)

    # 学習時間を記録するボタン
    if st.button("学習時間を追加"):
        learning_progress[subject]["total_time"] += study_time
        learning_progress[subject]["sessions"] += 1
        save_learning_data(learning_progress)  # 学習データを保存
        st.success(f"{study_time}分の学習時間が記録されました！")

# 学習進捗の表示
st.header("学習進捗")
if learning_progress:
    for subject, data in learning_progress.items():
        if subject != "pomodoro_cycles":  # ポモドーロサイクルは除外
            total_time = data["total_time"]
            sessions = data["sessions"]
            st.write(f"{subject}: {total_time}分 (セッション数: {sessions})")

# 完了したポモドーロサイクル数を表示
st.write(f"完了したポモドーロサイクル数: {pomodoro_cycles}")
