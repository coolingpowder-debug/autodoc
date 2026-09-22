import streamlit as st
from google import genai
import datetime
import re
import urllib.parse

# ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="App AI ช่วยร่าง-โต้ตอบหนังสือราชการ",
    page_icon="📝",
    layout="wide",
)

# ตกแต่ง CSS เพิ่มความสวยงาม เรียบร้อย
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

# ใช้ st.session_state เพื่อเก็บประวัติและสถิติแบบสะสมต่อเนื่องไม่รีเซต
if "history" not in st.session_state:
    st.session_state.history = []

# หัวข้อและคำอธิบาย
st.title("📝 App AI ช่วยร่าง-โต้ตอบหนังสือราชการ")
st.markdown("อ้างอิงจาก ระเบียบสำนักนายกรัฐมนตรีว่าด้วยงานสารบรรณ พ.ศ. 2526 และหลักการเขียนหนังสือราชการ")
st.markdown("เหมาะสำหรับ ข้าราชการ เจ้าหน้าที่รัฐทั่วไป เจ้าหน้าที่ธุรการและงานสารบรรณ")
st.markdown("⚠️ **กรุณาตรวจสอบความถูกต้องโดยละเอียดอีกครั้งหนึ่ง AI อาจผิดพลาดได้**")
st.markdown("---")

