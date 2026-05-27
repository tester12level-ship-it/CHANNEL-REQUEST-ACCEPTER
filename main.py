import json
import os
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ChatJoinRequestHandler, CallbackQueryHandler, ContextTypes

# ========== टोकन और फाइलें ==========
BOT_TOKEN = "8758660395:AAEW0Ox53WAWRH0XU"
DATA_FILE = "bot_data.json"
LANG_FILE = "user_lang.json"

# ========== स्टाइलिश टेक्स्ट कनवर्टर ==========
def to_stylish_primary(text: str) -> str:
    small_caps = {
        'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ',
        'f': 'ғ', 'g': 'ɢ', 'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ',
        'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ',
        'p': 'ᴘ', 'q': 'ϙ', 'r': 'ʀ', 's': 'ꜱ', 't': 'ᴛ',
        'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ', 'z': 'ᴢ'
    }
    def transform_word(word: str) -> str:
        if not word:
            return word
        first = word[0].upper() if word[0].isalpha() else word[0]
        rest = word[1:]
        styled_rest = ''.join(small_caps.get(ch.lower(), ch) for ch in rest)
        return first + styled_rest
    tokens = re.findall(r'([A-Za-z]+|[^A-Za-z]+)', text)
    styled_tokens = [transform_word(tok) if tok.isalpha() else tok for tok in tokens]
    return ''.join(styled_tokens)

# ========== 12+ भाषाओं के लिए टेक्स्ट ==========
TEXTS = {
    "hi": {  # हिंदी
        "welcome": "👋 नमस्ते [{first_name}](tg://user?id={user_id})!\n\n🤖 *{bot_name}* में आपका स्वागत है!\n\n⚡ मैं आपके चैनल या ग्रुप में सभी ज्वाइन रिक्वेस्ट को **अपने आप अप्रूव** कर देता हूँ।\n\n📌 *उपयोग कैसे करें?*\n➊ मुझे अपने *चैनल* या *ग्रुप* में ऐड करें\n➋ मुझे *एडमिन* बनाएँ\n➌ *लिंक से सदस्य जोड़ने की अनुमति* चालू करें\n➍ *नए सदस्यों को अप्रूव करें* ऑन करें\n\n✅ बस! मैं बिना देरी हर जॉइन रिक्वेस्ट अप्रूव कर दूँगा।\n\n🚀 तेज़ • सुरक्षित • अपने आप\n💎 बड़े कम्युनिटी के लिए परफेक्ट!",
        "approve_msg": "🎉 *जॉइन रिक्वेस्ट स्वीकृत!*\n\n✅ *{chat_title}* में शामिल होने की आपकी रिक्वेस्ट मंजूर कर ली गई है।\n\n🤖 हमारे {chat_type} में आपका स्वागत है!\n\n💡 मेरे बारे में अधिक जानने के लिए /start भेजें।",
        "lang_changed": "✅ आपकी भाषा हिंदी में बदल दी गई है।",
        "choose_lang": "🌐 कृपया अपनी भाषा चुनें:",
        "btn_updates": "📢 अपडेट चैनल",
        "btn_add_channel": "➕ चैनल में जोड़ें",
        "btn_add_group": "👥 ग्रुप में जोड़ें",
        "group": "ग्रुप",
        "channel": "चैनल"
    },
    "en": {  # अंग्रेजी
        "welcome": "👋 Hello [{first_name}](tg://user?id={user_id})!\n\n🤖 Welcome to *{bot_name}*\n\n⚡ I can automatically approve all join requests in your channel or group instantly.\n\n📌 *How To Use?*\n➊ Add me to your *Channel* or *Group*\n➋ Promote me as *Admin*\n➌ Enable *Invite Users via Link*\n➍ Turn on *Approve New Members*\n\n✅ That's it! I will automatically accept all join requests without any delay.\n\n🚀 Fast • Secure • Automatic\n💎 Perfect for large communities!",
        "approve_msg": "🎉 *Join Request Approved!*\n\n✅ Your request to join *{chat_title}* has been approved successfully.\n\n🤖 Welcome to our {chat_type}!\n\n💡 Send /start to know more about me.",
        "lang_changed": "✅ Your language has been changed to English.",
        "choose_lang": "🌐 Please choose your language:",
        "btn_updates": "📢 Updates Channel",
        "btn_add_channel": "➕ Add To Channel",
        "btn_add_group": "👥 Add To Group",
        "group": "group",
        "channel": "channel"
    },
    "es": {  # स्पेनिश
        "welcome": "👋 Hola [{first_name}](tg://user?id={user_id})!\n\n🤖 Bienvenido a *{bot_name}*\n\n⚡ Puedo aprobar automáticamente todas las solicitudes de unión en tu canal o grupo al instante.\n\n📌 *¿Cómo usar?*\n➊ Agrégame a tu *Canal* o *Grupo*\n➋ Asciéndeme a *Administrador*\n➌ Habilita *Invitar usuarios mediante enlace*\n➍ Activa *Aprobar nuevos miembros*\n\n✅ ¡Eso es todo! Aceptaré automáticamente todas las solicitudes de unión sin demora.\n\n🚀 Rápido • Seguro • Automático\n💎 ¡Perfecto para comunidades grandes!",
        "approve_msg": "🎉 *¡Solicitud de unión aprobada!*\n\n✅ Tu solicitud para unirte a *{chat_title}* ha sido aprobada exitosamente.\n\n🤖 ¡Bienvenido a nuestro {chat_type}!\n\n💡 Envía /start para saber más sobre mí.",
        "lang_changed": "✅ Tu idioma ha sido cambiado a español.",
        "choose_lang": "🌐 Por favor, elige tu idioma:",
        "btn_updates": "📢 Canal de Actualizaciones",
        "btn_add_channel": "➕ Agregar al Canal",
        "btn_add_group": "👥 Agregar al Grupo",
        "group": "grupo",
        "channel": "canal"
    },
    "fr": {  # फ्रेंच
        "welcome": "👋 Bonjour [{first_name}](tg://user?id={user_id})!\n\n🤖 Bienvenue à *{bot_name}*\n\n⚡ Je peux approuver automatiquement toutes les demandes d'adhésion dans votre chaîne ou groupe instantanément.\n\n📌 *Comment utiliser?*\n➊ Ajoutez-moi à votre *Chaîne* ou *Groupe*\n➋ Promouvez-moi comme *Admin*\n➌ Activez *Inviter des utilisateurs via un lien*\n➍ Activez *Approuver les nouveaux membres*\n\n✅ C'est tout! J'accepterai automatiquement toutes les demandes d'adhésion sans délai.\n\n🚀 Rapide • Sécurisé • Automatique\n💎 Parfait pour les grandes communautés!",
        "approve_msg": "🎉 *Demande d'adhésion approuvée!*\n\n✅ Votre demande pour rejoindre *{chat_title}* a été approuvée avec succès.\n\n🤖 Bienvenue dans notre {chat_type}!\n\n💡 Envoyez /start pour en savoir plus sur moi.",
        "lang_changed": "✅ Votre langue a été changée en français.",
        "choose_lang": "🌐 Veuillez choisir votre langue:",
        "btn_updates": "📢 Chaîne de mises à jour",
        "btn_add_channel": "➕ Ajouter à la chaîne",
        "btn_add_group": "👥 Ajouter au groupe",
        "group": "groupe",
        "channel": "chaîne"
    },
    "de": {  # जर्मन
        "welcome": "👋 Hallo [{first_name}](tg://user?id={user_id})!\n\n🤖 Willkommen bei *{bot_name}*\n\n⚡ Ich kann alle Beitrittsanfragen in deinem Kanal oder deiner Gruppe sofort automatisch genehmigen.\n\n📌 *Wie benutzt man?*\n➊ Füge mich zu deinem *Kanal* oder *Gruppe* hinzu\n➋ Mache mich zum *Admin*\n➌ Aktiviere *Benutzer über Link einladen*\n➍ Aktiviere *Neue Mitglieder genehmigen*\n\n✅ Das ist es! Ich werde alle Beitrittsanfragen ohne Verzögerung automatisch annehmen.\n\n🚀 Schnell • Sicher • Automatisch\n💎 Perfekt für große Communities!",
        "approve_msg": "🎉 *Beitrittsanfrage genehmigt!*\n\n✅ Deine Anfrage, *{chat_title}* beizutreten, wurde erfolgreich genehmigt.\n\n🤖 Willkommen in unserem {chat_type}!\n\n💡 Sende /start, um mehr über mich zu erfahren.",
        "lang_changed": "✅ Deine Sprache wurde auf Deutsch geändert.",
        "choose_lang": "🌐 Bitte wähle deine Sprache:",
        "btn_updates": "📢 Updates Kanal",
        "btn_add_channel": "➕ Zum Kanal hinzufügen",
        "btn_add_group": "👥 Zur Gruppe hinzufügen",
        "group": "Gruppe",
        "channel": "Kanal"
    },
    "it": {  # इतालवी
        "welcome": "👋 Ciao [{first_name}](tg://user?id={user_id})!\n\n🤖 Benvenuto a *{bot_name}*\n\n⚡ Posso approvare automaticamente tutte le richieste di adesione nel tuo canale o gruppo istantaneamente.\n\n📌 *Come usare?*\n➊ Aggiungimi al tuo *Canale* o *Gruppo*\n➊ Promuovimi come *Admin*\n➌ Abilita *Invita utenti tramite link*\n➍ Attiva *Approva nuovi membri*\n\n✅ Questo è tutto! Accetterò automaticamente tutte le richieste di adesione senza ritardi.\n\n🚀 Veloce • Sicuro • Automatico\n💎 Perfetto per grandi comunità!",
        "approve_msg": "🎉 *Richiesta di adesione approvata!*\n\n✅ La tua richiesta per unirti a *{chat_title}* è stata approvata con successo.\n\n🤖 Benvenuto nel nostro {chat_type}!\n\n💡 Invia /start per saperne di più su di me.",
        "lang_changed": "✅ La tua lingua è stata cambiata in italiano.",
        "choose_lang": "🌐 Scegli la tua lingua:",
        "btn_updates": "📢 Canale aggiornamenti",
        "btn_add_channel": "➕ Aggiungi al canale",
        "btn_add_group": "👥 Aggiungi al gruppo",
        "group": "gruppo",
        "channel": "canale"
    },
    "pt": {  # पुर्तगाली
        "welcome": "👋 Olá [{first_name}](tg://user?id={user_id})!\n\n🤖 Bem-vindo ao *{bot_name}*\n\n⚡ Posso aprovar automaticamente todos os pedidos de adesão no seu canal ou grupo instantaneamente.\n\n📌 *Como usar?*\n➊ Adicione-me ao seu *Canal* ou *Grupo*\n➋ Promova-me a *Admin*\n➌ Ative *Convidar usuários via link*\n➍ Ative *Aprovar novos membros*\n\n✅ É isso! Aceitarei automaticamente todos os pedidos de adesão sem demora.\n\n🚀 Rápido • Seguro • Automático\n💎 Perfeito para grandes comunidades!",
        "approve_msg": "🎉 *Pedido de adesão aprovado!*\n\n✅ Seu pedido para entrar em *{chat_title}* foi aprovado com sucesso.\n\n🤖 Bem-vindo ao nosso {chat_type}!\n\n💡 Envie /start para saber mais sobre mim.",
        "lang_changed": "✅ Seu idioma foi alterado para português.",
        "choose_lang": "🌐 Por favor, escolha seu idioma:",
        "btn_updates": "📢 Canal de atualizações",
        "btn_add_channel": "➕ Adicionar ao canal",
        "btn_add_group": "👥 Adicionar ao grupo",
        "group": "grupo",
        "channel": "canal"
    },
    "ru": {  # रूसी
        "welcome": "👋 Привет [{first_name}](tg://user?id={user_id})!\n\n🤖 Добро пожаловать в *{bot_name}*\n\n⚡ Я могу мгновенно автоматически одобрять все запросы на вступление в ваш канал или группу.\n\n📌 *Как использовать?*\n➊ Добавьте меня в свой *Канал* или *Группу*\n➋ Назначьте меня *Администратором*\n➌ Включите *Приглашать пользователей по ссылке*\n➍ Включите *Одобрять новых участников*\n\n✅ Вот и всё! Я буду автоматически принимать все запросы на вступление без задержки.\n\n🚀 Быстро • Безопасно • Автоматически\n💎 Идеально для больших сообществ!",
        "approve_msg": "🎉 *Запрос на вступление одобрен!*\n\n✅ Ваш запрос на вступление в *{chat_title}* успешно одобрен.\n\n🤖 Добро пожаловать в наш {chat_type}!\n\n💡 Отправьте /start, чтобы узнать больше обо мне.",
        "lang_changed": "✅ Ваш язык изменён на русский.",
        "choose_lang": "🌐 Пожалуйста, выберите ваш язык:",
        "btn_updates": "📢 Канал обновлений",
        "btn_add_channel": "➕ Добавить в канал",
        "btn_add_group": "👥 Добавить в группу",
        "group": "группу",
        "channel": "канал"
    },
    "ar": {  # अरबी
        "welcome": "👋 مرحبا [{first_name}](tg://user?id={user_id})!\n\n🤖 مرحبا بك في *{bot_name}*\n\n⚡ يمكنني الموافقة تلقائيا على جميع طلبات الانضمام في قناتك أو مجموعتك فورا.\n\n📌 *كيف تستخدم؟*\n➊ أضفني إلى *قناتك* أو *مجموعتك*\n➋ رقيني إلى *مشرف*\n➌ فعّل *دعوة المستخدمين عبر الرابط*\n➍ فعّل *الموافقة على الأعضاء الجدد*\n\n✅ هذا كل شيء! سأقبل تلقائيا جميع طلبات الانضمام دون تأخير.\n\n🚀 سريع • آمن • تلقائي\n💎 مثالي للمجتمعات الكبيرة!",
        "approve_msg": "🎉 *تمت الموافقة على طلب الانضمام!*\n\n✅ تمت الموافقة على طلبك للانضمام إلى *{chat_title}* بنجاح.\n\n🤖 مرحبا بك في {chat_type}!\n\n💡 أرسل /start لمعرفة المزيد عني.",
        "lang_changed": "✅ تم تغيير لغتك إلى العربية.",
        "choose_lang": "🌐 الرجاء اختيار لغتك:",
        "btn_updates": "📢 قناة التحديثات",
        "btn_add_channel": "➕ أضف إلى القناة",
        "btn_add_group": "👥 أضف إلى المجموعة",
        "group": "المجموعة",
        "channel": "القناة"
    },
    "tr": {  # तुर्की
        "welcome": "👋 Merhaba [{first_name}](tg://user?id={user_id})!\n\n🤖 *{bot_name}*'a hoş geldiniz!\n\n⚡ Kanalınızdaki veya grubunuzdaki tüm katılma isteklerini anında otomatik olarak onaylayabilirim.\n\n📌 *Nasıl Kullanılır?*\n➊ Beni *Kanalınıza* veya *Grubunuza* ekleyin\n➋ Beni *Yönetici* yapın\n➌ *Bağlantıyla Kullanıcı Davet Et*'i etkinleştirin\n➍ *Yeni Üyeleri Onayla*'yı açın\n\n✅ İşte bu! Tüm katılma isteklerini gecikmeden otomatik olarak kabul edeceğim.\n\n🚀 Hızlı • Güvenli • Otomatik\n💎 Büyük topluluklar için mükemmel!",
        "approve_msg": "🎉 *Katılma isteği onaylandı!*\n\n✅ *{chat_title}*'a katılma isteğiniz başarıyla onaylandı.\n\n🤖 {chat_type}umuza hoş geldiniz!\n\n💡 Benim hakkımda daha fazla bilgi edinmek için /start gönderin.",
        "lang_changed": "✅ Diliniz Türkçe olarak değiştirildi.",
        "choose_lang": "🌐 Lütfen dilinizi seçin:",
        "btn_updates": "📢 Güncelleme Kanalı",
        "btn_add_channel": "➕ Kanala Ekle",
        "btn_add_group": "👥 Gruba Ekle",
        "group": "grup",
        "channel": "kanal"
    },
    "id": {  # इंडोनेशियाई
        "welcome": "👋 Halo [{first_name}](tg://user?id={user_id})!\n\n🤖 Selamat datang di *{bot_name}*\n\n⚡ Saya dapat menyetujui semua permintaan bergabung di saluran atau grup Anda secara instan.\n\n📌 *Bagaimana Cara Menggunakan?*\n➊ Tambahkan saya ke *Saluran* atau *Grup* Anda\n➋ Angkat saya sebagai *Admin*\n➌ Aktifkan *Undang Pengguna melalui Tautan*\n➍ Aktifkan *Setujui Anggota Baru*\n\n✅ Itu saja! Saya akan secara otomatis menerima semua permintaan bergabung tanpa penundaan.\n\n🚀 Cepat • Aman • Otomatis\n💎 Sempurna untuk komunitas besar!",
        "approve_msg": "🎉 *Permintaan Bergabung Disetujui!*\n\n✅ Permintaan Anda untuk bergabung dengan *{chat_title}* telah berhasil disetujui.\n\n🤖 Selamat datang di {chat_type} kami!\n\n💡 Kirim /start untuk mengetahui lebih lanjut tentang saya.",
        "lang_changed": "✅ Bahasa Anda telah diubah menjadi Bahasa Indonesia.",
        "choose_lang": "🌐 Silakan pilih bahasa Anda:",
        "btn_updates": "📢 Saluran Pembaruan",
        "btn_add_channel": "➕ Tambah ke Saluran",
        "btn_add_group": "👥 Tambah ke Grup",
        "group": "grup",
        "channel": "saluran"
    },
    "bn": {  # बंगाली
        "welcome": "👋 হ্যালো [{first_name}](tg://user?id={user_id})!\n\n🤖 *{bot_name}* এ স্বাগতম!\n\n⚡ আমি আপনার চ্যানেল বা গ্রুপে সমস্ত জয়েন রিকোয়েস্ট তাৎক্ষণিকভাবে স্বয়ংক্রিয়ভাবে অনুমোদন করতে পারি।\n\n📌 *কীভাবে ব্যবহার করবেন?*\n➊ আমাকে আপনার *চ্যানেল* বা *গ্রুপে* যোগ করুন\n➋ আমাকে *অ্যাডমিন* করুন\n➌ *লিঙ্কের মাধ্যমে ব্যবহারকারীদের আমন্ত্রণ জানান* সক্রিয় করুন\n➍ *নতুন সদস্যদের অনুমোদন করুন* চালু করুন\n\n✅ ব্যাস! আমি কোনো বিলম্ব না করেই সমস্ত জয়েন রিকোয়েস্ট স্বয়ংক্রিয়ভাবে গ্রহণ করব।\n\n🚀 দ্রুত • নিরাপদ • স্বয়ংক্রিয়\n💎 বড় কমিউনিটির জন্য পারফেক্ট!",
        "approve_msg": "🎉 *জয়েন রিকোয়েস্ট অনুমোদিত!*\n\n✅ *{chat_title}* এ যোগদানের জন্য আপনার অনুরোধ সফলভাবে অনুমোদিত হয়েছে।\n\n🤣 আমাদের {chat_type} এ স্বাগতম!\n\n💡 আমার সম্পর্কে আরও জানতে /start পাঠান।",
        "lang_changed": "✅ আপনার ভাষা বাংলায় পরিবর্তন করা হয়েছে।",
        "choose_lang": "🌐 অনুগ্রহ করে আপনার ভাষা নির্বাচন করুন:",
        "btn_updates": "📢 আপডেট চ্যানেল",
        "btn_add_channel": "➕ চ্যানেলে যোগ করুন",
        "btn_add_group": "👥 গ্রুপে যোগ করুন",
        "group": "গ্রুপ",
        "channel": "চ্যানেল"
    }
}

# ========== यूजर डाटा फंक्शन ==========
def load_langs():
    if os.path.exists(LANG_FILE):
        with open(LANG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_langs(langs):
    with open(LANG_FILE, "w") as f:
        json.dump(langs, f)

def get_user_lang(user_id):
    langs = load_langs()
    return langs.get(str(user_id), "hi")  # डिफ़ॉल्ट हिंदी

def set_user_lang(user_id, lang):
    langs = load_langs()
    langs[str(user_id)] = lang
    save_langs(langs)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"idstore": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# ========== /start कमांड ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    lang = get_user_lang(user_id)
    t = TEXTS[lang]

    data = load_data()
    idstore = data["idstore"]
    if user_id not in idstore:
        idstore.append(user_id)
        data["idstore"] = idstore
        save_data(data)

    keyboard = [
        [InlineKeyboardButton(to_stylish_primary(t["btn_updates"]), url="https://t.me/DGDRIFT")],
        [InlineKeyboardButton(to_stylish_primary(t["btn_add_channel"]), url=f"https://t.me/{context.bot.username}?startchannel=true")],
        [InlineKeyboardButton(to_stylish_primary(t["btn_add_group"]), url=f"https://t.me/{context.bot.username}?startgroup=true")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    raw_text = t["welcome"].format(first_name=user.first_name, user_id=user_id, bot_name=context.bot.first_name)
    styled_text = to_stylish_primary(raw_text)
    await update.message.reply_text(styled_text, parse_mode="Markdown", reply_markup=reply_markup)

# ========== /language कमांड – 12+ भाषाओं के साथ ==========
async def language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # भाषा बटन – 2 कॉलम में 12 भाषाएँ (6 पंक्तियाँ)
    keyboard = [
        [InlineKeyboardButton(to_stylish_primary("🇮🇳 हिंदी"), callback_data="lang_hi"),
         InlineKeyboardButton(to_stylish_primary("🇬🇧 English"), callback_data="lang_en")],
        [InlineKeyboardButton(to_stylish_primary("🇪🇸 Español"), callback_data="lang_es"),
         InlineKeyboardButton(to_stylish_primary("🇫🇷 Français"), callback_data="lang_fr")],
        [InlineKeyboardButton(to_stylish_primary("🇩🇪 Deutsch"), callback_data="lang_de"),
         InlineKeyboardButton(to_stylish_primary("🇮🇹 Italiano"), callback_data="lang_it")],
        [InlineKeyboardButton(to_stylish_primary("🇵🇹 Português"), callback_data="lang_pt"),
         InlineKeyboardButton(to_stylish_primary("🇷🇺 Русский"), callback_data="lang_ru")],
        [InlineKeyboardButton(to_stylish_primary("🇸🇦 العربية"), callback_data="lang_ar"),
         InlineKeyboardButton(to_stylish_primary("🇹🇷 Türkçe"), callback_data="lang_tr")],
        [InlineKeyboardButton(to_stylish_primary("🇮🇩 Indonesia"), callback_data="lang_id"),
         InlineKeyboardButton(to_stylish_primary("🇧🇩 বাংলা"), callback_data="lang_bn")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    choose_text = to_stylish_primary("🌐 कृपया अपनी भाषा चुनें:\nPlease choose your language:")
    await update.message.reply_text(choose_text, reply_markup=reply_markup)

async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    lang_code = query.data.split("_")[1]  # "lang_hi" -> "hi"
    set_user_lang(user_id, lang_code)
    t = TEXTS[lang_code]
    styled_msg = to_stylish_primary(t["lang_changed"])
    await query.edit_message_text(text=styled_msg)

# ========== जॉइन रिक्वेस्ट ऑटो-अप्रूव ==========
async def auto_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    join_request = update.chat_join_request
    chat = join_request.chat
    user = join_request.from_user

    lang = get_user_lang(user.id)
    t = TEXTS[lang]
    chat_type = t["group"] if chat.type in ["group", "supergroup"] else t["channel"]

    try:
        await context.bot.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
    except Exception as e:
        print(f"अप्रूव त्रुटि: {e}")
        return

    raw_text = t["approve_msg"].format(chat_title=chat.title, chat_type=chat_type)
    styled_text = to_stylish_primary(raw_text)
    try:
        await context.bot.send_message(chat_id=user.id, text=styled_text, parse_mode="Markdown")
    except Exception as e:
        print(f"{user.id} को मैसेज नहीं भेज सका: {e}")

# ========== बॉट चलाएँ ==========
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("language", language))
    app.add_handler(CallbackQueryHandler(language_callback, pattern="^lang_"))
    app.add_handler(ChatJoinRequestHandler(auto_approve))
    print("✅ बॉट चालू है | ")
    app.run_polling()

if __name__ == "__main__":
    main()