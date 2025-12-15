import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import sqlite3
import os
import json

st = MemoryStorage()

# Удаляем старую базу данных если есть
if os.path.exists("survey.db"):
    os.remove("survey.db")

# Создаем новую базу данных
def create_db():
    conn = sqlite3.connect("survey.db")
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tg_id INTEGER,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        language TEXT DEFAULT 'uz',
        started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        completed BOOLEAN DEFAULT 0
    )
    """)
    
    # Таблица ответов
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        q1 TEXT,
        q2 TEXT,
        q2_text TEXT,
        q3 TEXT,
        q4 TEXT,
        q4_text TEXT,
        q5 TEXT,
        q5_text TEXT,
        q6 TEXT,
        q6_text TEXT,
        q7 TEXT,
        q8 TEXT,
        q9 TEXT,
        q9_text TEXT,
        q10 TEXT,
        q11 TEXT,
        q12 TEXT,
        completed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)
    
    conn.commit()
    conn.close()
    print("База данных успешно создана")

# Функции для работы с базой данных
def add_user_start(tg_id, username, first_name, last_name):
    conn = sqlite3.connect("survey.db")
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO users (tg_id, username, first_name, last_name) 
    VALUES (?, ?, ?, ?)
    """, (tg_id, username, first_name, last_name))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id

