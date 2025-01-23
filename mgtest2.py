import streamlit as st
from langchain_groq import ChatGroq

# Function to fetch a specific section of the monograph via API
def fetch_monograph_section(drug_name, section):
    """Fetch a specific section of the monograph for the given drug name."""
    llm = ChatGroq(
        temperature=0, 
        groq_api_key="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", 
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
    st.markdown("""<style>
        /* Center-align title relative to input box */
        .title-container {
            display: flex;
            justify-content: center;
            width: 100%;
        }
        /* Right-align the title on the page */
        .title {
            text-align: center;
            width: 100%;
        }
        /* Center-align the drug name input and make it 30% of the page width */
        .drug-input-container {
           
            justify-content: center;
            margin-top: 50px;
        }
        .drug-input {
            width: 70%;  /* Reduced width to 30% */
        }
    </style>""", unsafe_allow_html=True)
    
    st.markdown('<div class="title-container"><h1 class="title">Drug Monograph Generator</h1></div>', unsafe_allow_html=True)

    # Center the drug name input box (30% width)
    st.markdown('<div class="drug-input-container" style="width:400px !important; margin:0 auto">', unsafe_allow_html=True)
    drug_name = st.text_input(
        "Enter Drug Name:", value="", placeholder="e.g., Diclofenac", key="drug_input", help="Type the name of the drug."
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # Create two columns for dynamic title
    col1, col2 = st.columns([1, 1])

    with col1:
        if drug_name.strip():
            st.markdown(f"### Monographs for {drug_name}")
        else:
            st.markdown("")

    if drug_name.strip():
        # Predefined monograph sections and icons
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
            ("REFERENCES", "🔗")
        ]

        # Session state for active section
        if "active_section" not in st.session_state:
            st.session_state.active_section = "INTRODUCTION"

        # Styling for custom buttons
        button_style = """
        <style>
        .button-container {
            display: flex;
            flex-direction: column;
            gap: 10px;
            margin-top: 10px;
        }
        .button {
            font-size: 14px;
            padding: 10px 15px;
            border: 1px solid #ccc;
            border-radius: 5px;
            background-color: #f9f9f9;
            text-align: center;
            cursor: pointer;
            width: 100%;
        }
        .button:hover {
            background-color: #e6e6e6;
        }
        .button.selected {
            background-color: #007bff;
            color: white;
            border-color: #0056b3;
        }
        </style>
        """
        st.markdown(button_style, unsafe_allow_html=True)

        # Create columns: one for buttons, one for content
        col1, col2 = st.columns([1, 3])  # Adjust the column width as needed

        with col1:
            st.markdown("### Sections")
            for section, icon in sections:
                is_selected = section == st.session_state.active_section
                button_class = "button selected" if is_selected else "button"
                button_html = (
                    f'<div class="{button_class}" onclick="fetchMonograph(\'{section}\')">'
                    f"{icon} {section}</div>"
                )
                if st.button(f"{icon} {section}", key=section):
                    st.session_state.active_section = section

        with col2:
            # Fetch and display content for the active section
            with st.spinner(f"Fetching content for {st.session_state.active_section}..."):
                result = fetch_monograph_section(drug_name, st.session_state.active_section)
                content = result.get("content", "No content available.")
                source = result.get("source", None)

            st.subheader(st.session_state.active_section)
            st.write(content)

            # Display reference (if any)
            if source:
                st.markdown(f"**Reference:** [Source]({source})")

    else:
        st.info("Please enter a drug name to begin.")

if __name__ == "__main__":
    main()
