import base64
import streamlit as st
from groq import Groq

# إعدادات الصفحة
st.set_page_config(
    page_title="My AI",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# تصميم CSS لواجهة أنيقة كتخدم مزيان فالهاتف
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0f0f0f;
        color: #ffffff;
    }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stChatMessage {
        border-radius: 14px;
        padding: 8px 12px;
        margin-bottom: 8px;
    }
    [data-testid="stChatInput"] {
        border-radius: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🤖 الذكاء الاصطناعي الخاص بي")

# الشريط الجانبي للإعدادات
with st.sidebar:
    st.header("⚙️ الإعدادات")
    
    groq_api_key = st.text_input(
        "Groq API Key",
        type="password",
        placeholder="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",
        help="حط الساروت ديال Groq هنا"
    )
    
    model_option = st.selectbox(
        "اختر الموديل:",
        [
            "llama-4-scout-17b-16e-instruct",
            "llama-4-maverick-17b-128e-instruct",
            "qwen/qwen2.5-vl-32b-instruct",
            "deepseek-r1-distill-llama-70b",
            "llama-3.3-70b-versatile",
            "qwen-2.5-coder-32b",
        ],
        index=0,
    )
    
    st.info("💡 الموديلات لي فيها VL أو Scout كيشوفو التصاور")
    
    if st.button("🗑️ مسح المحادثة"):
        st.session_state.messages = []
        st.rerun()

# التحقق من API Key
if not groq_api_key:
    st.warning("⚠️ المرجو إدخال Groq API Key من القائمة الجانبية")
    st.stop()

# إنشاء العميل
client = Groq(api_key=groq_api_key)

# تهيئة المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسائل السابقة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # عرض النص
        if isinstance(message["content"], str):
            st.markdown(message["content"])
        # عرض النص + الصورة (للرسائل لي فيها صورة)
        elif isinstance(message["content"], list):
            for part in message["content"]:
                if part["type"] == "text":
                    st.markdown(part["text"])
                elif part["type"] == "image_url":
                    st.image(part["image_url"]["url"])

# رفع الصورة
uploaded_file = st.file_uploader(
    "📷 صيفط صورة (اختياري)",
    type=["jpg", "jpeg", "png", "webp", "gif"],
    accept_multiple_files=False,
)

# إدخال المستخدم
if prompt := st.chat_input("كتب الميساج ديالك هنا..."):
    user_content = []

    # إضافة الصورة إذا تم رفعها
    if uploaded_file is not None:
        try:
            image_bytes = uploaded_file.getvalue()
            base64_image = base64.b64encode(image_bytes).decode("utf-8")
            mime_type = uploaded_file.type or "image/jpeg"
            image_url_data = f"data:{mime_type};base64,{base64_image}"

            user_content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": image_url_data},
                }
            )
        except Exception as e:
            st.error(f"خطأ فقراءة الصورة: {e}")

    # إضافة النص
    user_content.append({"type": "text", "text": prompt})

    # حفظ رسالة المستخدم
    st.session_state.messages.append({"role": "user", "content": user_content})

    # عرض رسالة المستخدم
    with st.chat_message("user"):
        for part in user_content:
            if part["type"] == "text":
                st.markdown(part["text"])
            elif part["type"] == "image_url":
                st.image(part["image_url"]["url"])

    # توليد الرد
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            # تحويل الرسائل للتنسيق المناسب لـ Groq (Vision)
            api_messages = []
            for m in st.session_state.messages:
                if isinstance(m["content"], str):
                    api_messages.append({"role": m["role"], "content": m["content"]})
                elif isinstance(m["content"], list):
                    api_messages.append({"role": m["role"], "content": m["content"]})

            completion = client.chat.completions.create(
                model=model_option,
                messages=api_messages,
                stream=True,
                temperature=0.7,
                max_tokens=4096,
            )

            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

        except Exception as e:
            error_msg = str(e)
            st.error(f"خطأ: {error_msg}")
            full_response = ""

    # حفظ رد المساعد
    if full_response:
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )
