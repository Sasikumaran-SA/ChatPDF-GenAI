import streamlit as st
import os
from langchain_qdrant import QdrantVectorStore
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from qdrant_client import QdrantClient

st.set_page_config(layout="wide", page_title="ChatPDF 🗣️ (Talk with your pdf)", initial_sidebar_state="expanded")
st.markdown(
    """
<style>
    .st-emotion-cache-1mph9ef {
        flex-direction: row-reverse;
        text-align: right;
    }
    [data-testid='stHeaderActionElements'] {
        display: none;
    }
</style>
""",
    unsafe_allow_html=True,
)

if "connect" not in st.session_state:
    st.session_state["connect"] = False

if "uploaded_file" not in st.session_state:
    st.session_state["uploaded_file"] = None

if "file_mkr" not in st.session_state:
    st.session_state["file_mkr"] = False

if "file_path" not in st.session_state:
    st.session_state["file_path"] = None

if "file_processed" not in st.session_state:
    st.session_state["file_processed"] = False

if "vector_store" not in st.session_state:
    st.session_state["vector_store"] = None

if "rag_chain" not in st.session_state:
    st.session_state["rag_chain"] = None

if "messages" not in st.session_state:
    st.session_state["messages"] = []

def process_pdf(pdf_path: str) -> QdrantVectorStore:
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(documents)

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    vector_store = QdrantVectorStore.from_documents(
        documents=splits,
        embedding=embeddings,
        url=os.environ["QDRANT_URL"],
        api_key=os.environ["QDRANT_API_KEY"],
        collection_name="chatpdf_vectors",
        force_recreate=True,
        timeout=10
    )
    return vector_store

def setup_rag_chain(vector_store: QdrantVectorStore):
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.2)

    retriever = vector_store.as_retriever(search_kwargs={"k": 5,"lambda_mult":0.7},search_type="mmr")

    rag_template = """
    You are an AI assistant for answering questions about a PDF document.
    Use the following context to answer the question.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.

    Context: {context}

    Question: {question}
    """
    rag_prompt = ChatPromptTemplate.from_template(rag_template)
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | rag_prompt
        | llm
        | StrOutputParser()
    )
    return rag_chain

st.markdown("<h1 style='text-align: center;'>ChatPDF 🗣️ (Talk with your pdf)</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='background: -webkit-linear-gradient(#2f85d6, #e80ecb);-webkit-text-fill-color: transparent;-webkit-background-clip: text'>" \
"Chat with your PDF files using Gemini AI. This app allows you to upload a PDF file and interact with it using natural language queries. The app " \
"uses Gemini AI for processing and Qdrant for vector storage and retrieval.</h2>", unsafe_allow_html=True)

with st.sidebar:
    st.header("🔐 API Configurations",divider="gray")

    st.subheader("Gemini API:",divider="blue",width="content")
    st.write(f"If you don't have create one from [here](https://aistudio.google.com/app/apikey).")
    gemini_api = st.text_input("Enter Gemini API Key", type="password",disabled=st.session_state["connect"])
    os.environ["GOOGLE_API_KEY"] = gemini_api

    st.subheader("Qdrant API:",divider="green",width="content")
    st.write(f"If you don't have create one from [here](https://qdrant.tech/documentation/cloud-quickstart).")
    qdrant_url = st.text_input("Enter Qdrant URL",placeholder="Ex: https://###.###.gcp.cloud.qdrant.io",disabled=st.session_state["connect"])
    qdrant_api = st.text_input("Enter Qdrant API Key", type="password",disabled=st.session_state["connect"])
    os.environ["QDRANT_URL"] = qdrant_url
    os.environ["QDRANT_API_KEY"] = qdrant_api

    btn = st.button("Connect",use_container_width=True, disabled=st.session_state["connect"])
    if not gemini_api or not qdrant_url or not qdrant_api:
        btn = False
    if btn:
        st.session_state["connect"] = True
        st.rerun()
    
    if st.session_state["connect"]:
        if st.button("Disconnect", use_container_width=True):
            st.session_state["connect"] = False
            st.session_state["uploaded_file"] = None
            st.session_state["file_path"] = None
            st.session_state["file_processed"] = False
            st.session_state["vector_store"] = None
            st.session_state["rag_chain"] = None
            st.session_state["messages"] = []
            try:
                client = QdrantClient(url=os.environ["QDRANT_URL"], api_key=os.environ["QDRANT_API_KEY"])
                client.delete_collection(collection_name="chatpdf_vectors")
            except:
                pass
            st.rerun()

