"""
帮我写个企微智能机器人的服务，用户发消息，回复：你好 YYYY-MM-DD HH:MM:SS
注意，机器人是API 长连接模式，用websocket ，不需要搞内网穿透、公网IP等
代码写在这个脚本就好了，功能极简。
你帮我测试一下，确保代码能启动就好了。
botid=aibi4-9wJs3bUcqmlF4yHrA10dqN5vI538Q
botsecret=QEdToJfP4nYj7uISPkaleqRg5wnYBnk8pH9xjEFeEeh
"""

import asyncio
import json
import logging
import sys
import uuid
from datetime import datetime, timezone, timedelta

import websockets

# ---------- 配置 ----------
WSS_URL = "wss://openws.work.weixin.qq.com"
BOT_ID = "aibi4-9wJs3bUcqmlF4yHrA10dqN5vI538Q"
BOT_SECRET = "QEdToJfP4nYj7uISPkaleqRg5wnYBnk8pH9xjEFeEeh"
HEARTBEAT_INTERVAL = 30  # 秒
RECONNECT_BASE = 1       # 重连基数（秒）
RECONNECT_MAX = 60       # 最大重连间隔（秒）

# ---------- 日志 ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("qwbot")


def now_cst() -> str:
    """返回中国标准时间字符串"""
    cst = timezone(timedelta(hours=8))
    return datetime.now(cst).strftime("%Y-%m-%d %H:%M:%S")


def gen_req_id(prefix: str = "req") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


async def heartbeat(ws):
    """30 秒发送一次 ping 保活"""
    while True:
        try:
            await asyncio.sleep(HEARTBEAT_INTERVAL)
            await ws.send(json.dumps({"cmd": "ping"}))
            logger.debug("heartbeat ping sent")
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.warning(f"heartbeat failed: {e}")
            break


async def handle_message(ws, raw: str):
    """处理企微推送的单帧消息"""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning(f"invalid json: {raw[:200]}")
        return

    cmd = data.get("cmd")
    headers = data.get("headers", {})
    body = data.get("body", {})
    req_id = headers.get("req_id")

    # 打印所有收到的原始帧（调试用）
    logger.debug(f"recv raw: {raw[:500]}")

    # 处理通用响应/ack（如 subscribe 或 respond_msg 的返回）
    if "errcode" in data:
        logger.info(f"server ack: errcode={data.get('errcode')} errmsg={data.get('errmsg')} cmd={cmd}")
        return

    logger.info(f"recv [{cmd}] req_id={req_id}")

    if cmd == "aibot_msg_callback":
        msgtype = body.get("msgtype")
        if msgtype == "text":
            content = body.get("text", {}).get("content", "")
            sender = body.get("from", {}).get("userid", "unknown")
            logger.info(f"user={sender} says: {content}")

            reply = {
                "cmd": "aibot_respond_msg",
                "headers": {"req_id": req_id},
                "body": {
                    "msgtype": "markdown",
                    "markdown": {"content": f"你好，{sender}， **{now_cst()}**"},
                },
            }
            raw_reply = json.dumps(reply, ensure_ascii=False)
            logger.info(f"sending reply: {raw_reply}")
            await ws.send(raw_reply)
            logger.info(f"reply sent: req_id={req_id}")
        else:
            logger.info(f"ignore msgtype={msgtype}")

    elif cmd == "aibot_event_callback":
        event = body.get("event", {})
        event_type = event.get("type")
        logger.info(f"event type={event_type}")

    elif cmd == "ping":
        # 如果服务器主动发 ping，按协议可回 pong（企微一般不需要）
        pass

    else:
        logger.debug(f"unhandled cmd={cmd}")


async def connect_and_serve():
    """建立连接、鉴权、启动心跳、进入接收循环"""
    logger.info(f"connecting to {WSS_URL} ...")
    async with websockets.connect(WSS_URL) as ws:
        # 1. 订阅鉴权
        subscribe = {
            "cmd": "aibot_subscribe",
            "headers": {"req_id": gen_req_id("sub")},
            "body": {"bot_id": BOT_ID, "secret": BOT_SECRET},
        }
        await ws.send(json.dumps(subscribe, ensure_ascii=False))
        logger.info(f"subscribe sent bot_id={BOT_ID}")

        # 2. 启动心跳
        hb_task = asyncio.create_task(heartbeat(ws))

        # 3. 接收循环
        try:
            async for raw in ws:
                await handle_message(ws, raw)
        finally:
            hb_task.cancel()
            try:
                await hb_task
            except asyncio.CancelledError:
                pass


async def main():
    """带指数退避的断线重连主循环"""
    attempt = 0
    while True:
        try:
            await connect_and_serve()
        except websockets.ConnectionClosed as e:
            logger.warning(f"connection closed: {e}")
        except websockets.InvalidStatusCode as e:
            logger.error(f"handshake failed: {e}")
        except Exception as e:
            logger.error(f"unexpected error: {e}", exc_info=True)

        # 指数退避
        delay = min(RECONNECT_BASE * (2 ** attempt), RECONNECT_MAX)
        attempt += 1
        logger.info(f"reconnecting in {delay}s ... (attempt={attempt})")
        await asyncio.sleep(delay)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("shutdown by user")
        sys.exit(0)
