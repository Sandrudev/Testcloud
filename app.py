import streamlit as st
import asyncio
from telethon import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

api_id = '22328650'
api_hash = '20b45c386598fab8028b1d99b63aeeeb'
session_name = 'session_name'

client = TelegramClient(session_name, api_id, api_hash)

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
    
    return [user.username for user in participants]

def main():
    st.title("Telegram Group Participant Fetcher")
    group_username = st.text_input("Введите имя группы Telegram:")

    if st.button("Получить участников"):
        if group_username:
            # Создаем новый цикл событий и запускаем корутину
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            usernames = loop.run_until_complete(fetch_participants(group_username))
            st.write("Никнеймы участников:")
            for username in usernames:
                st.write(username)
        else:
            st.error("Пожалуйста, введите корректное имя группы.")

if __name__ == "__main__":
    main()
    if st.button("Fetch Participants"):
        if group_username:
            # Create a new event loop and run the fetch_participants coroutine
            usernames = asyncio.run(fetch_participants(group_username))
            st.write("Usernames of participants:")
            for username in usernames:
                st.write(username)
        else:
            st.error("Please enter a valid username.")

if __name__ == "__main__":
    main()
