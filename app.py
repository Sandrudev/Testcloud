import streamlit as st
from telethon import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest, InviteToChannelRequest
from telethon.tl.types import ChannelParticipantsSearch
import asyncio

api_id = '22328650'
api_hash = '20b45c386598fab8028b1d99b63aeeeb'
session_file = 'session_name'  # Убедитесь, что файл сессии находится в той же директории

async def process_users(source_group, target_channel):
    async with TelegramClient(session_file, api_id, api_hash) as client:
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
                st.write(f"Добавлен {user.username}")  # Выводим информацию о добавлении
                await asyncio.sleep(20)  # Задержка во избежание превышения лимита
            except Exception as e:
                st.write(f"Пропущен {user.username}: {e}")  # Выводим информацию об ошибках

def main():
    st.title("Пригласитель пользователей Telegram")

    source_group_username = st.text_input("Введите юзернейм группы для парсинга:")
    target_channel_username = st.text_input("Введите юзернейм канала для добавления:")

    if st.button("Начать приглашение"):
        if source_group_username and target_channel_username:
            try:
                asyncio.run(process_users(source_group_username, target_channel_username))
                st.success("Процесс приглашения завершен!")
            except Exception as e:
                st.error(f"Ошибка: {e}")
        else:
            st.error("Пожалуйста, заполните оба поля.")

if __name__ == "__main__":
    main()
