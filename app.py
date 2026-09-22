import streamlit as st
from google import genai
import datetime

# ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="App AI ช่วยร่าง-โต้ตอบหนังสือราชการ",
    page_icon="📝",
    layout="wide",
)

# ตกแต่ง CSS เพิ่มความสวยงามให้แดชบอร์ดและการ์ดสถิติ
st.markdown(
    """
    <style>
    .stat-card {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .stat-number {
        font-size: 32px;
        font-weight: bold;
        color: #1f77b4;
    }
    .stat-label {
        font-size: 16px;
        color: #6c757d;
        margin-top: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ใช้ st.session_state เพื่อเก็บบันทึกประวัติ
if "history" not in st.session_state:
    st.session_state.history = []

# หัวข้อและคำอธิบายตามที่กำหนด
st.title("📝 App AI ช่วยร่าง-โต้ตอบหนังสือราชการ")
st.markdown("อ้างอิงจาก ระเบียบสำนักนายกรัฐมนตรีว่าด้วยงานสารบรรณ พ.ศ. 2526 และหลักการเขียนหนังสือราชการ")
st.markdown("เหมาะสำหรับ ข้าราชการ เจ้าหน้าที่รัฐทั่วไป เจ้าหน้าที่ธุรการและงานสารบรรณ")
st.markdown("⚠️ **กรุณาตรวจสอบความถูกต้องโดยละเอียดอีกครั้งหนึ่ง AI อาจผิดพลาดได้**")
st.markdown("---")

# สร้าง Tabs แยกส่วน
tab1, tab2 = st.tabs(["✨ สร้างบันทึกข้อความ", "📊 แดชบอร์ดและสถิติการใช้งาน"])

# --- TAB 1: ฟอร์มสร้างเอกสาร ---
with tab1:
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
                if not doc_subject:
                    st.warning("⚠️ กรุณาระบุหัวข้อเรื่อง")
                else:
                    with st.spinner("AI กำลังจัดฟอร์มและเรียบเรียงตามรูปแบบสารบรรณ..."):
                        contents = []
                        has_file = uploaded_file is not None

                        if has_file:
                            file_bytes = uploaded_file.getvalue()
                            mime_type = uploaded_file.type
                            file_part = genai.types.Part.from_bytes(
                                data=file_bytes, mime_type=mime_type
                            )
                            contents.append(file_part)

                        prompt = f"""
                        คุณเป็นผู้เชี่ยวชาญด้านงานสารบรรณราชการไทย 
                        จงสร้างเนื้อหา "บันทึกข้อความ" ตามรูปแบบฟอร์มหนังสือราชการไทยอย่างเป็นทางการ โดยอ้างอิงระเบียบสำนักนายกรัฐมนตรีว่าด้วยงานสารบรรณ พ.ศ. 2526 โดยจัดรูปแบบโครงสร้างและข้อความให้ออกมาเป็นฟอร์มพร้อมคัดลอกไปใส่เอกสาร Word ดังนี้:

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

                        result_text = response.text
                        current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                        
                        st.session_state.history.insert(
                            0,
                            {
                                "subject": doc_subject,
                                "has_file": has_file,
                                "date": current_date,
                                "content": result_text,
                            },
                        )

                        st.success("✅ สร้างฟอร์มบันทึกข้อความเรียบร้อยแล้วครับ!")
                        st.markdown("### 📄 รูปแบบข้อความสำหรับนำไปใส่ฟอร์มราชการ")
                        st.code(result_text, language="markdown")
                        st.markdown("---")
                        st.markdown(result_text)

        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการเชื่อมต่อ: {e}")

# --- TAB 2: แดชบอร์ดและสถิติการใช้งาน ---
with tab2:
    st.subheader("📊 แดชบอร์ดสรุปสถิติและประวัติการสร้างหนังสือ")
    
    total_docs = len(st.session_state.history)
    total_with_file = sum(1 for item in st.session_state.history if item["has_file"])
    total_without_file = total_docs - total_with_file

    # แสดงการ์ดสถิติด้านบน
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-number">{total_docs}</div>
                <div class="stat-label">📁 จำนวนครั้งที่สร้างทั้งหมด</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_s2:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-number" style="color: #28a745;">{total_with_file}</div>
                <div class="stat-label">🟢 มีการอัปโหลดไฟล์วิเคราะห์</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_s3:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-number" style="color: #dc3545;">{total_without_file}</div>
                <div class="stat-label">🔴 สร้างจากข้อความอย่างเดียว</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("### 📋 ตารางประวัติรายการหนังสือ")

    if not st.session_state.history:
        st.info("📌 ยังไม่มีประวัติการสร้างหนังสือ ลองสร้างที่แท็บแรกก่อนครับ")
    else:
        dashboard_data = []
        for idx, item in enumerate(st.session_state.history, start=1):
            status_badge = "🟢 มี (อัปโหลดแล้ว)" if item["has_file"] else "🔴 ไม่มี (ไม่ได้อัปโหลด)"
            dashboard_data.append(
                {
                    "ลำดับ": idx,
                    "หัวเรื่องหนังสือที่ AI สร้างให้": item["subject"],
                    "สถานะอัพโหลดหนังสือให้วิเคราะห์เนื้อหา": status_badge,
                    "วันที่สร้าง": item["date"],
                }
            )

        st.dataframe(dashboard_data, use_container_width=True)

        st.markdown("---")
        st.markdown("### 🔍 เรียกดูเนื้อหาหนังสือย้อนหลัง")
        selected_index = st.selectbox(
            "เลือกรายการลำดับที่ต้องการเปิดดูเนื้อหา:",
            options=[item["ลำดับ"] for item in dashboard_data],
        )

        if selected_index:
            selected_item = st.session_state.history[selected_index - 1]
            st.markdown(f"**หัวเรื่อง:** {selected_item['subject']}")
            st.markdown(f"**วันที่สร้าง:** {selected_item['date']}")
            st.code(selected_item["content"], language="markdown")
