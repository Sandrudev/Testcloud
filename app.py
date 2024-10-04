import random
import string
import os
import telebot
import streamlit as st
import sqlite3

# Настройки вашего приложения
TELEGRAM_BOT_TOKEN = '5660590671:AAHboouGd0fFTpdjJSZpTfrtLyWsK1GM2JE'  # Ваш токен бота
CHANNEL_ID = '-1002173127202'  # Ваш ID канала Telegram
UPLOAD_FOLDER = 'uploads'
DB_FILE = 'tokens_files.db'  # Имя файла базы данных

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Создаем экземпляр бота Telegram
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Создание подключения к базе данных
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
c = conn.cursor()

# Создание таблицы для токенов и файлов
c.execute('''
    CREATE TABLE IF NOT EXISTS tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        token TEXT UNIQUE
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        token TEXT,
        filename TEXT,
        filetype TEXT,
        filepath TEXT,
        FOREIGN KEY(token) REFERENCES tokens(token)
    )
''')
conn.commit()

# Функция для генерации случайных токенов
def generate_token(length=12):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Функция для загрузки файла
def upload_file(file, user_token):
    filename = file.name
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    with open(file_path, 'wb') as f:
        f.write(file.getbuffer())

    file_type = 'image' if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')) else 'video'
    
    # Отправляем файл в канал Telegram с токеном в качестве подписи
    try:
        with open(file_path, 'rb') as f:
            bot.send_document(chat_id=CHANNEL_ID, document=f, caption=user_token)
        
        # Сохраняем файл в базу данных
        c.execute('''
            INSERT INTO files (token, filename, filetype, filepath) VALUES (?, ?, ?, ?)
        ''', (user_token, filename, file_type, file_path))
        conn.commit()
        
    except telebot.apihelper.ApiTelegramException as e:
        st.error(f"Ошибка при отправке файла в Telegram: {e}")
        print(f"Ошибка при отправке файла: {e}")  # Выводим подробную ошибку для отладки

# Функция для проверки токена в базе данных
def check_token(token):
    c.execute('SELECT token FROM tokens WHERE token = ?', (token,))
    return c.fetchone() is not None

# Функция для сохранения токена в базе данных
def save_token(token):
    c.execute('INSERT INTO tokens (token) VALUES (?)', (token,))
    conn.commit()

# Функция для получения файлов по токену
def get_files_by_token(token):
    c.execute('SELECT filename, filepath, filetype FROM files WHERE token = ?', (token,))
    return c.fetchall()

# Основной интерфейс Streamlit
def main():
    st.title("Приложение Streamlit с интеграцией Telegram")

    # Раздел для входа
    if 'admin_token' not in st.session_state:
        st.subheader("Вход")
        login_token = st.text_input("Введите ваш токен")

        if st.button("Войти"):
            if check_token(login_token):
                st.session_state['admin_token'] = login_token
                st.success("Вход выполнен успешно!")
                # Перезагружаем приложение для обновления состояния
                st.session_state.clear()  # Очистить сессию и обновить страницу

        st.subheader("Или зарегистрируйтесь")
        admin_password = st.text_input("Введите админский пароль для регистрации", type="password")

        if st.button("Зарегистрироваться"):
            if admin_password == 'adminmorshen1995':
                token = generate_token()
                try:
                    bot.send_message(chat_id=CHANNEL_ID, text=f"Новый токен: {token}")
                    save_token(token)  # Сохраняем токен в базу данных
                    st.session_state['admin_token'] = token
                    st.success(f"Регистрация прошла успешно! Ваш токен: {token}")
                except telebot.apihelper.ApiTelegramException as e:
                    st.error(f"Ошибка при отправке сообщения в Telegram: {e}")
                    print(f"Ошибка при отправке сообщения: {e}")  # Выводим подробную ошибку для отладки
            else:
                st.error("Неверный админский пароль!")

    # После входа показываем панель управления
    else:
        st.subheader("Панель управления")

        # Опция загрузки файла
        uploaded_file = st.file_uploader("Выберите файл для загрузки")
        if uploaded_file is not None:
            upload_file(uploaded_file, st.session_state['admin_token'])
            st.success("Файл успешно загружен!")

        # Отображаем загруженные файлы по токену
        files = get_files_by_token(st.session_state['admin_token'])
        if files:
            st.subheader("Загруженные файлы")
            for filename, filepath, filetype in files:
                if filetype == 'image':
                    st.image(filepath, caption=filename)
                elif filetype == 'video':
                    st.video(filepath)

        # Опция выхода из системы
        if st.button("Выйти"):
            del st.session_state['admin_token']
            st.experimental_rerun()

if __name__ == "__main__":
    main()
