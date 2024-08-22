import streamlit as st
from main_page import show_main_page
from modified_page import show_modified_page

st.set_page_config(page_title="Multipage App", page_icon="📊", layout="wide")

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Main Page", "Modified Entries"])

    if page == "Main Page":
        show_main_page()
    elif page == "Modified Entries":
        show_modified_page()

if __name__ == "__main__":
    main()