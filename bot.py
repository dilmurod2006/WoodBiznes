import calendar
from datetime import datetime
import os
import sqlite3
from telebot import TeleBot, types
from database_crud import (
    get_connection,
    add_admin,
    add_worker,
    delete_worker,
    delete_admin,
    add_daily_work,
    add_wood_data,
    parse_input_data1,
    export_daily_work_to_excel,
    get_reports_wood,
    format_date,
    get_admin_info_by_tg_id
)

TOKEN = "7309361689:AAHi3s4p68nilimXiUgB3bIrAS_vm9uKyT8"
bot = TeleBot(TOKEN)


conn,cur = get_connection()
# Adminlar ro'yxatini olish
cur.execute('SELECT tg_id FROM Admin')
admin_ids = cur.fetchall()
# Adminlar ID ro'yxatini tayyorlash
admin_ids = [id[0] for id in admin_ids]
# basic admins ID
ADMINS = [5420071824, 114226828]

# Ma'lumotlarni vaqtinchalik saqlash uchun dictionary
user_data = {}

# Dictionary to hold user states
user_states = {}

# Define states
STATE_TRANSITION = "kunlik_kiritish"
STATE_WORKERS = "workers"
STATE_REMAINDER = "ostatok"
STATE_CONSUMPTION = "rasxod"
STATE_ADD_ADMIN = "add_admin"
STATE_DELETE_ADMIN = "delete_admin"
STATE_ADD_WORKER = "add_worker"
STATE_DELETE_WORKER = "delete_worker"
OTHER_FUNCTION = "other_function"
STATE_ADD_WORK_VOLUME1 = "add_work_volume1"
STATE_ADD_WORK_VOLUME2 = "add_work_volume2"
STATE_ADD_WOOD = "add_wood"
STATE_GET_DAILY_WORK_REPORT = "get_daily_work_report"
STATE_GET_WOOD_DATA_REPORT = "get_wood_data_report"

# Start command
@bot.message_handler(commands=["start"])
def start(message):
    """
    start funksiyasi bu botga /start commandasi berilganda
    botni ishga tushurish uchun ishlatiladi
    va bosh sahifaga qaytaradi
    bosh menu 4ta tugmadan iborat bo'ladi
    bular: "переход ➕", 'рабочие 👥'
            'остаток', 'расход'
    """
    try:
        # check if user is admin
        conn, cur = get_connection()
        cur.execute("SELECT * FROM Admin WHERE tg_id = ?", (str(message.from_user.id),))
        admin = cur.fetchone()
        if message.from_user.id in ADMINS or admin:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.row("переход ➕", 'рабочие 👥')
            markup.row('остаток', 'расход')
            markup.row('другие функции')
            # text = """
            # Assalomu aleykum botga xush kelibsiz!
            # tugmar haqida:
            # "переход ➕" tugmasi bu sizga har kunlik ishchilarni ishlagn ishini kiritsh uchun yordam beradi.
            # "рабочие 👥" tugmasi bu sizga har oylik ishchilarni qilgan ishini ko'rsatish sizga excel file tashlab beradi.
            # "остаток" tugmasi bu sizga qoldiqni ko'rsatadi
            # "расход" tugmasi bu sizga qilgan xarajatlaringizni ko'rsatadi
            # tugmlarni tanlang:
            # """
            bot.send_message(message.chat.id, 'Выберите действие', reply_markup=markup)
        else:
            bot.send_message(message.chat.id, 'Доступ запрещен.')
    except Exception as e:
        print(f"Error: {e}")

