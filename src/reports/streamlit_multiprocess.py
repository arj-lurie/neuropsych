import streamlit as st
import time
import multiprocessing
from pathlib import Path
import tempfile
import os
import shutil

# -----------------------------
# Your existing process_pdf
# -----------------------------
from main_multiprocess import process_pdf


# -----------------------------
# Helper to save uploaded PDFs
# -----------------------------
def save_uploaded_file(uploaded_file):
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, uploaded_file.name)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return temp_path, temp_dir  # return dir to clean up later

# -----------------------------
# Streamlit App
# -----------------------------
def main():
    st.title("📄 NHORA: Neuropsych History Observation & Reporting Assistant")

    uploaded_files = st.file_uploader(
        "Upload one or more PDFs", 
        type=["pdf"], 
        accept_multiple_files=True
    )

    if uploaded_files and st.button("Process PDFs"):
        total_start = time.time()
        saved_files = [save_uploaded_file(f) for f in uploaded_files]
        pdf_paths = [f[0] for f in saved_files]
        temp_dirs = [f[1] for f in saved_files]  # for cleanup later

        st.info(f"Found {len(pdf_paths)} PDFs. Processing...")

        progress = st.progress(0)
        status_text = st.empty()
        processed_html_contents = []

        # Multiprocessing
        with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
            for i, (name, html_content) in enumerate(pool.imap_unordered(process_pdf, pdf_paths), 1):
                progress.progress(i / len(pdf_paths))
                status_text.text(f"Processed {i}/{len(pdf_paths)} PDFs")
                processed_html_contents.append((name, html_content))

        total_elapsed = time.time() - total_start
        st.success(f"🏁 All PDFs processed in {total_elapsed:.2f} seconds.")

        # Display HTML inline and provide download button
        for name, html_content in processed_html_contents:
            st.markdown(f"### {name}")
            with st.expander(f"View & Download {name}", expanded=True):
                st.components.v1.html(html_content, height=600, scrolling=True)
                st.download_button(
                    label="Download HTML",
                    data=html_content.encode("utf-8"),
                    file_name=name,
                    mime="text/html"
                )
            
        # # Cleanup temp dirs safely
        st.session_state.temp_dirs = temp_dirs

if __name__ == "__main__":
    main()
