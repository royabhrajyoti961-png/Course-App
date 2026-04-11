import streamlit as st
import sqlite3
import hashlib
import datetime
import random
from fpdf import FPDF
import qrcode

# ---------------- CONFIG ----------------
st.set_page_config(page_title="CourseHub Pro 🎓", layout="wide")

# ---------------- PRO UI ----------------
st.markdown("""
<style>

/* BACKGROUND */
[data-testid="stAppViewContainer"] {
    background: #0f172a;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: #020617;
}

/* TEXT */
h1, h2, h3, h4, h5 {
    color: white;
}

/* CONTAINER */
.block-container {
    padding: 2rem 3rem;
}

/* CARD */
.card {
    background: #1e293b;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 20px;
    box-shadow: 0px 5px 25px rgba(0,0,0,0.4);
}

/* BUTTON */
.stButton>button {
    background: #3b82f6;
    color: white;
    border-radius: 10px;
    border: none;
}

/* INPUT */
input, textarea {
    background: #1e293b !important;
    color: white !important;
}

/* METRIC BOX */
.metric-box {
    background: #1e293b;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
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
        role TEXT
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

def login(email,password):
    c.execute("SELECT * FROM users WHERE email=? AND password=?",
              (email,hash_password(password)))
    return c.fetchone()

# ---------------- SESSION ----------------
if "user" not in st.session_state:
    st.session_state.user = None
if "role_selected" not in st.session_state:
    st.session_state.role_selected = None

# ---------------- ROLE SELECT ----------------
if st.session_state.role_selected is None:
    st.title("🚀 CourseHub Platform")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🎓 Student Portal"):
            st.session_state.role_selected = "student"

    with col2:
        if st.button("⚙️ Admin Portal"):
            st.session_state.role_selected = "admin"

    st.stop()

# ---------------- MENU ----------------
menu = []
if st.session_state.user is None:
    menu = ["Login","Register"]
else:
    if st.session_state.user[4] == "admin":
        menu = ["Admin Panel","Logout"]
    else:
        menu = ["Dashboard","Courses","Logout"]

choice = st.sidebar.selectbox("Menu",menu)

# ---------------- REGISTER ----------------
if choice == "Register":
    st.subheader(f"{st.session_state.role_selected.capitalize()} Register")

    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        try:
            c.execute("INSERT INTO users(name,email,password,role) VALUES(?,?,?,?)",
                      (name,email,hash_password(password),st.session_state.role_selected))
            conn.commit()
            st.success("Registered Successfully!")
        except:
            st.error("Email already exists!")

# ---------------- LOGIN ----------------
elif choice == "Login":
    st.subheader(f"{st.session_state.role_selected.capitalize()} Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = login(email,password)
        if user and user[4] == st.session_state.role_selected:
            st.session_state.user = user
            st.success("Login Successful!")
        else:
            st.error("Invalid credentials or wrong portal!")

# ---------------- DASHBOARD ----------------
elif choice == "Dashboard":
    st.title(f"👋 Welcome {st.session_state.user[1]}")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="metric-box"><h3>📚 Courses</h3><h2>5</h2></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-box"><h3>✅ Completed</h3><h2>2</h2></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-box"><h3>📜 Certificates</h3><h2>1</h2></div>', unsafe_allow_html=True)

# ---------------- COURSES ----------------
elif choice == "Courses":
    st.title("📚 Courses")

    c.execute("SELECT * FROM courses")
    courses = c.fetchall()

    cols = st.columns(3)

    for i, course in enumerate(courses):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="card">
                <h3>{course[1]}</h3>
                <p>{course[2]}</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("Open", key=course[0]):
                st.session_state.course_id = course[0]

    if "course_id" in st.session_state:
        st.markdown("## 📖 Lessons")

        c.execute("SELECT * FROM lessons WHERE course_id=?",(st.session_state.course_id,))
        lessons = c.fetchall()

        for lesson in lessons:
            st.markdown(f'<div class="card"><h4>{lesson[2]}</h4></div>', unsafe_allow_html=True)

            if lesson[5]=="video":
                st.video(lesson[4])
            else:
                st.write(lesson[3])

# ---------------- ADMIN PANEL ----------------
elif choice == "Admin Panel":
    st.title("⚙️ Admin Panel")

    tab1, tab2 = st.tabs(["Courses","Add Lesson"])

    with tab1:
        title = st.text_input("Course Title")
        desc = st.text_area("Description")

        if st.button("Add Course"):
            c.execute("INSERT INTO courses(title,description) VALUES(?,?)",(title,desc))
            conn.commit()
            st.success("Course Added")

    with tab2:
        c.execute("SELECT * FROM courses")
        courses = c.fetchall()
        course_dict = {c[1]:c[0] for c in courses}

        course = st.selectbox("Select Course", list(course_dict.keys()))
        title = st.text_input("Lesson Title")
        content = st.text_area("Content")
        video = st.text_input("Video URL")
        typ = st.selectbox("Type",["video","article"])

        if st.button("Add Lesson"):
            c.execute("INSERT INTO lessons(course_id,title,content,video_url,type) VALUES(?,?,?,?,?)",
                      (course_dict[course],title,content,video,typ))
            conn.commit()
            st.success("Lesson Added")

# ---------------- LOGOUT ----------------
elif choice == "Logout":
    st.session_state.user = None
    st.session_state.role_selected = None
    st.success("Logged out")
