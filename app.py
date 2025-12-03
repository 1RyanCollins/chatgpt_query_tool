import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import re

st.title("AI Overview Link Scraper (Google Search)")

st.write("Paste a Google search URL, and this tool will extract all AI overview links.")

# User input
search_url = st.text_input("Enter Google search URL:")

# Optional keyword filter
keyword_filter = st.text_input("Optional: filter links containing keyword(s) (comma-separated)", value="AI,Artificial-Intelligence")

# Optional domain filter
domain_filter = st.text_input("Optional: include only specific domains (comma-separated, e.g., .edu,.org)")

if search_url:
    st.info("Fetching Google search results...")

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
        }
        response = requests.get(search_url, headers=headers)
        if response.status_code != 200:
            st.error(f"Failed to fetch page. Status code: {response.status_code}")
        else:
            soup = BeautifulSoup(response.text, "html.parser")
            links = []

            for a in soup.find_all("a", href=True):
                href = a['href']

                # Handle Google redirect /url?q=
                if href.startswith("/url?q="):
                    parsed_url = parse_qs(urlparse(href).query).get("url")
                    if parsed_url:
                        links.append(parsed_url[0])
                # Direct links
                elif href.startswith("http"):
                    links.append(href)

            # Remove duplicates
            links = list(set(links))

            # Apply keyword filter
            if keyword_filter.strip():
                keywords = [k.strip().lower() for k in keyword_filter.split(",")]
                links = [link for link in links if any(kw in link.lower() for kw in keywords)]

            # Apply domain filter
            if domain_filter.strip():
                domains = [d.strip().lower() for d in domain_filter.split(",")]
                links = [link for link in links if any(link.lower().endswith(d) or d in link.lower() for d in domains)]

            if links:
                st.subheader(f"Found {len(links)} AI overview links:")
                for u in links:
                    st.write(u)

                # Download button
                st.download_button(
                    label="Download URLs as TXT",
                    data="\n".join(links),
                    file_name="ai_overview_links.txt",
                    mime="text/plain"
                )
            else:
                st.warning("No links matched the filters.")

    except Exception as e:
        st.error(f"Error: {e}")





