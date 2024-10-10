import os
import random
import string
import sqlite3
import asyncio
from telethon import TelegramClient
import streamlit as st

# Telegram API configuration
api_id = '22328650'
api_hash = '20b45c386598fab8028b1d99b63aeeeb'
GROUP_ID = '4584864883'  # Your Telegram group ID
DB_FILE = 'tokens.db'

# Initialize the Telegram client with session file
client = TelegramClient('session_name', api_id, api_hash)

# Database setup
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        token TEXT UNIQUE
    )
''')
conn.commit()

def generate_token(length=12):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

async def upload_file(file, user_token):
    await client.start()
    await client.send_file(GROUP_ID, file, caption=user_token)

async def get_files_by_token(token):
    await client.start()
    messages = await client.get_messages(GROUP_ID)
    files = [msg for msg in messages if msg.caption and token in msg.caption]
    return files

def check_token(token):
    c.execute('SELECT token FROM tokens WHERE token = ?', (token,))
    return c.fetchone() is not None

def save_token(token):
    c.execute('INSERT INTO tokens (token) VALUES (?)', (token,))
    conn.commit()

def main():
    st.title("Streamlit App with Telethon Integration")

    if 'admin_token' in st.session_state:
        st.subheader("Control Panel")
        uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

        if uploaded_file:
            # Save the uploaded file temporarily
            with open(uploaded_file.name, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Upload the file using the authenticated user's account
            asyncio.run(upload_file(uploaded_file.name, st.session_state['admin_token']))
            st.success("Image uploaded successfully!")

            # Clean up the temporary file after uploading
            os.remove(uploaded_file.name)

        # Display files published under the user's token
        files = asyncio.run(get_files_by_token(st.session_state['admin_token']))
        if files:
            st.subheader("Published Files")
            for file in files:
                st.write(f"File: {file.document.file_name} - [Download](https://t.me/{GROUP_ID}/{file.id})")

        if st.button("Logout"):
            del st.session_state['admin_token']
            st.experimental_rerun()

    else:
        st.subheader("Login")
        login_token = st.text_input("Enter your token")

        if st.button("Login"):
            if check_token(login_token):
                st.session_state['admin_token'] = login_token
                st.success("Login successful!")
                st.experimental_rerun()

        st.subheader("Register")
        if st.button("Register"):
            token = generate_token()
            save_token(token)
            st.success(f"Registration successful! Your token: {token}")

if __name__ == "__main__":
    main()
