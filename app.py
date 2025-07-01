import streamlit as st
import os

# import pdfminer
# from pdfminer.high_level import extract_text
# from dotenv import load_dotenv

# load_dotenv()

if "connect" not in st.session_state:
    st.session_state["connect"] = False

st.header("ChatPDF 🗣️ (Talk with your pdf)")

with st.sidebar:
    if not st.session_state["connect"]:
        st.header("🔐 API Configurations",divider="gray")

        st.subheader("Gemini API:",divider="blue",width="content")
        st.write(f"If you don't have create one from [here](https://aistudio.google.com/app/apikey).")
        gemini_api = st.text_input("Enter Gemini API Key", type="password")
        os.environ["GOOGLE_API_KEY"] = gemini_api

        st.subheader("Qdrant API:",divider="green",width="content")
        st.write(f"If you don't have create one from [here](https://qdrant.tech/documentation/cloud-quickstart).")
        qdrant_url = st.text_input("Enter Qdrant URL",placeholder="Ex: https://###.###.gcp.cloud.qdrant.io")
        qdrant_api = st.text_input("Enter Qdrant API Key", type="password")
        os.environ["QDRANT_URL"] = qdrant_url
        os.environ["QDRANT_API_KEY"] = qdrant_api

        btn = st.button("Connect",use_container_width=True)
        if not gemini_api or not qdrant_url or not qdrant_api:
            btn = False
        if btn:
            # validate the inputs
            st.session_state["connect"] = True
            st.rerun()
    else:
        st.header("History")

col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("Upload a PDF file", type='pdf')
    saved_file = ''

    if uploaded_file is not None:
        target_folder = "uploaded_pdfs"
        os.makedirs(target_folder, exist_ok=True)
        save_path = os.path.join(target_folder, uploaded_file.name)
        saved_file = save_path

        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(f"File saved to {save_path}")

# if "count" not in st.session_state:
#     st.session_state["count"] = 0
# if st.button("add"):
#     st.session_state["count"] += 1

if st.session_state["connect"]:
    # st.success("Connected successfully!")
    # st.button("hi")
    btn = st.button("Disconnect",use_container_width=True)
    if btn:
        st.session_state["connect"] = False

# print(str(st.session_state["connect"]) + "hi")
# print(st.session_state["count"])
# print(uploaded_file.getbuffer() if uploaded_file else "No file uploaded")