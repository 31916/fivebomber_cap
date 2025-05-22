import cv2
import mediapipe as mp
import numpy as np

# Mediapipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# カメラ初期化
cap = cv2.VideoCapture(0)

# Poseモデル（複数人対応）
with mp_pose.Pose(static_image_mode=False,
                  model_complexity=1,
                  enable_segmentation=False,
                  min_detection_confidence=0.5,
                  min_tracking_confidence=0.5) as pose:

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("カメラを読み込めません")
            break

        # 画像をRGBに変換
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)

        h, w, _ = image.shape
        output_image = image.copy()

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            # 上半身の座標（肩と頭）
            left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            nose = landmarks[mp_pose.PoseLandmark.NOSE]

            # ピクセル座標へ変換
            x1 = int(min(left_shoulder.x, right_shoulder.x) * w)
            x2 = int(max(left_shoulder.x, right_shoulder.x) * w)
            y1 = int(nose.y * h - (x2 - x1) * 0.5)  # 頭上まで含む
            y2 = int(max(left_shoulder.y, right_shoulder.y) * h + 50)

            # 安全な矩形に制限
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)

            # 上半身だけ切り取り
            cropped = image[y1:y2, x1:x2]

            # ウィンドウ表示
            cv2.imshow("Upper Body", cropped)

        # 元の映像も表示
        cv2.imshow('Camera', output_image)

        if cv2.waitKey(5) & 0xFF == 27:  # ESCキーで終了
            break

cap.release()
cv2.destroyAllWindows()
