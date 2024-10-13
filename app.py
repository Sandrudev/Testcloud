import streamlit as st
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.errors import FloodWaitError, ChannelPrivateError
import asyncio

# Конфигурация Telegram API
API_ID = 22328650  # Ваш API ID
API_HASH = '20b45c386598fab8028b1d99b63aeeeb'  # Ваш API Hash
GROUP_ID = -1002394787009  # ID группы (отрицательный)

# Функция для получения сообщений
async def get_messages(api_id, api_hash, group_id):
    client = TelegramClient('session_name', api_id, api_hash)
    await client.start()
    
    messages = []
    offset_id = 0
    limit = 100

    while True:
        try:
            history = await client(GetHistoryRequest(
                peer=group_id,
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
st.title("Получение сообщений из Telegram")

if st.button("Получить сообщения"):
    with st.spinner("Получение сообщений..."):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        messages = loop.run_until_complete(get_messages(API_ID, API_HASH, GROUP_ID))
        
        if isinstance(messages, str):
            st.error(messages)
        else:
            for message in messages:
                st.write(f"ID: {message.id}, Текст: {message.message if hasattr(message, 'message') else 'Нет текста.'}")
