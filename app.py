import io
import base64
import streamlit as st
from groq import Groq

st.set_page_config(page_title="MyAI Pro", page_icon="🤖",
                   layout="centered", initial_sidebar_state="collapsed")

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
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">🤖 MyAI Pro</h1>', unsafe_allow_html=True)

# ⚠️ حط الساروت ديالك هنا (ما تنساه!)
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# ===== جلب الموديلات أوتوماتيكياً =====
@st.cache_data(ttl=600)
def get_models():
    try:
        return [m.id for m in client.models.list().data]
    except Exception:
        return []

available = get_models()

# موديلات النص
TEXT_CANDIDATES = ["openai/gpt-oss-120b", "openai/gpt-oss-20b",
                   "qwen/qwen3-32b", "llama-3.1-8b-instant"]
skip = ("whisper", "tts", "guard", "embed")
text_models = [m for m in TEXT_CANDIDATES if m in available] or \
              [m for m in available if not any(s in m.lower() for s in skip)]

# موديلات الصور: كنقلبو على أي موديل فيزيون معروف عند Groq
VISION_KEYWORDS = ("scout", "maverick", "llama-4")
vision_models = [m for m in available
                 if any(k in m.lower() for k in VISION_KEYWORDS)
                 and "guard" not in m.lower()]

TEXT_MODEL = text_models[0] if text_models else None
VISION_MODEL = vision_models[0] if vision_models else None

# ===== السايدبار: الحالة + اللائحة الكاملة =====
with st.sidebar:
    st.subheader("⚙️ الحالة ديال الموديلات")
    st.markdown(f"📝 النص: `{TEXT_MODEL or '❌'}`")
    st.markdown(f"👁️ الصور: `{VISION_MODEL or '❌ غير متوفر'}`")
    with st.expander("📋 اللائحة الكاملة (صيفطها ليا إلى كان مشكل)"):
        st.write("\n".join(f"- `{m}`" for m in available) or "خاوية")
    if st.button("🗑️ مسح المحادثة", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if not TEXT_MODEL:
    st.error("❌ ماكاين حتى موديل! تأكد من الـ API Key ديالك.")
    st.stop()

# مسح الصورة القديمة من الأپلودر (باش الميساج الجاي ماياخدهاش)
if st.session_state.pop("clear_up", False):
    st.session_state.pop("up_img", None)

if "messages" not in st.session_state:
    st.session_state.messages = []

# تنبيه واضح إلى مافيهاش موديل صور
if not VISION_MODEL:
    st.warning("⚠️ **موديل الصور ماكاينش فحسابك دبا!** الكتابة خدامة عادي، "
               "ولكن باش يقرا التصاور: حل خانة 'اللائحة الكاملة' فالسايدبار، "
               "دير ليها سكرينشوت وصيفطو ليا باش نلقى ليك الحل.")

uploaded_image = st.file_uploader("📷 طلع تصويرة (درس، وثيقة...)",
                                  type=["jpg", "jpeg", "png"], key="up_img")

# ===== عرض المحادثة =====
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🧑" if message["role"] == "user" else "🤖"):
        if message.get("image"):
            st.image(io.BytesIO(message["image"]), width=220)
        st.markdown(message["content"])

# ===== الشات =====
if prompt := st.chat_input("كتب الميساج ديالك هنا..."):
    has_image = uploaded_image is not None

    with st.chat_message("user", avatar="🧑"):
        if has_image:
            st.image(uploaded_image, width=220)
        st.markdown(prompt)

    if has_image and not VISION_MODEL:
        err = ("⚠️ ماقدرتش نشوف التصويرة حيت **موديل الصور ماكاينش فحسابك**.\n\n"
               "حل 'اللائحة الكاملة' فالسايدبار، صيفط ليها سكرينشوت باش نصلحو هادشي.")
        st.session_state.messages.append({"role": "user", "content": prompt, "image": uploaded_image.getvalue()})
        st.session_state.messages.append({"role": "assistant", "content": err, "image": None})
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(err)
        st.session_state.clear_up = True
    else:
        api_messages = [{
            "role": "system",
            "content": "أنت MyAI، مساعد ذكي جداً. جاوب بدقة واحترافية، وبنفس لغة المستخدم (دارجة مغربية، عربية، فرنسية أو إنجليزية)."
        }]
        for m in st.session_state.messages:
            api_messages.append({"role": m["role"], "content": m["content"]})

        if has_image:
            b64 = base64.b64encode(uploaded_image.getvalue()).decode()
            api_messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url",
                     "image_url": {"url": f"data:{uploaded_image.type};base64,{b64}"}},
                ],
            })
            st.session_state.messages.append({"role": "user", "content": prompt, "image": uploaded_image.getvalue()})
            model_to_use = VISION_MODEL
        else:
            api_messages.append({"role": "user", "content": prompt})
            st.session_state.messages.append({"role": "user", "content": prompt, "image": None})
            model_to_use = TEXT_MODEL

        with st.chat_message("assistant", avatar="🤖"):
            placeholder = st.empty()
            full_response = ""
            try:
                stream = client.chat.completions.create(
                    model=model_to_use, messages=api_messages,
                    stream=True, temperature=0.7,
                )
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                        placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)
            except Exception as e:
                full_response = ""
                placeholder.markdown(f"⚠️ وقع خطأ: `{e}`")

        if full_response:
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.session_state.clear_up = True
