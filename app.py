import streamlit as st
import sqlite3
import hashlib
import datetime
import random
from fpdf import FPDF
import qrcode

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="CourseHub 🎓", layout="wide")

# ---------------- UI ----------------
st.title("🎓 CourseHub Academy")

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

# ---------------- SESSION ----------------
if "user" not in st.session_state:
    st.session_state.user = None

# ---------------- MENU ----------------
menu = ["Login","Register"]

if st.session_state.user:
    if st.session_state.user[4] == "admin":
        menu = ["Admin Panel","Logout"]
    else:
        menu = ["Dashboard","Courses","Logout"]

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

    # ---- ADD COURSE ----
    with tab1:
        title = st.text_input("Course Title")
        desc = st.text_area("Description")

        if st.button("Add Course"):
            c.execute("INSERT INTO courses(title,description) VALUES(?,?)",(title,desc))
            conn.commit()
            st.success("Course Added!")

    # ---- ADD VIDEO / ARTICLE ----
    with tab2:
        c.execute("SELECT * FROM courses")
        courses = c.fetchall()
        course_dict = {course[1]: course[0] for course in courses}

        selected_course = st.selectbox("Select Course", list(course_dict.keys()))
        lesson_title = st.text_input("Lesson Title")
        lesson_content = st.text_area("Article Content")
        video_url = st.text_input("Video URL (YouTube etc)")
        lesson_type = st.selectbox("Type", ["video","article"])

        if st.button("Add Lesson"):
            c.execute("""INSERT INTO lessons(course_id,title,content,video_url,type)
                         VALUES(?,?,?,?,?)""",
                      (course_dict[selected_course], lesson_title, lesson_content, video_url, lesson_type))
            conn.commit()
            st.success("Lesson Added!")

    # ---- USER ACTIVITY ----
    with tab3:
        st.subheader("Users Progress")

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

    # ---- CERTIFICATES ----
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

# ---------------- LOGOUT ----------------
elif choice == "Logout":
    st.session_state.user = None
    st.success("Logged out")
