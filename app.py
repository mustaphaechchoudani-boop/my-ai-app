import base64
import streamlit as st
from groq import Groq

st.set_page_config(page_title="My AI", page_icon="🤖", layout="centered")
st.title("🤖 الذكاء الاصطناعي - صيفط التمرين وصورتو")

GROQ_API_KEY = "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"

# موديل Vision كيقرا التصاور
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسائل القديمة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message.get("image"):
            st.image(message["image"], width=300)
        st.markdown(message["content"])

# رفع التصويرة من الجنب
img = st.sidebar.file_uploader("📷 صيفط تصويرة التمرين", type=["jpg", "jpeg", "png"])
if img:
    st.sidebar.image(img, width=200)

prompt = st.chat_input("كتب السؤال ديالك على التمرين...")

if prompt:
    user_msg = {"role": "user", "content": prompt}
    if img:
        user_msg["image"] = img.getvalue()
    st.session_state.messages.append(user_msg)

    with st.chat_message("user"):
        if img:
            st.image(img, width=300)
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        client = Groq(api_key=GROQ_API_KEY)

        # بناء الرسائل (مع التصويرة إلا كانت)
        api_messages = []
        for m in st.session_state.messages:
            if m.get("image"):
                b64 = base64.b64encode(m["image"]).decode()
                api_messages.append({
                    "role": m["role"],
                    "content": [
                        {"type": "text", "text": m["content"]},
                        {"type": "image_url",
                         "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                    ]
                })
            else:
                api_messages.append({"role": m["role"], "content": m["content"]})

        completion = client.chat.completions.create(
            model=VISION_MODEL,
            messages=api_messages,
            stream=True,
        )
        for chunk in completion:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                placeholder.markdown(full_response + "▌")
        placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
