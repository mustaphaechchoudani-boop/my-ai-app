import streamlit as st
from groq import Groq

st.set_page_config(
    page_title="Claude 3.5 Sonnet", page_icon="✴️", layout="centered"
)

# 🔐 قراءة الساروت بأمان من Streamlit Secrets أو من Sidebar
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["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"]
else:
    # إلا ما درتيهش فـ secrets، كيعطيك خانة فـ الجنب تدخلو بيدك
    api_key = st.sidebar.text_input("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", type="password")

if not api_key:
    st.warning("⚠️ المرجو إدخال API Key للبدء.")
    st.stop()

client = Groq(api_key=api_key)

# عنوان الصفحة
st.title("✴️ Claude 3.5 Sonnet (Groq)")

# تهيئة الذاكرة
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسائل القديمة
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "✴️"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# استقبال السؤال
if prompt := st.chat_input("بماذا يمكنني مساعدتك اليوم؟"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="✴️"):
        placeholder = st.empty()
        full_response = ""
        try:
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
                temperature=0.3,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    full_response += delta
                    placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )
        except Exception as e:
            placeholder.error(f"⚠️ خطأ: `{e}`")