# สร้าง Tabs แยกส่วน
tab1, tab2 = st.tabs(["✨ สร้างหนังสือราชการ", "📊 แดชบอร์ดและสถิติการใช้งาน"])

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
                st.subheader("📌 เลือกประเภทและกำหนดข้อมูลหนังสือ")

                doc_type = st.selectbox(
                    "📂 เลือกประเภทเอกสารราชการ",
                    [
                        "หนังสือภายใน (บันทึกข้อความ)",
                        "หนังสือภายนอก (ตราครุฑ)",
                    ],
                )

                uploaded_file = st.file_uploader(
                    "📂 อัปโหลดหนังสือต้นเรื่อง (ถ้ามี / PDF หรือ รูปภาพ)",
                    type=["pdf", "png", "jpg", "jpeg"],
                )

                col1, col2 = st.columns(2)
                with col1:
                    if doc_type == "หนังสือภายใน (บันทึกข้อความ)":
                        doc_org = st.text_input("ส่วนราชการ (หน่วยงานเจ้าของเรื่อง)", "กลุ่มงาน... โทร. ...")
                        doc_to = st.text_input("เรียน (ผู้รับหนังสือภายใน)", "ผู้อำนวยการ...")
                    else:
                        doc_org = st.text_input("หน่วยงานเจ้าของหนังสือ (มุมซ้ายบน)", "สำนักงาน... / กระทรวง... โทร. ...")
                        doc_to = st.text_input("เรียน (ผู้รับหนังสือภายนอก/บุคคลภายนอก)", "อธิบดีกรม... / ผู้ว่าราชการจังหวัด...")
                with col2:
                    doc_from = st.text_input("จาก / ผู้ลงนาม (สำหรับหนังสือภายนอกระบุชื่อตำแหน่ง)", "ปลัด... / อธิบดี...")
                    doc_subject = st.text_input("เรื่อง", "ขออนุมัติ... / ขอความอนุเคราะห์...")

                doc_ref = st.text_input("อ้างถึง (ถ้ามี เช่น หนังสือเดิมที่เคยติดต่อ)", "")
                doc_materials = st.text_input("สิ่งที่ส่งมาด้วย (ถ้ามี เช่น เอกสารประกอบ 1 ชุด)", "")

                doc_details = st.text_area(
                    "รายละเอียดเพิ่มเติม / ข้อความเนื้อหา (ภาคเหตุ ภาคความประสงค์ ภาคสรุป)",
                    placeholder="ใส่ข้อมูลหรือรายละเอียดที่ต้องการให้ AI เรียบเรียงลงในเนื้อหาหนังสือ...",
                    height=120,
                )

                submitted = st.form_submit_button("✨ สร้างร่างหนังสือราชการด้วย AI")

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

                        if doc_type == "หนังสือภายใน (บันทึกข้อความ)":
                            form_structure = f"""
                            ประเภท: หนังสือภายใน (บันทึกข้อความ)
                            - ส่วนราชการ: {doc_org}
                            - ที่: (เว้นว่างไว้เติมเลขที่) วันที่: (เว้นว่างไว้เติมวันที่)
                            - เรื่อง: {doc_subject}
                            - เรียน: {doc_to}
                            - จาก: {doc_from}
                            """
                        else:
                            form_structure = f"""
                            ประเภท: หนังสือภายนอก (ตราครุฑ)
                            - (มีตราครุฑกึ่งกลางหน้ากระดาษ)
                            - ที่: (เว้นว่างไว้เติมเลขที่)
                            - หน่วยงานเจ้าของหนังสือ: {doc_org}
                            - วันที่: (เว้นว่างไว้เติมวันที่)
                            - เรื่อง: {doc_subject}
                            - เรียน: {doc_to}
                            - อ้างถึง: {doc_ref if doc_ref else "- (ถ้ามี)"}
                            - สิ่งที่ส่งมาด้วย: {doc_materials if doc_materials else "- (ถ้ามี)"}
                            """

                        prompt = f"""
                        คุณเป็นผู้เชี่ยวชาญด้านงานสารบรรณราชการไทย 
                        จงสร้างเนื้อหาหนังสือราชการอย่างเป็นทางการ โดยอ้างอิงระเบียบสำนักนายกรัฐมนตรีว่าด้วยงานสารบรรณ พ.ศ. 2526 
                        ตามรูปแบบโครงสร้างที่ถูกต้องเป๊ะๆ ดังนี้:

                        {form_structure}
                        - ข้อมูลรายละเอียด/อ้างอิงจากต้นเรื่อง: {doc_details}

                        โครงสร้างเนื้อหาภายในแบ่งเป็น 3 ภาค:
                        1. ภาคเหตุ (ระบุที่มา เหตุผลความจำเป็น หรืออ้างอิงหนังสือต้นเรื่อง)
                        2. ภาคความประสงค์ (ระบุความต้องการ หรือสิ่งที่เสนอขอให้ดำเนินการ)
                        3. ภาคสรุป (ข้อเสนอเพื่อโปรดพิจารณาอนุมัติ / โปรดสั่งการ)

                        ส่วนท้าย (เฉพาะหนังสือภายนอก):
                        - ลงท้าย: ขอแสดงความนับถือ
                        - ลงชื่อ: (ลายมือชื่อ)
                        - (พิมพ์ชื่อเต็มในวงเล็บ)
                        - ตำแหน่งผู้ลงนาม: {doc_from}
                        - ส่วนราชการเจ้าของเรื่องและเบอร์ติดต่อ

                        *หมายเหตุ: ขอเนื้อหาเน้นๆ ที่อยู่ในรูปแบบฟอร์มหนังสือราชการที่ถูกต้องตามระเบียบ ใช้ภาษาทางการกระชับ ไม่ต้องเกริ่นนำนอกเหนือจากตัวเนื้อหา*
                        """
                        contents.append(prompt)

                        response = client.models.generate_content(
                            model="gemini-3.6-flash", contents=contents
                        )

                        result_text = response.text
                        current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                        
                        clean_subject = re.sub(r'^(กอง|สำนักงาน|กรม|ฝ่าย|กลุ่มงาน|สำนัก)[^\s]*\s*', '', doc_subject).strip()
                        if not clean_subject:
                            clean_subject = doc_subject

                        st.session_state.history.insert(
                            0,
                            {
                                "doc_type": doc_type,
                                "subject": clean_subject,
                                "has_file": has_file,
                                "date": current_date,
                                "content": result_text,
                            },
                        )

                        st.success("✅ สร้างฟอร์มหนังสือราชการเรียบร้อยแล้วครับ!")
                        st.markdown(f"### 📄 รูปแบบข้อความ ({doc_type}) สำหรับนำไปใช้งาน")
                        st.code(result_text, language="markdown")
                        st.markdown("---")
                        st.markdown(result_text)

        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการเชื่อมต่อ: {e}")

