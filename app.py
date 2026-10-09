import base64
import io
import streamlit as st
from groq import Groq

# ==========================================
# 1. إعدادات الصفحة بتصميم Claude AI
# ==========================================
st.set_page_config(
    page_title="Claude AI", page_icon="🟠", layout="centered"
)

# تصميم Claude المظلم والأنيق
st.markdown(
    """
<style>
    /* خلفية Claude */
    .stApp {
        background-color: #181816 !important;
        color: #e6e4df !important;
    }
    header, footer, #MainMenu { visibility: hidden; }
    
    /* الهيدر والعنوان */
    .claude-header {
        text-align: center;
        padding: 20px 0 10px 0;
    }
    .claude-logo {
        font-size: 2.2rem;
        font-weight: 700;
        color: #d97757;
        letter-spacing: -1px;
    }
    .claude-sub {
        color: #8e8c85;
        font-size: 0.9rem;
    }

    /* أسلوب الرسائل */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        border: none !important;
        padding: 1rem 0 !important;
    }
    
    /* مربع الكتابة */
    [data-testid="stChatInput"] textarea {
        background-color: #22221f !important;
        color: #e6e4df !important;
        border: 1px solid #3b3a34 !important;
        border-radius: 14px !important;
    }
    [data-testid="stChatInput"] textarea:focus {
        border-color: #d97757 !important;
    }

    /* زر رفع الملفات */
    .stFileUploader {
        background-color: #22221f;
        border-radius: 12px;
        padding: 10px;
        border: 1px dashed #3b3a34;
    }
</style>
""",
    unsafe_allow_html=True,
)

# عنوان الواجهة
st.markdown(
    """
    <div class="claude-header">
        <div class="claude-logo">🟠 Claude 3.5</div>
        <div class="claude-sub">مساعدك الذكي بقوة Groq & Vision</div>
    </div>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 2. الساروت والموديلات الرسمية
# ==========================================
GROQ_API_KEY = "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"  # ⚠️ حط الساروت ديالك هنا (لي كيبدا بـ gsk_)

client = Groq(api_key=GROQ_API_KEY)

TEXT_MODEL = "llama-3.3-70b-versatile"  # أذكى موديل كتابة
VISION_MODEL = "llama-3.2-11b-vision-preview"  # الموديل الرسمي للصور

# ==========================================
# 3. إدارة الجلسة والمحادثة
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

# زر مسح الشات فالجنب
with st.sidebar:
    st.markdown("### ⚙️ الخيارات")
    if st.button("🗑️ محادثة جديدة"):
        st.session_state.messages = []
        st.rerun()

# مكان رفع الصورة (تصميم خفيف)
uploaded_image = st.file_uploader(
    "📎 إرفاق صورة (تمرين، درس، مستند...)", type=["jpg", "jpeg", "png"]
)

# عرض الأرشيف
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "🟠"
    with st.chat_message(msg["role"], avatar=avatar):
        if msg.get("image"):
            st.image(io.BytesIO(msg["image"]), width=280)
        st.markdown(msg["content"])

# ==========================================
# 4. التفاعل مع المستخدم
# ==========================================
if prompt := st.chat_input("بماذا يمكنني مساعدتك اليوم؟"):

    has_image = uploaded_image is not None

    # إضافة ميساج المستخدم للذاكرة
    if has_image:
        img_bytes = uploaded_image.getvalue()
        st.session_state.messages.append(
            {"role": "user", "content": prompt, "image": img_bytes}
        )
    else:
        st.session_state.messages.append(
            {"role": "user", "content": prompt, "image": None}
        )

    # عرض ميساج المستخدم فالبلاصة
    with st.chat_message("user", avatar="👤"):
        if has_image:
            st.image(uploaded_image, width=280)
        st.markdown(prompt)

    # بناء الطلب لـ Groq
    api_messages = [
        {
            "role": "system",
            "content": "أنت Claude، مساعد ذكي جداً وعالي الدقة. أجب بأسلوب راقٍ ومباشر بنفس لغة المستخدم (الدارجة المغربية، العربية، أو الفرنسية). إذا أُرفقت صورة، قم بتحليلها بدقة وحل التمارين الموجودة فيها خطوة بخطوة.",
        }
    ]

    # تجهيز محتوى الرسالة الحالية
    if has_image:
        b64_img = base64.b64encode(uploaded_image.getvalue()).decode("utf-8")
        current_content = [
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
        selected_model = VISION_MODEL
    else:
        current_content = prompt
        selected_model = TEXT_MODEL

    # إضافة التاريخ
    for m in st.session_state.messages[:-1]:
        api_messages.append({"role": m["role"], "content": m["content"]})

    api_messages.append({"role": "user", "content": current_content})

    # إجابة الـ AI
    with st.chat_message("assistant", avatar="🟠"):
        placeholder = st.empty()
        full_response = ""

        try:
            stream = client.chat.completions.create(
                model=selected_model,
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
            placeholder.markdown(f"⚠️ **خطأ:** `{e}`")
            full_response = ""

    if full_response:
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )
