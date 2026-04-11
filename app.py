import streamlit as st
import sqlite3
import hashlib

# ---------------- CONFIG ----------------
st.set_page_config(page_title="CourseHub Pro 🎓", layout="wide")

# ---------------- PRO UI ----------------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {background:#0f172a;}
[data-testid="stSidebar"] {background:#020617;}
h1,h2,h3,h4 {color:white;}
.block-container {padding:2rem 3rem;}

.card {
    background:#1e293b;
    padding:20px;
    border-radius:15px;
    margin-bottom:20px;
}

.stButton>button {
    background:#3b82f6;
    color:white;
    border-radius:10px;
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
        st.markdown("<div class='card'><h3>🎓 Learner Portal</h3></div>", unsafe_allow_html=True)
        if st.button("Enter Learner Portal"):
            st.session_state.portal = "student"

    with col2:
        st.markdown("<div class='card'><h3>⚙️ Admin Portal</h3></div>", unsafe_allow_html=True)
        if st.button("Enter Admin Portal"):
            st.session_state.portal = "admin"

    st.stop()

# ---------------- AUTH MENU ----------------
if st.session_state.user is None:
    auth_choice = st.sidebar.radio("Account", ["Login","Register"])
else:
    auth_choice = None

# ---------------- REGISTER ----------------
if auth_choice == "Register":
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
elif auth_choice == "Login":
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

    st.markdown("## 📚 Available Courses")

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

# ---------------- ADMIN DASHBOARD ----------------
elif st.session_state.portal == "admin":
    st.title("⚙️ Admin Dashboard")

    tab1, tab2 = st.tabs(["Add Course","View Courses"])

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

        for cdata in courses:
            st.markdown(f"""
            <div class="card">
                <h3>{cdata[1]}</h3>
                <p>{cdata[2]}</p>
            </div>
            """, unsafe_allow_html=True)

# ---------------- LOGOUT ----------------
if st.session_state.user:
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.session_state.portal = None
        st.success("Logged out")
