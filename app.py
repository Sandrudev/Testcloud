import streamlit as st
from telethon import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest, InviteToChannelRequest
from telethon.tl.types import ChannelParticipantsSearch
import asyncio

api_id = '22328650'
api_hash = '20b45c386598fab8028b1d99b63aeeeb'
session_file = 'session_name'  # Убедитесь, что файл сессии находится в той же директории

client = TelegramClient(session_file, api_id, api_hash)

async def process_users(source_group, target_channel):
    await client.start()
    participants = []
    offset = 0
    limit = 100

    while True:
        chunk = await client(GetParticipantsRequest(
            source_group,
            ChannelParticipantsSearch(''),
            offset,
            limit,
            hash=0
        ))
        if not chunk.users:
            break
        participants.extend(chunk.users)
        offset += len(chunk.users)

    for user in participants:
        if user.username is None:
            continue
        
        try:
            user_to_add = await client.get_input_entity(user.username)
            await client(InviteToChannelRequest(target_channel, [user_to_add]))
            print(f"Добавлен {user.username}")
            await asyncio.sleep(20)  # Задержка во избежание превышения лимита
        except Exception as e:
            print(f"Пропущен {user.username}: {e}")

st.title("Пригласитель пользователей Telegram")

source_group_username = st.text_input("Введите юзернейм группы для парсинга:")
target_channel_username = st.text_input("Введите юзернейм канала для добавления:")

if st.button("Начать приглашение"):
    if source_group_username and target_channel_username:
        asyncio.run(process_users(source_group_username, target_channel_username))
        st.success("Процесс приглашения начат!")
    else:
        st.error("Пожалуйста, заполните оба поля.")
