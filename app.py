import io
import base64
import streamlit as st
from groq import Groq

# ===== إعدادات الصفحة =====
st.set_page_config(page_title="MyAI Pro", page_icon="🤖",
                   layout="centered", initial_sidebar_state="collapsed")

# ===== التصميم الاحترافي =====
st.markdown("""
<style>
    .stApp { background: linear-gradient(180deg,#0f0f23 0%,#1a1a2e 100%); color:#fff; }
    header, footer, #MainMenu { visibility: hidden; }
    .main-title {
        text-align:center; font-size:2.2rem; font-weight:800; padding:10px 0;
        background: linear-gradient(90deg,#00d2ff,#928dff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    [data-testid="stChatMessage"] {
        background-color: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px; padding: 12px; margin-bottom: 12px;
    }
    [data-testid="stChatInput"] textarea {
        background-color: #262636 !important; color: white !important;
        border-radius: 15px !important; border: 1px solid #4a4a6a !important;
    }
    .stButton > button {
        width: 100%; border-radius: 12px; border: none; color: white;
        font-weight: bold; background: linear-gradient(90deg,#00d2ff,#928dff);
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">🤖 MyAI Pro</h1>', unsafe_allow_html=True)

# ===== الساروت (حط الساروت ديالك هنا) =====
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# ===== جلب الموديلات أوتوماتيكياً (بلا مشاكل السميات) =====
@st.cache_data(ttl=600)
def get_models():
    try:
        return [m.id for m in client.models.list().data]
    except Exception:
        return []

available = get_models()

TEXT_CANDIDATES = [
    "openai/gpt-oss-120b",      # الأقوى (قريب لـ GPT-5)
    "openai/gpt-oss-20b",
    "qwen/qwen3-32b",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
]
VISION_CANDIDATES = [
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "meta-llama/llama-4-maverick-17b-128e-instruct",
]

text_models = [m for m in TEXT_CANDIDATES if m in available]
vision_models = [m for m in VISION_CANDIDATES if m in available]

# إلى ما لقاش حتى واحد معروف، ياخذ أي موديل خدام
if not text_models:
    text_models = [m for m in available
                   if not any(x in m for x in ("whisper", "tts", "guard", "embed"))]

# ===== القائمة الجانبية =====
with st.sidebar:
    st.subheader("⚙️ الإعدادات")
    TEXT_MODEL = st.selectbox("🧠 موديل الكتابة:", text_models) if text_models else None
    VISION_MODEL = st.selectbox("👁️ موديل الصور:", vision_models) if vision_models else None
    if st.button("🗑️ مسح المحادثة", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if not TEXT_MODEL:
    st.error("❌ ماكاين حتى موديل! تأكد من الـ API Key ديالك.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

uploaded_image = st.file_uploader("📷 إلى بغيتي تسول على تصويرة (درس، وثيقة...)", type=["jpg", "jpeg", "png"])

# ===== عرض المحادثة =====
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🧑" if message["role"] == "user" else "🤖"):
        if message.get("image"):
            st.image(io.BytesIO(message["image"]), width=220)
        st.markdown(message["content"])

# ===== الشات =====
if prompt := st.chat_input("كتب الميساج ديالك هنا..."):
    api_messages = [{
        "role": "system",
        "content": "أنت MyAI، مساعد ذكي جداً وقوي. جاوب بدقة واحترافية على كل الأسئلة، وبنفس لغة المستخدم (دارجة مغربية، عربية، فرنسية أو إنجليزية). كن مباشراً ومفيداً."
    }]
    for m in st.session_state.messages:
        api_messages.append({"role": m["role"], "content": m["content"]})

    has_image = uploaded_image is not None

    if has_image and VISION_MODEL:
        b64 = base64.b64encode(uploaded_image.getvalue()).decode()
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

    with st.chat_message("user", avatar="🧑"):
        if has_image and VISION_MODEL:
            st.image(uploaded_image, width=220)
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        placeholder = st.empty()
        full_response = ""
        try:
            stream = client.chat.completions.create(
                model=model_to_use,
                messages=api_messages,
                stream=True,
                temperature=0.7,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    full_response += delta
                    placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)
        except Exception as e:
            placeholder.markdown(f"⚠️ وقع خطأ: `{e}`")
            full_response = ""

    if full_response:
        st.session_state.messages.append({"role": "assistant", "content": full_response})
