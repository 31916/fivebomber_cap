import asyncio
import websockets
import json
import base64
import hashlib

OBS_WS_URL = "ws://localhost:4455"
PASSWORD = "114514"  # OBSで設定したものと同じに

async def connect_to_obs():
    async with websockets.connect(OBS_WS_URL) as websocket:
        # Step 1: Get Hello message
        hello = json.loads(await websocket.recv())
        if "authentication" in hello["d"]:
            # Step 2: Authenticate if required
            auth = hello["d"]["authentication"]
            secret = base64.b64encode(
                hashlib.sha256((PASSWORD + auth["salt"]).encode()).digest()
            ).decode()
            auth_response = base64.b64encode(
                hashlib.sha256((secret + auth["challenge"]).encode()).digest()
            ).decode()
            await websocket.send(json.dumps({
                "op": 1,
                "d": {
                    "rpcVersion": 1,
                    "authentication": auth_response
                }
            }))
            response = json.loads(await websocket.recv())
            if response["op"] == 2 and response["d"]["negotiatedRpcVersion"] >= 1:
                print("✅ 接続＆認証成功！")
            else:
                print("❌ 認証失敗")
        else:
            print("🔓 認証なしで接続成功")

asyncio.run(connect_to_obs())
