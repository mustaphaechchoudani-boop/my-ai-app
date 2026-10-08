import streamlit as st
from groq import Groq

# إعدادات الشاشة
st.set_page_config(page_title="My AI", page_icon="🤖", layout="centered")

# عنوان التطبيق
st.title("🤖 MC AI ")

# الساروت ديال Groq (حط الساروت ديالك هنا فبلاصة gsk_xxx)
GROQ_API_KEY = "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"

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسائل القديمة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# بلاصة الكتابة
if prompt := st.chat_input("كتب الميساج ديالك هنا..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        client = Groq(api_key=GROQ_API_KEY)
        completion = client.chat.completions.create(
            model="qwen-2.5-coder-32b",
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            stream=True,
        )
        for chunk in completion:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
        
    st.session_state.messages.append({"role": "assistant", "content": full_response})
