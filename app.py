import streamlit as st
import sqlite3
import hashlib

# ---------------- CONFIG ----------------
st.set_page_config(page_title="CourseHub Pro 🎓", layout="wide")

# ---------------- LIGHT PREMIUM UI ----------------
st.markdown("""
<style>

/* 🌈 LIGHT GRADIENT BACKGROUND */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #e0f2fe, #f0fdf4, #fef9c3);
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: #ffffff;
}

/* TEXT */
h1, h2, h3, h4 {
    color: #0f172a;
}

/* CONTAINER */
.block-container {
    padding: 2rem 3rem;
}

/* CARD */
.card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 20px;
    box-shadow: 0px 5px 20px rgba(0,0,0,0.08);
}

/* BUTTON */
.stButton>button {
    background: linear-gradient(45deg, #3b82f6, #6366f1);
    color: white;
    border-radius: 10px;
    border: none;
}

/* INPUT */
input, textarea {
    background: #f8fafc !important;
    color: black !important;
}

/* METRIC */
.metric-box {
    background: white;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0px 5px 20px rgba(0,0,0,0.08);
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

    conn.commit()

create_tables()

# ---------------- UTILS ----------------
def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

def login(email,password,role):
    c.execute("SELECT * FROM users WHERE email=? AND password=? AND role=?",
              (email,hash_password(password),role))
    return c.fetchone()

# ---------------- SESSION ----------------
if "portal" not in st.session_state:
    st.session_state.portal = None
if "user" not in st.session_state:
    st.session_state.user = None

# ---------------- PORTAL SELECTION ----------------
if st.session_state.portal is None:
    st.title("🚀 CourseHub Platform")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='card'><h3>🎓 Learner Portal</h3><p>Start learning courses</p></div>", unsafe_allow_html=True)
        if st.button("Enter Learner Portal"):
            st.session_state.portal = "student"

    with col2:
        st.markdown("<div class='card'><h3>⚙️ Admin Portal</h3><p>Manage platform</p></div>", unsafe_allow_html=True)
        if st.button("Enter Admin Portal"):
            st.session_state.portal = "admin"

    st.stop()

# ---------------- AUTH ----------------
if st.session_state.user is None:
    auth = st.sidebar.radio("Account", ["Login","Register"])
else:
    auth = None

# ---------------- REGISTER ----------------
if auth == "Register":
    st.subheader(f"{st.session_state.portal.capitalize()} Register")

    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        try:
            c.execute("INSERT INTO users(name,email,password,role) VALUES(?,?,?,?)",
                      (name,email,hash_password(password),st.session_state.portal))
            conn.commit()
            st.success("Registered Successfully!")
        except:
            st.error("Email already exists!")

# ---------------- LOGIN ----------------
elif auth == "Login":
    st.subheader(f"{st.session_state.portal.capitalize()} Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = login(email,password,st.session_state.portal)
        if user:
            st.session_state.user = user
            st.success("Login Successful!")
        else:
            st.error("Invalid credentials!")

# ---------------- LEARNER DASHBOARD ----------------
elif st.session_state.portal == "student":
    st.title(f"🎓 Welcome {st.session_state.user[1]}")

    st.markdown("## 📚 Your Courses")

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

            if st.button("Open Course", key=course[0]):
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

# ---------------- ADMIN DASHBOARD ----------------
elif st.session_state.portal == "admin":
    st.title("⚙️ Admin Dashboard")

    tab1, tab2 = st.tabs(["Add Course","Add Lesson"])

    with tab1:
        title = st.text_input("Course Title")
        desc = st.text_area("Description")

        if st.button("Add Course"):
            c.execute("INSERT INTO courses(title,description) VALUES(?,?)",(title,desc))
            conn.commit()
            st.success("Course Added!")

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
            st.success("Lesson Added!")

# ---------------- LOGOUT ----------------
if st.session_state.user:
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.session_state.portal = None
        st.success("Logged out")
