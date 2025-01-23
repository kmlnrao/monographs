import streamlit as st
import requests
from PyPDF2 import PdfReader
from langchain_groq import ChatGroq

def extract_text_from_pdf(pdf_file):
    """Extracts text from an uploaded PDF file."""
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def get_monographs_from_api(pdf_text):
    """Send the PDF text to the Groq Generative AI API and get monograph responses."""
    llm = ChatGroq(
        temperature=0, 
        groq_api_key='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', 
        model_name="llama3-8b-8192"
    )
    response = llm.invoke(pdf_text)

    try:
         return response.content;
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {e}")
        return {}

# Streamlit UI
def main():
    st.title("Drug Monograph Generator")

    st.sidebar.header("Upload PDF File")
    uploaded_files = st.sidebar.file_uploader(
        "Upload PDF files", type=["pdf"], accept_multiple_files=True
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            st.subheader(f"Processing: {uploaded_file.name}")

            # Extract text from the PDF
            with st.spinner("Extracting text from the PDF..."):
                pdf_text = extract_text_from_pdf(uploaded_file)

            # Send text to Groq API and get monographs
            with st.spinner("Fetching drug monographs..."):
                monographs = get_monographs_from_api(pdf_text)

            if monographs:
                # Display monographs in tabs
                tabs = st.tabs(list(monographs.keys()))
                for tab, (drug_name, monograph_text) in zip(tabs, monographs.items()):
                    with tab:
                        st.header(drug_name)
                        st.write(monograph_text)
            else:
                st.warning(f"No monographs found for {uploaded_file.name}.")

if __name__ == "__main__":
    main()
