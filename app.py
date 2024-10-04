import random
import string
import os
import telebot
import streamlit as st
import sqlite3

# Настройки вашего приложения
TELEGRAM_BOT_TOKEN = '5660590671:AAHboouGd0fFTpdjJSZpTfrtLyWsK1GM2JE'  # Ваш токен бота
CHANNEL_ID = '-1002173127202'  # Ваш ID канала Telegram
DB_FILE = 'tokens_files.db'  # Имя файла базы данных

# Создание экземпляра бота Telegram
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Создание подключения к базе данных
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
c = conn.cursor()

# Создание таблицы для токенов
c.execute('''
    CREATE TABLE IF NOT EXISTS tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        token TEXT UNIQUE
    )
''')
conn.commit()

# Функция для генерации случайных токенов
def generate_token(length=12):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Функция для отправки файла в канал Telegram
def upload_file(file, user_token):
    # Отправляем файл в канал Telegram с токеном в качестве подписи
    try:
        bot.send_document(chat_id=CHANNEL_ID, document=file, caption=user_token)
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

# Функция для получения файлов из Telegram-канала
def get_files_by_token(token):
    updates = bot.get_updates()
    files = []
    for update in updates:
        if update.message and update.message.chat.id == int(CHANNEL_ID):
            if update.message.caption and token in update.message.caption:
                if update.message.document:
                    files.append({
                        'filename': update.message.document.file_name,
                        'file_id': update.message.document.file_id,
                        'file_size': update.message.document.file_size,
                    })
    return files

# Функция для скачивания файла по file_id
def download_file(file_id):
    file_info = bot.get_file(file_id)
    file_path = f"downloads/{file_info.file_path.split('/')[-1]}"
    downloaded_file = bot.download_file(file_info.file_path)

    # Сохранить файл на сервере (в папку downloads)
    os.makedirs('downloads', exist_ok=True)
    with open(file_path, 'wb') as f:
        f.write(downloaded_file)

    return file_path

# Основной интерфейс Streamlit
def main():
    st.title("Приложение Streamlit с интеграцией Telegram")

    # Проверка на авторизацию
    if 'admin_token' in st.session_state:
        # После входа показываем панель управления
        st.subheader("Панель управления")

        # Опция загрузки файла
        uploaded_file = st.file_uploader("Выберите файл для загрузки", type=["png", "jpg", "jpeg", "gif", "mp4"])
        if uploaded_file is not None:
            upload_file(uploaded_file, st.session_state['admin_token'])
            st.success("Файл успешно загружен!")

        # Отображаем загруженные файлы по токену
        files = get_files_by_token(st.session_state['admin_token'])
        if files:
            st.subheader("Загруженные файлы")
            for file in files:
                if st.button(f"Скачать {file['filename']}"):
                    file_path = download_file(file['file_id'])
                    st.success(f"Файл {file['filename']} успешно скачан в {file_path}")

        # Опция выхода из системы
        if st.button("Выйти"):
            del st.session_state['admin_token']
            st.experimental_rerun()  # Перезагрузить страницу после выхода

    else:
        # Раздел для входа
        st.subheader("Вход")
        login_token = st.text_input("Введите ваш токен")

        if st.button("Войти"):
            if check_token(login_token):
                st.session_state['admin_token'] = login_token
                st.success("Вход выполнен успешно!")
                st.experimental_rerun()  # Перезагрузить страницу после входа

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

if __name__ == "__main__":
    main()
