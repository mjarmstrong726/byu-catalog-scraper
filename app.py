import streamlit as st
from byu_catalog_scraper import scrape_major
from pathlib import Path

st.set_page_config(page_title="BYU Catalog Scraper", layout="centered")

st.title("📘 BYU Catalog Scraper")
st.markdown("Enter a BYU catalog program URL below to extract program and course outcomes.")

# Input field
url = st.text_input("BYU Catalog Program URL", "https://catalog.byu.edu/programs/34250")

# Button to trigger scraping
if st.button("Compile Outcomes"):
    output_file = "outcomes.txt"

    try:
        scrape_major(url, output_file=output_file, offline=False)
        st.success("✅ Scraping complete!")

        # Display the text content
        txt_content = Path(output_file).read_text(encoding="utf-8")
        st.text_area("Scraped Outcomes", value=txt_content, height=400)

        # Allow download of the .txt file
        st.download_button("Download Outcomes", data=txt_content, file_name="outcomes.txt", mime="text/plain")

    except Exception as e:
        st.error(f"❌ Error: {e}")

