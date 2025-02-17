import streamlit as st
import os
import requests
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage

# Load Groq API key
GROQ_API_KEY = "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"

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
    """Fetches top PubMed research articles and extracts abstracts and links."""
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
        
        abstract = "No Abstract Available"
        if fetch_response.status_code == 200:
            abstract_start = fetch_response.text.find("<AbstractText>")
            abstract_end = fetch_response.text.find("</AbstractText>")
            if abstract_start != -1 and abstract_end != -1:
                abstract = fetch_response.text[abstract_start+14:abstract_end]

        papers.append({"title": f"PubMed Paper {paper_id}", "abstract": abstract, "url": f"https://pubmed.ncbi.nlm.nih.gov/{paper_id}/"})

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
        abstract = paper.get("abstract", "No Abstract Available")
        url = paper.get("id", "No URL Available")

        papers.append({"title": title, "abstract": abstract, "url": url})

    return papers

# Function to generate structured analysis from all abstracts
def analyze_combined_abstracts(papers):
    if not papers:
        return "No abstracts available for analysis."

    # Limit the number of abstracts to prevent token overload
    limited_abstracts = papers[:5]  # Limit to first 5 papers to keep input size manageable
    combined_abstracts = "\n\n".join([paper["abstract"] for paper in limited_abstracts if paper["abstract"] != "No Abstract Available"])

    # Create reference links
    reference_links = "\n".join([f"- [{paper['title']}]({paper['url']})" for paper in limited_abstracts])

    # Create a dynamic prompt based on the query
    prompt = f"""
    Based on the following abstracts from multiple research papers on the drug interaction query: "{query}", provide a structured analysis.

    {combined_abstracts}

    **Generate a single structured summary including:**

    **1. Risk Summary:**
    - What are the potential risks or dangers associated with this combination?
    - Focus on risks like elevated potassium levels, kidney function, etc.

    **2. Potential Mechanism:**
    - How does this drug interaction occur at a physiological level?
    - Describe the biological mechanisms involved.

    **3. Clinical Implications:**
    - How can this interaction affect patient health?
    - What should healthcare providers monitor or be cautious about?

    **4. Recommendations:**
    - What actions should healthcare providers take to mitigate risks?
    - Should dose adjustments or alternative medications be considered?

    Please ensure the language is **professionally structured**, **clinically relevant**, and **actionable for healthcare providers**.
    """

    try:
        response = llm([HumanMessage(content=prompt)])
        analysis = response.content
        return analysis, reference_links
    except Exception as e:
        st.error(f"Groq API Error: {str(e)}")
        return "Error analyzing content", ""

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
        analysis, references = analyze_combined_abstracts(all_papers)
        st.write(analysis)

        st.write("### 🔗 Reference Links for Verification")
        st.markdown(references)

st.caption("Powered by PubMed, OpenAlex & Groq AI")
