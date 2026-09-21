import streamlit as st
from google import genai

# ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="ระบบพิมพ์บันทึกข้อความราชการ",
    page_icon="📝",
    layout="wide",
)

st.title("📝 ระบบพิมพ์ร่างบันทึกข้อความราชการ (ฟอร์มมาตรฐาน)")
st.markdown("กรอกข้อมูลหรืออัปโหลดเอกสารต้นเรื่อง แล้ว AI จะจัดหน้าเป็นฟอร์มบันทึกข้อความราชการพร้อมใช้งาน")

# ดึง API Key จาก Secrets ของระบบ
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = None

if not api_key:
    st.error("⚠️ ยังไม่ได้ตั้งค่า GEMINI_API_KEY ใน Streamlit Secrets กรุณาตั้งค่าก่อนใช้งาน")
else:
    try:
        client = genai.Client(api_key=api_key)

        with st.form("doc_form"):
            st.subheader("📌 กำหนดข้อมูลหัวหนังสือและรายละเอียด")

            uploaded_file = st.file_uploader(
                "📂 อัปโหลดหนังสือต้นเรื่อง (ถ้ามี / PDF หรือ รูปภาพ)",
                type=["pdf", "png", "jpg", "jpeg"],
            )

            col1, col2 = st.columns(2)
            with col1:
                doc_org = st.text_input("ส่วนราชการ (หน่วยงานเจ้าของเรื่อง)", "... โทร. ...")
                doc_to = st.text_input("เรียน (ผู้รับหนังสือ/ผู้บังคับบัญชา)", "ผู้อำนวยการ...")
            with col2:
                doc_from = st.text_input("จาก (ผู้ส่งหนังสือ/กลุ่มงาน)", "...")
                doc_subject = st.text_input("เรื่อง", "ขออนุมัติ...")

            doc_details = st.text_area(
                "รายละเอียดเพิ่มเติม / ข้อสั่งการ / ประเด็นโต้ตอบ",
                placeholder="ใส่ข้อมูลที่ต้องการให้ AI เรียบเรียงลงในเนื้อหาหนังสือ...",
                height=120,
            )

            submitted = st.form_submit_button("✨ สร้างฟอร์มบันทึกข้อความราชการ")

        if submitted:
            with st.spinner("AI กำลังจัดฟอร์มและเรียบเรียงตามรูปแบบสารบรรณ..."):
                contents = []

                if uploaded_file is not None:
                    file_bytes = uploaded_file.getvalue()
                    mime_type = uploaded_file.type
                    file_part = genai.types.Part.from_bytes(
                        data=file_bytes, mime_type=mime_type
                    )
                    contents.append(file_part)

                prompt = f"""
                คุณเป็นผู้เชี่ยวชาญด้านงานสารบรรณราชการไทย 
                จงสร้างเนื้อหา "บันทึกข้อความ" ตามรูปแบบฟอร์มหนังสือราชการไทยอย่างเป็นทางการ โดยจัดรูปแบบโครงสร้างและข้อความให้ออกมาเป็นฟอร์มพร้อมคัดลอกไปใส่เอกสาร Word ดังนี้:

                - ส่วนราชการ: {doc_org}
                - ที่: (เว้นว่างไว้เติมเลขที่) วันที่: (เว้นว่างไว้เติมวันที่)
                - เรื่อง: {doc_subject}
                - เรียน: {doc_to}
                - จาก: {doc_from}
                - ข้อมูลรายละเอียด/อ้างอิงจากต้นเรื่อง: {doc_details}

                โครงสร้างเนื้อหาภายในแบ่งเป็น:
                1. ภาคเหตุ (ระบุที่มาหรือเหตุผลความจำเป็น หรืออ้างอิงหนังสือต้นเรื่อง)
                2. ภาคความประสงค์ (ระบุความต้องการหรือสิ่งที่เสนอขอให้ดำเนินการ)
                3. ภาคสรุป (ข้อเสนอเพื่อโปรดพิจารณาอนุมัติ / โปรดสั่งการ)

                *หมายเหตุ: ขอเนื้อหาเน้นๆ ที่อยู่ในรูปแบบฟอร์มบันทึกข้อความราชการ ใช้ภาษาทางการที่ถูกต้องกระชับ ไม่ต้องเกริ่นนำนอกเหนือจากตัวเนื้อหาหนังสือ*
                """
                contents.append(prompt)

                response = client.models.generate_content(
                    model="gemini-3.6-flash", contents=contents
                )

                st.success("✅ สร้างฟอร์มบันทึกข้อความเรียบร้อยแล้วครับ!")
                st.markdown("### 📄 รูปแบบข้อความสำหรับนำไปใส่ฟอร์มราชการ")
                
                # แสดงผลในกล่องข้อความเพื่อให้กด Copy ง่ายๆ
                st.code(response.text, language="markdown")
                
                # แสดงผลแบบปกติด้วย
                st.markdown("---")
                st.markdown(response.text)

    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการเชื่อมต่อ: {e}")
