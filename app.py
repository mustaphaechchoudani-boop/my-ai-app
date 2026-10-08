import streamlit as st
from groq import Groq

# إعدادات الشاشة
st.set_page_config(page_title="My AI", page_icon="🤖", layout="centered", initial_sidebar_state="expanded")

# تصميم CSS للتطبيق
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0f172a;
        color: #ffffff;
    }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stChatMessage {
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# عنوان التطبيق
st.title("🤖 الذكاء الاصطناعي الخاص بي")

# الشريط الجانبي
with st.sidebar:
    st.header("⚙️ الإعدادات")
    
    # إدخال API Key
    groq_api_key = st.text_input(
        "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",
        type="password",
        help="حط الساروت ديال Groq هنا (يبدأ بـ gsk_)"
    )
    
    # اختيار الموديل
    model_option = st.selectbox(
        "اختر نموذج الذكاء الاصطناعي:",
        [
            "qwen/qwen3-32b",
            "qwen/qwen3-8b",
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "deepseek-r1-distill-qwen-32b",
        ],
        index=0,
    )
    
    st.info("💡 اختر **qwen/qwen3-32b** هو الأقوى والأحسن دبا")
    
    # زر مسح المحادثة
    if st.button("🗑️ مسح المحادثة", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.caption("تم التطوير بـ Python + Streamlit + Groq")

# التحقق من API Key
if not groq_api_key:
    st.warning("⚠️ المرجو إدخال Groq API Key فالشريط الجانبي للبدء")
    st.stop()

# إنشاء عميل Groq
client = Groq(api_key=groq_api_key)

# تهيئة سجل المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسائل السابقة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# إدخال المستخدم
if prompt := st.chat_input("كتب سؤالك هنا..."):
    # إضافة رسالة المستخدم
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # توليد رد الذكاء الاصطناعي
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            completion = client.chat.completions.create(
                model=model_option,
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
                temperature=0.7,
                max_tokens=2048,
            )

            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

        except Exception as e:
            error_msg = str(e)
            if "model_not_found" in error_msg or "does not exist" in error_msg:
                st.error("❌ الموديل ما كاينش دبا. جرب موديل آخر من القائمة الجانبية.")
            else:
                st.error(f"❌ حدث خطأ: {error_msg}")

    # حفظ رد المساعد
    if full_response:
        st.session_state.messages.append({"role": "assistant", "content": full_response})
