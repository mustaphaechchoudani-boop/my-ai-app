import base64
import streamlit as st
from groq import Groq

st.set_page_config(page_title="My AI", page_icon="🤖", layout="centered")
st.title("🤖 الذكاء الاصطناعي الخاص بي")

# ⚠️ الساروت ديالك (راه موجود من قبل، ما تبدلش إلا كان مزيان)
GROQ_API_KEY = "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"

# موديل الكتابة + موديل الرؤية (العينين)
MODEL_TEXTE = "qwen-2.5-coder-32b"
MODEL_VISION = "meta-llama/llama-4-scout-17b-16e-instruct"

client = Groq(api_key=GROQ_API_KEY)

if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسائل القديمة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message.get("image"):
            st.image(message["image"], width=250)
        st.markdown(message["content"])

# 📷 بلاصة رفع الصور
uploaded = st.file_uploader("📷 اختار تصويرة من التيليفون", type=["jpg", "jpeg", "png", "webp"])
photo = st.camera_input("📸 ولا صور ديريكت بالكاميرا")

img_bytes = None
picked = uploaded or photo
if picked is not None:
    img_bytes = picked.getvalue()
    st.image(img_bytes, width=150)

# بلاصة الكتابة
if prompt := st.chat_input("كتب الميساج ديالك هنا..."):
    # عرض ميساج المستخدم
    st.session_state.messages.append({"role": "user", "content": prompt, "image": img_bytes})
    with st.chat_message("user"):
        if img_bytes is not None:
            st.image(img_bytes, width=250)
        st.markdown(prompt)

    # بناء الرسائل للـ API
    api_messages = []
    for m in st.session_state.messages[:-1]:
        content = m["content"]
        if m.get("image"):
            content += " (كانت معاها صورة)"
        api_messages.append({"role": m["role"], "content": content})

    # 👇 هنا الذكاء: إلا كانت صورة نستعملو الموديل اللي كيشوف
    if img_bytes is not None:
        model = MODEL_VISION
        api_messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {
                    "url": f"data:image/jpeg;base64,{base64.b64encode(img_bytes).decode()}"
                }},
            ],
        })
    else:
        model = MODEL_TEXTE
        api_messages.append({"role": "user", "content": prompt})

    # توليد الجواب
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full = ""
        try:
            stream = client.chat.completions.create(
                model=model,
                messages=api_messages,
                stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    full += delta
                    placeholder.markdown(full + "▌")
            placeholder.markdown(full)
        except Exception as e:
            st.error(f"وقع خطأ: {e}")

    if full:
        st.session_state.messages.append({"role": "assistant", "content": full})
