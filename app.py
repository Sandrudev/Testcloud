import streamlit as st
import asyncio
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

api_id = '22328650'
api_hash = '20b45c386598fab8028b1d99b63aeeeb'
session_name = 'session_name'

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

    return [user.username for user in participants]

async def login(phone_number):
    client = TelegramClient(session_name, api_id, api_hash)

    await client.connect()

    if not await client.is_user_authorized():
        try:
            await client.send_code_request(phone_number)
        except Exception as e:
            raise RuntimeError(f"Ошибка при отправке кода: {e}")

        # Streamlit будет запрашивать код подтверждения и пароль, если потребуется
        code = st.text_input("Введите код подтверждения, который вы получили в Telegram:", "")
        if code:
            try:
                await client.sign_in(phone_number, code)
            except SessionPasswordNeededError:
                password = st.text_input("Введите пароль двухфакторной аутентификации:", type="password")
                if password:
                    await client.sign_in(password=password)
                else:
                    raise RuntimeError("Необходимо ввести пароль двухфакторной аутентификации.")
            except Exception as e:
                raise RuntimeError(f"Ошибка авторизации: {e}")
    return client

def main():
    st.title("Telegram Group Participant Fetcher")

    phone_number = st.text_input("Введите ваш номер телефона в формате +1234567890:")
    group_username = st.text_input("Введите имя группы Telegram:")

    if st.button("Получить участников"):
        if phone_number and group_username:
            try:
                # Используем asyncio.run для корректного запуска корутин
                client = asyncio.run(login(phone_number))
                usernames = asyncio.run(fetch_participants(client, group_username))
                st.write("Никнеймы участников:")
                for username in usernames:
                    st.write(username)
                asyncio.run(client.disconnect())
            except Exception as e:
                st.error(f"Ошибка: {e}")
        else:
            st.error("Пожалуйста, введите номер телефона и корректное имя группы.")

if __name__ == "__main__":
    main()
