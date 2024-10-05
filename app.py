import streamlit as st
from telethon import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
import asyncio

api_id = '22328650'
api_hash = '20b45c386598fab8028b1d99b63aeeeb'
client = TelegramClient('session_name', api_id, api_hash)

async def fetch_participants(group_username):
    await client.start()
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

st.title("Получение участников группы Telegram")
group_username = st.text_input("Введите имя группы (username):")
if st.button("Получить участников"):
    if group_username:
        participants = asyncio.run(fetch_participants(group_username))
        for user in participants:
            st.write(f"ID: {user.id}, Username: {user.username}")
    else:
        st.error("Пожалуйста, введите корректное имя группы.")
