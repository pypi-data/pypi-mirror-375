import cv2
import mediapipe as mp
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import threading
import time
import os
import urllib.request

# === Konfigurasi ===
INPUT_VIDEO = "input.mp4"
OUTPUT_VIDEO_TEMP = "output_temp.mp4"
OUTPUT_VIDEO_FINAL = "output.mp4"
VOICE_INTERVAL = 10
TARGET_PUSHUPS = 250
GLOW_DURATION = 0.4
BELL_URL = "https://cdn.pixabay.com/download/audio/2021/08/04/audio_3335508b5e.mp3?filename=bell-notification-86105.mp3"
BELL_FILE = "bell.mp3"

# Unduh file bell.mp3 jika belum ada
if not os.path.exists(BELL_FILE):
    print("Mengunduh file bel...")
    try:
        urllib.request.urlretrieve(BELL_URL, BELL_FILE)
        print("✅ Unduhan bel berhasil!")
    except Exception as e:
        print(f"Gagal mengunduh bel: {e}")
        # Jika gagal, notifikasi bel tidak akan diputar
        BELL_FILE = None

# Inisialisasi Mediapipe
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Variabel audio
bell_sound = AudioSegment.from_mp3(BELL_FILE) if BELL_FILE else None

cap = cv2.VideoCapture(INPUT_VIDEO)
if not cap.isOpened():
    print("Error: Tidak bisa membuka video input.")
    exit()

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

fourcc = cv2.VideoWriter_fourcc(*'avc1')
out = cv2.VideoWriter(OUTPUT_VIDEO_TEMP, fourcc, fps, (width, height))

counter = 0
stage = None
start_time = time.time()
last_increment_time = 0

def get_text_position(w, h):
    if h > w:
        return (int(w*0.25), int(h*0.1))
    else:
        return (50, 80)

def format_time(seconds):
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"

def play_count_voice(num):
    text = f"{num}"
    tts = gTTS(text=text, lang='id')
    filename = f"voice_{num}.mp3"
    tts.save(filename)
    sound = AudioSegment.from_mp3(filename)
    play(sound)
    os.remove(filename)

def play_bell_sound():
    if bell_sound:
        play(bell_sound)

try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
            )

            nose = results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE]
            right_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            left_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]

            shoulder_avg_y = (right_shoulder.y + left_shoulder.y) / 2

            if nose.y > shoulder_avg_y:
                stage = "down"
            
            if stage == "down" and nose.y < shoulder_avg_y:
                stage = "up"
                counter += 1
                last_increment_time = time.time()

                threading.Thread(target=play_bell_sound).start()

                if counter % VOICE_INTERVAL == 0:
                    threading.Thread(target=play_count_voice, args=(counter,)).start()

        elapsed = time.time() - start_time
        timer_text = format_time(elapsed)

        pos = get_text_position(width, height)
        cv2.putText(image, f'Push-ups: {counter}', pos,
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0,255,0), 5, cv2.LINE_AA)

        cv2.putText(image, f'Time: {timer_text}', (pos[0], pos[1]+80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255,255,255), 3, cv2.LINE_AA)

        bar_x, bar_y = 50, height - 100
        bar_width, bar_height = width - 100, 40

        progress = min(counter / TARGET_PUSHUPS, 1.0)
        filled_width = int(bar_width * progress)

        cv2.rectangle(image, (bar_x, bar_y),
                      (bar_x + bar_width, bar_y + bar_height),
                      (100,100,100), -1)

        glow_intensity = 0
        if time.time() - last_increment_time < GLOW_DURATION:
            glow_intensity = int(255 * (1 - (time.time() - last_increment_time) / GLOW_DURATION))

        cv2.rectangle(image, (bar_x, bar_y),
                      (bar_x + filled_width, bar_y + bar_height),
                      (0,255,0), -1)

        if glow_intensity > 0:
            overlay = image.copy()
            cv2.rectangle(overlay, (bar_x, bar_y),
                          (bar_x + filled_width, bar_y + bar_height),
                          (0, 255, 0), -1)
            alpha = glow_intensity / 255.0
            cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)

        cv2.putText(image, f"{counter}/{TARGET_PUSHUPS}",
                    (bar_x + int(bar_width/2) - 60, bar_y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255,255,255), 3, cv2.LINE_AA)

        out.write(image)

except Exception as e:
    print(f"Terjadi kesalahan saat memproses video: {e}")
finally:
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print("Mulai menggabungkan audio dan video...")

    try:
        command = f"ffmpeg -y -i {OUTPUT_VIDEO_TEMP} -i {INPUT_VIDEO} -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 -shortest {OUTPUT_VIDEO_FINAL}"
        os.system(command)
        print("✅ Selesai! Video hasil tersimpan sebagai output.mp4")
    except Exception as e:
        print(f"Gagal menggabungkan audio/video: {e}")
    
    if os.path.exists(OUTPUT_VIDEO_TEMP):
        os.remove(OUTPUT_VIDEO_TEMP)
    if os.path.exists(BELL_FILE) and BELL_FILE != "bell.mp3":
        os.remove(BELL_FILE)
