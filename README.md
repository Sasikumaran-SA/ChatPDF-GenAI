# ChatPDF 🗣️ - Using Generative AI
This is a **Streamlit** hosting website, where user can give their own Gemini API key and Qdrant API key, and upload a PDF file and ask any question from that PDF.
A interactive user interface is made using streamlit, and the uploaded book content is broken down into multiple chucks and get stored in the **Qdrant vector-base**.
The user questions are processed using **gemini-2.0-flash model**, where the related content from **Qdrant vector-base** are retrived and sent along with query to the gemini model.

---

## 🧠 Built With
- **Streamlit**
- **Langchain**
- **Qdrant**
- **Google Generative AI**

---

## ☁️ Website link
<ins>[https://chatpdf-genai-z9sddcsazzfxoocx56jtvq.streamlit.app](https://chatpdf-genai-z9sddcsazzfxoocx56jtvq.streamlit.app)</ins>

---

## 🔐 Setup
1. Download this repository from github.
```bash
git clone https://github.com/Sasikumaran-SA/ChatPDF-GenAI.git
cd ChatPDF-GenAI
```

2. Setup the virtual environment.
You can setup virtual environment if you want. (Optional)
```bash
python -m venv .venv
./.venv/Scripts/activate
```

3. Install requirements.
```bash
pip install -r requirements.txt
```

4. Run the app.
```bash
streamlit run app.py
```

---

## 🧑‍💻 How to use the website
1. Open the link given above in any browser.
2. Give Gemini API key, Qdrant URL, Qdrant API key. (If you don't have one create using the link given below)
    - [Gemini API](https://aistudio.google.com/app/apikey)
    - [Qdrant](https://qdrant.tech/documentation/cloud-quickstart)
3. Upload a PDF. (Importantly, the uploading PDF should have text which can be seleted/copied)
4. Select **Process PDF** and wait for some time. This will take time depending upon the size of the pdf and the network speed.
5. Now using the dialog box shown below the website, you can ask your questions about the PDF and get the answers from it.
