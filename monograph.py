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
    st.title("Drug Monograph Generator")
    st.write("Enter a drug name below to fetch detailed monographs, interactions, and allergy information.")

    # Drug name input
    drug_name = st.text_input("Enter Drug Name (e.g., Diclofenac):", value="")
    
    if drug_name.strip():
        # Predefined monograph sections
        sections = [
            "INTRODUCTION", "CLASSIFICATION", "INDICATIONS AND USAGE", "DOSAGE FORMS AND STRENGTHS",
            "DOSAGE AND ADMINISTRATION", "CONTRAINDICATIONS", "WARNING AND PRECAUTIONS", 
            "ADVERSE REACTIONS", "DRUG INTERACTIONS", "USE IN SPECIFIC POPULATIONS", 
            "CLINICAL PHARMACOLOGY", "NONCLINICAL TOXICOLOGY", "CLINICAL STUDIES",
            "DRUG TO DRUG INTERACTIONS", "DRUG TO FOOD ALLERGIES"
        ]
        
        # Additional section for References
        sections.append("REFERENCES")

        # Initialize a dictionary to store references
        references = {}

        # Create tabs for each section
        tabs = st.tabs([section.upper() for section in sections])
        
        for i, section in enumerate(sections):
            with tabs[i]:
                if section == "REFERENCES":
                    # Display references collected from other sections
                    st.header("REFERENCES")
                    if references:
                        for sec, ref in references.items():
                            st.subheader(sec.upper())
                            if ref:
                                st.write(ref)
                            else:
                                st.write("No reference available.")
                    else:
                        st.write("No references collected yet.")
                else:
                    # Fetch content for each section
                    st.header(section.upper())
                    with st.spinner(f"Fetching {section} content..."):
                        result = fetch_monograph_section(drug_name, section)
                        content = result.get("content", "No content available.")
                        source = result.get("source", None)
                        
                        st.write(content)
                        
                        # Save reference URL if available
                        if source:
                            references[section] = source
                        else:
                            references[section] = "No reference provided."

    else:
        st.info("Please enter a drug name to begin.")

if __name__ == "__main__":
    main()