def get_user_by_tg_id(tg_id):
    conn = sqlite3.connect("survey.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE tg_id=?", (tg_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def update_user_language(tg_id, language):
    conn = sqlite3.connect("survey.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET language=? WHERE tg_id=?", (language, tg_id))
    conn.commit()
    conn.close()

def add_response(user_id, data):
    conn = sqlite3.connect("survey.db")
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT INTO responses 
    (user_id, q1, q2, q2_text, q3, q4, q4_text, q5, q5_text, 
     q6, q6_text, q7, q8, q9, q9_text, q10, q11, q12) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id, 
        data.get('q1', ''), data.get('q2', ''), data.get('q2_text', ''), 
        data.get('q3', ''), data.get('q4', ''), data.get('q4_text', ''),
        data.get('q5', ''), data.get('q5_text', ''), data.get('q6', ''), 
        data.get('q6_text', ''), data.get('q7', ''), data.get('q8', ''),
        data.get('q9', ''), data.get('q9_text', ''), data.get('q10', ''),
        data.get('q11', ''), data.get('q12', '')
    ))
    
    cursor.execute("UPDATE users SET completed=1 WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

# Инициализация бота
bot = Bot(token="8350093484:AAEoy8Dk0Lyr3H0lNdCIk2UxvJZXnfmZzPQ")
dp = Dispatcher(bot, storage=st)
create_db()

# Словари переводов
translations = {
    'uz': {
        'choose_language': 'Iltimos, tilni tanlang:',
        'welcome': """Hurmatli xodim, mazkur anonim so'rovnoma xolislik, shaffoflik va qonuniylik tamoyillarini mustahkamlash maqsadida o'tkazilmoqda.
Sizdan so'raladigan barcha ma'lumotlar to'liq anonim tarzda qabul qilinadi va Sizning shaxsiy ma'lumotlaringiz hech qanday holatda oshkor etilmaydi.
Iltimos, har bir savolga xolis, oydin va aniq javob bering. Sizning fikringiz bankdagi haqiqiy holatni anglash va islohotlarni amalga oshirishda beqiyos ahamiyatga ega.
Fikringiz biz uchun juda muxim. Ishonchingiz va faolligingiz uchun rahmat!""",
        'q1': "1. Qaysi tijorat bankida faoliyat yuritasiz? (Bank nomi va filialni to'liq ko'rsating)",
        'q1_accepted': "Javobingiz qabul qilindi. Rahmat!",
        'q2': "2. Siz faoliyat yuritayotgan tijorat bank xodimlari o'rtasida korruptsiya yoki manfaatlar to'qnashuvi holatlariga duch kelganmisiz?",
        'q2_details': "Batafsil yozib qoldiring:",
        'q3': "3. Siz jamoadagi muhitdan qoniqasizmi?",
        'q4': "4. Sizga nisbatan rahbar xodimlar tomonidan noqonuniy topshiriqlar berilish holatlar mavjudmi?",
        'q4_details': "Batafsil yozib qoldiring:",
        'q5': "5. Bankning rahbar xodimlari tomonidan bankning ichki normativ-huquqiy hujjatlari talablarining buzilish holatlarini bilasizmi?",
        'q5_details': "Batafsil yozib qoldiring:",
        'q6': "6. Bankda xodimlarining rotatsiya (yuqori lavozimga tayinlanishi) jarayonida bank rahbariyati tomonidan tanish-bilishchilik, nepotizm, manfaatlar to'qnashuvi holatlariga duch kelganmisiz?",
        'q6_details': "Batafsil yozib qoldiring:",
        'q7': "7. Bankga ishga qabul qilish tizimi shaffofligi va xolisligini qay darajada baholaysiz? (1 dan 10 gacha baholang)",
        'q8': "8. Bank xodimlari tomonidan o'z xizmat vazifalarini bajarish jarayonida ularning xatti-harakatlarida korrupsiya yoki manfaatlar to'qnashuvi holatlariga duch kelganmisiz?",
        'q9': "9. Tijorat bank tomonidan pul yig'imlari (homiylik, tadbirlar yoki boshqa maqsadlarda) tashkil etiladimi?",
        'q9_details': "Batafsil yozib qoldiring (nima maqsadda, summasi, kim tomonidan):",
        'q10': "10. Sizga nisbatan tijorat bank rahbar xodimlari tomonidan adolatsiz yoki noxolis qarorlar qabul qilinishiga duch kelganmisiz?",
        'q11': "11. Siz taqdim etgan ma'lumotlar asosida qo'shimcha o'rganish o'tkazish lozim deb hisoblasangiz, sizdan batafsil ma'lumot olish uchun telefon raqamingizni qoldiring! (Anonimligi to'liq ta'minlanadi).\n\n*Ixtiyoriy, agar kerak bo'lsa*",
        'q12': "12. Qo'shimcha har qanday fikr-mulohaza va takliflaringiz bo'lsa yozib qoldiring",
        'thank_you': "So'rovnomangiz uchun rahmat! Sizning javoblaringiz anonim tarzda saqlandi.",
        'yes': "Ha",
        'no': "Yo'q",
        'partially': "Qisman",
        'skip': "O'tkazib yuborish"
    },
    'ru': {
        'choose_language': 'Пожалуйста, выберите язык:',
        'welcome': """Уважаемый сотрудник, данный анонимный опрос проводится с целью укрепления принципов беспристрастности, прозрачности и законности.
Все запрашиваемые у Вас данные принимаются полностью анонимно, и Ваши личные данные ни при каких обстоятельствах не будут раскрыты.
Пожалуйста, дайте честный, ясный и точный ответ на каждый вопрос. Ваше мнение имеет бесценное значение для понимания реальной ситуации в банке и осуществления реформ.
Ваше мнение очень важно для нас. Спасибо за Ваше доверие и активность!""",
        'q1': "1. В каком коммерческом банке Вы работаете? (Укажите полное название банка и филиала)",
        'q1_accepted': "Ваш ответ принят. Спасибо!",
        'q2': "2. Сталкивались ли Вы с случаями коррупции или конфликта интересов среди сотрудников коммерческого банка, в котором Вы работаете?",
        'q2_details': "Подробно опишите:",
        'q3': "3. Вы удовлетворены атмосферой в коллективе?",
        'q4': "4. Были ли случаи, когда руководители давали Вам незаконные поручения?",
        'q4_details': "Подробно опишите:",
        'q5': "5. Известны ли Вам случаи нарушения требований внутренних нормативно-правовых документов банка со стороны руководителей банка?",
        'q5_details': "Подробно опишите:",
        'q6': "6. Сталкивались ли Вы с фаворитизмом, кумовством, конфликтом интересов со стороны руководства банка в процессе ротации сотрудников (назначения на вышестоящие должности)?",
        'q6_details': "Подробно опишите:",
        'q7': "7. Как Вы оцениваете прозрачность и объективность системы приема на работу в банк? (Оцените от 1 до 10)",
        'q8': "8. Сталкивались ли Вы с коррупцией или конфликтом интересов в поведении сотрудников банка при выполнении ими своих служебных обязанностей?",
        'q9': "9. Организуются ли коммерческим банком денежные сборы (спонсорство, мероприятия или для других целей)?",
        'q9_details': "Подробно опишите (с какой целью, сумма, кем организовано):",
        'q10': "10. Сталкивались ли Вы с несправедливыми или предвзятыми решениями в отношении Вас со стороны руководителей коммерческого банка?",
        'q11': "11. Если Вы считаете, что на основе предоставленной информации необходимо провести дополнительное изучение, оставьте свой номер телефона для получения подробной информации! (Полная анонимность гарантируется).\n\n*По желанию, если необходимо*",
        'q12': "12. Если у Вас есть дополнительные мнения и предложения, напишите их здесь",
        'thank_you': "Спасибо за участие в опросе! Ваши ответы сохранены анонимно.",
        'yes': "Да",
        'no': "Нет",
        'partially': "Частично",
        'skip': "Пропустить"
    },
    'kar': {
        'choose_language': 'Өтиншем, тилди танланг:',
        'welcome': """Құрметті қызметкер, бул анонимдик сауалнама адалдық, ашықтық және заңдылық принциптерин нығайту мақсатында өткізілуде.
Сізден сұралатын барлық мағлұматтар толық анонимдик түрде қабылданады және Сіздің жеке мағлұматтарыңыз ешқандай жағдайда ашық етілмейді.
Өтиншем, әрбір сұраққа адал, анық және нақты жауап беріңіз. Сіздің пікіріңіз банктегі нақты жағдайды түсіну және реформаларды жүзеге асыру үшін баға жетпес маңызға ие.
Сіздің пікіріңіз біз үшін өте маңызды. Сеніміңіз және белсенділігіңіз үшін рақмет!""",
        'q1': "1. Қай коммерциялық банкте қызмет етесіз? (Банктың атауы мен филиалын толық көрсетіңіз)",
        'q1_accepted': "Жауабыңыз қабылданды. Рахмет!",
        'q2': "2. Сіз қызмет ететін коммерциялық банк қызметкерлері арасында жемқорлық немесе мүдделер қақтығысы жағдайларына кездескенсіз бе?",
        'q2_details': "Толық сипаттап жазыңыз:",
        'q3': "3. Сіз командадағы атмосферадан қанағаттанасыз ба?",
        'q4': "4. Сізге басшы қызметкерлер тарапынан заңсыз тапсырмалар берілген жағдайлар бар ма?",
        'q4_details': "Толық сипаттап жазыңыз:",
        'q5': "5. Банк басшылығы тарапынан банктің ішкі нормативтік-құқықтық құжаттары талаптарының бұзылу жағдайларын білесіз бе?",
        'q5_details': "Толық сипаттап жазыңыз:",
        'q6': "6. Банкте қызметкерлердің ротациясы (жоғары лауазымға тағайындалуы) процесінде банк басшылығы тарапынан таныс-білісшілік, непотизм, мүдделер қақтығысы жағдайларына кездескенсіз бе?",
        'q6_details': "Толық сипаттап жазыңыз:",
        'q7': "7. Банкке жұмысқа қабылдау жүйесінің ашықтығы мен адалдығын қандай дәрежеде бағалайсыз? (1 ден 10 ға бағалаңыз)",
        'q8': "8. Банк қызметкерлері тарапынан өз қызметтік міндеттерін орындау процесінде олардың әрекеттерінде жемқорлық немесе мүдделер қақтығысы жағдайларына кездескенсіз бе?",
        'q9': "9. Коммерциялық банк тарапынан ақша жинаулар (демеушілік, іс-шаралар немесе басқа мақсаттар үшін) ұйымдастырылады ма?",
        'q9_details': "Толық сипаттап жазыңыз (не үшін, сомасы, кім тарапынан):",
        'q10': "10. Сізге қатысты коммерциялық банк басшы қызметкерлері тарапынан әділетсіз немесе бейтарап емес шешімдер қабылдануына кездескенсіз бе?",
        'q11': "11. Сіз ұсынған мағлұматтар негізінде қосымша зерттеу жүргізу қажет деп есептесеңіз, толық мағлұмат алу үшін телефон нөміріңізді қалдырыңыз! (Толық анонимдік қамтамасыз етіледі).\n\n*Міндетті емес, қажет болса*",
        'q12': "12. Қосымша кез келген пікір-ойларыңыз және ұсыныстарыңыз болса, жазып қалдырыңыз",
        'thank_you': "Сауалнамаға қатысқаныңыз үшін рақмет! Сіздің жауаптарыңыз анонимдик түрде сақталды.",
        'yes': "Һа",
        'no': "Йоқ",
        'partially': "Жартылай",
        'skip': "Өткізіп жіберу"
    }
}

class LanguageForm(StatesGroup):
    language = State()

class SurveyForm(StatesGroup):
    q1 = State()
    q2 = State()
    q2_text = State()
    q3 = State()
    q4 = State()
    q4_text = State()
    q5 = State()
    q5_text = State()
    q6 = State()
    q6_text = State()
    q7 = State()
    q8 = State()
    q9 = State()
    q9_text = State()
    q10 = State()
    q11 = State()
    q12 = State()

# Список для хранения ID сообщений, которые нужно удалять
user_message_history = {}

async def clean_previous_messages(chat_id):
    """Удаляем предыдущие сообщения"""
    if chat_id in user_message_history:
        for msg_id in user_message_history[chat_id]:
            try:
                await bot.delete_message(chat_id, msg_id)
            except:
                pass
        user_message_history[chat_id] = []

def add_message_to_history(chat_id, message_id):
    """Добавляем ID сообщения в историю"""
    if chat_id not in user_message_history:
        user_message_history[chat_id] = []
    user_message_history[chat_id].append(message_id)

@dp.message_handler(commands=['start', 'help'])
async def start_cmd(message: types.Message):
    # Очищаем историю сообщений для этого пользователя
    user_message_history[message.chat.id] = []
    
    # Добавляем пользователя в базу
    user_id = add_user_start(
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.first_name or "",
        message.from_user.last_name or ""
    )
    
    # Предлагаем выбрать язык
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    keyboard.add(
        types.InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz"),
        types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        types.InlineKeyboardButton("🇺🇿 Қарақалпақша", callback_data="lang_kar")
    )
    
    msg = await message.answer(translations['uz']['choose_language'], reply_markup=keyboard)
    add_message_to_history(message.chat.id, msg.message_id)
    
    await LanguageForm.language.set()

@dp.callback_query_handler(lambda c: c.data.startswith('lang_'), state=LanguageForm.language)
async def process_language(callback_query: types.CallbackQuery, state: FSMContext):
    # Удаляем сообщение с выбором языка
    await bot.delete_message(callback_query.from_user.id, callback_query.message.message_id)
    
    language = callback_query.data.split('_')[1]
    await state.update_data(language=language)
    
    # Сохраняем язык в базе данных
    update_user_language(callback_query.from_user.id, language)
    
    # Получаем user_id из базы и сохраняем в состояние
    user = get_user_by_tg_id(callback_query.from_user.id)
    if user:
        user_id = user[0]
        await state.update_data(user_id=user_id)
    
    # Получаем переводы для выбранного языка
    t = translations[language]
    
    # Отправляем приветствие
    welcome_msg = await bot.send_message(callback_query.from_user.id, t['welcome'])
    add_message_to_history(callback_query.from_user.id, welcome_msg.message_id)
    
    # Отправляем вопрос 1
    q1_msg = await bot.send_message(callback_query.from_user.id, t['q1'])
    add_message_to_history(callback_query.from_user.id, q1_msg.message_id)
    
    await SurveyForm.q1.set()
    await callback_query.answer()

@dp.message_handler(state=SurveyForm.q1)
async def process_q1(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language', 'uz')
    t = translations[language]
    
    # Удаляем предыдущие сообщения
    await clean_previous_messages(message.chat.id)
    
    # Сохраняем ответ
    await state.update_data(q1=message.text)
    
    # Отправляем вопрос 2
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton(t['yes'], callback_data="q2_ha"),
        types.InlineKeyboardButton(t['no'], callback_data="q2_yoq")
    )
    
    q2_msg = await message.answer(t['q2'], reply_markup=keyboard)
    add_message_to_history(message.chat.id, q2_msg.message_id)
    
    await SurveyForm.q2.set()

@dp.callback_query_handler(lambda c: c.data.startswith('q2_'), state=SurveyForm.q2)
async def process_q2(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    language = data.get('language', 'uz')
    t = translations[language]
    
    # Удаляем предыдущие сообщения
    await clean_previous_messages(callback_query.from_user.id)
    
    answer = callback_query.data.split('_')[1]
    await state.update_data(q2=answer)
    
    if answer == 'ha':
        # Отправляем вопрос 2.1
        q2_text_msg = await bot.send_message(callback_query.from_user.id, t['q2_details'])
        add_message_to_history(callback_query.from_user.id, q2_text_msg.message_id)
        await SurveyForm.q2_text.set()
    else:
        # Отправляем вопрос 3
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        keyboard.add(
            types.InlineKeyboardButton(t['yes'], callback_data="q3_ha"),
            types.InlineKeyboardButton(t['no'], callback_data="q3_yoq"),
            types.InlineKeyboardButton(t['partially'], callback_data="q3_qisman")
        )
        q3_msg = await bot.send_message(callback_query.from_user.id, t['q3'], reply_markup=keyboard)
        add_message_to_history(callback_query.from_user.id, q3_msg.message_id)
        await SurveyForm.q3.set()
    
    await callback_query.answer()

@dp.message_handler(state=SurveyForm.q2_text)
async def process_q2_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language', 'uz')
    t = translations[language]
    
    # Удаляем предыдущие сообщения
    await clean_previous_messages(message.chat.id)
    
    await state.update_data(q2_text=message.text)
    
    # Отправляем вопрос 3
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    keyboard.add(
        types.InlineKeyboardButton(t['yes'], callback_data="q3_ha"),
        types.InlineKeyboardButton(t['no'], callback_data="q3_yoq"),
        types.InlineKeyboardButton(t['partially'], callback_data="q3_qisman")
    )
    
    q3_msg = await message.answer(t['q3'], reply_markup=keyboard)
    add_message_to_history(message.chat.id, q3_msg.message_id)
    
    await SurveyForm.q3.set()

@dp.callback_query_handler(lambda c: c.data.startswith('q3_'), state=SurveyForm.q3)
async def process_q3(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    language = data.get('language', 'uz')
    t = translations[language]
    
    # Удаляем предыдущие сообщения
    await clean_previous_messages(callback_query.from_user.id)
    
    answer = callback_query.data.split('_')[1]
    await state.update_data(q3=answer)
    
    # Отправляем вопрос 4
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton(t['yes'], callback_data="q4_ha"),
        types.InlineKeyboardButton(t['no'], callback_data="q4_yoq")
    )
    
    q4_msg = await bot.send_message(callback_query.from_user.id, t['q4'], reply_markup=keyboard)
    add_message_to_history(callback_query.from_user.id, q4_msg.message_id)
    
    await SurveyForm.q4.set()
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data.startswith('q4_'), state=SurveyForm.q4)
async def process_q4(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    language = data.get('language', 'uz')
    t = translations[language]
    
    # Удаляем предыдущие сообщения
    await clean_previous_messages(callback_query.from_user.id)
    
    answer = callback_query.data.split('_')[1]
    await state.update_data(q4=answer)
    
    if answer == 'ha':
        # Отправляем вопрос 4.1
        q4_text_msg = await bot.send_message(callback_query.from_user.id, t['q4_details'])
        add_message_to_history(callback_query.from_user.id, q4_text_msg.message_id)
        await SurveyForm.q4_text.set()
    else:
        # Отправляем вопрос 5
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            types.InlineKeyboardButton(t['yes'], callback_data="q5_ha"),
            types.InlineKeyboardButton(t['no'], callback_data="q5_yoq")
        )
        q5_msg = await bot.send_message(callback_query.from_user.id, t['q5'], reply_markup=keyboard)
        add_message_to_history(callback_query.from_user.id, q5_msg.message_id)
        await SurveyForm.q5.set()
    
    await callback_query.answer()

@dp.message_handler(state=SurveyForm.q4_text)
async def process_q4_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language', 'uz')
    t = translations[language]
    
    # Удаляем предыдущие сообщения
    await clean_previous_messages(message.chat.id)
    
    await state.update_data(q4_text=message.text)
    
    # Отправляем вопрос 5
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton(t['yes'], callback_data="q5_ha"),
        types.InlineKeyboardButton(t['no'], callback_data="q5_yoq")
    )
    
    q5_msg = await message.answer(t['q5'], reply_markup=keyboard)
    add_message_to_history(message.chat.id, q5_msg.message_id)
    
    await SurveyForm.q5.set()