# kunlik transition command 
@bot.message_handler(commands=['transition'])
def kunlik_kiritish(message):
    """
    kunlik kiritish funksiyasi bu botga /transition commandasi berilganda
    sizga:
            <b>Добавить полное имя работника</b>
            <b>Добавьте объём работы для данного работника</b>


            <b>Пример:</b>
                <b>Иван Иванов</b>
                <b>Толщина*Ширина*Длина*Кол-во</b>
                <b>0.034*0.081*6*100</b>
                <b>0.0034*0.0098*6*15</b>
                <b>0.0037*0.0099*4*10</b>
                <b>0.0038*0.0098*9*5</b>
                <b>0.0039*0.0099*8*5</b>
            bunga xoxlagancha kiritib ketish mumkun yani xoxlagancha malumot kiritish mumkun
    va bosh sahifaga qaytaradi
    """
    try:
        conn, cur = get_connection()
        cur.execute("SELECT * FROM Admin WHERE tg_id = ?", (str(message.from_user.id),))
        admin = cur.fetchone()
        if message.from_user.id in ADMINS or admin:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.row('Отмена ❌')
            text = """
            <b>Добавить полное имя работника</b>
            <b>Добавьте объём работы для данного работника</b>


            <b>Пример:</b>
                <b>Иван Иванов</b>
                <b>Толщина*Ширина*Длина*Кол-во</b>
                <b>0.034*0.081*6*100</b>
                <b>0.0034*0.0098*6*15</b>
                <b>0.0037*0.0099*4*10</b>
                <b>0.0038*0.0098*9*5</b>
                <b>0.0039*0.0099*8*5</b>
            bunga xoxlagancha kiritib ketish mumkun yani xoxlagancha malumot kiritish mumkun
            """
            msg = bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=markup)
            bot.register_next_step_handler(msg, add_work_volume2_process)
    except Exception as e:
        print(f"Error: {e}")

# remainder command 
@bot.message_handler(commands=['remainder'])
def ostatok(message):
    """
    Bu funksiya ostadokni ko'rsatadi.
    """
    try:
        conn, cur = get_connection()
        cur.execute("SELECT * FROM Admin WHERE tg_id = ?", (str(message.from_user.id),))
        admin = cur.fetchone()
        if message.from_user.id in ADMINS or admin:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.row('Отмена ❌')
            msg = bot.send_message(message.chat.id, "Bu funksiya qoldiqni ko'rsatadi.", reply_markup=markup)
            bot.register_next_step_handler(msg, view_reminder_process)
    except Exception as e:
        print(f"Error: {e}")

# consumption command for view consumption
@bot.message_handler(commands=['consumption'])
def rasxod(message):
    """
    Bu funksiya rasxodlarni ko'rsatadi.
    """
    try:
        conn, cur = get_connection()
        cur.execute("SELECT * FROM Admin WHERE tg_id = ?", (str(message.from_user.id),))
        admin = cur.fetchone()
        if message.from_user.id in ADMINS or admin:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.row('Отмена ❌')
            msg = bot.send_message(message.chat.id, "Bu funksiya rasxodlarni ko'rsatadi.", reply_markup=markup)
            bot.register_next_step_handler(msg, view_consumption_process)
    except Exception as e:
        print(f"Error: {e}")

# Other command function
@bot.message_handler(commands=['other_function'])
def other_function(message):
    """
    Bu funksiya boshqa funksiyalarni ko'rsatadi.
    """
    try:
        conn, cur = get_connection()
        cur.execute("SELECT * FROM Admin WHERE tg_id = ?", (str(message.from_user.id),))
        admin = cur.fetchone()
        if message.from_user.id in ADMINS or admin:
            text = """
Другие функции:

/add_admin - Добавить администратора ➕

/delete_admin - Удалить администратора ➖

/add_worker - Добавить работника ➕

/delete_worker - Удалить работника ➖

/add_work_volume1 - <b>Добавить объём работы 📈

/add_work_volume2 - Добавить объём работы 📈

/add_wood - Добавить древесину 📈

/get_worker_reports - Получайте отчеты работников 📄

/get_wood_reports - Получить отчеты о древесине 📄

/start - главное меню 🏘

/help - Помощь
"""
            bot.send_message(message.chat.id, text,)
    except Exception as e:
        print(f"Error: {e}")

# help command
@bot.message_handler(commands=['help'])
def help(message):
    """
    Bu funksiya botni qanday ishlatish haqida.
    """
    try:
        conn, cur = get_connection()
        cur.execute("SELECT * FROM Admin WHERE tg_id = ?", (str(message.from_user.id),))
        admin = cur.fetchone()
        if message.from_user.id in ADMINS or admin:
            bot.send_message(message.chat.id, 'Помощь', parse_mode='HTML')
    except Exception as e:
        print(f"Error: {e}")

