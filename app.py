import streamlit as st
import sqlite3
import hashlib
import datetime
import random
from fpdf import FPDF
import qrcode

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="CourseHub 🎓", layout="wide")

# ---------------- POPPINS FONT (FINAL FIX) ----------------
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">

<style>
* {
    font-family: 'Poppins', sans-serif !important;
}

[data-testid="stAppViewContainer"] * {
    font-family: 'Poppins', sans-serif !important;
}

[data-testid="stSidebar"] * {
    font-family: 'Poppins', sans-serif !important;
}

button, input, textarea {
    font-family: 'Poppins', sans-serif !important;
}

h1 { font-weight: 700; }
h2 { font-weight: 600; }
h3 { font-weight: 600; }

.stButton>button {
    border-radius: 12px;
    padding: 10px 18px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- DB ----------------
conn = sqlite3.connect("coursehub.db", check_same_thread=False)
c = conn.cursor()

def create_tables():
    c.execute('''CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS courses(
        id INTEGER PRIMARY KEY,
        title TEXT,
        description TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS lessons(
        id INTEGER PRIMARY KEY,
        course_id INTEGER,
        title TEXT,
        content TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS progress(
        user_id INTEGER,
        lesson_id INTEGER
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS certificates(
        cert_id TEXT,
        user_name TEXT,
        course_name TEXT,
        date TEXT
    )''')
    conn.commit()

create_tables()

# ---------------- UTILS ----------------
def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

def generate_cert_id():
    return f"CERT-{datetime.datetime.now().year}-{random.randint(10000,99999)}"

# ---------------- AUTH ----------------
def register(name,email,password):
    try:
        c.execute("INSERT INTO users(name,email,password) VALUES(?,?,?)",
                  (name,email,hash_password(password)))
        conn.commit()
        return True
    except:
        return False

def login(email,password):
    c.execute("SELECT * FROM users WHERE email=? AND password=?",
              (email,hash_password(password)))
    return c.fetchone()

# ---------------- CERTIFICATE ----------------
def generate_certificate(user, course, cert_id):
    qr = qrcode.make(f"Certificate ID: {cert_id}")
    qr.save("qr.png")

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial","B",22)
    pdf.cell(0,20,"CERTIFICATE OF COMPLETION",ln=True,align="C")

    pdf.ln(10)
    pdf.set_font("Arial","",14)
    pdf.cell(0,10,"This is to certify that",ln=True,align="C")

    pdf.set_font("Arial","B",18)
    pdf.cell(0,10,user,ln=True,align="C")

    pdf.set_font("Arial","",14)
    pdf.cell(0,10,"has successfully completed the course",ln=True,align="C")

    pdf.set_font("Arial","B",16)
    pdf.cell(0,10,course,ln=True,align="C")

    pdf.ln(10)
    pdf.cell(0,10,f"Certificate ID: {cert_id}",ln=True,align="C")

    date = datetime.date.today()
    pdf.cell(0,10,f"Date: {date}",ln=True,align="C")

    pdf.image("qr.png", x=80, y=160, w=50)

    file = f"{cert_id}.pdf"
    pdf.output(file)
    return file

# ---------------- SESSION ----------------
if "user" not in st.session_state:
    st.session_state.user = None

# ---------------- UI ----------------
st.title("🎓 CourseHub Academy")

menu = ["Login","Register"]
if st.session_state.user:
    menu = ["Dashboard","Courses","Verify Certificate","Logout"]

choice = st.sidebar.selectbox("Menu",menu)

# ---------------- REGISTER ----------------
if choice == "Register":
    st.subheader("Create Account")
    n = st.text_input("Name")
    e = st.text_input("Email")
    p = st.text_input("Password", type="password")

    if st.button("Register"):
        if register(n,e,p):
            st.success("Registered Successfully!")
        else:
            st.error("Email already exists!")

# ---------------- LOGIN ----------------
elif choice == "Login":
    st.subheader("Login")
    e = st.text_input("Email")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        user = login(e,p)
        if user:
            st.session_state.user = user
            st.success("Login Successful!")
        else:
            st.error("Invalid credentials")

# ---------------- DASHBOARD ----------------
elif choice == "Dashboard":
    st.subheader(f"Welcome {st.session_state.user[1]} 👋")
    st.write("Start learning and earn certificates!")

# ---------------- COURSES ----------------
elif choice == "Courses":

    c.execute("SELECT * FROM courses")
    if not c.fetchall():
        c.execute("INSERT INTO courses(title,description) VALUES('Python Basics','Learn Python')")
        c.execute("INSERT INTO lessons(course_id,title,content) VALUES(1,'Intro','Python Introduction')")
        c.execute("INSERT INTO lessons(course_id,title,content) VALUES(1,'Variables','Learn Variables')")
        conn.commit()

    c.execute("SELECT * FROM courses")
    courses = c.fetchall()

    for course in courses:
        st.subheader(course[1])
        st.write(course[2])

        if st.button(f"Open Course {course[0]}"):
            st.session_state.course_id = course[0]

    if "course_id" in st.session_state:
        st.subheader("Lessons")

        c.execute("SELECT * FROM lessons WHERE course_id=?",
                  (st.session_state.course_id,))
        lessons = c.fetchall()

        for lesson in lessons:
            st.write(f"### {lesson[2]}")
            st.write(lesson[3])

            if st.button(f"Complete Lesson {lesson[0]}"):
                c.execute("INSERT INTO progress VALUES(?,?)",
                          (st.session_state.user[0], lesson[0]))
                conn.commit()
                st.success("Lesson Completed!")

        c.execute("SELECT COUNT(*) FROM lessons WHERE course_id=?",
                  (st.session_state.course_id,))
        total = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM progress WHERE user_id=?",
                  (st.session_state.user[0],))
        done = c.fetchone()[0]

        if done >= total:
            if st.button("Generate Certificate 🎓"):
                cert_id = generate_cert_id()

                file = generate_certificate(
                    st.session_state.user[1],
                    "Python Basics",
                    cert_id
                )

                c.execute("INSERT INTO certificates VALUES(?,?,?,?)",
                          (cert_id, st.session_state.user[1], "Python Basics", str(datetime.date.today())))
                conn.commit()

                with open(file,"rb") as f:
                    st.download_button("Download Certificate", f, file)

# ---------------- VERIFY ----------------
elif choice == "Verify Certificate":
    st.subheader("Verify Certificate")

    cid = st.text_input("Enter Certificate ID")

    if st.button("Verify"):
        c.execute("SELECT * FROM certificates WHERE cert_id=?", (cid,))
        data = c.fetchone()

        if data:
            st.success("Valid Certificate ✅")
            st.write(f"Name: {data[1]}")
            st.write(f"Course: {data[2]}")
            st.write(f"Date: {data[3]}")
        else:
            st.error("Invalid Certificate ❌")

# ---------------- LOGOUT ----------------
elif choice == "Logout":
    st.session_state.user = None
    st.success("Logged out")
