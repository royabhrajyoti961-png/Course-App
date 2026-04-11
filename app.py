import streamlit as st
import sqlite3
import hashlib
import datetime
import random
from fpdf import FPDF
import qrcode

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="CourseHub 🎓", layout="wide")

# ---------------- THEME TOGGLE ----------------
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

toggle = st.sidebar.toggle("🌗 Toggle Theme", value=True)

st.session_state.theme = "dark" if toggle else "light"

# ---------------- UI ----------------
if st.session_state.theme == "dark":
    st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
    * { font-family: 'Poppins', sans-serif !important; }

    [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg,#ff003c,#ff5e00,#ff9900,#7a5cff,#3a86ff,#00c853);
        background-size: 400% 400%;
        animation: gradientMove 12s ease infinite;
    }

    @keyframes gradientMove {
        0%{background-position:0% 50%;}
        50%{background-position:100% 50%;}
        100%{background-position:0% 50%;}
    }

    .block-container {
        background: rgba(0,0,0,0.55);
        padding: 25px;
        border-radius: 15px;
        color: white;
    }

    [data-testid="stSidebar"] {
        background: rgba(0,0,0,0.7);
    }

    .stButton>button {
        border-radius: 12px;
        padding: 10px;
        background: linear-gradient(45deg,#ff4d00,#ff9900);
        color:white;
    }
    </style>
    """, unsafe_allow_html=True)

else:
    st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
    * { font-family: 'Poppins', sans-serif !important; }

    [data-testid="stAppViewContainer"] { background:#f5f7fa; }

    .block-container {
        background:white;
        padding:25px;
        border-radius:15px;
    }

    .stButton>button {
        border-radius:12px;
        background: linear-gradient(45deg,#3a86ff,#00c853);
        color:white;
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

# ---------------- CREATE ADMIN ----------------
def create_admin():
    c.execute("SELECT * FROM users WHERE email=?", ("admin@coursehub.com",))
    if not c.fetchone():
        c.execute("INSERT INTO users(name,email,password,role) VALUES(?,?,?,?)",
                  ("Admin","admin@coursehub.com",
                   hashlib.sha256("admin123".encode()).hexdigest(),
                   "admin"))
        conn.commit()

create_admin()

# ---------------- UTILS ----------------
def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

def generate_cert_id():
    return f"CERT-{datetime.datetime.now().year}-{random.randint(10000,99999)}"

# ---------------- AUTH ----------------
def register(name,email,password):
    try:
        c.execute("INSERT INTO users(name,email,password,role) VALUES(?,?,?,?)",
                  (name,email,hash_password(password),"user"))
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
    qr = qrcode.make(cert_id)
    qr.save("qr.png")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial","B",22)
    pdf.cell(0,20,"CERTIFICATE OF COMPLETION",ln=True,align="C")

    pdf.ln(10)
    pdf.set_font("Arial","",14)
    pdf.cell(0,10,"This certifies",ln=True,align="C")

    pdf.set_font("Arial","B",18)
    pdf.cell(0,10,user,ln=True,align="C")

    pdf.cell(0,10,f"completed {course}",ln=True,align="C")
    pdf.cell(0,10,cert_id,ln=True,align="C")

    pdf.image("qr.png", x=80, y=150, w=40)

    file = f"{cert_id}.pdf"
    pdf.output(file)
    return file

# ---------------- SESSION ----------------
if "user" not in st.session_state:
    st.session_state.user = None

# ---------------- MENU ----------------
menu = ["Login","Register"]

if st.session_state.user:
    role = st.session_state.user[4]
    if role == "admin":
        menu = ["Admin Panel","Logout"]
    else:
        menu = ["Dashboard","Courses","Verify Certificate","Logout"]

choice = st.sidebar.selectbox("Menu",menu)

# ---------------- LOGIN ----------------
if choice == "Login":
    e = st.text_input("Email")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        user = login(e,p)
        if user:
            st.session_state.user = user
            st.success("Logged in")
        else:
            st.error("Invalid")

# ---------------- REGISTER ----------------
elif choice == "Register":
    n = st.text_input("Name")
    e = st.text_input("Email")
    p = st.text_input("Password", type="password")

    if st.button("Register"):
        if register(n,e,p):
            st.success("Registered")
        else:
            st.error("Email exists")

# ---------------- ADMIN PANEL ----------------
elif choice == "Admin Panel":
    st.title("👨‍💼 Admin Panel")

    tab1, tab2, tab3 = st.tabs(["Add Course","Add Lesson","Users"])

    with tab1:
        title = st.text_input("Course Title")
        desc = st.text_area("Description")
        if st.button("Add Course"):
            c.execute("INSERT INTO courses(title,description) VALUES(?,?)",(title,desc))
            conn.commit()
            st.success("Added")

    with tab2:
        c.execute("SELECT * FROM courses")
        courses = c.fetchall()
        course_dict = {c[1]:c[0] for c in courses}

        selected = st.selectbox("Course", list(course_dict.keys()))
        ltitle = st.text_input("Lesson Title")
        content = st.text_area("Video Link / Article")

        if st.button("Add Lesson"):
            c.execute("INSERT INTO lessons(course_id,title,content) VALUES(?,?,?)",
                      (course_dict[selected],ltitle,content))
            conn.commit()
            st.success("Lesson Added")

    with tab3:
        c.execute("SELECT name,email,role FROM users")
        for u in c.fetchall():
            st.write(u)

# ---------------- COURSES ----------------
elif choice == "Courses":
    c.execute("SELECT * FROM courses")
    for course in c.fetchall():
        st.subheader(course[1])

        if st.button("Open", key=f"c{course[0]}"):
            st.session_state.cid = course[0]

    if "cid" in st.session_state:
        c.execute("SELECT * FROM lessons WHERE course_id=?",(st.session_state.cid,))
        lessons = c.fetchall()

        for l in lessons:
            st.write(l[2])

            if st.button("Complete", key=f"l{l[0]}"):
                c.execute("INSERT INTO progress VALUES(?,?)",
                          (st.session_state.user[0],l[0]))
                conn.commit()

        if st.button("Get Certificate"):
            cert = generate_cert_id()
            file = generate_certificate(st.session_state.user[1],"Course",cert)
            with open(file,"rb") as f:
                st.download_button("Download",f,file)

# ---------------- VERIFY ----------------
elif choice == "Verify Certificate":
    cid = st.text_input("Certificate ID")
    if st.button("Verify"):
        c.execute("SELECT * FROM certificates WHERE cert_id=?", (cid,))
        if c.fetchone():
            st.success("Valid")
        else:
            st.error("Invalid")

# ---------------- LOGOUT ----------------
elif choice == "Logout":
    st.session_state.user = None
    st.success("Logged out")
