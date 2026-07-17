import streamlit as st
import requests
import time

# Настройка страницы чата
st.set_page_config(page_title="Потуйно-ай", page_icon="⚡", layout="centered")

st.markdown("<h1 style='text-align: center;'>⚡ Потуйно-ай</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Твой личный искусственный интеллект</p>", unsafe_allow_html=True)

# Инициализируем историю сообщений, чтобы чат помнил контекст
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Привет! Я Потуйно-ай. Готов к работе! Задавай любой вопрос."}
    ]

# Отображаем переписку
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Поле для ввода сообщения
if prompt := st.chat_input("Напиши что-нибудь..."):
    # Показываем сообщение пользователя
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Запрос к нейросети Meta Llama 3 через бесплатный сервер
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("*Потужно думает...*")
        
        # Используем современную открытую модель Llama-3
        API_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"
        
        # Твой рабочий токен
        headers = {"Authorization": "Bearer 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"}
        
        # Формируем промт так, чтобы ИИ понимал, что это чат
        formatted_prompt = f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
        
        try:
            response = requests.post(API_URL, headers=headers, json={
                "inputs": formatted_prompt,
                "parameters": {"max_new_tokens": 512, "temperature": 0.7}
            }, timeout=15) # Добавили ограничение по времени ожидания
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    full_response = result[0].get('generated_text', '')
                    # Чистим ответ от технических тегов модели
                    if formatted_prompt in full_response:
                        full_response = full_response.replace(formatted_prompt, "")
                    full_response = full_response.split("<|eot_id|>")[0].strip()
                else:
                    full_response = f"Сервер вернул странный ответ: {result}"
            
            elif response.status_code == 503:
                full_response = "Модель сейчас загружается на сервере Hugging Face. Подожди секунд 20-30 и повтори запрос!"
            elif response.status_code == 401:
                full_response = "Ошибка авторизации (401). Похоже, Hugging Face заблокировал этот токен, так как он попал в открытый доступ."
            else:
                full_response = f"Ошибка сервера ИИ. Код: {response.status_code}. Текст: {response.text}"
                
        except Exception as e:
            full_response = f"Не удалось связаться с сервером ИИ. Ошибка подключения: {e}"

        # Эффект печатающегося текста
        animated_text = ""
        for char in full_response:
            animated_text += char
            message_placeholder.markdown(animated_text + "▌")
            time.sleep(0.01)
        message_placeholder.markdown(full_response)
    
    # Сохраняем ответ в память
    st.session_state.messages.append({"role": "assistant", "content": full_response})
