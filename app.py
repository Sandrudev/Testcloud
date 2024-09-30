import random
import string
import os
import telebot
import streamlit as st

# Settings for your app
TELEGRAM_BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
CHANNEL_ID = '-1002173127202'  # Your Telegram channel ID
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Create Telegram bot instance
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Function to generate random tokens
def generate_token(length=12):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Function to upload file
def upload_file(file, user_token):
    filename = file.name
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    with open(file_path, 'wb') as f:
        f.write(file.getbuffer())

    file_type = 'image' if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')) else 'video'
    
    # Send file to Telegram channel with token as caption
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
            # Check if the token exists in the Telegram channel messages
            messages = bot.get_chat_history(CHANNEL_ID)
            if any(login_token in msg.text for msg in messages):
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
                # Send the generated token to the Telegram channel
                bot.send_message(chat_id=CHANNEL_ID, text=f"New Token: {token}")
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

        # Display a message indicating that files can be uploaded under this token.
        st.info(f"Files uploaded under your token: {st.session_state['admin_token']}")

        # Option to log out
        if st.button("Log Out"):
            del st.session_state['admin_token']
            st.experimental_rerun()

if __name__ == "__main__":
    main()
