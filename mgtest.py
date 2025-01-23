import streamlit as st
from langchain_groq import ChatGroq

# Function to fetch a specific section of the monograph via API
def fetch_monograph_section(drug_name, section):
    """Fetch a specific section of the monograph for the given drug name."""
    llm = ChatGroq(
        temperature=0, 
        groq_api_key='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', 
        model_name="llama3-8b-8192"
    )
    
    prompt = f"Provide a detailed {section} section for the drug '{drug_name}' in at least one page, along with the source URL."
    
    try:
        response = llm.invoke(prompt)
        if isinstance(response.content, str):  # If plain text is returned
            return {"content": response.content, "source": None}
        elif isinstance(response.content, dict):  # If JSON-like dictionary is returned
            return response.content
        else:
            return {"content": "No content available for this section.", "source": None}
    except Exception as e:
        return {"content": f"Error fetching data for {section}: {e}", "source": None}

# Streamlit UI
def main():
    st.set_page_config(layout="wide")  # Use full-page width
    st.title("Drug Monograph Generator")

    # Input for drug name
    drug_name = st.text_input("Enter Drug Name:", value="", placeholder="e.g., Diclofenac", key="drug_input")

    if drug_name.strip():
        # Predefined monograph sections
        sections = [
            "INTRODUCTION", "CLASSIFICATION", "INDICATIONS AND USAGE", "DOSAGE FORMS AND STRENGTHS",
            "DOSAGE AND ADMINISTRATION", "CONTRAINDICATIONS", "WARNING AND PRECAUTIONS", 
            "ADVERSE REACTIONS", "DRUG INTERACTIONS", "USE IN SPECIFIC POPULATIONS", 
            "CLINICAL PHARMACOLOGY", "NONCLINICAL TOXICOLOGY", "CLINICAL STUDIES",
            "DRUG TO DRUG INTERACTIONS", "DRUG TO FOOD ALLERGIES", "REFERENCES"
        ]

        # Layout for vertical tabs
        col1, col2 = st.columns([1, 4])  # Left column for buttons, right column for content
        with col1:
            st.markdown("### Sections")
            active_section = st.radio("Select a section:", sections, index=0, label_visibility="collapsed")

        with col2:
            # Fetch and display content for the active section
            with st.spinner(f"Fetching {active_section} content..."):
                result = fetch_monograph_section(drug_name, active_section)
                content = result.get("content", "No content available.")
                source = result.get("source", None)

            st.header(active_section)
            st.write(content)

            # Display reference (if any)
            if source:
                st.markdown(f"**Reference:** [Source]({source})")
    else:
        st.info("Please enter a drug name to begin.")

if __name__ == "__main__":
    main()
