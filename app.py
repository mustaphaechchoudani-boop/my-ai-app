import base64
import streamlit as st
from groq import Groq

st.set_page_config(page_title="My AI", page_icon="🤖", layout="centered")
st.title("🤖 الذكاء الاصطناعي الخاص بي")

# ⚠️ حط الساروت ديالك هنا (داك اللي كيبدا بـ gsk_)
GROQ_API_KEY = "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"

# الموديلات الصحيحة دبا فـ Groq
TEXT_MODEL = "openai/gpt-oss-120b"
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

client = Groq(api_key=GROQ_API_KEY)

if "messages" not in st.session_state:
    st.session_state.messages = []

# رفع تصويرة (اختياري)
uploaded_image = st.file_uploader(
    "📷 إلى بغيتي تسول على تصويرة، طلعها هنا",
    type=["jpg", "jpeg", "png"],
)

# عرض الرسائل القديمة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message.get("image"):
            st.image(message["image"], width=250)
        st.markdown(message["content"])

if prompt := st.chat_input("كتب الميساج ديالك هنا..."):
    api_messages = [{
        "role": "system",
        "content": "أنت مساعد ذكي ومفيد. جاوب بنفس لغة المستخدم (دارجة مغربية، عربية، فرنسية أو إنجليزية).",
    }]
    for m in st.session_state.messages:
        api_messages.append({"role": m["role"], "content": m["content"]})

    has_image = uploaded_image is not None
    if has_image:
        b64 = base64.b64encode(uploaded_image.getvalue()).decode("utf-8")
        user_content = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:{uploaded_image.type};base64,{b64}"}},
        ]
        model_to_use = VISION_MODEL
        st.session_state.messages.append({"role": "user", "content": prompt, "image": uploaded_image})
    else:
        user_content = prompt
        model_to_use = TEXT_MODEL
        st.session_state.messages.append({"role": "user", "content": prompt, "image": None})

    api_messages.append({"role": "user", "content": user_content})

    with st.chat_message("user"):
        if has_image:
            st.image(uploaded_image, width=250)
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        try:
            completion = client.chat.completions.create(
                model=model_to_use,
                messages=api_messages,
                stream=True,
            )
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)
        except Exception as e:
            placeholder.markdown(f"⚠️ وقع خطأ: `{e}`")
            full_response = ""

    if full_response:
        st.session_state.messages.append({"role": "assistant", "content": full_response})
