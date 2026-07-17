import streamlit as st
import requests
import time

# Настройка страницы
st.set_page_config(page_title="Потуйно-ай", page_icon="⚡", layout="centered")

st.markdown("<h1 style='text-align: center;'>⚡ Потуйно-ай</h1>", unsafe_allow_html=True)

# История сообщений
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Привет! Я готов к работе. Задавай вопрос!"}]

# Вывод сообщений
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Ввод пользователя
if prompt := st.chat_input("Напиши что-нибудь..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        API_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"
        headers = {"Authorization": "Bearer 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"}
        
        try:
            response = requests.post(API_URL, headers=headers, json={"inputs": prompt}, timeout=15)
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    answer = result[0].get('generated_text', '...')
                else:
                    answer = str(result)
            else:
                answer = f"Ошибка сервера: {response.status_code}"
        except Exception as e:
            answer = f"Ошибка: {e}"
        
        message_placeholder.markdown(answer)
    
    st.session_state.messages.append({"role": "assistant", "content": answer})
