import streamlit as st
from langchain_groq import ChatGroq

# Function to fetch a specific section of the monograph via API
def fetch_monograph_section(drug_name, section):
    """Fetch a specific section of the monograph for the given drug name from approved sources."""
    llm = ChatGroq(
        temperature=0,
        groq_api_key="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",
        model_name="llama3-8b-8192"
    )
    prompt = (
        f"Provide a detailed {section} section for the drug '{drug_name}' using references from NCI, "
        "WHO-ATC, FDA, Dailymed, Canada, TGA, Pubchem, and Statpearls only. Include the source URL."
    )
    
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
    st.set_page_config(layout="wide")
    st.markdown(
        """<style>
        .title-container {
            display: flex;
            justify-content: center;
            width: 100%;
        }
        .title {
            text-align: center;
            width: 100%;
        }
        .drug-input-container {
            justify-content: center;
            margin-top: 50px;
        }
        .drug-input {
            width: 70%;
        }
    </style>""",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="title-container"><h1 class="title">Drug Monograph Generator</h1></div>', unsafe_allow_html=True)

    st.markdown('<div class="drug-input-container" style="width:400px !important; margin:0 auto">', unsafe_allow_html=True)
    drug_name = st.text_input("Enter Drug Name:", value="", placeholder="e.g., Diclofenac", key="drug_input", help="Type the name of the drug.")
    st.markdown('</div>', unsafe_allow_html=True)

    if drug_name.strip():
        sections = [
            ("INTRODUCTION", "📘"),
            ("CLASSIFICATION", "📚"),
            ("INDICATIONS AND USAGE", "💊"),
            ("DOSAGE FORMS AND STRENGTHS", "🧪"),
            ("DOSAGE AND ADMINISTRATION", "📝"),
            ("CONTRAINDICATIONS", "🚫"),
            ("WARNING AND PRECAUTIONS", "⚠️"),
            ("ADVERSE REACTIONS", "😷"),
            ("DRUG INTERACTIONS", "🔄"),
            ("USE IN SPECIFIC POPULATIONS", "👩‍👩‍👦"),
            ("CLINICAL PHARMACOLOGY", "🔬"),
            ("NONCLINICAL TOXICOLOGY", "🐀"),
            ("CLINICAL STUDIES", "📊"),
            ("DRUG TO DRUG INTERACTIONS", "🔗"),
            ("DRUG TO FOOD ALLERGIES", "🍎"),
            ("REFERENCES", "🔗"),
        ]

        if "active_section" not in st.session_state:
            st.session_state.active_section = "INTRODUCTION"

        col1, col2 = st.columns([1, 3])

        with col1:
            st.markdown("### Sections")
            for section, icon in sections:
                is_selected = section == st.session_state.active_section
                if st.button(f"{icon} {section}", key=section):
                    st.session_state.active_section = section

        with col2:
            with st.spinner(f"Fetching content for {st.session_state.active_section}..."):
                result = fetch_monograph_section(drug_name, st.session_state.active_section)
                content = result.get("content", "No content available.")
                source = result.get("source", None)

            st.subheader(st.session_state.active_section)
            st.write(content)

            if source:
                st.markdown(f"**Reference:** [Source]({source})")
    else:
        st.info("Please enter a drug name to begin.")


if __name__ == "__main__":
    main()
