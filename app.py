import streamlit as st
import asyncio
from telethon import TelegramClient

# Введите ваши api_id и api_hash
api_id = '22328650'
api_hash = '20b45c386598fab8028b1d99b63aeeeb'

client = TelegramClient('session_name', api_id, api_hash)

async def main(phone, code, password):
    await client.start(phone=phone)
    
    if code:
        await client.sign_in(phone, code, password=password)
    
    st.success("Успешно авторизован!")

    # Выбор чата для парсинга
    chat = st.text_input("Введите имя чата или его ID:")
    
    if st.button("Запустить парсер"):
        if chat:
            messages = []
            async for message in client.iter_messages(chat):
                messages.append(f"{message.sender_id}: {message.text}")
            st.write("\n".join(messages))
        else:
            st.error("Пожалуйста, введите имя чата.")

if __name__ == "__main__":
    if "loop" not in st.session_state:
        st.session_state.loop = asyncio.new_event_loop()
    
    phone = st.text_input("Введите номер телефона:")
    code = st.text_input("Введите код подтверждения:")
    password = st.text_input("Введите пароль (если есть):", type="password")

    if st.button("Авторизоваться"):
        asyncio.set_event_loop(st.session_state.loop)
        try:
            st.session_state.loop.run_until_complete(main(phone, code, password))
        except Exception as e:
            st.error(f"Произошла ошибка: {e}")