# add_admin command
@bot.message_handler(commands=['add_admin'])
def add_admin_command(message):
    """
    Bu funksiya admin qo'shish uchun ishlatiladi.
    bunda user_states[message.chat.id] = STATE_ADD_ADMIN
    bo'limiga active qiladi va add_admin_process() funksiyasini ishlatadi
    """
    try:
        conn, cur = get_connection()
        cur.execute("SELECT * FROM Admin WHERE tg_id = ?", (str(message.from_user.id),))
        admin = cur.fetchone()
        if message.from_user.id in ADMINS or admin:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.row('Отмена ❌')
            text = """
            <b><i>Добавить администратора:</i></b> 
            <b>1.Имя Фамилия:</b>
            <b>2.Телеграм ID:</b>

            <b>Пример:</b>
            <b>Иван Иванов</b>
            <b>5420071824</b>
            """
            msg = bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=markup)
            bot.register_next_step_handler(msg, add_admin_process)
            user_states[message.chat.id] = STATE_ADD_ADMIN
    except Exception as e:
        print(f"Error: {e}")

# delete admin command
@bot.message_handler(commands=['delete_admin'])
def delete_admin_command(message):
    """
    Bu funksiya adminni o'chirish uchun ishlatiladi.
    bunda user_states[message.chat.id] = STATE_DELETE_ADMIN
    bo'limiga active qiladi va delete_admin_process() funksiyasini ishlatadi
    """
    try:
        conn, cur = get_connection()
        cur.execute("SELECT * FROM Admin WHERE tg_id = ?", (str(message.from_user.id),))
        admin = cur.fetchone()
        if message.from_user.id in ADMINS or admin:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.row('Отмена ❌')
            text = """
            <i><b>Удалить администратора:</b></i>
            <b>1.Имя Фамилия:</b>

            <b>Пример:</b>
            <b><i>Иван Иванов</i></b>
            """
            msg = bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=markup)
            bot.register_next_step_handler(msg, delete_admin_process)
            user_states[message.chat.id] = STATE_DELETE_ADMIN
    except Exception as e:
        print(f"Error: {e}")

# add_worker command
@bot.message_handler(commands=['add_worker'])
def add_worker_command(message):
    """
    Bu funksiya worker qo'shish uchun ishlatiladi.
    bunda user_states[message.chat.id] = STATE_ADD_WORKER
    bo'limiga active qiladi va add_worker_process() funksiyasini ishlatadi
    """
    try:
        conn, cur = get_connection()
        cur.execute("SELECT * FROM Admin WHERE tg_id = ?", (str(message.from_user.id),))
        admin = cur.fetchone()
        if message.from_user.id in ADMINS or admin:
            markup  = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.row('Отмена ❌')
            text = """
            <b><i>Добавить работника:</i></b>
            <b>1.Имя Фамилия:</b>

            <b>Пример:</b>
            <b>Иван Иванов</b>
            """
            msg = bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=markup)
            bot.register_next_step_handler(msg, add_worker_process)
            user_states[message.chat.id] = STATE_ADD_WORKER
    except Exception as e:
        print(f"Error: {e}")

# delete worker command
@bot.message_handler(commands=['delete_worker'])
def delete_worker_command(message):
    """
    Bu funksiya workerni o'chirish uchun ishlatiladi.
    bunda user_states[message.chat.id] = STATE_DELETE_WORKER
    bo'limiga active qiladi va delete_worker_process() funksiyasini ishlatadi
    """
    try:
        conn, cur = get_connection()
        cur.execute("SELECT * FROM Admin WHERE tg_id = ?", (str(message.from_user.id),))
        admin = cur.fetchone()
        if message.from_user.id in ADMINS or admin:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.row('Отмена ❌')
            text = """
            <b><i>Удалить работника:</i></b>
            <b>1.Имя Фамилия:</b>

            <b>Пример:</b>
            <b>Иван Иванов</b>
            """
            msg = bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=markup)
            bot.register_next_step_handler(msg, delete_worker_process)
            user_states[message.chat.id] = STATE_DELETE_WORKER
    except Exception as e:
        print(f"Error: {e}")

