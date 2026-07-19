from pyrogram import Client
api_id = 33421644
api_hash = "f22e5554f51fd494a664b2cb90ec64c2"
with Client("my_account", api_id=api_id, api_hash=api_hash) as app:
    print("သင့်ရဲ့ Session String အောက်မှာ ပြထားပါတယ်-")
    print(app.export_session_string())
