import streamlit as st
import sqlite3
import hashlib
import datetime
import random
from fpdf import FPDF
import qrcode

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="CourseHub 🎓", layout="wide")

# ---------------- PREMIUM UI ----------------
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">

<style>

/* 🌈 Animated Gradient Background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(
        180deg,
        #ff003c,
        #ff5e00,
        #ff9900,
        #7a5cff,
        #3a86ff,
        #00c853
    );
    background-size: 400% 400%;
    animation: gradientMove 12s ease infinite;
}

/* Animation */
@keyframes gradientMove {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

/* Glass UI */
.block-container {
    background: rgba(0,0,0,0.55);
    padding: 25px;
    border-radius: 15px;
    color: white;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: rgba(0,0,0,0.7);
}

/* Font */
* {
    font-family: 'Poppins', sans-serif !important;
}

/* Buttons */
.stButton>button {
    border-radius: 12px;
    padding: 10px 18px;
    background: linear-gradient(45deg, #ff4d00, #ff9900);
    color: white;
    border: none;
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
        password TEXT,
        role TEXT DEFAULT 'student'
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
        content TEXT,
        video_url TEXT,
        type TEXT
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

# ---------------- MENU ----------------
menu = ["Login","Register"]

if st.session_state.user:
    if st.session_state.user[4] == "admin":
        menu = ["Admin Panel","Logout"]
    else:
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

# ---------------- ADMIN PANEL ----------------
elif choice == "Admin Panel":
    st.subheader("⚙️ Admin Dashboard")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📚 Add Course",
        "🎥 Add Content",
        "👨‍🎓 Users Activity",
        "📜 Certificates"
    ])

    # Add Course
    with tab1:
        title = st.text_input("Course Title")
        desc = st.text_area("Description")

        if st.button("Add Course"):
            c.execute("INSERT INTO courses(title,description) VALUES(?,?)",(title,desc))
            conn.commit()
            st.success("Course Added!")

    # Add Lesson
    with tab2:
        c.execute("SELECT * FROM courses")
        courses = c.fetchall()
        course_dict = {course[1]: course[0] for course in courses}

        selected_course = st.selectbox("Select Course", list(course_dict.keys()))
        lesson_title = st.text_input("Lesson Title")
        lesson_content = st.text_area("Article Content")
        video_url = st.text_input("Video URL")
        lesson_type = st.selectbox("Type", ["video","article"])

        if st.button("Add Lesson"):
            c.execute("""INSERT INTO lessons(course_id,title,content,video_url,type)
                         VALUES(?,?,?,?,?)""",
                      (course_dict[selected_course], lesson_title, lesson_content, video_url, lesson_type))
            conn.commit()
            st.success("Lesson Added!")

    # Users Activity
    with tab3:
        c.execute("SELECT * FROM users")
        users = c.fetchall()

        for u in users:
            st.write(f"👤 {u[1]} ({u[2]})")

            c.execute("""
            SELECT lessons.title FROM progress
            JOIN lessons ON progress.lesson_id = lessons.id
            WHERE progress.user_id=?
            """,(u[0],))

            progress = c.fetchall()

            if progress:
                for p in progress:
                    st.write(f"   ✅ {p[0]}")
            else:
                st.write("   ❌ No progress")

    # Certificates
    with tab4:
        c.execute("SELECT * FROM certificates")
        certs = c.fetchall()

        for cert in certs:
            st.write(f"📜 {cert[0]} | {cert[1]} | {cert[2]} | {cert[3]}")

# ---------------- COURSES ----------------
elif choice == "Courses":
    c.execute("SELECT * FROM courses")
    courses = c.fetchall()

    for course in courses:
        st.subheader(course[1])
        st.write(course[2])

        if st.button(f"Open {course[1]}", key=course[0]):
            st.session_state.course_id = course[0]

    if "course_id" in st.session_state:
        c.execute("SELECT * FROM lessons WHERE course_id=?",(st.session_state.course_id,))
        lessons = c.fetchall()

        for lesson in lessons:
            st.write(f"### {lesson[2]}")

            if lesson[5] == "video" and lesson[4]:
                st.video(lesson[4])
            else:
                st.write(lesson[3])

            if st.button(f"Complete {lesson[0]}", key=f"l{lesson[0]}"):
                c.execute("INSERT INTO progress VALUES(?,?)",
                          (st.session_state.user[0], lesson[0]))
                conn.commit()
                st.success("Completed!")

# ---------------- DASHBOARD ----------------
elif choice == "Dashboard":
    st.subheader(f"Welcome {st.session_state.user[1]} 👋")

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