# add_work_volume1 command function
@bot.message_handler(commands=['add_work_volume1'])
def add_work_volume1_command(message):
    """
    Bu funksiya shunchaki test sifatida ishlayapti
    mijozga ko'rsatish uchun agar mijoz maqullas qo'laniladi bu funksiya
    """
    try:
        conn, cur = get_connection()
        cur.execute("SELECT * FROM Admin WHERE tg_id = ?", (str(message.from_user.id),))
        admin = cur.fetchone()
        if message.from_user.id in ADMINS or admin:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.row('Отмена ❌')
            text = """
            <b>Добавить полное имя работника</b>
            <b>Добавьте объём работы для данного работника</b>


            <b>Пример:</b>
                Иван Иванов
                Толщина*Ширина*Длина*Кол-во
                0.034*0.081*6*100
                0.0034*0.0098*6*15
                0.0037*0.0099*4*10
                0.0038*0.0098*9*5
                0.0039*0.0099*8*5
                
            bunga xoxlagancha kiritib ketish mumkun yani xoxlagancha malumot kiritish mumkun
        """
            msg = bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=markup)
            bot.register_next_step_handler(msg, add_work_volume1_process)
            user_states[message.chat.id] = STATE_ADD_WORK_VOLUME1
    except Exception as e:
        print(f"Error: {e}")

# add_work_volume2 command function
@bot.message_handler(commands=['add_work_volume2'])
def add_work_volume2_command(message):
    """
    Bu funksiya shunchaki test sifatida ishlayapti
    mijozga ko'rsatish uchun agar mijoz maqullas qo'laniladi bu funksiya
    """
    try:
        conn, cur = get_connection()
        cur.execute("SELECT * FROM Admin WHERE tg_id = ?", (str(message.from_user.id),))
        admin = cur.fetchone()
        if message.from_user.id in ADMINS or admin:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.row('Отмена ❌')
            text = """
            <b>Добавить полное имя работника</b>
            <b>Добавьте объём работы для данного работника</b>


            <b>Пример:</b>
                Иван Иванов
                Толщина*Ширина*Длина*Кол-во
                0.034*0.081*6*100
                0.0034*0.0098*6*15
                0.0037*0.0099*4*10
                0.0038*0.0098*9*5
                0.0039*0.0099*8*5

            bunga xoxlagancha kiritib ketish mumkun yani xoxlagancha malumot kiritish mumkun
        """
            msg = bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=markup)
            bot.register_next_step_handler(msg, add_work_volume2_process)
            user_states[message.chat.id] = STATE_ADD_WORK_VOLUME2
    except Exception as e:
        print(f"Error: {e}")

# add_wood command function
@bot.message_handler(commands=['add_wood'])
def add_wood_command(message):
    """
    Bu funksiya Yog'och qo'shish uchun ishlatiladi.
    /add_wood komandasini bosganda add_wood_process() funksiyasini ishlatadi.
    """
    try:
        conn, cur = get_connection()
        cur.execute("SELECT * FROM Admin WHERE tg_id = ?", (str(message.from_user.id),))
        admin = cur.fetchone()
        if message.from_user.id in ADMINS or admin:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.row('Отмена ❌')
            text = """
Добавить древесину в базу

введите название Авто номер

Добавить название дерева
введите размеры:
Толщина*Ширина*Длина*Кол-во
Толщина*Ширина*Длина*Кол-во
Толщина*Ширина*Длина*Кол-во
Толщина*Ширина*Длина*Кол-во

# Описание

Пример:
"
60S248ZA

Archa
0.034*0.081*6*100
0.034*0.081*8*23
0.034*0.081*7*223
0.034*0.081*4*325
0.034*0.081*6*564

# Tel:7 912 811 00 02
"

bunga xoxlagancha kiritib ketish mumkun yani xoxlagancha malumot kiritish mumkun
        """
            msg = bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=markup)
            bot.register_next_step_handler(msg, add_wood_process)
    except Exception as e:
        print(f"Error: {e}")

# get_worker_reports command
@bot.message_handler(commands=['get_worker_reports'])
def get__worker_reports(message):
    """
    Bu funksiya workerlarni 1 oylik qilgan ishlarini excel filega export qiladi.
    """
    try: 
        conn, cur = get_connection()
        cur.execute("SELECT * FROM Admin WHERE tg_id = ?", (str(message.from_user.id),))
        admin = cur.fetchone()
        if message.from_user.id in ADMINS or admin:
            today = datetime.today()
            first_day = today.replace(day=1)
            last_day = today.replace(day=calendar.monthrange(today.year, today.month)[1])
            start_date = format_date(first_day)
            end_date = format_date(last_day)
            export_daily_work_to_excel(start_date, end_date)
            file_path = f'работники_отчет_{start_date}_до_{end_date}.xlsx'
            with open(file_path, 'rb') as file:
                bot.send_document(message.chat.id, file, caption=f'Отчет от {start_date} до {end_date}')
            os.remove(file_path)
    except Exception as e:
        print(f"Error: {e}")

