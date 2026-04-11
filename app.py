import streamlit as st

st.set_page_config(page_title="CourseFinder 🎓", layout="wide")

# ---------------- TITLE ----------------
st.title("🎓 CourseFinder - Learn & Get Certified")
st.write("Find the best courses and get official certificates from trusted platforms 🚀")

# ---------------- COURSE DATABASE (MANUAL + SAFE) ----------------
courses_db = [
    {
        "title": "Python for Beginners",
        "platform": "Kaggle",
        "description": "Learn Python from scratch",
        "url": "https://www.kaggle.com/learn/python",
        "certificate": "Free"
    },
    {
        "title": "Intro to Machine Learning",
        "platform": "Kaggle",
        "description": "Basic ML concepts",
        "url": "https://www.kaggle.com/learn/intro-to-machine-learning",
        "certificate": "Free"
    },
    {
        "title": "Google Digital Marketing",
        "platform": "Google Digital Garage",
        "description": "Learn digital marketing",
        "url": "https://learndigital.withgoogle.com/digitalgarage",
        "certificate": "Free"
    },
    {
        "title": "AI For Everyone",
        "platform": "Coursera",
        "description": "AI basics by Andrew Ng",
        "url": "https://www.coursera.org/learn/ai-for-everyone",
        "certificate": "Paid"
    },
    {
        "title": "Full Web Development Course",
        "platform": "YouTube",
        "description": "Complete web dev course",
        "url": "https://www.youtube.com",
        "certificate": "No"
    }
]

# ---------------- SEARCH ----------------
query = st.text_input("🔍 Search course (Python, AI, Web Dev...)")

# ---------------- FILTER ----------------
free_only = st.checkbox("Show only FREE certificates")

# ---------------- FUNCTION ----------------
def filter_courses(query):
    results = []
    for course in courses_db:
        if query.lower() in course["title"].lower():
            if free_only:
                if course["certificate"] == "Free":
                    results.append(course)
            else:
                results.append(course)
    return results

# ---------------- DISPLAY ----------------
if st.button("Search"):
    results = filter_courses(query)

    if results:
        for course in results:
            with st.container():
                col1, col2 = st.columns([3,1])

                with col1:
                    st.subheader(course["title"])
                    st.write(course["description"])
                    st.write(f"📚 Platform: {course['platform']}")

                    if course["certificate"] == "Free":
                        st.success("🎓 Free Certificate Available")
                    elif course["certificate"] == "Paid":
                        st.warning("🎓 Certificate (Paid)")
                    else:
                        st.error("❌ No Certificate")

                with col2:
                    st.link_button("Go to Course 🚀", course["url"])

                st.divider()
    else:
        st.error("No courses found")

# ---------------- SIDEBAR ----------------
st.sidebar.title("📌 About")
st.sidebar.write("""
This app helps you find courses and redirects you to official platforms where you can learn and earn certificates.
""")

st.sidebar.write("Built with ❤️ using Streamlit")
