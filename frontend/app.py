import streamlit as st
from utils import upload_document, ask_question

st.set_page_config(
    page_title="Mediquery",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# custom css
st.markdown("""
<style>
    /* Main header */
    .main-header {
        background: linear-gradient(90deg, #1a73e8, #0d47a1);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: white;
    }
    .main-header h1 { margin: 0; font-size: 2rem; }
    .main-header p  { margin: 0.3rem 0 0 0; opacity: 0.85; font-size: 1rem; }

    /* Chat bubbles */
    .chat-user {
        background: #e3f2fd;
        border-left: 4px solid #1a73e8;
        padding: 0.8rem 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .chat-assistant {
        background: #f1f8e9;
        border-left: 4px solid #2e7d32;
        padding: 0.8rem 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }

    /* Source citation card */
    .source-card {
        background: #fff8e1;
        border: 1px solid #f9a825;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        margin: 0.3rem 0;
        font-size: 0.85rem;
    }

    /* Uploaded doc pill */
    .doc-pill {
        background: #e8f5e9;
        border: 1px solid #a5d6a7;
        border-radius: 20px;
        padding: 0.3rem 0.8rem;
        font-size: 0.85rem;
        margin: 0.2rem 0;
        display: inline-block;
    }

    /* Hide Streamlit branding */
    #MainMenu { visibility: hidden; }
    footer     { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

#session state initialization
if "uploaded_docs" not in st.session_state:
    st.session_state.uploaded_docs = [] # list of {document_id, filename, pages, chunks}

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [] # list of {role, content, sources}

if "selected_doc_id" not in st.session_state:
    st.session_state.selected_doc_id = None


# header
st.markdown("""
<div class="main-header">
    <h1>🏥 MediQuery</h1>
    <p>AI-powered Healthcare Document Q&A — Upload a PDF and ask anything.</p>
</div>
""", unsafe_allow_html=True)

# layout: two columns
left_col, right_col = st.columns([1,2], gap="large")

# left column - upload panel
with left_col:
    st.subheader("📁 Document Upload")

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Max file size: 10MB. Healthcare PDFs only."
    )

    if uploaded_file:
        file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
        st.caption(f"📄 {uploaded_file.name} — {file_size_mb:.2f} MB")

        if st.button("Upload & Index", use_container_width=True, type="primary"):
            # check duplicate
            already_uploaded = any(
                d["filename"] == uploaded_file.name
                for d in st.session_state.upload_docs
            )
            if already_uploaded:
                st.warning("This file is already uploaded.")
            else:
                with st.spinner("Parsing, chunking, and indexing document..."):
                    result = upload_document(uploaded_file)

                if result:
                    st.session_state.uploaded_docs.append({
                        "document_id": result["document_id"],
                        "filename": result["filename"],
                        "pages": result["pages"],
                        "chunks": result["chunks_stored"]
                    })
                    st.success(f"✅ Indexed {result['chunks_stored']} chunks from {result['pages']} pages!")

    # uploaded documents list
    st.divider()
    st.subheader("📚 Indexed Documents")

    if not st.session_state.uploaded_docs:
        st.info("No documents uploaded yet.")
    else:
        doc_options = {"🔍 Search all documents": None}
        for doc in st.session_state.uploaded_docs:
            label = f"📄 {doc['filename']}"
            doc_options[label] = doc["document_id"]

        selected_label = st.radio(
            "Scope your question to:",
            options=list(doc_options.keys()),
            index=0
        )
        st.session_state.selected_doc_id = doc_options[selected_label]

        st.divider()
        st.caption("**Uploaded files:**")
        for doc in st.session_state.uploaded_docs:
            st.markdown(
                f'<div class="doc-pill">✅ {doc["filename"]} '
                f'— {doc["pages"]}p / {doc["chunks"]} chunks</div>',
                unsafe_allow_html=True
            )

    # clear chat
    st.divider()
    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# right column - chat panel
with right_col:
    st.subheader("💬 Ask a Question")

    # chat history display
    chat_container = st.container()
    with chat_container:
        if not st.session_state.chat_history:
            st.markdown("""
            > 👋 **Welcome to MediQuery!**
            > Upload a healthcare PDF on the left, then ask questions here.
            > Answers are grounded in your documents with source citations.
            """)
        else:
            for entry in st.session_state.chat_history:
                if entry["role"] == "user":
                    st.markdown(
                        f'<div class="chat-user">🧑 <strong>You:</strong> {entry["content"]}</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f'<div class="chat-assistant">🤖 <strong>MediQuery:</strong> {entry["content"]}</div>',
                        unsafe_allow_html=True
                    )

                    # show sources if available
                    if entry.get("sources"):
                        with st.expander(f"📄 View {len(entry['sources'])} source(s)"):
                            for i, source in enumerate(entry["sources"], 1):
                                st.markdown(
                                    f'<div class="source-card">'
                                    f'<strong>Source {i}</strong> — '
                                    f'📄 {source["filename"]} | Page {source["page"]}<br>'
                                    f'<em>"{source["content"]}..."</em>'
                                    f'</div>',
                                    unsafe_allow_html=True
                                )

    st.divider()

    # question input
    if not st.session_state.uploaded_docs:
        st.warning("⬅️ Please upload a document first before asking questions.")
    else:
        with st.form(key="question_form", clear_on_submit=True):
            question = st.text_area(
                "Your question:",
                placeholder="e.g. What are the contraindications for this medication?",
                height=80
            )
            col1, col2 = st.columns([3,1])
            with col1:
                scope_label = (
                    f"📄 {selected_label.replace('📄 ', '')}"
                    if st.session_state.selected_doc_id
                    else "🔍 All documents"
                )
                st.caption(f"Searching: **{scope_label}**")
            with col2:
                submit = st.form_submit_button(
                    "Ask ➤",
                    use_container_width=True,
                    type="primary"
                )

        if submit and question.strip():
            # add user message to history
            st.session_state.chat_history.append({
                "role": "user",
                "content": question
            })

            with st.spinner("🔍 Retrieving and generating answer..."):
                result = ask_question(
                    question,
                    st.session_state.selected_doc_id
                )

            if result:
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "sources": result["sources"]
                })

            st.rerun()

        elif submit and not question.strip():
            st.warning("Please enter a question.")