# get_wood_reports command
@bot.message_handler(commands=['get_wood_reports'])
def get_wood_reports(message):
    """
    Bu funksiya Yog'ochlarni excel ko'rinishda olish uchun ishlatiladi.
    """
    try: 
        conn, cur = get_connection()
        cur.execute("SELECT * FROM Admin WHERE tg_id = ?", (str(message.from_user.id),))
        admin = cur.fetchone()
        if message.from_user.id in ADMINS or admin:
            text = """
Bu funksiya yog'ochlarni excel ko'rinishda olish uchun ishlatiladi.
boshlanish sana va tugash sana kiritiladi.

Пример:
    01.07.2024 
    31.07.2024

"""
            msg = bot.send_message(message.chat.id,text)
            bot.register_next_step_handler(msg, get_wood_reports_process)
            user_states[message.chat.id] = STATE_GET_WOOD_DATA_REPORT
    except Exception as e:
        print(f"Error: {e}")



# Message Handler functions
@bot.message_handler(content_types=['text'])
def handle_text_messages(message):
    # commands for function
    state = user_states.get(message.chat.id)
    if state == STATE_ADD_ADMIN:
        add_admin_process(message)
    elif state == STATE_DELETE_ADMIN:
        delete_admin_process(message)
    elif state == STATE_ADD_WORKER:
        add_worker_process(message)
    elif state == STATE_DELETE_WORKER:
        delete_worker_process(message)
    elif state == OTHER_FUNCTION:
        other_function(message)
    elif state == STATE_ADD_WORK_VOLUME1:
        add_work_volume1_process(message)
    elif state == STATE_ADD_WORK_VOLUME2:
        add_work_volume2_process(message)
    elif state == STATE_ADD_WOOD:
        add_wood_process(message)
    elif state == STATE_GET_WOOD_DATA_REPORT:
        get_wood_reports_process(message)
    elif message.text == "другие функции":
        other_function(message)
    
    # main menu buttons function
    elif "переход ➕" == message.text:
       try:
            conn, cur = get_connection()
            cur.execute("SELECT * FROM Admin WHERE tg_id = ?", (str(message.from_user.id),))
            admin = cur.fetchone()
            if message.from_user.id in ADMINS or admin:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.row('Отмена ❌')
                text = """
            <b>Добавить полное имя работника</b>
            <b>Добавьте объём работы для данного работника</b>


            <b>Пример:</b>
                <b>Иван Иванов</b>
                <b>Толщина*Ширина*Длина*Кол-во</b>
                <b>0.034*0.081*6*100</b>
                <b>0.0034*0.0098*6*15</b>
                <b>0.0037*0.0099*4*10</b>
                <b>0.0038*0.0098*9*5</b>
                <b>0.0039*0.0099*8*5</b>
            bunga xoxlagancha kiritib ketish mumkun yani xoxlagancha malumot kiritish mumkun
            """
                msg = bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=markup)
                bot.register_next_step_handler(msg, add_work_volume2_process)
       except Exception as e:
            print(f"Error: {e}")
    elif "рабочие 👥" == message.text:
        try: 
            conn, cur = get_connection()
            cur.execute("SELECT * FROM Admin WHERE tg_id = ?", (str(message.from_user.id),))
            admin = cur.fetchone()
            if message.from_user.id in ADMINS or admin:
                today = datetime.today()
                first_day = today.replace(day=1)
                last_day = today.replace(day=calendar.monthrange(today.year, today.month)[1])
                export_daily_work_to_excel(format_date(first_day), format_date(last_day))
                # export_daily_work_to_excel(start_date, end_date)
                with open(f'работники_отчет_{format_date(first_day)}_до_{format_date(last_day)}.xlsx', 'rb') as file:
                    bot.send_document(message.chat.id, file, caption=f'Отчет от {format_date(first_day)} до {format_date(last_day)}')
                # os.remove(f'работники_отчет_{format_date(first_day)}_до_{format_date(last_day)}.xlsx')
        except Exception as e:
            print(f"Error: {e}")
    elif message.text == 'Отмена ❌':
        bot.send_message(message.chat.id, 'Действие отменено.', reply_markup=types.ReplyKeyboardRemove())
        start(message)
        user_states.pop(message.chat.id, None)
    elif message.text == "главное меню 🏘":
        start(message)

