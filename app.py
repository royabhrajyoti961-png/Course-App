import streamlit as st
from reportlab.pdfgen import canvas
from io import BytesIO

st.set_page_config(page_title="Course Dashboard", layout="wide")
# 1. Mock Data
courses = [
    {"id": 1, "title": "Full Stack Web Dev", "desc": "Learn React and Flask", "completed": True},
    {"id": 2, "title": "AI & Machine Learning", "desc": "Master Python for AI", "completed": False}
]
# 2. Certificate Logic (Returns a buffer instead of a file)
def generate_certificate(user_name, course_name):
    buffer = BytesIO()
    c = canvas.Canvas(buffer)
    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(300, 700, "CERTIFICATE OF COMPLETION")
    c.setFont("Helvetica", 20)
    c.drawCentredString(300, 600, f"This is to certify that {user_name}")
    c.drawCentredString(300, 550, f"has successfully completed {course_name}")
    c.save()
    buffer.seek(0)
    return buffer

# 3. UI Layout
st.title("My Learning Dashboard")
user_name = st.sidebar.text_input("Student Name", "John Doe")

cols = st.columns(len(courses))

for i, course in enumerate(courses):
    with cols[i]:
        st.subheader(course["title"])
        st.write(course["desc"])
        
        if course["completed"]:
            st.success("Completed!")
            pdf = generate_certificate(user_name, course["title"])
            st.download_button(
                label="Download Certificate",
                data=pdf,
                file_name=f"{course['title']}_Cert.pdf",
                mime="application/pdf"
            )
        else:
            st.info("In Progress")
            st.progress(40)
