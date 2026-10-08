import io
import base64
import streamlit as st
from groq import Groq

st.set_page_config(page_title="My AI", page_icon="🤖", layout="centered")
st.title("🤖 الذكاء الاصطناعي الخاص بي")

# ⚠️ حط الساروت ديالك هنا
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# ===== 1) جلب الموديلات المتوفرة أوتوماتيكياً من Groq =====
@st.cache_data(ttl=600)
def get_available_models():
    try:
        return [m.id for m in client.models.list().data]
    except Exception as e:
        st.error(f"مشكل فجلب الموديلات: {e}")
        return []

available = get_available_models()

# ===== 2) اختار أحسن موديل خدام =====
skip = ("whisper", "tts", "guard", "embed", "distil")
text_pool = [m for m in available if not any(s in m.lower() for s in skip)]

TEXT_CANDIDATES = ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
VISION_CANDIDATES = [
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "meta-llama/llama-4-maverick-17b-128e-instruct",
]

TEXT_MODEL = next((m for m in TEXT_CANDIDATES if m in available), text_pool[0] if text_pool else None)
VISION_MODEL = next((m for m in VISION_CANDIDATES if m in available), None)
if not VISION_MODEL:
    VISION_MODEL = next((m for m in available if "vision" in m.lower() or "llama-4" in m.lower()), None)

# ===== 3) لوحة المعلومات فالجنب =====
with st.sidebar:
    st.subheader("⚙️ الموديلات الخدامة")
    st.write(f"📝 النص: `{TEXT_MODEL}`")
    st.write(f"📷 الصور: `{VISION_MODEL or '❌ ماكاينش'}`")
    with st.expander("📋 شوف كاع الموديلات المتوفرة"):
        for m in available:
            st.write(f"- {m}")
    if st.button("🗑️ مسح المحادثة"):
        st.session_state.messages = []
        st.rerun()

if not TEXT_MODEL:
    st.error("ماكاين حتى موديل! تأكد من الـ API Key ديالك.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

uploaded_image = st.file_uploader("📷 إلى بغيتي تسول على تصويرة، طلعها هنا", type=["jpg", "jpeg", "png"])

# ===== عرض الرسائل القديمة =====
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message.get("image"):
            st.image(io.BytesIO(message["image"]), width=250)
        st.markdown(message["content"])

# ===== الشات =====
if prompt := st.chat_input("كتب الميساج ديالك هنا..."):
    has_image = uploaded_image is not None
    if has_image and not VISION_MODEL:
        st.warning("⚠️ موديل الصور ماكيخدمش دبا فحسابك. جرب غير بالكتابة.")
        st.stop()

    api_messages = [{
        "role": "system",
        "content": "أنت مساعد ذكي ومفيد. جاوب بنفس لغة المستخدم (دارجة مغربية، عربية، فرنسية أو إنجليزية).",
    }]
    for m in st.session_state.messages:
        api_messages.append({"role": m["role"], "content": m["content"]})

    if has_image:
        b64 = base64.b64encode(uploaded_image.getvalue()).decode("utf-8")
        user_content = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:{uploaded_image.type};base64,{b64}"}},
        ]
        model_to_use = VISION_MODEL
        st.session_state.messages.append({"role": "user", "content": prompt, "image": uploaded_image.getvalue()})
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
