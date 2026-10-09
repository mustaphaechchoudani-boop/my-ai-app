import base64
import io
import streamlit as st
from groq import Groq

# =========================================================
# 1. إعدادات الصفحة بتصميم Claude AI الأصلي
# =========================================================
st.set_page_config(
    page_title="Claude 3.5 Sonnet", page_icon="✴️", layout="centered"
)

# تصميم Claude المظلم والأنيق
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700&display=swap');

    /* خلفية Claude الأصلية */
    .stApp {
        background-color: #141413 !important;
        color: #ece9e1 !important;
        font-family: 'Sora', -apple-system, sans-serif !important;
    }
    header, footer, #MainMenu { visibility: hidden; }

    /* عنوان Claude */
    .claude-container {
        text-align: center;
        padding: 20px 0 15px 0;
    }
    .claude-logo {
        font-size: 2.3rem;
        font-weight: 700;
        color: #da7756;
        letter-spacing: -1px;
    }
    .claude-badge {
        background-color: #2b2823;
        color: #b7b3a8;
        font-size: 0.8rem;
        padding: 4px 12px;
        border-radius: 20px;
        border: 1px solid #3e3b33;
        display: inline-block;
        margin-top: 6px;
    }

    /* رسائل المحادثة */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        border: none !important;
        padding: 1rem 0 !important;
    }

    /* مربع الإدخال */
    [data-testid="stChatInput"] textarea {
        background-color: #1f1e1b !important;
        color: #ece9e1 !important;
        border: 1px solid #383630 !important;
        border-radius: 14px !important;
    }
    [data-testid="stChatInput"] textarea:focus {
        border-color: #da7756 !important;
        box-shadow: 0 0 0 1px #da7756 !important;
    }

    /* زر رفع الصور */
    .stFileUploader {
        background-color: #1f1e1b;
        border: 1px dashed #383630;
        border-radius: 12px;
        padding: 8px;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #191816 !important;
        border-right: 1px solid #2b2823 !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# هيدر التطبيق
st.markdown(
    """
    <div class="claude-container">
        <div class="claude-logo">✴️ Claude</div>
        <div class="claude-badge">Powered by Groq Ultra-Fast AI</div>
    </div>
""",
    unsafe_allow_html=True,
)

# =========================================================
# 2. المفتاح والجلب الذكي للموديلات (يمنع أي خطأ 404)
# =========================================================
GROQ_API_KEY = "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"  # ⚠️ حط الساروت ديالك هنا (اللي كيبدا بـ gsk_)

client = Groq(api_key=GROQ_API_KEY)


@st.cache_data(ttl=3600)
def detect_working_models(key):
    try:
        c = Groq(api_key=key)
        models = [m.id for m in c.models.list().data]

        # اختيار الموديل الممتاز للنص
        text_list = [
            "llama-3.3-70b-versatile",
            "qwen-2.5-coder-32b",
            "llama-3.1-8b-instant",
        ]
        best_text = next(
            (m for m in text_list if m in models),
            models[0] if models else "llama-3.3-70b-versatile",
        )

        # اختيار الموديل المعتمد للصور
        vision_list = [
            "llama-3.2-11b-vision-preview",
            "llama-3.2-90b-vision-preview",
            "llava-v1.5-7b-4096-preview",
        ]
        best_vision = next(
            (m for m in vision_list if m in models),
            next(
                (m for m in models if "vision" in m),
                "llama-3.2-11b-vision-preview",
            ),
        )

        return best_text, best_vision
    except:
        return "llama-3.3-70b-versatile", "llama-3.2-11b-vision-preview"


TEXT_MODEL, VISION_MODEL = detect_working_models(GROQ_API_KEY)

# القائمة الجانبية
with st.sidebar:
    st.markdown("### ⚙️ Claude Settings")
    st.caption(f"🧠 Text Engine: `{TEXT_MODEL}`")
    st.caption(f"👁️ Vision Engine: `{VISION_MODEL}`")
    st.markdown("---")
    if st.button("🗑️ محادثة جديدة", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# =========================================================
# 3. محرك المحادثة والصور
# =========================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

# خانة إرفاق صورة
uploaded_image = st.file_uploader(
    "📎 إرفاق صورة (تمرين، درس، صورة...)", type=["jpg", "jpeg", "png"]
)

# عرض أرشيف المحادثة
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "✴️"
    with st.chat_message(msg["role"], avatar=avatar):
        if msg.get("image"):
            st.image(io.BytesIO(msg["image"]), width=280)
        st.markdown(msg["content"])

# استقبال الميساج من المستخدم
if prompt := st.chat_input("بماذا يمكنني مساعدتك اليوم؟"):

    has_image = uploaded_image is not None

    # حفظ رسالة المستخدم فـ الذاكرة
    if has_image:
        img_bytes = uploaded_image.getvalue()
        st.session_state.messages.append(
            {"role": "user", "content": prompt, "image": img_bytes}
        )
    else:
        st.session_state.messages.append(
            {"role": "user", "content": prompt, "image": None}
        )

    # عرض رسالة المستخدم
    with st.chat_message("user", avatar="👤"):
        if has_image:
            st.image(uploaded_image, width=280)
        st.markdown(prompt)

    # إعداد الطلب للـ API
    system_prompt = (
        "أنت Claude، نموذج ذكاء اصطناعي فائق الذكاء، دقيق للغاية وسريع. "
        "تجيب بأسلوب راقٍ ومباشر باللغة التي يكلمك بها المستخدم (الدارجة المغربية، العربية، الفرنسية، أو الإنجليزية). "
        "إذا أُرفقت صورة، قم بتحليلها بالكامل وقراءة النصوص والرموز الموجودة فيها وحل التمارين خطوة بخطوة."
    )

    api_messages = [{"role": "system", "content": system_prompt}]

    # إضافة الأرشيف السابق كـ نص فقط لضمان السرعة وعدم حدوث خطأ
    for m in st.session_state.messages[:-1]:
        api_messages.append({"role": m["role"], "content": m["content"]})

    # إعداد الرسالة الحالية (نص أو تصويرة)
    if has_image:
        b64_img = base64.b64encode(uploaded_image.getvalue()).decode("utf-8")
        current_payload = [
            {
                "type": "text",
                "text": prompt
                if prompt
                else "حل واشرح المحتوى الموجود في هذه الصورة بالتفصيل.",
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{uploaded_image.type};base64,{b64_img}"
                },
            },
        ]
        model_to_use = VISION_MODEL
    else:
        current_payload = prompt
        model_to_use = TEXT_MODEL

    api_messages.append({"role": "user", "content": current_payload})

    # توليد استجابة الـ AI
    with st.chat_message("assistant", avatar="✴️"):
        placeholder = st.empty()
        full_response = ""

        try:
            stream = client.chat.completions.create(
                model=model_to_use,
                messages=api_messages,
                stream=True,
                temperature=0.2,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    full_response += delta
                    placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)
        except Exception as e:
            placeholder.markdown(f"⚠️ **تنبيه:** `{e}`")
            full_response = ""

    if full_response:
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )
