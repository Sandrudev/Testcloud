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

async def login(phone_number, code=None, password=None, phone_code_hash=None):
    client = TelegramClient(session_name, api_id, api_hash)

    await client.connect()

    if not await client.is_user_authorized():
        if code is None:
            # Отправляем код на номер телефона
            try:
                sent = await client.send_code_request(phone_number)
                return client, sent.phone_code_hash, "Введите код подтверждения, который вы получили в Telegram."
            except Exception as e:
                raise RuntimeError(f"Ошибка при отправке кода: {e}")
        else:
            try:
                # Используем хэш кода для входа
                await client.sign_in(phone_number, code, phone_code_hash=phone_code_hash)
            except SessionPasswordNeededError:
                if password is None:
                    return client, None, "Введите пароль двухфакторной аутентификации."
                else:
                    await client.sign_in(password=password)
            except Exception as e:
                raise RuntimeError(f"Ошибка авторизации: {e}")
    return client, None, None

def main():
    st.title("Telegram Group Participant Fetcher")

    phone_number = st.text_input("Введите ваш номер телефона в формате +1234567890:")
    group_username = st.text_input("Введите имя группы Telegram:")
    
    # Храним состояния для кода, пароля и хэша
    code = st.session_state.get("code", "")
    password = st.session_state.get("password", "")
    phone_code_hash = st.session_state.get("phone_code_hash", "")

    if 'client' not in st.session_state:
        st.session_state.client = None

    if st.button("Получить участников"):
        if phone_number and group_username:
            try:
                if st.session_state.client is None:
                    # Выполняем логин
                    st.session_state.client, phone_code_hash, message = asyncio.run(login(phone_number))
                    st.session_state.phone_code_hash = phone_code_hash
                    if message:
                        st.session_state.message = message
                    else:
                        usernames = asyncio.run(fetch_participants(st.session_state.client, group_username))
                        st.write("Никнеймы участников:")
                        for username in usernames:
                            st.write(username)
                else:
                    usernames = asyncio.run(fetch_participants(st.session_state.client, group_username))
                    st.write("Никнеймы участников:")
                    for username in usernames:
                        st.write(username)

            except RuntimeError as e:
                st.error(f"Ошибка: {e}")

    if st.session_state.client:
        code = st.text_input("Введите код подтверждения:", value=code, max_chars=6)
        if code:
            st.session_state.code = code
            try:
                st.session_state.client, phone_code_hash, message = asyncio.run(login(phone_number, code, password, st.session_state.get("phone_code_hash", "")))
                st.session_state.phone_code_hash = phone_code_hash
                if message:
                    st.session_state.message = message
                else:
                    usernames = asyncio.run(fetch_participants(st.session_state.client, group_username))
                    st.write("Никнеймы участников:")
                    for username in usernames:
                        st.write(username)
            except RuntimeError as e:
                st.error(f"Ошибка: {e}")

        if "Введите пароль двухфакторной аутентификации." in st.session_state.get("message", ""):
            password = st.text_input("Введите пароль двухфакторной аутентификации:", type="password")
            if password:
                st.session_state.password = password
                try:
                    st.session_state.client, _, message = asyncio.run(login(phone_number, code, password, st.session_state.get("phone_code_hash", "")))
                    if message:
                        st.session_state.message = message
                    else:
                        usernames = asyncio.run(fetch_participants(st.session_state.client, group_username))
                        st.write("Никнеймы участников:")
                        for username in usernames:
                            st.write(username)
                except RuntimeError as e:
                    st.error(f"Ошибка: {e}")

    if 'message' in st.session_state:
        st.info(st.session_state.message)

if __name__ == "__main__":
    main()
