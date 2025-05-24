import cv2
import mediapipe as mp
import numpy as np

# Mediapipe Pose
mp_pose = mp.solutions.pose

# カメラ初期化
cap = cv2.VideoCapture(0)

# Poseモデル
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

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)

        h, w, _ = image.shape
        output_image = image.copy()

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            nose = landmarks[mp_pose.PoseLandmark.NOSE]

            x1 = int(min(left_shoulder.x, right_shoulder.x) * w) - 40
            x2 = int(max(left_shoulder.x, right_shoulder.x) * w) + 40

            shoulder_y = int(max(left_shoulder.y, right_shoulder.y) * h)
            head_top_y = int(nose.y * h - (x2 - x1) * 0.8)
            body_bottom_y = int(shoulder_y + (x2 - x1) * 2.0)

            y1 = max(0, head_top_y)
            y2 = min(h, body_bottom_y)
            x1 = max(0, x1)
            x2 = min(w, x2)

            cropped = image[y1:y2, x1:x2]

            if cropped.size != 0:
                target_w, target_h = 180, 240
                ch, cw = cropped.shape[:2]
                scale = max(target_w / cw, target_h / ch)  # 「大きめに拡大」してあとで中心をクロップ

                resized = cv2.resize(cropped, (int(cw * scale), int(ch * scale)))
                rh, rw = resized.shape[:2]

                # 中央を切り出し
                x_start = (rw - target_w) // 2
                y_start = (rh - target_h) // 2
                cropped_center = resized[y_start:y_start + target_h, x_start:x_start + target_w]

                cv2.imshow("Upper Body (Natural Aspect Ratio)", cropped_center)

        cv2.imshow('Camera', output_image)

        if cv2.waitKey(5) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
