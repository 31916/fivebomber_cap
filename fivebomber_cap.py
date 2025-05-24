import cv2
import mediapipe as mp
import asyncio
import json
import websockets
import base64
import hashlib

# OBS接続設定
OBS_WS_URL = "ws://localhost:4455"
OBS_PASSWORD = "114514"
SOURCE_NAMES = ["Face1", "Face2", "Face3", "Face4", "Face5"]  # OBSソース名と対応させる

# MediaPipe初期化
mp_face = mp.solutions.face_detection
face_detection = mp_face.FaceDetection(model_selection=0, min_detection_confidence=0.5)

# 認証付きOBS接続
async def connect_obs():
    ws = await websockets.connect(OBS_WS_URL)
    hello = json.loads(await ws.recv())
    if "authentication" in hello["d"]:
        auth = hello["d"]["authentication"]
        secret = base64.b64encode(
            hashlib.sha256((OBS_PASSWORD + auth["salt"]).encode()).digest()
        ).decode()
        auth_response = base64.b64encode(
            hashlib.sha256((secret + auth["challenge"]).encode()).digest()
        ).decode()
        await ws.send(json.dumps({
            "op": 1,
            "d": {
                "rpcVersion": 1,
                "authentication": auth_response
            }
        }))
        await ws.recv()
    return ws

# クロップ送信
async def send_crop(ws, source_name, x, y, width, height, frame_width, frame_height):
    crop_data = {
        "left": int(x),
        "top": int(y),
        "right": int(frame_width - (x + width)),
        "bottom": int(frame_height - (y + height))
    }
    await ws.send(json.dumps({
        "op": 6,
        "d": {
            "requestType": "SetSourceFilterSettings",
            "requestId": "crop_" + source_name,
            "requestData": {
                "sourceName": source_name,
                "filterName": "Crop/Pad",
                "filterSettings": crop_data
            }
        }
    }))

# メイン処理
async def main():
    ws = await connect_obs()
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        height, width, _ = frame.shape
        results = face_detection.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        if results.detections:
            for i, detection in enumerate(results.detections[:5]):
                bbox = detection.location_data.relative_bounding_box
                x = int(bbox.xmin * width)
                y = int(bbox.ymin * height)
                w = int(bbox.width * width)
                h = int(bbox.height * height)
                source_name = SOURCE_NAMES[i]
                await send_crop(ws, source_name, x, y, w, h, width, height)

        cv2.imshow("Camera", frame)
        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    await ws.close()

if __name__ == "__main__":
    asyncio.run(main())
