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
    " ตามระเบียบงานสารบรรณ พร้อมวิเคราะห์จากเอกสารต้นเรื่อง"
)

# ดึง API Key จาก Secrets ของระบบ
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

        with st.form("doc_form"):
            st.subheader("📌 ข้อมูลสำหรับร่างบันทึกข้อความ")

            # ช่องอัปโหลดไฟล์หนังสือต้นเรื่อง (PDF หรือ รูปภาพ)
            uploaded_file = st.file_uploader(
                "📂 อัปโหลดหนังสือต้นเรื่อง (PDF หรือ รูปภาพ สำหรับให้ AI อ่านและวิเคราะห์โต้ตอบ)",
                type=["pdf", "png", "jpg", "jpeg"],
            )

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
                "รายละเอียดเพิ่มเติม หรือประเด็นที่ต้องการสั่งการ/ตอบกลับ",
                placeholder=(
                    "ใส่ข้อมูลเพิ่มเติม เช่น ต้องการเสนอความเห็นอย่างไร"
                    " หรือกำหนดการเพิ่มเติม..."
                ),
                height=100,
            )

            submitted = st.form_submit_button(
                "✨ วิเคราะห์และร่างบันทึกข้อความด้วย AI"
            )

        if submitted:
            with st.spinner("AI กำลังอ่านเอกสารและเรียบเรียงเนื้อหาตามหลักสารบรรณ..."):
                contents = []

                # จัดการไฟล์ที่อัปโหลด (แปลงเป็น Part สำหรับ SDK ใหม่)
                if uploaded_file is not None:
                    file_bytes = uploaded_file.getvalue()
                    mime_type = uploaded_file.type
                    file_part = genai.types.Part.from_bytes(
                        data=file_bytes, mime_type=mime_type
                    )
                    contents.append(file_part)

                prompt = f"""
                คุณเป็นผู้เชี่ยวชาญด้านงานสารบรรณราชการไทย 
                จงวิเคราะห์หนังสือต้นเรื่องที่แนบมา (ถ้ามี) ร่วมกับข้อมูลที่ผู้ใช้ระบุ แล้วร่าง "บันทึกข้อความ" อย่างเป็นทางการ:
                - เรียน: {doc_to}
                - จาก: {doc_from}
                - เรื่อง: {doc_subject}
                - วัตถุประสงค์: {doc_objective}
                - รายละเอียดเพิ่มเติม: {doc_details}

                โดยแบ่งโครงสร้างออกเป็น 3 ส่วนชัดเจนตามหลักสารบรรณ:
                1. ภาคเหตุ (อ้างอิงจากหนังสือต้นเรื่องที่แนบมา และสรุปที่มาปัญหา)
                2. ภาคความประสงค์ (สิ่งที่ต้องการให้ดำเนินการ หรือข้อเสนอเพื่อโต้ตอบ/สั่งการ)
                3. ภาคสรุป (ข้อเสนอเพื่อพิจารณาอนุมัติ/โปรดพิจารณา)
                
                ใช้ภาษาทางการที่ถูกต้องกระชับ เหมาะสำหรับราชการไทย
                """
                contents.append(prompt)

                response = client.models.generate_content(
                    model="gemini-3.6-flash", contents=contents
                )

                st.success("✅ ร่างบันทึกข้อความเสร็จเรียบร้อย!")
                st.markdown("### 📄 ผลลัพธ์ร่างบันทึกข้อความ")
                st.markdown(response.text)

    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการเชื่อมต่อ: {e}")
