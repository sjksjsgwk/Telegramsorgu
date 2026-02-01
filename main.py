import os
import json
import telebot
from telebot import types
import requests
from datetime import datetime
from time import time

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# KANALLAR
KANAL_1 = "@lethasystem"
KANAL_2 = "@israiltek"
KANAL_3 = "@lethayedek"
KANAL_4 = "@israilkrallik" # Yeni eklenen

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

    # KANAL 4 KONTROLÜ
    if not uye_mi(uid, KANAL_4):
        eksik_kanallar.append(("📢 Kanal 4", "https://t.me/israilkrallik"))

    if not eksik_kanallar:
        return True

    kb = types.InlineKeyboardMarkup(row_width=1)
    for ad, url in eksik_kanallar:
        kb.add(types.InlineKeyboardButton(ad, url=url))

    # KONTROL ET BUTONU
    kb.add(types.InlineKeyboardButton("✅ Kontrol Et", callback_data="kontrol_et"))
    
    return False


@bot.callback_query_handler(func=lambda call: call.data == "kontrol_et")
def kontrol_et(call):
    kb = types.InlineKeyboardMarkup(row_width=1)

    # OSINT BOT START (MESAJ DEĞİŞMEDEN)
    kb.add(
        types.InlineKeyboardButton(
            "🤖 OSINT Botu Başlat",
            url="https://t.me/lethaosint2026bot?start=zorunlu"
        )
    )

    kb.add(
        types.InlineKeyboardButton(
            "🔁 Tekrar Kontrol Et",
            callback_data="kontrol_et"
        )
    )

    bot.edit_message_caption(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        caption=(
            "Önce Gerekli Kanallara Katılman Gerek.\n\n"
            "Kanallara Katıldıktan Sonra /komutlar Aracılığı İle "
            "Güvenli Ve Uzun Ömür Erişim Sağlayın."
        ),
        reply_markup=kb
    )


def send_query_result(chat_id, data_list, mode):
    txt = ""
    for idx, d in enumerate(data_list,1):
        txt += f"📌 Kayıt {idx}:\n"
        for k,v in d.items():
            txt += f"{k}: {v}\n"
        txt += "\n---\n"
    with open("sonuc.txt","w",encoding="utf-8") as f:
        f.write(txt)
    with open("sonuc.txt","rb") as f:
        bot.send_document(chat_id,f)
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton("🔄 Tekrar Sorgula", callback_data=mode),types.InlineKeyboardButton("🏠 Ana Menüye Dön", callback_data=f"{mode}_ana"))
    bot.send_message(chat_id,"İstersen tekrar sorgu yapabilirsin:", reply_markup=kb)

def send_structured_result_basic(chat_id, js):
    txt = ""
    def fmt_basic(x):
        return f"TC: {x.get('TC','')}\nGSM: {x.get('GSM','')}\n"
    if "data" in js: txt += fmt_basic(js["data"]) + "\n"
    for c in js.get("cocuklar",[]): txt += fmt_basic(c) + "\n"
    if not txt: txt = "Veri bulunamadı"
    with open("sonuc.txt","w",encoding="utf-8") as f: f.write(txt)
    with open("sonuc.txt","rb") as f: bot.send_document(chat_id,f)
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("🔄 Tekrar Sorgula", callback_data="ailegsm" if "kisi" in js else "sulalegsm"),types.InlineKeyboardButton("🏠 Ana Menüye Dön", callback_data="ailegsm_ana" if "kisi" in js else "sulalegsm_ana"))
    bot.send_message(chat_id,"İstersen tekrar sorgu yapabilirsin:", reply_markup=kb)

from datetime import datetime
from zoneinfo import ZoneInfo
import random

@bot.message_handler(commands=["start"])
def start(message):
    if message.chat.type != "private":
        return

    ad = message.from_user.first_name or ""
    soyad = message.from_user.last_name or ""
    isim = f"{ad} {soyad}".strip()

    # İstanbul zamanı
    ist_time = datetime.now(ZoneInfo("Europe/Istanbul")).strftime("%d.%m.%Y | %H:%M:%S")

    # Rastgele mesajlar
    mesajlar = [
        "Bugün veri okyanusunda biraz yüzmeye ne dersin? 🌊🔎",
        "Dedektif şapkası hazır mı? Çünkü başlıyoruz! 🕵️‍♂️✨",
        "Sistemler sıcak, sorgular hazır — sadece sen eksiksin! ⚡",
        "Hadi bakalım… bugün neler öğreneceğiz! 👀",
        "Veriler yalan söylemez… ama biz okumasını bilirsek 😎",
        "Sakin… derin nefes… ve sorguya başla! 🧠"
    ]

    secilen = random.choice(mesajlar)

    caption = (
        f"👋 Hoş geldin {isim}!\n\n"
        f"{secilen}\n\n"
        f"⏱ Başlatma Bilgisi\n"
        f"━━━━━━━━━━━━━━\n"
        f"📅 Tarih: {ist_time.split('|')[0].strip()}\n"
        f"🕒 Saat (İstanbul): {ist_time.split('|')[1].strip()}\n"
        f"━━━━━━━━━━━━━━\n"
        f"➡️ Başlamak için /komutlar yaz."
    )

    bot.send_message(
    message.chat.id,
    caption
)

@bot.message_handler(commands=["komutlar"])
def komutlar(message):
    if message.chat.type != "private":
        return
    if not kanal_kontrol(message.from_user.id, message.chat.id):
        return
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("🔎 Sxrgu İşlemleri", callback_data="sxrgu"),
        types.InlineKeyboardButton("⭐ V.I.P Sxrgu İşlemleri", callback_data="vip_sxrgu"),
        types.InlineKeyboardButton("💻 Destek / Yazılım", callback_data="yazilim"),
        types.InlineKeyboardButton("❓ Bu Bot Ne İşe Yarar?", callback_data="nedir")
    )
    bot.send_message(message.chat.id, "Menü:", reply_markup=kb)

def vip_sxrgu_menu(chat_id):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("🚗 T.C ➜ Plaka Sxrgu", callback_data="vip"),
        types.InlineKeyboardButton("🚘 Plaka ➜ T.C", callback_data="vip"),
        types.InlineKeyboardButton("📝 Ehliyet Vesika Sxrgu", callback_data="vip"),
        types.InlineKeyboardButton("⚖️ Adli Sicil Kaydı Sxrgu", callback_data="vip"),
        types.InlineKeyboardButton("🎓 Öğrenci Vesika Sxrgu", callback_data="vip"),
        types.InlineKeyboardButton("📸 +25 Yaş Vesika Sxrgu", callback_data="vip"),
        types.InlineKeyboardButton("💊 İlaç Sorgu", callback_data="vip"),
        types.InlineKeyboardButton("🧾 Rapor Sorgu", callback_data="vip"),
        types.InlineKeyboardButton("💉 Aşı Sxrgu", callback_data="vip"),
        types.InlineKeyboardButton("🏛️ Tapu Pro", callback_data="vip"),
        types.InlineKeyboardButton("⬅️ Geri Dön", callback_data="geri_ana")
    )
    bot.send_message(chat_id, "⭐ V.I.P Sxrgu Menüsü:", reply_markup=kb)

def sxrgu_menu(chat_id):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
    types.InlineKeyboardButton("👤 Ad Soyad", callback_data="adsoyad"),
    types.InlineKeyboardButton("🆔 TC Pro", callback_data="tcpro"),
    types.InlineKeyboardButton("🏠 Aile Pro", callback_data="ailepro"),
    types.InlineKeyboardButton("👨‍👩‍👧 Sülale Pro", callback_data="sulalepro"),
    types.InlineKeyboardButton("📞 TC ➜ GSM", callback_data="tcgsm"),
    types.InlineKeyboardButton("📲 GSM ➜ TC", callback_data="gsmtc"),
    types.InlineKeyboardButton("🧒 Çocuk Sxrgu", callback_data="cocuksorgu"),
    types.InlineKeyboardButton("🏢 İşyeri Sxrgu", callback_data="isyeri"),
    types.InlineKeyboardButton("📜 Tapu Sxrgu", callback_data="tapu"),
    types.InlineKeyboardButton("🗺 Ada Parsel Sxrgu", callback_data="adaparsel"),
    types.InlineKeyboardButton("🔙 Geri Dön", callback_data="geri_ana")
)

    bot.send_message(chat_id,"Sxrgu türünü seç:",reply_markup=kb)
@bot.callback_query_handler(func=lambda c: True)
def callback_handler(call):
    if call.message.chat.type != "private":
        return

    chat_id = call.message.chat.id
    uid = call.from_user.id

    if not kanal_kontrol(uid, chat_id):
        return

    if call.data == "ilce_bilinmiyor":
        state = user_states.get(uid)
        if not state or state.get("mode") != "adsoyad":
            bot.answer_callback_query(call.id)
            return

        try:
            r = requests.get(
                "https://lethasorgu.com/alwaydsalvoxd/adsoyad.php",
                params={
                    "ad": state["ad"],
                    "soyad": state["soyad"],
                    "il": state["il"],
                    "ilce": " "
                },
                timeout=10
            )

            last_query_time[uid] = time()

            raw = r.text.strip()

            if not raw.startswith("{") and not raw.startswith("["):
                bot.send_message(chat_id, "ARTIK İLÇE GİRMEK ZORUNLUDUR!")
                return

            resp = json.loads(raw)
            data_list = resp.get("veri", [])

            if data_list:
                send_query_result(chat_id, data_list, "adsoyad")
            else:
                bot.send_message(chat_id, "Veri bulunamadı")

        except requests.exceptions.Timeout:
            bot.send_message(chat_id, "Sunucu yanıt vermedi (timeout).")
        except Exception as e:
            bot.send_message(chat_id, f"Hata: {e}")

        user_states.pop(uid, None)
        bot.answer_callback_query(call.id)
        return


    if call.data == "geri_ana" or call.data.endswith("_ana"):
        ad = call.from_user.first_name or ""
        soyad = call.from_user.last_name or ""
        isim = f"{ad} {soyad}".strip()
        zaman = datetime.now().strftime("%d.%m.%Y | %H:%M:%S")
        caption = (
            f"👋 Hoş geldin {isim} Bugün Hava Çok Güneşli Haa?!\n\n"
            f"Ne Dersin Sorgulamak İçin Güzel Bir Güne Benziyor!🕵️‍♂\n\n"
            f"⏱ Başlatma Tarihi\n"
            f"━━━━━━━━━━━━━━\n"
            f"📅 Tarih: {zaman.split('|')[0].strip()}\n"
            f"━━━━━━━━━━━━━━\n"
            f"🕒 Saat: {zaman.split('|')[1].strip()}\n"
            f"━━━━━━━━━━━━━━\n"
            f"➡️ Sistemimizden Yararlanmak İçin /komutlar Yaz."
        )
        with open("logo.PNG", "rb") as p:
            bot.send_photo(chat_id, p, caption=caption)
        komutlar(call.message)
        return
    if call.data == "vip_sxrgu":
        vip_sxrgu_menu(chat_id)
        return
    if call.data == "vip":
        bot.send_message(chat_id,"Bu komutu kullanmak için VIP üyelik satın almanız gerekmektedir.\n\n@ifsalanmam  ile iletişime geçiniz")
        return
    if call.data == "sxrgu":
        sxrgu_menu(chat_id)
    elif call.data == "yazilim":
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("🔙 Geri Dön", callback_data="geri_ana"))
        bot.send_message(chat_id,"💻 Yazılım Ekibi:\n\n@destekyazilim tarafından geliştirilmiştir.\nV.I.P için @ifsalanmam ve @AhmettKaraca ile iletişime geçiniz.",reply_markup=kb)
    elif call.data == "nedir":
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("🔙 Geri Dön", callback_data="geri_ana"))
        bot.send_message(chat_id,"❓ Bu Bot Ne İşe Yarar?\n\nBu bot çeşitli sxrgu işlemlerini tek merkezden yapmanızı sağlar. 15+ sxrgu mevcuttur. İşyeri, Tapu, Ada Parsel gibi sorgular ücretsizdir.\n\nErişim için gerekli kanallara katılıp /komutlar yazmanız yeterlidir.",reply_markup=kb)
    elif call.data in ["adsoyad","tcpro","ailepro","sulalepro","tcgsm","gsmtc","cocuksorgu","isyeri","tapu","adaparsel","ailegsm","sulalegsm"]:
        user_states[uid] = {"mode": call.data}
        if call.data == "adsoyad":
            bot.send_message(chat_id, "Ad gir:")
        elif call.data in ["tcpro","ailepro","sulalepro","tcgsm","isyeri","tapu","ailegsm","sulalegsm"]:
            bot.send_message(chat_id, "TC gir:")
        elif call.data == "gsmtc":
            bot.send_message(chat_id, "GSM gir:")
        elif call.data == "cocuksorgu":
            bot.send_message(chat_id, "TC gir (Çocuk sorgusu için):")
        elif call.data == "adaparsel":
            bot.send_message(chat_id, "Ada gir:")

