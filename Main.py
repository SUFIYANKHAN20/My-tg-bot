import asyncio
import json
import os
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import google.generativeai as genai

# Server par variables set karenge hum
API_ID = 29689733
API_HASH = 'cfcbc674330f331dfbe3370663ac2996'
SESSION_STRING = os.getenv("SESSION_STRING")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

DATA_FILE = "approved_users.json"
approved_users = set()

if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE, "r") as f: approved_users = set(json.load(f))
    except: pass

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash", system_instruction="Aap ek intelligent aur fast AI hain. Har sawal ka precise jawab dein.")

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.approve$'))
async def approve(event):
    if not event.is_reply: return await event.edit("❌ Reply karke .approve likhein.")
    r = await event.get_reply_message()
    approved_users.add(r.sender_id)
    with open(DATA_FILE, "w") as f: json.dump(list(approved_users), f)
    await event.edit("✅ AI Access Granted!")

@client.on(events.NewMessage(outgoing=True, pattern=r'^\.demote$'))
async def demote(event):
    if not event.is_reply: return await event.edit("❌ Reply karke .demote likhein.")
    r = await event.get_reply_message()
    if r.sender_id in approved_users: approved_users.remove(r.sender_id)
    with open(DATA_FILE, "w") as f: json.dump(list(approved_users), f)
    await event.edit("🔴 AI Access Removed.")

@client.on(events.NewMessage(incoming=True))
async def reply(event):
    if event.sender_id in approved_users and event.text and not event.text.startswith(('.', '/')):
        await asyncio.sleep(3)
        try:
            res = model.generate_content(event.text)
            if res.text: await event.reply(f"💡 **AI:** {res.text}")
        except Exception as e: print(e)

print("Bot starting...")
client.start()
client.run_until_disconnected()

