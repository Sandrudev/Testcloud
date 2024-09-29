import random
import string
import sqlite3
import os
import telebot
import streamlit as st

# Settings for your app
TELEGRAM_BOT_TOKEN = '5660590671:AAHboouGd0fFTpdjJSZpTfrtLyWsK1GM2JE'
CHANNEL_ID = '-1002173127202'  # Your Telegram channel ID
DATABASE = 'app.db'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Create Telegram bot instance
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Initialize the SQLite3 database
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT UNIQUE NOT NULL
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            filetype TEXT NOT NULL,
            token TEXT NOT NULL,
            FOREIGN KEY(token) REFERENCES tokens(token)
        )
        ''')
        conn.commit()

init_db()

# Function to generate random tokens
def generate_token(length=12):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Get files for a specific token from the database
def get_files_from_folder(token):
    files = []
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT filename, filetype FROM files WHERE token = ?', (token,))
        rows = cursor.fetchall()
        for row in rows:
            filename, file_type = row
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            files.append({'name': filename, 'url': file_path, 'type': file_type})
    return files

# Function to upload file
def upload_file(file, user_token):
    filename = file.name
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    with open(file_path, 'wb') as f:
        f.write(file.getbuffer())

    file_type = 'image' if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')) else 'video'
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO files (filename, filetype, token) VALUES (?, ?, ?)', 
                       (filename, file_type, user_token))
        conn.commit()

    with open(file_path, 'rb') as f:
        try:
            bot.send_document(chat_id=CHANNEL_ID, document=f, caption=user_token)
        except telebot.apihelper.ApiException as e:
            st.error(f"Error sending file to Telegram: {e}")

# Streamlit UI
def main():
    st.title("Streamlit App with Telegram Integration")

    # Login section
    if 'admin_token' not in st.session_state:
        st.subheader("Login")
        login_token = st.text_input("Enter your token")

        if st.button("Login"):
            with sqlite3.connect(DATABASE) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT token FROM tokens WHERE token = ?', (login_token,))
                result = cursor.fetchone()

                if result:
                    st.session_state['admin_token'] = login_token
                    st.success("Login successful!")
                    st.experimental_rerun()  # Reload the app to reflect logged-in state
                else:
                    st.error("Invalid token! Please check and try again.")

        st.subheader("Or Register")
        admin_password = st.text_input("Enter admin password to register", type="password")

        if st.button("Register"):
            if admin_password == 'adminmorshen1995':
                token = generate_token()
                with sqlite3.connect(DATABASE) as conn:
                    cursor = conn.cursor()
                    cursor.execute('INSERT INTO tokens (token) VALUES (?)', (token,))
                    conn.commit()
                st.session_state['admin_token'] = token
                st.success(f"Registration successful! Your token is: {token}")
            else:
                st.error("Incorrect admin password!")

    # After login, show the dashboard
    else:
        st.subheader("Dashboard")

        # Show file upload option
        uploaded_file = st.file_uploader("Choose a file to upload")
        if uploaded_file is not None:
            upload_file(uploaded_file, st.session_state['admin_token'])
            st.success("File uploaded successfully!")

        # Fetch and display uploaded files
        user_files = get_files_from_folder(st.session_state['admin_token'])
        if user_files:
            st.subheader("Uploaded Files")
            for file in user_files:
                if file['type'] == 'image':
                    st.image(file['url'], caption=file['name'])
                elif file['type'] == 'video':
                    st.video(file['url'])

        # Option to log out
        if st.button("Log Out"):
            del st.session_state['admin_token']
            st.experimental_rerun()

if __name__ == "__main__":
    main()
