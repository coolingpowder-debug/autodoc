import streamlit as st
from google import genai

# ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="ระบบช่วยเขียนบันทึกข้อความราชการอัจฉริยะ",
    page_icon="📝",
    layout="wide",
)

st.title("📝 ระบบช่วยเขียนบันทึกข้อความ (ด้วยหลักการสารบรรณ)")
st.markdown(
    "ช่วยสังเคราะห์ ภาคเหตุ, ภาคความประสงค์ และภาคสรุป อัตโนมัติ"
    " ตามระเบียบงานสารบรรณ"
)

# ดึง API Key จาก Secrets ของระบบ (ซ่อนไม่ให้คนอื่นเห็น)
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = None

if not api_key:
    st.error(
        "⚠️ ยังไม่ได้ตั้งค่า GEMINI_API_KEY ใน Streamlit Secrets"
        " กรุณาตั้งค่าก่อนใช้งาน"
    )
else:
    try:
        client = genai.Client(api_key=api_key)

        # ฟอร์มรับข้อมูล
        with st.form("doc_form"):
            st.subheader("📌 ข้อมูลสำหรับร่างบันทึกข้อความ")

            col1, col2 = st.columns(2)
            with col1:
                doc_to = st.text_input(
                    "เรียน (หน่วยงานหรือผู้รับรอง)", "ผู้อำนวยการกอง..."
                )
                doc_from = st.text_input("จาก (หน่วยงานผู้ส่ง)", "กลุ่มงาน...")
            with col2:
                doc_subject = st.text_input(
                    "เรื่อง (หัวข้อหลัก)", "ขออนุมัติจัดโครงการ..."
                )
                doc_objective = st.text_input(
                    "วัตถุประสงค์หลัก", "เพื่อพัฒนาทักษะ..."
                )

            doc_details = st.text_area(
                "รายละเอียดหรือข้อมูลดิบ (เหตุผลที่ต้องทำหนังสือฉบับนี้)",
                placeholder=(
                    "ใส่ข้อมูลดิบ เช่น กำหนดการ งบประมาณ"
                    " หรือปัญหาที่พบ..."
                ),
                height=120,
            )

            doc_reference = st.text_area(
                "📄 ข้อความจากหนังสือต้นเรื่อง / เอกสารอ้างอิง (ถ้ามี)",
                placeholder=(
                    "คัดลอกข้อความจากหนังสือต้นเรื่องมาวางที่นี่"
                    " เพื่อให้ AI ช่วยตอบกลับหรืออ้างอิง..."
                ),
                height=120,
            )

            submitted = st.form_submit_button(
                "✨ สังเคราะห์และร่างบันทึกข้อความด้วย AI"
            )

        if submitted:
            if not doc_details and not doc_reference:
                st.error("⚠️ กรุณากรอกรายละเอียด หรือข้อมูลจากหนังสือต้นเรื่องอย่างน้อย 1 ช่อง")
            else:
                with st.spinner("AI กำลังเรียบเรียงเนื้อหาตามหลักสารบรรณ..."):
                    prompt = f"""
                    คุณเป็นผู้เชี่ยวชาญด้านงานสารบรรณราชการไทย 
                    จงร่าง "บันทึกข้อความ" อย่างเป็นทางการ โดยอิงจากข้อมูลต่อไปนี้:
                    - เรียน: {doc_to}
                    - จาก: {doc_from}
                    - เรื่อง: {doc_subject}
                    - วัตถุประสงค์: {doc_objective}
                    - รายละเอียด/ข้อมูลดิบ: {doc_details}
                    - ข้อมูลจากหนังสือต้นเรื่อง/อ้างอิง: {doc_reference}

                    โดยแบ่งโครงสร้างออกเป็น 3 ส่วนชัดเจนตามหลักสารบรรณ:
                    1. ภาคเหตุ (ที่มาและปัญหา หรืออ้างอิงหนังสือต้นเรื่อง)
                    2. ภาคความประสงค์ (สิ่งที่ต้องการให้ดำเนินการ หรือขออนุมัติอะไร)
                    3. ภาคสรุป (ข้อเสนอเพื่อพิจารณาอนุมัติ/โปรดพิจารณา)
                    
                    ใช้ภาษาทางการที่ถูกต้องกระชับ เหมาะสำหรับราชการไทย
                    """

                    response = client.models.generate_content(
                        model="gemini-2.5-flash", contents=prompt
                    )

                    st.success("✅ ร่างบันทึกข้อความเสร็จเรียบร้อย!")
                    st.markdown("### 📄 ผลลัพธ์ร่างบันทึกข้อความ")
                    st.markdown(response.text)

    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการเชื่อมต่อ: {e}")