@dp.callback_query_handler(lambda c: c.data.startswith('q5_'), state=SurveyForm.q5)
async def process_q5(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    language = data.get('language', 'uz')
    t = translations[language]
    
    # Удаляем предыдущие сообщения
    await clean_previous_messages(callback_query.from_user.id)
    
    answer = callback_query.data.split('_')[1]
    await state.update_data(q5=answer)
    
    if answer == 'ha':
        # Отправляем вопрос 5.1
        q5_text_msg = await bot.send_message(callback_query.from_user.id, t['q5_details'])
        add_message_to_history(callback_query.from_user.id, q5_text_msg.message_id)
        await SurveyForm.q5_text.set()
    else:
        # Отправляем вопрос 6
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            types.InlineKeyboardButton(t['yes'], callback_data="q6_ha"),
            types.InlineKeyboardButton(t['no'], callback_data="q6_yoq")
        )
        q6_msg = await bot.send_message(callback_query.from_user.id, t['q6'], reply_markup=keyboard)
        add_message_to_history(callback_query.from_user.id, q6_msg.message_id)
        await SurveyForm.q6.set()
    
    await callback_query.answer()

@dp.message_handler(state=SurveyForm.q5_text)
async def process_q5_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language', 'uz')
    t = translations[language]
    
    # Удаляем предыдущие сообщения
    await clean_previous_messages(message.chat.id)
    
    await state.update_data(q5_text=message.text)
    
    # Отправляем вопрос 6
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton(t['yes'], callback_data="q6_ha"),
        types.InlineKeyboardButton(t['no'], callback_data="q6_yoq")
    )
    
    q6_msg = await message.answer(t['q6'], reply_markup=keyboard)
    add_message_to_history(message.chat.id, q6_msg.message_id)
    
    await SurveyForm.q6.set()

