import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus, ChatType
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped
import yt_dlp

# --- Config ---
API_ID = 33421644
API_HASH = "f22e5554f51fd494a664b2cb90ec64c2"
BOT_TOKEN = "8885714126:AAH-pNURgKFHoKl_Lr8OokQgHD9hsuTqbj0"
OWNER_ID = 8305397892

app = Client("music_userbot", api_id=API_ID, api_hash=API_HASH)
bot = Client("music_bot_api", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
call_py = PyTgCalls(app)

# ----------------- MUSIC -----------------
@app.on_message(filters.command("play") & filters.group)
async def play_handler(client, message):
    if len(message.command) < 2:
        await message.reply_text("သုံးနည်း - /play [Song Name or Link]")
        return
    query = message.text.split(None, 1)[1]
    # yt-dlp နဲ့ ရှာဖွေခြင်း
    ydl_opts = {"format": "bestaudio/best", "quiet": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        results = ydl.extract_info(f"ytsearch:{query}", download=False)
        video = results['entries'][0]
        url = video['url']
    
    await call_py.join_group_call(message.chat.id, AudioPiped(url))
    await message.reply_text(f"🎧 ဖွင့်နေသည်: {video['title']}")

@app.on_message(filters.command("stop") & filters.group)
async def stop_handler(client, message):
    await call_py.leave_group_call(message.chat.id)
    await message.reply_text("⏹ ရပ်လိုက်ပါပြီ။")

# ----------------- BROADCAST -----------------
# Bot ကို Start နှိပ်ထားသူအားလုံး နှင့် Admin ရထားသော Group များသို့ ပို့မည်
@bot.on_message(filters.command("post") & filters.user(OWNER_ID))
async def broadcast_handler(client, message):
    # (မှတ်ချက် - Database သုံးသင့်သော်လည်း ရိုးရှင်းစေရန် memory ကိုသုံးထားသည်)
    # ဤနေရာတွင် User IDs များကို သိမ်းဆည်းရန် လိုအပ်ပါသည်
    # ဤ code သည် လက်ရှိ dialogs များကို ရှာဖွေပြီး ပို့ပေးပါမည်
    async for dialog in bot.get_dialogs():
        try:
            if dialog.chat.type == ChatType.PRIVATE:
                await message.reply_to_message.copy(dialog.chat.id)
            elif dialog.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
                member = await bot.get_chat_member(dialog.chat.id, "me")
                if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                    await message.reply_to_message.copy(dialog.chat.id)
        except: continue
    await message.reply_text("✅ ပို့ပြီးပါပြီ။")

# ----------------- MENTION -----------------
@bot.on_message(filters.command("mention") & filters.group)
async def mention_handler(client, message):
    # Admin ဟုတ်မဟုတ် စစ်ဆေးခြင်း
    member = await message.chat.get_member(message.from_user.id)
    if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        await message.reply_text("❌ Admin များသာ ခေါ်နိုင်ပါသည်။")
        return
    
    # Member အားလုံးကို မန်းရှင်းခေါ်ခြင်း
    msg = ""
    async for m in bot.get_chat_members(message.chat.id):
        if not m.user.is_bot:
            msg += f"[{m.user.first_name}](tg://user?id={m.user.id}) "
            if len(msg) > 3000: break
    await message.reply_text(msg)

bot.run()
app.start()
call_py.start()
