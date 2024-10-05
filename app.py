import streamlit as st
import asyncio
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

# Встроенные данные API
API_ID = '22328650'
API_HASH = '20b45c386598fab8028b1d99b63aeeeb'
SESSION_NAME = 'session_name'

async def fetch_participants(client, group_username):
    participants = []
    offset = 0
    limit = 100

    while True:
        chunk = await client(GetParticipantsRequest(
            group_username,
            ChannelParticipantsSearch(''),
            offset,
            limit,
            hash=0
        ))
        if not chunk.users:
            break
        participants.extend(chunk.users)
        offset += len(chunk.users)

    return participants

async def start_client(phone_number):
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.start(phone=phone_number)
    return client

def main():
    st.title("Telegram Group Participants Fetcher")

    # Ввод номера телефона
    if 'client' not in st.session_state:
        st.session_state.client = None  # Инициализация клиента

    phone_number = st.text_input("Введите номер телефона (в формате +1234567890)")

    if st.button("Авторизация"):
        if phone_number:
            try:
                # Запускаем клиент в асинхронном режиме
                client = asyncio.run(start_client(phone_number))
                st.session_state.client = client  # Сохраняем клиент в состоянии

                # Проверяем, требуется ли код подтверждения
                if not client.is_user_authorized():
                    st.session_state.auth_step = "code_needed"  # Устанавливаем шаг авторизации
                    st.success("Код отправлен на ваш номер. Пожалуйста, введите его ниже.")
                else:
                    st.success("Вы уже авторизованы!")
            except Exception as e:
                st.error(f"Произошла ошибка: {e}")
        else:
            st.warning("Пожалуйста, введите номер телефона.")

    # Если требуется ввод кода подтверждения
    if 'auth_step' in st.session_state and st.session_state.auth_step == "code_needed":
        code = st.text_input("Введите код подтверждения", type="password")
        if st.button("Подтвердить код"):
            try:
                asyncio.run(st.session_state.client.sign_in(phone=phone_number, code=code))
                st.success("Код подтвержден успешно!")

                # Запрашиваем пароль, если это необходимо
                if isinstance(st.session_state.client.session, SessionPasswordNeededError):
                    password = st.text_input("Введите пароль", type="password")
                    if st.button("Подтвердить пароль"):
                        asyncio.run(st.session_state.client.sign_in(password=password))
                        st.success("Пароль подтвержден!")

                # Получаем участников группы
                group_username = st.text_input("Введите имя группы", value='maskmedic')
                if st.button("Получить участников"):
                    participants = asyncio.run(fetch_participants(st.session_state.client, group_username))
                    for user in participants:
                        st.write(f"ID: {user.id}, Username: {user.username or 'Нет имени пользователя'}")
            except Exception as e:
                st.error(f"Ошибка при подтверждении кода: {e}")

if __name__ == "__main__":
    main()
