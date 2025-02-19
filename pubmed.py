import streamlit as st
import os
import requests
import xml.etree.ElementTree as ET  # For XML parsing
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage

# Load Groq API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")

# Ensure API key is set
if not GROQ_API_KEY:
    st.error("Groq API key is missing! Set it as an environment variable or enter it manually.")
    st.stop()

# Initialize Groq LLM
llm = ChatGroq(
    temperature=0,
    groq_api_key=GROQ_API_KEY,
    model_name="llama3-8b-8192"
)

# API URLs
PUBMED_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
OPENALEX_API_URL = "https://api.openalex.org/works"

st.title("📚 Drug Interaction Research Analyzer for Healthcare Providers")

# User input
query = st.text_input("Enter drug interaction query:", "Ramipril and spironolactone drug interaction")

# Function to fetch research papers from PubMed
def fetch_papers_pubmed(query, num_papers=5):
    """Fetches top PubMed research articles and extracts titles, abstracts, and links."""
    search_params = {"db": "pubmed", "term": query, "retmode": "json", "retmax": num_papers}
    search_response = requests.get(PUBMED_SEARCH_URL, params=search_params)

    if search_response.status_code != 200:
        st.error(f"Failed to fetch PubMed data: {search_response.status_code}")
        return []

    search_results = search_response.json()
    paper_ids = search_results.get("esearchresult", {}).get("idlist", [])

    papers = []
    for paper_id in paper_ids:
        fetch_params = {"db": "pubmed", "id": paper_id, "retmode": "xml"}
        fetch_response = requests.get(PUBMED_FETCH_URL, params=fetch_params)
        
        title = f"PubMed Paper {paper_id}"  # Default title if missing
        abstract = "No Abstract Available"
        source_url = f"https://pubmed.ncbi.nlm.nih.gov/{paper_id}/"
        
        if fetch_response.status_code == 200:
            try:
                root = ET.fromstring(fetch_response.text)
                
                # Extract title
                title_elem = root.find(".//ArticleTitle")
                if title_elem is not None and title_elem.text:
                    title = title_elem.text.strip()
                
                # Extract abstract (Ensure all values are strings)
                abstract_elements = root.findall(".//AbstractText")
                if abstract_elements:
                    abstract = " ".join([str(elem.text) for elem in abstract_elements if elem.text])

            except ET.ParseError:
                st.error("Error parsing PubMed XML response.")

        papers.append({"title": title, "abstract": abstract, "url": source_url})

    return papers

# Function to fetch research papers from OpenAlex
def fetch_papers_openalex(query, num_papers=5):
    """Fetches top OpenAlex research articles and extracts abstracts and links."""
    params = {"search": query, "filter": "language:en", "per_page": num_papers}
    response = requests.get(OPENALEX_API_URL, params=params)

    if response.status_code != 200:
        st.error(f"Failed to fetch OpenAlex data: {response.status_code}")
        return []

    data = response.json()
    papers = []
    for paper in data.get("results", []):
        title = paper.get("title", "No Title")
        abstract = paper.get("abstract_inverted_index", {})
        source_url = paper.get("id", "")

        # Extract full abstract text
        if isinstance(abstract, dict):
            abstract_text = " ".join([" ".join(map(str, words)) for words in abstract.values()])
        else:
            abstract_text = "No Abstract Available"

        if source_url.startswith("https://openalex.org/"):
            papers.append({"title": title, "abstract": abstract_text, "url": source_url})

    return papers

# Function to generate structured analysis with source links
def analyze_combined_abstracts(papers):
    if not papers:
        return "No abstracts available for analysis.", ""

    # Limit to 5 abstracts with actual content
    limited_papers = [p for p in papers if p["abstract"] and p["abstract"] != "No Abstract Available"][:5]
    
    if not limited_papers:
        return "No valid abstracts found.", ""

    # Build prompt using abstracts
    combined_abstracts = "\n\n".join([p["abstract"] for p in limited_papers])

    # Create a dynamic prompt including references next to subtitles
    prompt = f"""
    Based on the following abstracts from research papers on the drug interaction query: "{query}", provide a structured analysis.

    {combined_abstracts}

    **Generate a single structured summary including:**

    **1. Risk Summary** ([Sources]({limited_papers[0]['url']})):
    - What are the potential risks or dangers associated with this combination?
    - Focus on risks like elevated potassium levels, kidney function, etc.

    **2. Potential Mechanism** ([Sources]({limited_papers[1]['url']})):
    - How does this drug interaction occur at a physiological level?
    - Describe the biological mechanisms involved.

    **3. Clinical Implications** ([Sources]({limited_papers[2]['url']})):
    - How can this interaction affect patient health?
    - What should healthcare providers monitor or be cautious about?

    **4. Recommendations** ([Sources]({limited_papers[3]['url']})):
    - What actions should healthcare providers take to mitigate risks?
    - Should dose adjustments or alternative medications be considered?

    Please ensure the language is **professionally structured**, **clinically relevant**, and **actionable for healthcare providers**.
    """

    try:
        response = llm([HumanMessage(content=prompt)])
        
        if not response or not hasattr(response, "content"):
            st.error("Groq API returned an empty or invalid response.")
            return "Error: No response from the AI model.", ""

        analysis = response.content
        return analysis, ""

    except Exception as e:
        st.error(f"Groq API Error: {str(e)}")
        return "Error: Failed to generate AI analysis.", ""

# Button to fetch and analyze papers
if st.button("Analyze Drug Interaction"):
    st.write("🔍 Searching for relevant research papers on PubMed and OpenAlex...")

    pubmed_papers = fetch_papers_pubmed(query)
    openalex_papers = fetch_papers_openalex(query)
    
    # Combine papers from both sources
    all_papers = pubmed_papers + openalex_papers

    if not all_papers:
        st.warning("No relevant abstracts found.")
    else:
        # Analyze combined abstracts and generate structured insights
        st.write("🔬 **Analyzing Content...**")
        structured_content, _ = analyze_combined_abstracts(all_papers)
        st.markdown(structured_content)

st.caption("Powered by PubMed, OpenAlex & Groq AI")
