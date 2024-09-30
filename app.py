import random
import string
import os
import telebot
import streamlit as st

# Настройки вашего приложения
TELEGRAM_BOT_TOKEN = '5660590671:AAHboouGd0fFTpdjJSZpTfrtLyWsK1GM2JE'  # Ваш токен бота
CHANNEL_ID = '-1002173127202'  # Ваш ID канала Telegram
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Создаем экземпляр бота Telegram
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Список для хранения токенов
tokens_list = []

# Функция для генерации случайных токенов
def generate_token(length=12):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Список для хранения загруженных файлов
uploaded_files_dict = {}

# Функция для загрузки файла
def upload_file(file, user_token):
    filename = file.name
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    with open(file_path, 'wb') as f:
        f.write(file.getbuffer())

    file_type = 'image' if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')) else 'video'
    
    # Отправляем файл в канал Telegram с токеном в качестве подписи
    with open(file_path, 'rb') as f:
        try:
            bot.send_document(chat_id=CHANNEL_ID, document=f, caption=user_token)
            # Добавляем файл в словарь загруженных по токену
            if user_token not in uploaded_files_dict:
                uploaded_files_dict[user_token] = []
            uploaded_files_dict[user_token].append({'name': filename, 'url': file_path, 'type': file_type})
        except telebot.apihelper.ApiException as e:
            st.error(f"Ошибка при отправке файла в Telegram: {e}")

# Проверка наличия токена в списке токенов
def check_token(token):
    return token in tokens_list

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
                st.experimental_rerun()  # Перезагружаем приложение для обновления состояния
            else:
                st.error("Неверный токен! Пожалуйста, проверьте и попробуйте снова.")

        st.subheader("Или зарегистрируйтесь")
        admin_password = st.text_input("Введите админский пароль для регистрации", type="password")

        if st.button("Зарегистрироваться"):
            if admin_password == 'adminmorshen1995':
                token = generate_token()
                # Отправляем сгенерированный токен в канал Telegram и добавляем его в список токенов
                bot.send_message(chat_id=CHANNEL_ID, text=f"Новый токен: {token}")
                tokens_list.append(token)  # Сохраняем токен в списке
                st.session_state['admin_token'] = token
                st.success(f"Регистрация прошла успешно! Ваш токен: {token}")
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
        user_token = st.session_state['admin_token']
        if user_token in uploaded_files_dict:
            st.subheader("Загруженные файлы")
            for file in uploaded_files_dict[user_token]:
                if file['type'] == 'image':
                    st.image(file['url'], caption=file['name'])
                elif file['type'] == 'video':
                    st.video(file['url'])

        # Опция выхода из системы
        if st.button("Выйти"):
            del st.session_state['admin_token']
            st.experimental_rerun()

if __name__ == "__main__":
    main()