# --- TAB 2: แดชบอร์ดและสถิติการใช้งาน ---
with tab2:
    st.subheader("📊 แดชบอร์ดสรุปสถิติและประวัติการสร้างหนังสือ")
    
    total_docs = len(st.session_state.history)
    total_internal = sum(1 for item in st.session_state.history if "ภายใน" in item["doc_type"])
    total_external = sum(1 for item in st.session_state.history if "ภายนอก" in item["doc_type"])
    total_with_file = sum(1 for item in st.session_state.history if item["has_file"])

    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-number">{total_docs}</div>
                <div class="stat-label">📁 สร้างทั้งหมด</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_s2:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-number" style="color: #17a2b8;">{total_internal}</div>
                <div class="stat-label">📥 หนังสือภายใน</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_s3:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-number" style="color: #6f42c1;">{total_external}</div>
                <div class="stat-label">📤 หนังสือภายนอก</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_s4:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-number" style="color: #28a745;">{total_with_file}</div>
                <div class="stat-label">🟢 มีไฟล์วิเคราะห์</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("### 📋 ตารางประวัติรายการหนังสือ (บันทึกสะสมต่อเนื่อง)")

    if not st.session_state.history:
        st.info("📌 ยังไม่มีประวัติการสร้างหนังสือ ลองสร้างที่แท็บแรกก่อนครับ")
    else:
        dashboard_data = []
        for idx, item in enumerate(st.session_state.history, start=1):
            status_badge = "🟢 มี" if item["has_file"] else "🔴 ไม่มี"
            dashboard_data.append(
                {
                    "ลำดับ": idx,
                    "ประเภทหนังสือ": item["doc_type"],
                    "ข้อความหัวเรื่องที่ระบบสร้างให้ (ปกปิดส่วนราชการ)": item["subject"],
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
            st.markdown(f"**ประเภท:** {selected_item['doc_type']}")
            st.markdown(f"**หัวเรื่อง:** {selected_item['subject']}")
            st.markdown(f"**วันที่สร้าง:** {selected_item['date']}")
            st.code(selected_item["content"], language="markdown")

# --- ส่วนท้าย (Footer) ข้อมูลผู้พัฒนา และอีเมลแบบคลิกดูเต็มๆ ---
st.markdown("---")
st.markdown("🛠️ **สร้างและพัฒนาโดย:** Admin Mine")

col_f1, col_f2 = st.columns([1, 6])
with col_f1:
    st.markdown("**ช่องทางติดต่อ >>**")
with col_f2:
    # ใช้ st.expander เพื่อให้ผู้ใช้คลิก 1 ครั้งเพื่อเปิดดูอีเมลทั้งหมดได้
    with st.expander("📧 คลิกเพื่อดูอีเมลติดต่อฉบับเต็ม"):
        contact_email = "admin.mine@domain.go.th"
        st.markdown(f"อีเมลผู้พัฒนา: `{contact_email}`")
        st.markdown(f"🔗 ส่งอีเมลโดยตรง: [คลิกที่นี่เพื่อส่งอีเมล](mailto:{contact_email})")
    
    # QR Code เชื่อมโยงไปที่อีเมลเช่นเดิม
    contact_email = "admin.mine@domain.go.th"
    mailto_url = f"mailto:{contact_email}"
    encoded_mailto = urllib.parse.quote(mailto_url, safe='')
    qr_api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={encoded_mailto}"
    st.image(qr_api_url, width=45)
