import streamlit as st
import sqlite3
import hashlib
from fpdf import FPDF
import datetime

# ---------------- DATABASE ----------------
conn = sqlite3.connect("course_app.db", check_same_thread=False)
c = conn.cursor()

def create_tables():
    c.execute('''CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS courses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS lessons(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER,
        title TEXT,
        content TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS progress(
        user_id INTEGER,
        lesson_id INTEGER
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS certificates(
        user_id INTEGER,
        course_id INTEGER,
        date TEXT
    )''')

    conn.commit()

create_tables()

# ---------------- UTILS ----------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(name, email, password):
    try:
        c.execute("INSERT INTO users(name,email,password) VALUES(?,?,?)",
                  (name, email, hash_password(password)))
        conn.commit()
        return True
    except:
        return False

def login_user(email, password):
    c.execute("SELECT * FROM users WHERE email=? AND password=?",
              (email, hash_password(password)))
    return c.fetchone()

# ---------------- CERTIFICATE ----------------
def generate_certificate(user_name, course_name):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 20)
    pdf.cell(0, 20, "CERTIFICATE OF COMPLETION", ln=True, align="C")

    pdf.ln(20)
    pdf.set_font("Arial", "", 14)
    pdf.cell(0, 10, f"This is to certify that", ln=True, align="C")

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, user_name, ln=True, align="C")

    pdf.set_font("Arial", "", 14)
    pdf.cell(0, 10, "has successfully completed", ln=True, align="C")

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, course_name, ln=True, align="C")

    date = datetime.date.today()
    pdf.ln(10)
    pdf.cell(0, 10, f"Date: {date}", ln=True, align="C")

    file_name = f"{user_name}_{course_name}.pdf"
    pdf.output(file_name)

    return file_name

# ---------------- SESSION ----------------
if "user" not in st.session_state:
    st.session_state.user = None

# ---------------- UI ----------------
st.title("🎓 Free Course App with Certificates")

menu = ["Login", "Register"]
if st.session_state.user:
    menu = ["Dashboard", "Courses", "Logout"]

choice = st.sidebar.selectbox("Menu", menu)

# ---------------- REGISTER ----------------
if choice == "Register":
    st.subheader("Create Account")
    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        if register_user(name, email, password):
            st.success("Registered Successfully!")
        else:
            st.error("Email already exists!")

# ---------------- LOGIN ----------------
elif choice == "Login":
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = login_user(email, password)
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
    st.subheader("Courses")

    # sample course auto insert
    c.execute("SELECT * FROM courses")
    if not c.fetchall():
        c.execute("INSERT INTO courses(title,description) VALUES('Python Basics','Learn Python')")
        conn.commit()

        c.execute("INSERT INTO lessons(course_id,title,content) VALUES(1,'Intro','Python Introduction')")
        c.execute("INSERT INTO lessons(course_id,title,content) VALUES(1,'Variables','Learn Variables')")
        conn.commit()

    c.execute("SELECT * FROM courses")
    courses = c.fetchall()

    for course in courses:
        st.write(f"### {course[1]}")
        st.write(course[2])

        if st.button(f"Open {course[0]}"):
            st.session_state.course_id = course[0]

    # show lessons
    if "course_id" in st.session_state:
        st.subheader("Lessons")
        c.execute("SELECT * FROM lessons WHERE course_id=?",
                  (st.session_state.course_id,))
        lessons = c.fetchall()

        for lesson in lessons:
            st.write(f"**{lesson[2]}**")
            st.write(lesson[3])

            if st.button(f"Complete {lesson[0]}"):
                c.execute("INSERT INTO progress(user_id,lesson_id) VALUES(?,?)",
                          (st.session_state.user[0], lesson[0]))
                conn.commit()
                st.success("Marked Completed")

        # check completion
        c.execute("SELECT COUNT(*) FROM lessons WHERE course_id=?",
                  (st.session_state.course_id,))
        total = c.fetchone()[0]

        c.execute("""SELECT COUNT(*) FROM progress 
                     WHERE user_id=?""",
                  (st.session_state.user[0],))
        done = c.fetchone()[0]

        if done >= total:
            if st.button("Generate Certificate"):
                file = generate_certificate(
                    st.session_state.user[1], "Python Basics"
                )
                with open(file, "rb") as f:
                    st.download_button("Download Certificate", f, file_name=file)

# ---------------- LOGOUT ----------------
elif choice == "Logout":
    st.session_state.user = None
    st.success("Logged out")
