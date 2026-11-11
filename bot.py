import os
import threading
import discord
from discord.ext import tasks
from flask import Flask

TOKEN = os.environ["TOKEN"]
CHANNEL_ID = int(os.environ["VOICE_CHANNEL_ID"])

# --- Web server nhỏ để UptimeRobot ping ---
app = Flask(__name__)

@app.route("/")
def home():
    return "ok"

def run_web():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

# --- Bot ---
client = discord.Client(intents=discord.Intents.default())

async def ensure_connected():
    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        return
    vc = channel.guild.voice_client
    if vc and vc.is_connected():
        if vc.channel.id != CHANNEL_ID:
            await vc.move_to(channel)
        return
    if vc:
        try:
            await vc.disconnect(force=True)
        except Exception:
            pass
    await channel.connect(reconnect=True)

@tasks.loop(seconds=30)
async def keep_alive():
    try:
        await ensure_connected()
    except Exception as e:
        print("Lỗi vào lại voice:", e)

@client.event
async def on_ready():
    print("Đã đăng nhập:", client.user)
    if not keep_alive.is_running():
        keep_alive.start()

threading.Thread(target=run_web, daemon=True).start()
client.run(TOKEN)