@bot.message_handler(func=lambda m: True)
def state_handler(message):
    if message.chat.type != "private":
        return
    uid = message.from_user.id
    chat_id = message.chat.id

    if not kanal_kontrol(uid, chat_id):
        user_states.pop(uid, None)
        return

    state = user_states.get(uid)
    if not state:
        return

    mode = state["mode"]

    # FREE TIMEOUT
    now = time()
    if mode in free_modes:
        last = last_query_time.get(uid, 0)
        if now - last < FREE_TIMEOUT:
            kalan = int(FREE_TIMEOUT - (now - last))
            bot.send_message(chat_id, f"⚠️ Sizin ve diğer üyelerimizin akıcı sorgu yapması için lütfen {kalan} saniye bekleyiniz.")
            return

    try:
        if mode in ["tcgsm","gsmtc","tcpro","isyeri","tapu"]:
            api_map = {
                "tcgsm": ("https://lethasorgu.com/alwaydsalvoxd/tc.php", {"tc": message.text}),
                "gsmtc": ("http://45.134.173.160/gsm.php?gsm=", {"gsm": message.text}),
                "tcpro": ("https://lethasorgu.com/alwaydsalvoxd/tc.php", {"tc": message.text}),
                "isyeri": ("https://lethasorgu.com/alwaydsalvoxd/isyeri.php", {"tc": message.text}),
                "tapu": ("https://lethasorgu.com/alwaydsalvoxd/tapu.php", {"tc": message.text})
            }
            url, params = api_map[mode]
            r = requests.get(url, params=params, timeout=10)
            last_query_time[uid] = time()
            data_list = r.json().get("data", [])
            if data_list: send_query_result(chat_id, data_list, mode)
            else: raise ValueError("Veri bulunamadı")

        elif mode == "adaparsel":
            if "ada" not in state:
                state["ada"] = message.text
                bot.send_message(chat_id, "Parsel gir:")
                return
            if "parsel" not in state:
                state["parsel"] = message.text
                bot.send_message(chat_id, "İl gir:")
                return
            if "il" not in state:
                state["il"] = message.text
                bot.send_message(chat_id, "İlçe gir:")
                return
            r = requests.get("https://lethasorgu.com/alwaydsalvoxd/adresparsel.php",params={"ada": state["ada"],"parsel": state["parsel"],"il": state["il"],"ilce": message.text},timeout=10)
            last_query_time[uid] = time()
            data_list = r.json().get("data", [])
            if data_list: send_query_result(chat_id, data_list, "adaparsel")
            else: raise ValueError("Veri bulunamadı")

        elif mode == "adsoyad":
            if "ad" not in state:
                state["ad"] = message.text
                bot.send_message(chat_id, "Soyad gir:")
                return
            if "soyad" not in state:
                state["soyad"] = message.text
                bot.send_message(chat_id, "İl gir:")
                return
            if "il" not in state:
                state["il"] = message.text
                kb = types.InlineKeyboardMarkup(row_width=1)
                kb.add(types.InlineKeyboardButton("📍 İlçeyi Bilmiyorum", callback_data="ilce_bilinmiyor"))
                bot.send_message(chat_id, "İlçe gir:", reply_markup=kb)
                return
            r = requests.get("https://lethasorgu.com/alwaydsalvoxd/adsoyad.php",params={"ad": state["ad"],"soyad": state["soyad"],"il": state["il"],"ilce": message.text},timeout=10)
            last_query_time[uid] = time()
            data_list = r.json().get("data", [])
            if data_list: send_query_result(chat_id, data_list, "adsoyad")
            else: bot.send_message(chat_id, "Veri bulunamadı")

        elif mode in ["ailepro","cocuksorgu"]:
            r = requests.get("https://lethasorgu.com/alwaydsalvoxd/aile.php", params={"tc": message.text}, timeout=10)
            last_query_time[uid] = time()
            js = r.json().get("data", {})
            txt = "KİŞİ\n" + "\n".join(f"{k}: {v}" for k, v in js["kisi"].items()) + "\n\n"
            for c in js.get("cocuklar", []):
                txt += "ÇOCUK\n" + "\n".join(f"{k}: {v}" for k, v in c.items()) + "\n\n"
            with open("sonuc.txt", "w", encoding="utf-8") as f: f.write(txt)
            with open("sonuc.txt", "rb") as f: bot.send_document(chat_id, f)

        elif mode == "sulalepro":
            r = requests.get("https://lethasorgu.com/alwaydsalvoxd/sulale.php", params={"tc": message.text}, timeout=10)
            last_query_time[uid] = time()
            js = r.json().get("data", {})
            txt = "KİŞİ\n" + "\n".join(f"{k}: {v}" for k, v in js["kisi"].items()) + "\n\n"
            if js.get("es"): txt += "EŞ\n" + "\n".join(f"{k}: {v}" for k, v in js["es"].items()) + "\n\n"
            for c in js.get("cocuklar", []):
                txt += "ÇOCUK\n" + "\n".join(f"{k}: {v}" for k, v in c.items()) + "\n\n"
            if js.get("anne"): txt += "ANNE\n" + "\n".join(f"{k}: {v}" for k, v in js["anne"].items()) + "\n\n"
            if js.get("baba"): txt += "BABA\n" + "\n".join(f"{k}: {v}" for k, v in js["baba"].items()) + "\n\n"
            with open("sonuc.txt", "w", encoding="utf-8") as f: f.write(txt)
            with open("sonuc.txt", "rb") as f: bot.send_document(chat_id, f)

        elif mode in ["ailegsm","sulalegsm"]:
            api_url = "https://lethasorgu.com/alwaydsalvoxd/aile.php" if mode == "ailegsm" else "https://lethasorgu.com/alwaydsalvoxd/sulale.php"
            r = requests.get(api_url, params={"tc": message.text}, timeout=10)
            last_query_time[uid] = time()
            js = r.json()
            data = js.get("data", {})
            send_structured_result_basic(chat_id, js)

    except Exception as e:
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(types.InlineKeyboardButton("🔄 Tekrar Dene", callback_data=mode + "_tekrar"))
        bot.send_message(chat_id, f"Veri Bulunamadı. {e}", reply_markup=kb)

    user_states.pop(uid, None)

print("Bot aktif")
bot.infinity_polling()
  
