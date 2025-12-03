import streamlit as st
from googlesearch import search
import re

st.title("AI Overview Link Scraper (Google Search)")

query = st.text_input("Enter your search query (e.g., 'AI overview websites')")

num_results = st.slider("Number of Google results to fetch:", min_value=5, max_value=50, value=10)

if query:
    st.info(f"Fetching top {num_results} results for: {query}")
    
    urls = []
    for url in search(query, num_results=num_results, lang="en"):
        urls.append(url)
    
    if urls:
        st.subheader(f"Found {len(urls)} URLs:")
        for u in urls:
            st.write(u)
        
        # Download button
        st.download_button(
            label="Download URLs as TXT",
            data="\n".join(urls),
            file_name="ai_overview_links.txt",
            mime="text/plain"
        )
    else:
        st.warning("No URLs found.")