@dp.callback_query_handler(lambda c: c.data.startswith('q6_'), state=SurveyForm.q6)
async def process_q6(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    language = data.get('language', 'uz')
    t = translations[language]
    
    # Удаляем предыдущие сообщения
    await clean_previous_messages(callback_query.from_user.id)
    
    answer = callback_query.data.split('_')[1]
    await state.update_data(q6=answer)
    
    if answer == 'ha':
        # Отправляем вопрос 6.1
        q6_text_msg = await bot.send_message(callback_query.from_user.id, t['q6_details'])
        add_message_to_history(callback_query.from_user.id, q6_text_msg.message_id)
        await SurveyForm.q6_text.set()
    else:
        # Отправляем вопрос 7
        q7_msg = await bot.send_message(callback_query.from_user.id, t['q7'])
        add_message_to_history(callback_query.from_user.id, q7_msg.message_id)
        await SurveyForm.q7.set()
    
    await callback_query.answer()

@dp.message_handler(state=SurveyForm.q6_text)
async def process_q6_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language', 'uz')
    t = translations[language]
    
    # Удаляем предыдущие сообщения
    await clean_previous_messages(message.chat.id)
    
    await state.update_data(q6_text=message.text)
    
    # Отправляем вопрос 7
    q7_msg = await message.answer(t['q7'])
    add_message_to_history(message.chat.id, q7_msg.message_id)
    
    await SurveyForm.q7.set()

@dp.message_handler(state=SurveyForm.q7)
async def process_q7(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language', 'uz')
    t = translations[language]
    
    # Удаляем предыдущие сообщения
    await clean_previous_messages(message.chat.id)
    
    await state.update_data(q7=message.text)
    
    # Отправляем вопрос 8
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton(t['yes'], callback_data="q8_ha"),
        types.InlineKeyboardButton(t['no'], callback_data="q8_yoq")
    )
    
    q8_msg = await message.answer(t['q8'], reply_markup=keyboard)
    add_message_to_history(message.chat.id, q8_msg.message_id)
    
    await SurveyForm.q8.set()

@dp.callback_query_handler(lambda c: c.data.startswith('q8_'), state=SurveyForm.q8)
async def process_q8(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    language = data.get('language', 'uz')
    t = translations[language]
    
    # Удаляем предыдущие сообщения
    await clean_previous_messages(callback_query.from_user.id)
    
    answer = callback_query.data.split('_')[1]
    await state.update_data(q8=answer)
    
    # Отправляем вопрос 9
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton(t['yes'], callback_data="q9_ha"),
        types.InlineKeyboardButton(t['no'], callback_data="q9_yoq")
    )
    
    q9_msg = await bot.send_message(callback_query.from_user.id, t['q9'], reply_markup=keyboard)
    add_message_to_history(callback_query.from_user.id, q9_msg.message_id)
    
    await SurveyForm.q9.set()
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data.startswith('q9_'), state=SurveyForm.q9)
async def process_q9(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    language = data.get('language', 'uz')
    t = translations[language]
    
    # Удаляем предыдущие сообщения
    await clean_previous_messages(callback_query.from_user.id)
    
    answer = callback_query.data.split('_')[1]
    await state.update_data(q9=answer)
    
    if answer == 'ha':
        # Отправляем вопрос 9.1
        q9_text_msg = await bot.send_message(callback_query.from_user.id, t['q9_details'])
        add_message_to_history(callback_query.from_user.id, q9_text_msg.message_id)
        await SurveyForm.q9_text.set()
    else:
        # Отправляем вопрос 10
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            types.InlineKeyboardButton(t['yes'], callback_data="q10_ha"),
            types.InlineKeyboardButton(t['no'], callback_data="q10_yoq")
        )
        q10_msg = await bot.send_message(callback_query.from_user.id, t['q10'], reply_markup=keyboard)
        add_message_to_history(callback_query.from_user.id, q10_msg.message_id)
        await SurveyForm.q10.set()
    
    await callback_query.answer()

