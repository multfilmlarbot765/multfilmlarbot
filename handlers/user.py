import asyncio
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from database import (add_user, get_content_by_code, get_files_by_content_id, increment_download,
                      search_content_by_keyword, get_top_content, get_random_content, get_setting,
                      add_feedback)
from keyboards.reply import get_main_menu, get_cancel_menu, get_user_main_menu
from keyboards.inline import get_content_inline_keyboard, get_top_content_keyboard, get_search_results_keyboard, get_start_menu, get_rating_keyboard, get_share_keyboard
from utils.fsm import ContactAdmin, RateBot
from utils.tasks import log_new_user, log_media_download, log_rating, log_contact
from utils.permissions import is_admin

router = Router()

async def send_content(message: Message, bot: Bot, code: int):
    content = await get_content_by_code(code)
    if not content:
        await message.answer("Bunday kodli multfilm yoki kino topilmadi. 😔")
        return
        
    files = await get_files_by_content_id(content['id'])
    if not files:
        await message.answer("Ushbu kontentda fayllar mavjud emas.")
        return
        
    await increment_download(content['id'])
    
    footer = await get_setting('custom_footer')
    bot_info = await bot.get_me()
    kb = get_content_inline_keyboard(content['code'], bot_info.username)
    
    # Send all files
    for i, f_id in enumerate(files, start=1):
        qism_matn = f"{i}-qism" if len(files) > 1 else "Yaxlit"
        
        caption = f"🍿 Nomi: {content['name']}\n"
        caption += f"🎞 Qism: {qism_matn}\n"
        
        if content['year']:
            caption += f"📅 Yil: {content['year']}\n"
        if content['quality']:
            caption += f"✨ Sifati: {content['quality']}\n"
        if content['genre']:
            caption += f"🎭 Janri: {content['genre']}\n"
            
        if footer:
            caption += f"\n\n{footer}"
            
        try:
            await message.answer_document(f_id, caption=caption, reply_markup=kb)
        except Exception:
            try:
                await message.answer_video(f_id, caption=caption, reply_markup=kb)
            except Exception as e:
                print(f"Error sending file: {e}")
                
    # Background log
    asyncio.create_task(log_media_download(
        bot,
        message.from_user.id,
        message.from_user.full_name,
        message.from_user.username,
        content['name'],
        content['code']
    ))

@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot, state: FSMContext):
    await state.clear()
    
    user = message.from_user
    is_new = await add_user(user.id, user.full_name, user.username)
    if is_new:
        asyncio.create_task(log_new_user(bot, user.id, user.full_name, user.username))
    
    args = message.text.split()
    if len(args) > 1 and args[1].isdigit():
        await send_content(message, bot, int(args[1]))
    else:
        admin_status = await is_admin(user.id)
        channel_link = await get_setting('main_channel_url')
        greeting = f"👋 Assalomu alaykum {user.full_name} botimizga xush kelibsiz.\n\n✍🏻 Multfilm kodini yuboring."
        
        if not admin_status:
            # For normal users, remove the Reply Keyboard invisibly
            msg = await message.answer("Yuklanmoqda...", reply_markup=get_user_main_menu(False))
            try:
                await msg.delete()
            except Exception:
                pass
                
        # Send greeting with Inline Keyboard
        await message.answer(greeting, reply_markup=get_start_menu(channel_link))

@router.callback_query(F.data == "start_random")
async def cb_random(callback: CallbackQuery, bot: Bot):
    content = await get_random_content()
    if content:
        msg = await callback.message.answer("Yuklanmoqda...")
        await send_content(callback.message, bot, content['code'])
        try:
            await msg.delete()
        except Exception:
            pass
    else:
        await callback.message.answer("Bazada ma'lumot yo'q.")
    await callback.answer()

@router.callback_query(F.data == "start_top")
async def cb_top_list(callback: CallbackQuery):
    top_contents = await get_top_content(10)
    if not top_contents:
        await callback.message.answer("Bazada ma'lumot yo'q.")
        await callback.answer()
        return
        
    text = "🏆 Top 10 eng ko'p yuklanganlar:\n\n"
    for i, content in enumerate(top_contents, start=1):
        ctype = "🍿" if content['type'] == 'multfilm' else "🎬"
        text += f"{i}. #{ctype}| Nomi: {content['name']} - {content['download_count']} marta yuklandi\n"
        
    await callback.message.answer(text, reply_markup=get_top_content_keyboard(top_contents))
    await callback.answer()

@router.callback_query(F.data == "start_search")
async def cb_search(callback: CallbackQuery):
    await callback.message.answer("Qidirmoqchi bo'lgan multfilm/kino nomini kiriting:")
    await callback.answer()

@router.callback_query(F.data.startswith("get_top_"))
async def cb_top(callback: CallbackQuery, bot: Bot):
    idx = int(callback.data.split("_")[2])
    top_contents = await get_top_content(10)
    if idx < len(top_contents):
        content = top_contents[idx]
        msg = await callback.message.answer("Yuklanmoqda...")
        await send_content(callback.message, bot, content['code'])
        try:
            await msg.delete()
        except Exception:
            pass
    await callback.answer()

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("Botdan foydalanish:\nKod yoki nom yozib yuboring.\nBuyruqlar: /start, /search, /contact, /rate, /share, /help, /creator")

@router.message(Command("search"))
async def cmd_search(message: Message):
    await message.answer("Qidirmoqchi bo'lgan multfilm/kino nomini kiriting:")

@router.message(Command("share"))
async def cmd_share(message: Message, bot: Bot):
    bot_info = await bot.get_me()
    await message.answer(
        "😊 Botimiz sizga yoqqan bo'lsa xursandmiz! Qolgan do'stlaringiz va guruhlarga ham ulashishingiz mumkin. 👇",
        reply_markup=get_share_keyboard(bot_info.username)
    )

@router.message(Command("creator"))
async def cmd_creator(message: Message):
    await message.answer("Ushbu botni yaratuvchisi: @Jamshidbek0722 \nSizga ham shunday bot kerak bo'lsa murojaat qiling @Jamshidbek0722")

@router.message(Command("contact"))
async def cmd_contact(message: Message, state: FSMContext):
    await message.answer("Adminga xabaringizni yozing:", reply_markup=get_cancel_menu())
    await state.set_state(ContactAdmin.message)

@router.message(ContactAdmin.message, F.text != "❌ Bekor qilish")
async def process_contact(message: Message, state: FSMContext, bot: Bot):
    user = message.from_user
    await add_feedback(user.id, "contact", message.text)
    
    # Dispatch event log
    asyncio.create_task(log_contact(bot, user.id, user.full_name, user.username, message.text))
    
    await message.answer("Xabaringiz adminga yuborildi. Rahmat!", reply_markup=ReplyKeyboardRemove())
    await state.clear()

@router.message(Command("rate"))
async def cmd_rate(message: Message):
    await message.answer("⭐️ Botimizga baho bering:", reply_markup=get_rating_keyboard())

@router.callback_query(F.data.startswith("rate_"))
async def cb_rating(callback: CallbackQuery, bot: Bot):
    stars = int(callback.data.split("_")[1])
    user = callback.from_user
    
    await add_feedback(user.id, "rate", str(stars))
    
    # Dispatch event log
    asyncio.create_task(log_rating(bot, user.id, user.full_name, user.username, stars))
    
    await callback.message.edit_text("Rahmat! Bahoyingiz qabul qilindi. 😊", reply_markup=None)
    await callback.answer()

@router.message(F.text == "❌ Bekor qilish")
async def btn_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Bekor qilindi.", reply_markup=ReplyKeyboardRemove())

@router.message(F.text)
async def process_text_search(message: Message, bot: Bot):
    text = message.text.strip()
    if text.isdigit():
        await send_content(message, bot, int(text))
    else:
        results = await search_content_by_keyword(text)
        if not results:
            await message.answer("Bunday nomdagi kontent topilmadi.")
            return
            
        if len(results) == 1:
            await send_content(message, bot, results[0]['code'])
        else:
            await message.answer("Quyidagi natijalar topildi:", reply_markup=get_search_results_keyboard(results))

@router.callback_query(F.data.startswith("get_content_"))
async def cb_get_content(callback: CallbackQuery, bot: Bot):
    code = int(callback.data.split("_")[2])
    msg = await callback.message.answer("Yuklanmoqda...")
    await send_content(callback.message, bot, code)
    try:
        await msg.delete()
    except Exception:
        pass
    await callback.answer()

@router.callback_query(F.data == "check_sub")
async def cb_check_sub(callback: CallbackQuery):
    await callback.message.delete()
    
    admin_status = await is_admin(callback.from_user.id)
    channel_link = await get_setting('main_channel_url')
    greeting = f"Obuna tasdiqlandi. 👋 Assalomu alaykum {callback.from_user.full_name} botimizga xush kelibsiz.\n\n✍🏻 Multfilm kodini yuboring."
    
    await callback.message.answer(
        greeting,
        reply_markup=get_start_menu(channel_link)
    )
    await callback.answer()


@router.callback_query(F.data == "check_forcesub")
async def cb_check_forcesub(callback: CallbackQuery, bot: Bot, state: FSMContext):
    import json
    channels_json = await get_setting('force_sub_channels')
    channels = []
    if channels_json:
        try:
            channels = json.loads(channels_json)
        except Exception:
            pass
    else:
        old_ch = await get_setting('force_sub_channel')
        if old_ch:
            channels = [{"id": old_ch}]
            
    if not channels:
        await cmd_start(callback.message, bot, state)
        await callback.message.delete()
        return
        
    try:
        is_subscribed = True
        for ch in channels:
            try:
                member = await bot.get_chat_member(chat_id=ch['id'], user_id=callback.from_user.id)
                if member.status in ['left', 'kicked']:
                    is_subscribed = False
                    break
            except Exception:
                pass
                
        if is_subscribed:
            # Subscribed
            await callback.message.delete()
            # Send greeting
            admin_status = await is_admin(callback.from_user.id)
            channel_link = await get_setting('main_channel_url')
            greeting = f"👋 Assalomu alaykum {callback.from_user.full_name} botimizga xush kelibsiz.\\n\\n✍🏻 Multfilm kodini yuboring."
            await callback.message.answer(greeting, reply_markup=get_start_menu(channel_link))
        else:
            # Not subscribed
            await callback.answer("❌ Siz hali kanalga obuna bo'lmadingiz!", show_alert=True)
    except Exception as e:
        print(f"Check forcesub error: {e}")
        await callback.message.delete()
        admin_status = await is_admin(callback.from_user.id)
        channel_link = await get_setting('main_channel_url')
        greeting = f"👋 Assalomu alaykum {callback.from_user.full_name} botimizga xush kelibsiz.\n\n✍🏻 Multfilm kodini yuboring."
        await callback.message.answer(greeting, reply_markup=get_start_menu(channel_link))
