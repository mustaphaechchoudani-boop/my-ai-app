import streamlit as st
from groq import Groq
import base64
from io import BytesIO

# إعدادات الشاشة
st.set_page_config(
    page_title="My AI", 
    page_icon="🤖", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# عنوان التطبيق
st.title("🤖 الذكاء الاصطناعي الخاص بي")

# الساروت ديال Groq
GROQ_API_KEY = "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"

# Sidebar للإعدادات
with st.sidebar:
    st.header("⚙️ الإعدادات")
    
    # اختيار الموديل
    model_option = st.selectbox(
        "اختر النموذج:",
        [
            "qwen-2.5-vl-32b-instruct",
            "llama-4-scout-17b-16e-instruct",
            "llama-3.2-90b-vision-preview"
        ],
        index=0
    )
    
    # زر مسح المحادثة
    if st.button("🗑️ مسح المحادثة", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.info("💡 تقدر ترفع صورة + تسول عليها مباشرة")

# التحقق من API Key
if GROQ_API_KEY == "حط_الساروت_ديالك_هنا":
    st.warning("⚠️ المرجو تحط الساروت ديال Groq API Key فالكود (السطر 13)")
    st.stop()

# إنشاء عميل Groq
client = Groq(api_key=GROQ_API_KEY)

# تهيئة سجل المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسائل القديمة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # عرض المحتوى (نص + صور)
        if isinstance(message["content"], list):
            for part in message["content"]:
                if part["type"] == "text":
                    st.markdown(part["text"])
                elif part["type"] == "image_url":
                    st.image(part["image_url"]["url"])
        else:
            st.markdown(message["content"])

# رفع الصورة + الكتابة
col1, col2 = st.columns([0.85, 0.15])

with col1:
    prompt = st.chat_input("كتب الميساج ديالك هنا...")

with col2:
    uploaded_file = st.file_uploader(
        "📷",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed",
        help="رفع صورة"
    )

# معالجة السؤال
if prompt or uploaded_file:
    # تجهيز محتوى رسالة المستخدم
    user_content = []
    
    # إضافة النص
    if prompt:
        user_content.append({"type": "text", "text": prompt})
    
    # إضافة الصورة
    image_data_url = None
    if uploaded_file is not None:
        # تحويل الصورة إلى base64
        bytes_data = uploaded_file.read()
        base64_image = base64.b64encode(bytes_data).decode("utf-8")
        mime_type = uploaded_file.type
        image_data_url = f"data:{mime_type};base64,{base64_image}"
        user_content.append({
            "type": "image_url",
            "image_url": {"url": image_data_url}
        })
    
    # إضافة رسالة المستخدم
    st.session_state.messages.append({"role": "user", "content": user_content})
    
    # عرض رسالة المستخدم
    with st.chat_message("user"):
        for part in user_content:
            if part["type"] == "text":
                st.markdown(part["text"])
            elif part["type"] == "image_url":
                st.image(part["image_url"]["url"])

    # توليد جواب الذكاء الاصطناعي
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            # إرسال الطلب إلى Groq
            completion = client.chat.completions.create(
                model=model_option,
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
                temperature=0.7,
                max_tokens=4096,
            )

            # عرض الجواب كلمة بكلمة
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

        except Exception as e:
            error_msg = f"حدث خطأ: {e}"
            message_placeholder.error(error_msg)
            full_response = error_msg

    # حفظ جواب المساعد
    if full_response:
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )
