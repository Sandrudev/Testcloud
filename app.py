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
    phone_number = st.text_input("Введите номер телефона (в формате +1234567890)")

    group_username = st.text_input("Введите имя группы", value='maskmedic')

    if st.button("Получить участников"):
        if phone_number:
            with st.spinner("Авторизация..."):
                try:
                    client = asyncio.run(start_client(phone_number))
                    
                    # Запрашиваем код подтверждения, если это необходимо
                    if client.is_user_authorized() == False:
                        code = st.text_input("Введите код подтверждения", type="password")
                        if code:
                            await client.sign_in(phone=phone_number, code=code)

                    # Запрашиваем пароль, если это необходимо
                    if isinstance(client.session, SessionPasswordNeededError):
                        password = st.text_input("Введите пароль", type="password")
                        if password:
                            await client.sign_in(password=password)

                    # Получаем участников группы
                    participants = asyncio.run(fetch_participants(client, group_username))
                    for user in participants:
                        st.write(f"ID: {user.id}, Username: {user.username or 'Нет имени пользователя'}")
                except Exception as e:
                    st.error(f"Произошла ошибка: {e}")
        else:
            st.warning("Пожалуйста, введите номер телефона.")

if __name__ == "__main__":
    main()