@dp.message_handler(state=SurveyForm.q9_text)
async def process_q9_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language', 'uz')
    t = translations[language]
    
    # Удаляем предыдущие сообщения
    await clean_previous_messages(message.chat.id)
    
    await state.update_data(q9_text=message.text)
    
    # Отправляем вопрос 10
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton(t['yes'], callback_data="q10_ha"),
        types.InlineKeyboardButton(t['no'], callback_data="q10_yoq")
    )
    
    q10_msg = await message.answer(t['q10'], reply_markup=keyboard)
    add_message_to_history(message.chat.id, q10_msg.message_id)
    
    await SurveyForm.q10.set()

@dp.callback_query_handler(lambda c: c.data.startswith('q10_'), state=SurveyForm.q10)
async def process_q10(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    language = data.get('language', 'uz')
    t = translations[language]
    
    # Удаляем предыдущие сообщения
    await clean_previous_messages(callback_query.from_user.id)
    
    answer = callback_query.data.split('_')[1]
    await state.update_data(q10=answer)
    
    # Отправляем вопрос 11
    q11_msg = await bot.send_message(callback_query.from_user.id, t['q11'])
    add_message_to_history(callback_query.from_user.id, q11_msg.message_id)
    
    await SurveyForm.q11.set()
    await callback_query.answer()

@dp.message_handler(state=SurveyForm.q11)
async def process_q11(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language', 'uz')
    t = translations[language]
    
    # Удаляем предыдущие сообщения
    await clean_previous_messages(message.chat.id)
    
    await state.update_data(q11=message.text)
    
    # Отправляем вопрос 12
    q12_msg = await message.answer(t['q12'])
    add_message_to_history(message.chat.id, q12_msg.message_id)
    
    await SurveyForm.q12.set()

@dp.message_handler(state=SurveyForm.q12)
async def process_q12(message: types.Message, state: FSMContext):
    data = await state.get_data()
    language = data.get('language', 'uz')
    t = translations[language]
    
    # Удаляем предыдущие сообщения
    await clean_previous_messages(message.chat.id)
    
    await state.update_data(q12=message.text)
    
    # Получаем user_id из состояния
    user_data = await state.get_data()
    
    # Получаем user_id из базы
    user = get_user_by_tg_id(message.from_user.id)
    if user:
        user_id = user[0]
        
        # Сохраняем ответы в базу
        add_response(user_id, user_data)
        
        await message.answer(t['thank_you'])
    else:
        await message.answer("Произошла ошибка: пользователь не найден. Пожалуйста, начните снова с /start")
    
    await state.finish()

# Команда для проверки статуса
@dp.message_handler(commands=['status'])
async def status_cmd(message: types.Message):
    user = get_user_by_tg_id(message.from_user.id)
    if user:
        status_text = f"""
Ваш статус:
ID: {user[0]}
Telegram ID: {user[1]}
Имя: {user[3]} {user[4]}
Язык: {user[5]}
Начал опрос: {user[6]}
Завершен: {'Да' if user[7] else 'Нет'}
"""
        await message.answer(status_text)
    else:
        await message.answer("Вы еще не начали опрос. Используйте /start")

if __name__ == "__main__":
    print("Бот запущен...")
    executor.start_polling(dp, skip_updates=True)