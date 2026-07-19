import asyncio
import os
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus, ChatType
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped
import yt_dlp

API_ID = int(os.getenv("API_ID", "33421644"))
API_HASH = os.getenv("API_HASH", "f22e5554f51fd494a664b2cb90ec64c2")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8885714126:AAH-pNURgKFHoKl_Lr8OokQgHD9hsuTqbj0")
OWNER_ID = int(os.getenv("OWNER_ID", "8305397892"))
SESSION_STRING = os.getenv("SESSION_STRING")

if SESSION_STRING:
    app = Client("music_userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
else:
    app = Client("music_userbot", api_id=API_ID, api_hash=API_HASH)

bot = Client("music_bot_api", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call_py = PyTgCalls(app)

START_USERS_FILE = "users.txt"
def load_users():
    if os.path.exists(START_USERS_FILE):
        with open(START_USERS_FILE, "r") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_user(user_id):
    users = load_users()
    if str(user_id) not in users:
        with open(START_USERS_FILE, "a") as f:
            f.write(f"{user_id}\n")

@bot.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    save_user(message.from_user.id)
    await message.reply_text("👋 မင်္ဂလာပါ! ကျွန်ုပ်သည် သီချင်းဖွင့်ပေးနိုင်ပြီး Broadcast လုပ်နိုင်သော Bot ဖြစ်ပါသည်။")

# ----------------- MUSIC -----------------
@bot.on_message(filters.command("play") & filters.group)
async def play_handler(client, message):
    if len(message.command) < 2:
        await message.reply_text("❌ အသုံးပြုပုံ - /play [သီချင်းနာမည် သို့မဟုတ် YouTube Link]")
        return
    
    query = message.text.split(None, 1)[1]
    status_msg = await message.reply_text("🔍 YouTube မှ သီချင်းကို ရှာဖွေနေပါသည်...")
    
    try:
        ydl_opts = {
            "format": "bestaudio/best",
            "quiet": True,
            "default_search": "ytsearch",
            "noplaylist": True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            results = ydl.extract_info(query, download=False)
            if 'entries' in results and results['entries']:
                video = results['entries'][0]
            else:
                video = results
            url = video['url']
            title = video['title']
        
        await status_msg.edit_text("🎵 Voice Chat သို့ ချိတ်ဆက်နေပါသည်...")
        await call_py.join_group_call(message.chat.id, AudioPiped(url))
        await status_msg.edit_text(f"🎧 စတင်ဖွင့်လှစ်နေပါပြီ-\n✨ **{title}**")
    except Exception as e:
        await status_msg.edit_text(f"❌ အမှားအယွင်းရှိခဲ့သည်- {str(e)}")

@bot.on_message(filters.command("stop") & filters.group)
async def stop_handler(client, message):
    try:
        await call_py.leave_group_call(message.chat.id)
        await message.reply_text("⏹ သီချင်းဖွင့်ခြင်းကို ရပ်ဆိုင်းလိုက်ပါပြီ။")
    except Exception:
        await message.reply_text("❌ Bot သည် Voice Chat ထဲတွင် ရှိမနေပါ။")

# ----------------- BROADCAST -----------------
@bot.on_message(filters.command("post") & filters.user(OWNER_ID))
async def broadcast_handler(client, message):
    if not message.reply_to_message:
        await message.reply_text("❌ အသုံးပြုပုံ- တင်လိုသော Post (စာ/ပုံ/ဗီဒီယို) ကို `/post` ဟု Reply ပြန်ပါ။")
        return

    status_msg = await message.reply_text("📢 Users များနှင့် Admin Groups များသို့ Post တင်ပေးနေပါသည်...")
    success_users = 0
    success_groups = 0
    
    users = load_users()
    for user_id in users:
        try:
            await message.reply_to_message.copy(int(user_id))
            success_users += 1
            await asyncio.sleep(0.5)
        except:
            continue

    async for dialog in bot.get_dialogs():
        try:
            if dialog.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
                member = await bot.get_chat_member(dialog.chat.id, "me")
                if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                    await message.reply_to_message.copy(dialog.chat.id)
                    success_groups += 1
                    await asyncio.sleep(0.5)
        except:
            continue
            
    await status_msg.edit_text(f"✅ အောင်မြင်ပါသည်။\n👤 Users: {success_users} ယောက်\n👥 Groups: {success_groups} ခု သို့ ပို့ပြီးပါပြီ။")

# ----------------- MENTION -----------------
@bot.on_message(filters.command("mention") & filters.group)
async def mention_handler(client, message):
    member = await message.chat.get_member(message.from_user.id)
    if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        await message.reply_text("❌ Admin များသာ ဤ Command ကို သုံးနိုင်ပါသည်။")
        return
        
    bot_member = await message.chat.get_member("me")
    if bot_member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        await message.reply_text("❌ Bot အား Admin ခွင့်ပြုချက် ပေးထားရပါမည်။")
        return

    status_msg = await message.reply_text("📣 အဖွဲ့ဝင်များကို မန်းရှင်းခေါ်ယူနေပါသည်...")
    
    mentions = []
    async for m in bot.get_chat_members(message.chat.id):
        if not m.user.is_bot:
            mentions.append(f"[{m.user.first_name}](tg://user?id={m.user.id})")
    
    if not mentions:
        await status_msg.edit_text("အဖွဲ့ဝင်များ ရှာမတွေ့ပါ။")
        return

    chunk_size = 20
    chunks = [mentions[i:i + chunk_size] for i in range(0, len(mentions), chunk_size)]
    
    await status_msg.delete()
    for chunk in chunks:
        await bot.send_message(message.chat.id, " ".join(chunk))
        await asyncio.sleep(1)

# ----------------- START ALL CLIENTS -----------------
async def boot_bot():
    await app.start()
    await bot.start()
    await call_py.start()
    print("=== Bot Running on Render Successfully ===")
    await asyncio.Event().wait()

if __name__ == "__main__":
    # Render ပေါ်တွင် Event Loop မရှိသော ပြဿနာကို ဖြေရှင်းရန် ဤနေရာတွင် အသစ်တည်ဆောက်ထားပါသည်
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(boot_bot())
      