if not st.session_state["connect"]:
    st.markdown("<h3>Please Give the API Configurations on the sidebar to get started.</h3>", unsafe_allow_html=True)
else:
    col1, col2 = st.columns(2)

    with col1:
        st.session_state["uploaded_file"] = st.file_uploader("Upload a PDF file", type='pdf',disabled=st.session_state["file_mkr"])
        if not st.session_state["uploaded_file"] and st.session_state["file_path"]:
            os.remove(st.session_state["file_path"])
            st.session_state["file_mkr"] = False
            st.session_state["file_path"] = None
            st.session_state["file_processed"] = False
            st.session_state["vector_store"] = None
            st.session_state["rag_chain"] = None
            st.session_state["messages"] = []
            try:
                client = QdrantClient(url=os.environ["QDRANT_URL"], api_key=os.environ["QDRANT_API_KEY"])
                client.delete_collection(collection_name="chatpdf_vectors")
            except:
                pass
            st.rerun()
        
        if st.session_state["uploaded_file"]:
            target_folder = "uploaded_pdfs"
            os.makedirs(target_folder, exist_ok=True)
            file_path = os.path.join(target_folder, st.session_state["uploaded_file"].name)
            st.session_state["file_path"] = file_path

            st.success(f"File saved to {st.session_state['file_path']}")
            if not st.session_state["file_mkr"]:
                with open(st.session_state["file_path"], "wb") as f:
                    f.write(st.session_state["uploaded_file"].getbuffer())
                st.session_state["file_mkr"] = True
                st.rerun()
        else:
            st.session_state["file_path"] = None

    with col2:
        if not st.session_state["file_path"]:
            st.session_state["file_processed"] = False
            st.session_state["vector_store"] = None
            st.session_state["rag_chain"] = None
            st.session_state["messages"] = []
            st.markdown("<h3 style='margin-left: 20px;'>Now Upload a PDF file.</h3>", unsafe_allow_html=True)
        if st.session_state["file_path"] and not st.session_state["file_processed"]:
            st.markdown("<h5 style='margin-left: 20px;'>If you want to change the PDF file, please delete the current file and upload a new one.</h5>", unsafe_allow_html=True)
            st.markdown("<h3 style='margin-left: 20px;'>Let's process your PDF file before chatting.</h3>", unsafe_allow_html=True)
            if st.button("Process PDF", use_container_width=True):
                st.write("Please wait for sometime...")
                try:
                    st.session_state["vector_store"] = process_pdf(st.session_state["file_path"])
                    st.session_state["rag_chain"] = setup_rag_chain(st.session_state["vector_store"])
                    st.session_state["file_processed"] = True
                    st.rerun()
                except Exception as e:
                    st.error()

        if st.session_state["file_processed"]:
            st.write("\n")
            st.markdown("<h5 style='margin-left: 20px;'>If you want to change the PDF file, please delete the current file and upload a new one.</h5>", unsafe_allow_html=True)
            st.markdown("<h3 style='margin-left: 20px;'>Now you are ready to chat with your PDF file.</h3>", unsafe_allow_html=True)
    
    if st.session_state["file_processed"]:
        st.markdown("<hr style='border: 1px solid; margin:5px'/><h3 style='margin-left: 20px;'>Chat with your PDF file:</h3>", unsafe_allow_html=True)
        st.chat_message("ai").markdown("What do you want to ask about your PDF file?")
        for message in st.session_state["messages"]:
            if message["role"] == "user":
                st.chat_message(message["role"]).markdown(f"<p style='text-align: right;'>{message["content"]}</p>", unsafe_allow_html=True)
            else:
                st.chat_message(message["role"]).write(message["content"], unsafe_allow_html=True)
        try:
            query = st.chat_input("Ask a question about your PDF file:")
        except Exception as e:
            st.error(e)
            st.rerun()
        if query:
            response = st.session_state["rag_chain"].invoke(query)
            st.session_state["messages"].append({"role": "user", "content": query})
            st.session_state["messages"].append({"role": "ai", "content": response})
            st.rerun()
