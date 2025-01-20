import discord
import requests
import os
import json
import time
import asyncio

TOKEN = os.getenv("TOKEN")  # Your Discord Bot Token
ATERNOS_SESSION = os.getenv("ATERNOS_SESSION")  # Aternos Session Cookie
ATERNOS_SERVER = os.getenv("ATERNOS_SERVER")  # Aternos Server Cookie

intents = discord.Intents.default()
client = discord.Client(intents=intents)

def send_request(action):
    """Send start/stop request to Aternos"""
    if action == "start":
        url = "https://aternos.org/panel/ajax/start.php"
    elif action == "stop":
        url = "https://aternos.org/panel/ajax/stop.php"
    else:
        return False  # Invalid action

    headers = {
        "Cookie": f"ATERNOS_SESSION={ATERNOS_SESSION}; ATERNOS_SERVER={ATERNOS_SERVER}",
        "Referer": "https://aternos.org/server/"
    }
    response = requests.get(url, headers=headers)
    return response.status_code == 200

def get_status():
    """Check Aternos server status"""
    url = "https://aternos.org/panel/ajax/status.php"
    headers = {
        "Cookie": f"ATERNOS_SESSION={ATERNOS_SESSION}; ATERNOS_SERVER={ATERNOS_SERVER}",
        "Referer": "https://aternos.org/server/"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return json.loads(response.text)
    return None

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower() == "!start":
        start_time = time.time()  # Record start time
        if send_request("start"):
            await message.channel.send("✅ Server is starting... Checking status every 30 seconds.")

            # Wait until server is online
            while True:
                await asyncio.sleep(30)  # Wait 30 seconds before checking again
                status = get_status()
                if status and status.get("online", False):  # Server is online
                    elapsed_time = round(time.time() - start_time)  # Calculate time taken
                    await message.channel.send(f"🟢 Server is now online! It took **{elapsed_time} seconds** to start.")
                    break
        else:
            await message.channel.send("❌ Failed to start server.")

    elif message.content.lower() == "!stop":
        if send_request("stop"):
            await message.channel.send("✅ Server is stopping...")
        else:
            await message.channel.send("❌ Failed to stop server.")

    elif message.content.lower() == "!status":
        status = get_status()
        if status:
            online = status.get("online", False)
            players = status.get("players", "0")
            version = status.get("version", "Unknown")
            motd = status.get("motd", "No MOTD")

            response = f"**Server Status:** {'🟢 Online' if online else '🔴 Offline'}\n"
            response += f"**Players Online:** {players}\n"
            response += f"**Version:** {version}\n"
            response += f"**MOTD:** {motd}"
            await message.channel.send(response)
        else:
            await message.channel.send("❌ Failed to fetch server status.")

client.run(TOKEN)
