import streamlit as st
import requests

# --- Настройки ---
API_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"
HF_TOKEN = "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"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

ASCII_CAT = """
 /\\_/\\
( o.o )  <-- Это я, твой ИИ-кот!
 > ^ <
/     \\
|  |  |
|  |  |
"""

st.set_page_config(page_title="Потуйно-ай", page_icon="🐱")
st.title("🐱 Потуйно-ай")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": f"Привет! Я Потуйно-ай.\n\n{ASCII_CAT}\n\nЧем могу помочь?",
        }
    ]

# Вывод истории чата
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


def query_hf(prompt: str) -> str:
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 512,
            "temperature": 0.7,
            "return_full_text": False,
        },
    }

    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=15)
    except requests.exceptions.Timeout:
        return "Ошибка: превышено время ожидания ответа (таймаут 15 секунд)."
    except requests.exceptions.ConnectionError:
        return "Ошибка: не удалось подключиться к серверу Hugging Face."
    except requests.exceptions.RequestException as e:
        return f"Ошибка запроса: {e}"

    if response.status_code == 200:
        try:
            data = response.json()
            if isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
                return data[0]["generated_text"].strip()
            elif isinstance(data, dict) and "error" in data:
                return f"Ошибка модели: {data['error']}"
            else:
                return str(data)
        except ValueError:
            return "Ошибка: не удалось разобрать ответ сервера (некорректный JSON)."
    elif response.status_code == 401:
        return "Ошибка 401: неверный или недействительный токен Hugging Face."
    elif response.status_code == 503:
        return "Ошибка 503: модель загружается или сервер временно недоступен. Попробуйте позже."
    elif response.status_code == 429:
        return "Ошибка 429: превышен лимит запросов. Подождите немного."
    else:
        return f"Ошибка {response.status_code}: {response.text}"


user_input = st.chat_input("Напишите сообщение...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Печатает..."):
            reply = query_hf(user_input)
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
