import streamlit as st
import asyncio
from telethon import TelegramClient
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

def main():
    st.title("Telegram Group Participants Fetcher")

    # Ввод номера телефона
    phone_number = st.text_input("Введите номер телефона (в формате +1234567890)")

    # Ввод кода подтверждения
    code = st.text_input("Введите код подтверждения", type="password")

    group_username = st.text_input("Введите имя группы", value='maskmedic')

    if st.button("Получить участников"):
        if phone_number and code:
            with st.spinner("Загрузка участников..."):
                try:
                    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

                    # Запуск клиента и авторизация
                    async def start_client():
                        await client.start(phone=phone_number, code=code)
                        return await fetch_participants(client, group_username)

                    participants = asyncio.run(start_client())
                    for user in participants:
                        st.write(f"ID: {user.id}, Username: {user.username or 'Нет имени пользователя'}")
                except Exception as e:
                    st.error(f"Произошла ошибка: {e}")
        else:
            st.warning("Пожалуйста, введите номер телефона и код подтверждения.")

if __name__ == "__main__":
    main()
