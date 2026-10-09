import base64
import io
import os
import streamlit as st
from groq import Groq

# =========================================================
# 1. إعدادات الصفحة والتصميم الفاخر (Claude 3.5 Sonnet UI)
# =========================================================
st.set_page_config(
    page_title="Claude 3.5 Sonnet Pro",
    page_icon="✴️",
    layout="centered",
    initial_sidebar_state="expanded",
)

# تخصيص CSS متطور شبيه بـ Claude الأصلي
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Fira+Code:wght@400;500&display=swap');

    /* الألوان الأساسية */
    :root {
        --bg-main: #141413;
        --bg-secondary: #1e1e1c;
        --claude-accent: #da7756;
        --claude-accent-hover: #e58565;
        --text-primary: #ece9e1;
        --text-secondary: #b7b3a8;
        --border-color: #2b2823;
    }

    .stApp {
        background-color: var(--bg-main) !important;
        color: var(--text-primary) !important;
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
    }

    /* إخفاء عناصر Streamlit الافتراضية */
    header, footer, #MainMenu { visibility: hidden; }

    /* الهيدر الأنيق */
    .claude-header {
        text-align: center;
        padding: 1.5rem 0 1rem 0;
        border-bottom: 1px solid var(--border-color);
        margin-bottom: 1.5rem;
    }
    .claude-logo {
        font-size: 2.2rem;
        font-weight: 700;
        color: var(--claude-accent);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
    }
    .claude-badge {
        background-color: #262420;
        color: var(--text-secondary);
        font-size: 0.78rem;
        padding: 4px 14px;
        border-radius: 20px;
        border: 1px solid var(--border-color);
        display: inline-block;
        margin-top: 8px;
    }

    /* حقل الكتابة */
    [data-testid="stChatInput"] {
        border-radius: 16px !important;
    }
    [data-testid="stChatInput"] textarea {
        background-color: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 14px !important;
        font-size: 0.95rem !important;
    }
    [data-testid="stChatInput"] textarea:focus {
        border-color: var(--claude-accent) !important;
        box-shadow: 0 0 0 1px var(--claude-accent) !important;
    }

    /* تخصيص الرسائل */
    [data-testid="stChatMessage"] {
        padding: 1.2rem 0 !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.03);
    }
    
    /* رفع الملفات */
    .stFileUploader {
        background-color: var(--bg-secondary);
        border: 1px dashed var(--border-color);
        border-radius: 12px;
        padding: 10px;
    }

    /* القائمة الجانبية */
    [data-testid="stSidebar"] {
        background-color: #181715 !important;
        border-right: 1px solid var(--border-color) !important;
    }

    /* تحسين مظهر الأكواد */
    pre, code {
        font-family: 'Fira Code', monospace !important;
        border-radius: 8px !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# =========================================================
# 2. القائمة الجانبية والإعدادات (Sidebar)
# =========================================================
with st.sidebar:
    st.markdown("### ⚙️ الإعدادات والموديلات")

    # إدخال المفتاح بشكل آمن
    api_key_input = st.text_input(
        "🔑 Groq API Key:",
        type="password",
        value=os.getenv("GROQ_API_KEY", ""),
        help="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",
    )

    st.markdown("---")

    # اختيار الموديل
    text_models = {
        "⚡ Llama 3.3 70B (الذكي والسريع)": "llama-3.3-70b-versatile",
        "🧠 DeepSeek R1 (للتفكير المعقد والرياضيات)": "deepseek-r1-distill-llama-70b",
        "🚀 Llama 3.1 8B (خفيف وسريع جداً)": "llama-3.1-8b-instant",
    }
    chosen_model_name = st.selectbox(
        "🧠 موديل النصوص:", list(text_models.keys())
    )
    TEXT_MODEL = text_models[chosen_model_name]

    VISION_MODEL = "llama-3.2-11b-vision-preview"

    st.markdown("---")
    temperature = st.slider("🌡️ درجة الإبداع (Temperature):", 0.0, 1.0, 0.3, 0.1)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ محو المحادثة", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with col2:
        if "messages" in st.session_state and st.session_state.messages:
            chat_text = "\n\n".join(
                [
                    f"{m['role'].upper()}: {m['content']}"
                    for m in st.session_state.messages
                ]
            )
            st.download_button(
                "📥 تحميل المحادثة",
                data=chat_text,
                file_name="chat_history.txt",
                mime="text/plain",
                use_container_width=True,
            )

# =========================================================
# 3. الهيدر الرئيسي
# =========================================================
st.markdown(
    """
    <div class="claude-header">
        <div class="claude-logo">✴️ Claude 3.5 Sonnet</div>
        <div class="claude-badge">Powered by Groq Llama 3.3 & DeepSeek</div>
    </div>
""",
    unsafe_allow_html=True,
)

# التحقق من وجود المفتاح
if not api_key_input:
    st.info("💡 **مرحباً بك!** من فضلك أدخل `Groq API Key` في القائمة الجانبية للبدء.")
    st.stop()

# تهيئة Groq Client
client = Groq(api_key=api_key_input)

# =========================================================
# 4. الذاكرة وعرض الرسائل
# =========================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

# خانة إرفاق صورة اختيارية
with st.expander("📎 إرفاق صورة (تمرين، كود، مسألة رياضية...)", expanded=False):
    uploaded_image = st.file_uploader(
        "اختر صورة:", type=["jpg", "jpeg", "png"], label_visibility="collapsed"
    )

# عرض أرشيف المحادثة
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "✴️"
    with st.chat_message(msg["role"], avatar=avatar):
        if msg.get("image"):
            st.image(
                io.BytesIO(msg["image"]), width=320, caption="الصورة المرفقة"
            )
        st.markdown(msg["content"])

# =========================================================
# 5. التفاعل واستقبال الرسائل
# =========================================================
if prompt := st.chat_input("بماذا يمكنني مساعدتك اليوم؟..."):

    has_image = uploaded_image is not None
    img_bytes = uploaded_image.getvalue() if has_image else None

    # حفظ رسالة المستخدم
    st.session_state.messages.append(
        {"role": "user", "content": prompt, "image": img_bytes}
    )

    # إظهار رسالة المستخدم مباشرة
    with st.chat_message("user", avatar="👤"):
        if has_image:
            st.image(uploaded_image, width=320)
        st.markdown(prompt)

    # تجهيز System Prompt احترافي
    system_prompt = (
        "أنت Claude 3.5 Sonnet، مساعد ذكي ومحترف للغاية من تطوير Anthropic ومُشغل عبر محرك Groq فائق السرعة. "
        "تعليماتك:\n"
        "1. تجيب بدقة عالية جداً وباللغة التي يخاطبك بها المستخدم (الدارجة المغربية، العربية الفصحى، الفرنسية، أو الإنجليزية).\n"
        "2. عند حل التمارين أو المسائل العلمية/البرمجية، اشرح الخطوات بوضوح واستخدم تنسيق Markdown و LaTeX للمعادلات الرياضية مثل: $E = mc^2$.\n"
        "3. إذا كان هناك صورة مرفقة، قم بتحليلها بالكامل، قراءة النصوص الموجودة فيها بدقة وحل المطلوب مباشرة وباحترافية."
    )

    api_messages = [{"role": "system", "content": system_prompt}]

    # إضافة السياق السابق (آخر 6 رسائل لتوفير التوكنز والحفاظ على السرعة)
    for m in st.session_state.messages[-7:-1]:
        api_messages.append({"role": m["role"], "content": m["content"]})

    # إعداد المحتوى الحالي (Vision أو Text)
    if has_image:
        b64_img = base64.b64encode(img_bytes).decode("utf-8")
        current_payload = [
            {
                "type": "text",
                "text": prompt
                if prompt.strip()
                else "حلل واشرح كل ما يوجد في هذه الصورة بالتفصيل وحل التمارين إن وجدت.",
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{uploaded_image.type};base64,{b64_img}"
                },
            },
        ]
        active_model = VISION_MODEL
    else:
        current_payload = prompt
        active_model = TEXT_MODEL

    api_messages.append({"role": "user", "content": current_payload})

    # توليد الإجابة بالبث المباشر (Streaming)
    with st.chat_message("assistant", avatar="✴️"):
        placeholder = st.empty()
        full_response = ""

        try:
            stream = client.chat.completions.create(
                model=active_model,
                messages=api_messages,
                stream=True,
                temperature=temperature,
            )

            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    full_response += delta
                    placeholder.markdown(full_response + " ▌")

            placeholder.markdown(full_response)

        except Exception as e:
            error_msg = str(e)
            if "rate_limit" in error_msg.lower():
                placeholder.error(
                    "⚠️ تم تجاوز حد الطلبات مؤقتاً، المرجو الانتظار دقيقة والمحاولة مجدداً."
                )
            elif "invalid_api_key" in error_msg.lower():
                placeholder.error(
                    "❌ الـ API Key غير صحيح! تأكد من إدخال مفتاح سليم من Groq."
                )
            else:
                placeholder.error(f"⚠️ **حدث خطأ:** `{error_msg}`")
            full_response = ""

    # حفظ الرد
    if full_response:
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )
