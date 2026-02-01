import os
import json
import telebot
from telebot import types
import requests
from datetime import datetime
from time import time
from zoneinfo import ZoneInfo
import random

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# KANALLAR
KANAL_1 = "@lethasystem"
KANAL_2 = "@israiltek"
KANAL_3 = "@lethayedek"
KANAL_4 = "@israilkrallik"

# DURUMLAR
user_states = {}

FREE_TIMEOUT = 15
last_query_time = {}

free_modes = [
    "adsoyad","tcpro","ailepro","sulalepro","tcgsm","gsmtc",
    "cocuksorgu","isyeri","tapu","adaparsel","ailegsm","sulalegsm"
]

# KULLANICI KANALDA MI?
def uye_mi(user_id, kanal):
    try:
        uye = bot.get_chat_member(kanal, user_id)
        return uye.status in ["member", "administrator", "creator"]
    except:
        return False


def kanal_kontrol(uid, chat_id):
    eksik_kanallar = []

    if not uye_mi(uid, KANAL_1):
        eksik_kanallar.append(("📢 Kanal 1", "https://t.me/lethasystem"))
    if not uye_mi(uid, KANAL_2):
        eksik_kanallar.append(("📢 Kanal 2", "https://t.me/israiltek"))
    if not uye_mi(uid, KANAL_3):
        eksik_kanallar.append(("📢 Kanal 3", "https://t.me/lethayedek"))
    if not uye_mi(uid, KANAL_4):
        eksik_kanallar.append(("📢 Kanal 4", "https://t.me/israilkrallik"))

    if not eksik_kanallar:
        return True

    kb = types.InlineKeyboardMarkup(row_width=1)
    for ad, url in eksik_kanallar:
        kb.add(types.InlineKeyboardButton(ad, url=url))
    kb.add(types.InlineKeyboardButton("✅ Kontrol Et", callback_data="kontrol_et"))

    bot.send_message(
        chat_id,
        "❗ Devam etmek için aşağıdaki kanallara katılman gerekiyor:",
        reply_markup=kb
    )
    return False


@bot.callback_query_handler(func=lambda call: call.data == "kontrol_et")
def kontrol_et(call):
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("🤖 OSINT Botu Başlat", url="https://t.me/lethaosint2026bot?start=zorunlu"))
    kb.add(types.InlineKeyboardButton("🔁 Tekrar Kontrol Et", callback_data="kontrol_et"))

    bot.edit_message_text(
        "Kanallara katıldıysan tekrar dene.\n\n/devam için /komutlar yaz.",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=kb
    )


def send_query_result(chat_id, data_list, mode):
    txt = ""
    for i, d in enumerate(data_list, 1):
        txt += f"📌 Kayıt {i}\n"
        for k, v in d.items():
            txt += f"{k}: {v}\n"
        txt += "\n---\n"

    with open("sonuc.txt", "w", encoding="utf-8") as f:
        f.write(txt)

    with open("sonuc.txt", "rb") as f:
        bot.send_document(chat_id, f)

    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("🔄 Tekrar Sorgula", callback_data=mode + "_tekrar"),
        types.InlineKeyboardButton("🏠 Ana Menü", callback_data="geri_ana")
    )
    bot.send_message(chat_id, "İstersen tekrar sorgu yapabilirsin:", reply_markup=kb)


@bot.message_handler(commands=["start"])
def start(message):
    if message.chat.type != "private":
        return

    ad = message.from_user.first_name or ""
    soyad = message.from_user.last_name or ""
    isim = f"{ad} {soyad}".strip()

    ist_time = datetime.now(ZoneInfo("Europe/Istanbul")).strftime("%d.%m.%Y | %H:%M:%S")

    mesajlar = [
        "Bugün veri okyanusunda biraz yüzmeye ne dersin? 🌊",
        "Dedektif şapkası hazır mı? 🕵️‍♂️",
        "Sistemler sıcak, sorgular hazır ⚡",
        "Hadi bakalım… bugün neler öğreneceğiz!"
    ]

    caption = (
        f"👋 Hoş geldin {isim}\n\n"
        f"{random.choice(mesajlar)}\n\n"
        f"📅 {ist_time}\n\n"
        f"➡️ Başlamak için /komutlar yaz"
    )

    bot.send_message(message.chat.id, caption)


@bot.message_handler(commands=["komutlar"])
def komutlar(message):
    if message.chat.type != "private":
        return
    if not kanal_kontrol(message.from_user.id, message.chat.id):
        return

    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("🔎 Sorgu İşlemleri", callback_data="sxrgu"),
        types.InlineKeyboardButton("⭐ VIP", callback_data="vip_sxrgu"),
        types.InlineKeyboardButton("❓ Bot Nedir?", callback_data="nedir")
    )
    bot.send_message(message.chat.id, "Menü:", reply_markup=kb)


def sxrgu_menu(chat_id):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("👤 Ad Soyad", callback_data="adsoyad"),
        types.InlineKeyboardButton("🆔 TC Pro", callback_data="tcpro"),
        types.InlineKeyboardButton("📞 TC ➜ GSM", callback_data="tcgsm"),
        types.InlineKeyboardButton("📲 GSM ➜ TC", callback_data="gsmtc"),
        types.InlineKeyboardButton("🔙 Geri", callback_data="geri_ana")
    )
    bot.send_message(chat_id, "Sorgu türünü seç:", reply_markup=kb)


@bot.callback_query_handler(func=lambda c: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    uid = call.from_user.id

    if not kanal_kontrol(uid, chat_id):
        return

    if call.data == "sxrgu":
        sxrgu_menu(chat_id)

    elif call.data.endswith("_tekrar"):
        mode = call.data.replace("_tekrar", "")
        user_states[uid] = {"mode": mode}
        bot.send_message(chat_id, "Tekrar bilgi gir:")

    elif call.data == "geri_ana":
        komutlar(call.message)

    elif call.data in ["adsoyad", "tcpro", "tcgsm", "gsmtc"]:
        user_states[uid] = {"mode": call.data}
        bot.send_message(chat_id, "Bilgiyi gir:")


@bot.message_handler(func=lambda m: True)
def state_handler(message):
    uid = message.from_user.id
    chat_id = message.chat.id

    state = user_states.get(uid)
    if not state:
        return

    mode = state["mode"]
    last_query_time[uid] = time()

    try:
        if mode == "tcgsm":
            r = requests.get("https://lethasorgu.com/alwaydsalvoxd/tc.php", params={"tc": message.text}, timeout=10)
            send_query_result(chat_id, r.json().get("data", []), mode)

        elif mode == "gsmtc":
            r = requests.get("http://45.134.173.160/gsm.php?gsm=" + message.text, timeout=10)
            send_query_result(chat_id, r.json().get("data", []), mode)

    except Exception as e:
        bot.send_message(chat_id, f"Hata oluştu: {e}")

    user_states.pop(uid, None)


print("Bot aktif")
bot.infinity_polling(skip_pending=True)
