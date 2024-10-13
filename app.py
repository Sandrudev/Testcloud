import streamlit as st
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest, SendMessageRequest
from telethon.errors import FloodWaitError, ChannelPrivateError
import asyncio

# Конфигурация Telegram API
API_ID = 22328650  # Ваш API ID
API_HASH = '20b45c386598fab8028b1d99b63aeeeb'  # Ваш API Hash
GROUP_ID = -1002394787009  # ID группы (отрицательный)

# Функция для отправки сообщений
async def send_message(username, message):
    async with TelegramClient('session_name', API_ID, API_HASH) as client:
        try:
            await client(SendMessageRequest(GROUP_ID, f"Пользователь {username} присоединился."))
            await client(SendMessageRequest(GROUP_ID, f"{username}: {message}"))
            return None  # Успешная отправка
        except Exception as e:
            return f"Ошибка при отправке сообщения: {e}"

# Функция для получения сообщений из группы
async def get_messages(username):
    async with TelegramClient('session_name', API_ID, API_HASH) as client:
        messages = []
        offset_id = 0
        limit = 100

        while True:
            try:
                history = await client(GetHistoryRequest(
                    peer=GROUP_ID,
                    offset_id=offset_id,
                    limit=limit,
                    hash=0
                ))

                if not history.messages:
                    break
                
                for message in history.messages:
                    if hasattr(message, 'message') and message.from_id == username:  # Фильтрация по ID пользователя
                        messages.append(message)
                
                offset_id = history.messages[-1].id

            except FloodWaitError as e:
                await asyncio.sleep(e.seconds)
            except ChannelPrivateError:
                return "Ошибка: У вас нет доступа к этой группе."
            except Exception as e:
                return f"Произошла ошибка: {e}"

        return messages

# Интерфейс Streamlit
st.title("Чат в Telegram")

# Запрос юзернейма у пользователя
if 'username' not in st.session_state:
    st.session_state.username = st.text_input("Введите ваш юзернейм:", "")
    
    if st.button("Подтвердить"):
        if st.session_state.username:
            st.session_state.username_id = st.session_state.username  # Сохранение никнейма в состоянии сессии
            st.success(f"Добро пожаловать, {st.session_state.username}!")
        else:
            st.error("Пожалуйста, введите юзернейм.")
else:
    # Проверка на наличие username_id перед обновлением сообщений
    if 'username_id' in st.session_state:
        if st.button("Обновить сообщения"):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            messages = loop.run_until_complete(get_messages(st.session_state.username_id))
            
            if isinstance(messages, str):
                st.error(messages)
            else:
                for message in messages:
                    if hasattr(message, 'message'):
                        sender_name = message.from_id  # Получение ID отправителя
                        st.write(f"{sender_name}: {message.message}")

        # Поле для ввода сообщения
        user_message = st.text_input("Ваше сообщение:")
        
        if st.button("Отправить"):
            if user_message:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(send_message(st.session_state.username_id, user_message))
                if result:
                    st.error(result)
                else:
                    st.success("Сообщение отправлено!")
            else:
                st.error("Введите сообщение перед отправкой.")
    else:
        st.error("Пожалуйста, подтвердите ваш никнейм.")