# add_admin process function
def add_admin_process(message):
    try:
        if message.text == 'Отмена ❌':
            bot.send_message(message.chat.id, 'Отмена добавления администратора.', reply_markup=types.ReplyKeyboardRemove())
            start(message)
            other_function(message)
            return
        # Split the message text by spaces
        admin_data = message.text.split()
        if len(admin_data) < 2:
            raise ValueError("Формат данных неверный. Убедитесь, что вы отправили имя и ID.")
        name = " ".join(admin_data[:-1]).strip()
        telegram_id = int(admin_data[-1].strip())
        # Store admin data
        user_data['admin_data'] = {'name': name, 'telegram_id': telegram_id}
        get_admin_data = get_admin_info_by_tg_id(message.chat.id)
        # Call the function to add admin
        add_admin(name, telegram_id)
        start(message)
        for admin_id in admin_ids:
            try:    
                text = f"""
{get_admin_data['full_name']} tomonidan:
{name} isimli adminstartor qo'shildi databazaga.
"""
                bot.send_message(admin_id, text)
            except Exception as e:
                print(e)
        bot.send_message(message.chat.id, 'Администратор успешно добавлен!', reply_markup=types.ReplyKeyboardRemove())
    except ValueError as ve:
        bot.send_message(message.chat.id, f"Ошибка: {ve}")
        add_admin_command(message)  # Restart the process
    except Exception as e:
        print(e)
    finally:
        user_states.pop(message.chat.id, None)

# delete_admin process function
def delete_admin_process(message):
    try:
        if message.text == 'Отмена ❌':
            bot.send_message(message.chat.id, 'Отмена удаления администратора.', reply_markup=types.ReplyKeyboardRemove())
            start(message)
            other_function(message)
            return
        name = message.text.strip()
        get_admin_data = get_admin_info_by_tg_id(message.chat.id)
        # Call the function to delete admin
        delete_admin(name)
        for admin_id in admin_ids:
            try:
                text = f"""
{get_admin_data['full_name']} tomonidan:
{name} isimli adminstartor  databazadan o'chirildi.
"""
                bot.send_message(admin_id, text)
            except Exception as e:
                print(e)
        start(message)
        bot.send_message(message.chat.id, 'Администратор успешно удален!', reply_markup=types.ReplyKeyboardRemove())
    except Exception as e:
        print(e)
    finally:
        user_states.pop(message.chat.id, None)

# add_worker process function
def add_worker_process(message):
    try:
        if message.text == 'Отмена ❌':
            bot.send_message(message.chat.id, 'Отмена добавления работника.', reply_markup=types.ReplyKeyboardRemove())
            start(message)
            other_function(message)
            return
        
        name = message.text.strip()
        
        # Store worker data
        user_data['worker_full_name'] = name
        get_admin_data = get_admin_info_by_tg_id(message.chat.id)
        # Call the function to add worker
        add_worker(name)
        for admin_id in admin_ids:
            try:
                text = f"""
{get_admin_data['full_name']} tomonidan:
{name} isimli adminstartor  databazaga qo'shildi.
"""
                bot.send_message(admin_id, text)
            except Exception as e:
                print(e)
        
        bot.send_message(message.chat.id, 'Работник успешно добавлен!', reply_markup=types.ReplyKeyboardRemove())
        start(message)
        other_function(message)
    except Exception as e:
        print(e)
    finally:
        user_states.pop(message.chat.id, None)

# delete_worker process function
def delete_worker_process(message):
    try:
        if message.text == 'Отмена ❌':
            bot.send_message(message.chat.id, 'Отмена удаления работника.', reply_markup=types.ReplyKeyboardRemove())
            start(message)
            other_function(message)
            return
        name = message.text.strip()
        # Store worker data
        user_data['worker_full_name'] = name
        get_admin_data = get_admin_info_by_tg_id(message.chat.id)
        # Call the function to delete worker
        delete_worker(name)
        for admin_id in admin_ids:
            try:
                text = f"""
{get_admin_data['full_name']} tomonidan:
{name} isimli ishchi  databazadan o'chirildi.
"""
                bot.send_message(admin_id, text)
            except Exception as e:
                print(e)
        bot.send_message(message.chat.id, 'Работник успешно удален!', reply_markup=types.ReplyKeyboardRemove())
        start(message)
    except Exception as e:
        print(e)
    finally:
        user_states.pop(message.chat.id, None)

