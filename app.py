import streamlit as st
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest, SendMessageRequest
from telethon.errors import FloodWaitError, ChannelPrivateError
import asyncio

# Конфигурация Telegram API
API_ID = 22328650  # Ваш API ID
API_HASH = '20b45c386598fab8028b1d99b63aeeeb'  # Ваш API Hash
GROUP_ID = -1002394787009  # ID группы (отрицательный)

# Инициализация клиента Telegram
client = TelegramClient('session_name', API_ID, API_HASH)

# Функция для отправки сообщений
async def send_message(username, message):
    await client.start()
    try:
        await client(SendMessageRequest(GROUP_ID, f"{username}: {message}"))
    except Exception as e:
        return f"Ошибка при отправке сообщения: {e}"

# Функция для получения сообщений из группы
async def get_messages():
    await client.start()
    messages = []
    offset_id = 0
    limit = 100

    while True:
        try:
            history = await client(GetHistoryRequest(
                peer=GROUP_ID,
                offset_id=offset_id,
                limit=limit,
                offset_date=None,
                add_offset=0,
                max_id=0,
                min_id=0,
                hash=0
            ))

            if not history.messages:
                break
            
            messages.extend(history.messages)
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
            st.success(f"Добро пожаловать, {st.session_state.username}!")
        else:
            st.error("Пожалуйста, введите юзернейм.")
else:
    # Отображение сообщений из группы
    messages = asyncio.run(get_messages())
    
    if isinstance(messages, str):
        st.error(messages)
    else:
        for message in messages:
            if hasattr(message, 'message'):
                st.write(f"{message.sender_id}: {message.message}")

    # Поле для ввода сообщения
    user_message = st.text_input("Ваше сообщение:")
    
    if st.button("Отправить"):
        if user_message:
            asyncio.run(send_message(st.session_state.username, user_message))
            st.success("Сообщение отправлено!")
        else:
            st.error("Введите сообщение перед отправкой.")
