import streamlit as st
import asyncio
from telethon import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

# Ввод данных API
api_id = st.text_input("Введите API ID", value='22328650')
api_hash = st.text_input("Введите API Hash", value='20b45c386598fab8028b1d99b63aeeeb')
group_username = st.text_input("Введите имя группы", value='maskmedic')

# Убедитесь, что файл сессии сохраняется в безопасном месте
session_name = 'session_name'  # Имя файла сессии

async def fetch_participants():
    async with TelegramClient(session_name, api_id, api_hash) as client:
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
    if st.button("Получить участников"):
        with st.spinner("Загрузка участников..."):
            try:
                participants = asyncio.run(fetch_participants())
                for user in participants:
                    st.write(f"ID: {user.id}, Username: {user.username or 'Нет имени пользователя'}")
            except Exception as e:
                st.error(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    main()