# view reminder process function
def view_reminder_process(message):
    try:
        if message.text == 'Отмена ❌':
            bot.send_message(message.chat.id, 'Отмена', reply_markup=types.ReplyKeyboardRemove())
            start(message)
            other_function(message)
            return
        
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}")
        print(e)
    finally:
        user_states.pop(message.chat.id, None)


# view consuption process function
def view_consumption_process(message):
    try:
        if message.text == 'Отмена ❌':
            bot.send_message(message.chat.id, 'Отмена', reply_markup=types.ReplyKeyboardRemove())
            start(message)
            other_function(message)
            return
        
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}")
        print(e)
    finally:
        user_states.pop(message.chat.id, None)

# add_work_volume1_process function
def add_work_volume1_process(message):
    try:
        if message.text == 'Отмена ❌':
            bot.send_message(message.chat.id, 'Отмена', reply_markup=types.ReplyKeyboardRemove())
            start(message)
            other_function(message)
            return
        
        input_data = message.text
        parse_input_data1(input_data)

        for admin_id in admin_ids:
            try:
                text = f"""
                {input_data}
                
shu data qo'shildi kunlik ishlarga.
                """
                bot.send_message(admin_id, text)
                # conn.close()
            except Exception as e:
                print(e)
        bot.send_message(message.chat.id, 'Ввод данных завершен', reply_markup=types.ReplyKeyboardRemove())
        user_states.pop(message.chat.id, None)
        start(message)
        other_function(message)
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}")
        print(e)

# add_work_volume2_process function
def add_work_volume2_process(message):
    try:
        if message.text == 'Отмена ❌':
            bot.send_message(message.chat.id, 'Отмена', reply_markup=types.ReplyKeyboardRemove())
            start(message)
            other_function(message)
            return

        input_data = message.text
        add_daily_work(input_data)
        admin_data = get_admin_info_by_tg_id(message.chat.id)
        for admin_id in admin_ids:
            try:
                text = f"""
{admin_data['full_name']} tomonidan:


{input_data}

shu datalar qo'shildi kunlik ishlarga.
                """
                bot.send_message(admin_id, text)
                # conn.close()
            except Exception as e:
                print(e)
        bot.send_message(message.chat.id, 'Ввод данных завер', reply_markup=types.ReplyKeyboardRemove())

        user_states.pop(message.chat.id, None)
        start(message)
        # other_function(message)
        
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {e}")
        print(e)

# add_wood_process function
def add_wood_process(message):
    try:
        if message.text == 'Отмена ❌':
            bot.send_message(message.chat.id, 'Отмена', reply_markup=types.ReplyKeyboardRemove())
            start(message)
            other_function(message)
            return
        input_data = message.text
        admin_data = get_admin_info_by_tg_id(message.chat.id)
        add_wood_data(input_data, admin_data['id'])
        for admin_id in admin_ids:
            try:
                text = f"""
{admin_data['full_name']} tomonidan:
                {input_data}
                
shu data qo'shildi yog'ochlar ma'lumotlar bazasiga.
                """
                bot.send_message(admin_id, text)
                # conn.close()
            except Exception as e:
                print(e)
        bot.send_message(message.chat.id, 'Ввод данных завершен', reply_markup=types.ReplyKeyboardRemove())
        user_states.pop(message.chat.id, None)
        start(message)
        other_function(message)
    except Exception as e:
        print(e)

def get_wood_reports_process(message):
    try:
        if message.text == 'Отмена ❌':
            bot.send_message(message.chat.id, 'Отмена', reply_markup=types.ReplyKeyboardRemove())
            start(message)
            other_function(message)
            return
        input_data = message.text
        dates = input_data.strip().split('\n')
        start_date = dates[0]
        end_date = dates[1]
        get_reports_wood(start_date, end_date)
        with open(f'деревья_отчет_{start_date}_до_{end_date}.xlsx', 'rb') as f:
            bot.send_document(message.chat.id, f)
            bot.send_message(message.chat.id, f'Отчет отправлен {start_date} - {end_date}', reply_markup=types.ReplyKeyboardRemove())
        os.remove(f'деревья_отчет_{start_date}_до_{end_date}.xlsx')
        user_states.pop(message.chat.id, None)
    except Exception as e:
        print(e)

conn.close()
# bot run
bot.polling(none_stop=True)