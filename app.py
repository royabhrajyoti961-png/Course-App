import streamlit as st
import sqlite3
import hashlib

# ---------------- CONFIG ----------------
st.set_page_config(page_title="CourseHub Pro 🎓", layout="wide")

# ---------------- ULTRA PRO UI ----------------
st.markdown("""
<style>

/* BACKGROUND */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(120deg,#eef2ff,#f0fdf4,#ecfeff);
}

/* NAVBAR */
.navbar {
    background: white;
    padding: 15px 30px;
    border-radius: 12px;
    margin-bottom: 20px;
    box-shadow: 0px 4px 20px rgba(0,0,0,0.08);
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: white;
}

/* TEXT */
h1,h2,h3,h4 {
    color:#0f172a;
}

/* CARD */
.card {
    background:white;
    padding:20px;
    border-radius:16px;
    box-shadow:0px 6px 25px rgba(0,0,0,0.08);
    transition:0.3s;
}
.card:hover {
    transform: translateY(-5px);
}

/* BUTTON */
.stButton>button {
    background: linear-gradient(45deg,#3b82f6,#6366f1);
    color:white;
    border-radius:10px;
    border:none;
}

/* INPUT */
input,textarea {
    background:#f1f5f9 !important;
}

/* METRIC */
.metric {
    background:white;
    padding:20px;
    border-radius:16px;
    text-align:center;
    box-shadow:0px 4px 20px rgba(0,0,0,0.08);
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

# ---------------- PORTAL ----------------
if st.session_state.portal is None:
    st.title("🚀 CourseHub Platform")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='card'><h3>🎓 Learner Portal</h3><p>Learn skills</p></div>", unsafe_allow_html=True)
        if st.button("Enter Learner"):
            st.session_state.portal="student"

    with col2:
        st.markdown("<div class='card'><h3>⚙️ Admin Portal</h3><p>Manage system</p></div>", unsafe_allow_html=True)
        if st.button("Enter Admin"):
            st.session_state.portal="admin"

    st.stop()

# ---------------- NAVBAR ----------------
st.markdown(f"""
<div class="navbar">
<b>🎓 CourseHub Pro</b>
</div>
""", unsafe_allow_html=True)

# ---------------- AUTH ----------------
if st.session_state.user is None:
    auth = st.sidebar.radio("Account",["Login","Register"])
else:
    auth = None

# ---------------- REGISTER ----------------
if auth=="Register":
    st.subheader("Register")

    name=st.text_input("Name")
    email=st.text_input("Email")
    password=st.text_input("Password",type="password")

    if st.button("Register"):
        try:
            c.execute("INSERT INTO users(name,email,password,role) VALUES(?,?,?,?)",
                      (name,email,hash_password(password),st.session_state.portal))
            conn.commit()
            st.success("Registered!")
        except:
            st.error("Email exists!")

# ---------------- LOGIN ----------------
elif auth=="Login":
    st.subheader("Login")

    email=st.text_input("Email")
    password=st.text_input("Password",type="password")

    if st.button("Login"):
        user=login(email,password,st.session_state.portal)
        if user:
            st.session_state.user=user
            st.success("Welcome!")
        else:
            st.error("Invalid login")

# ---------------- STUDENT DASHBOARD ----------------
elif st.session_state.portal=="student":
    st.title(f"👋 {st.session_state.user[1]}")

    col1,col2,col3=st.columns(3)
    col1.markdown("<div class='metric'><h3>Courses</h3><h2>5</h2></div>",unsafe_allow_html=True)
    col2.markdown("<div class='metric'><h3>Progress</h3><h2>60%</h2></div>",unsafe_allow_html=True)
    col3.markdown("<div class='metric'><h3>Certificates</h3><h2>2</h2></div>",unsafe_allow_html=True)

    st.markdown("## 📚 Courses")

    c.execute("SELECT * FROM courses")
    courses=c.fetchall()

    cols=st.columns(3)

    for i,course in enumerate(courses):
        with cols[i%3]:
            st.markdown(f"<div class='card'><h3>{course[1]}</h3><p>{course[2]}</p></div>",unsafe_allow_html=True)

# ---------------- ADMIN DASHBOARD ----------------
elif st.session_state.portal=="admin":
    st.title("⚙️ Admin Dashboard")

    tab1,tab2=st.tabs(["Add Course","Add Lesson"])

    with tab1:
        title=st.text_input("Course Title")
        desc=st.text_area("Description")

        if st.button("Add Course"):
            c.execute("INSERT INTO courses(title,description) VALUES(?,?)",(title,desc))
            conn.commit()
            st.success("Added")

    with tab2:
        c.execute("SELECT * FROM courses")
        courses=c.fetchall()
        course_dict={c[1]:c[0] for c in courses}

        course=st.selectbox("Course",list(course_dict.keys()))
        title=st.text_input("Lesson Title")
        content=st.text_area("Content")
        video=st.text_input("Video URL")
        typ=st.selectbox("Type",["video","article"])

        if st.button("Add Lesson"):
            c.execute("INSERT INTO lessons(course_id,title,content,video_url,type) VALUES(?,?,?,?,?)",
                      (course_dict[course],title,content,video,typ))
            conn.commit()
            st.success("Lesson Added")

# ---------------- LOGOUT ----------------
if st.session_state.user:
    if st.sidebar.button("Logout"):
        st.session_state.user=None
        st.session_state.portal=None
        st.success("Logged out")
