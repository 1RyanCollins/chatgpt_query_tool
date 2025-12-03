import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, parse_qs

st.title("Google Search URL Scraper")

search_url = st.text_input("Enter a Google search URL:")

if search_url:
    st.info("Fetching Google search results...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(search_url, headers=headers)
        if response.status_code != 200:
            st.error(f"Failed to fetch page. Status code: {response.status_code}")
        else:
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract URLs from <a> tags in search results
            links = []
            for a in soup.find_all("a", href=True):
                href = a['href']
                # Google search result URLs are usually in format "/url?q=<actual_url>&..."
                if href.startswith("/url?q="):
                    parsed_url = parse_qs(urlparse(href).query).get("q")
                    if parsed_url:
                        links.append(parsed_url[0])

            # Remove duplicates
            links = list(set(links))

            if links:
                st.subheader(f"Found {len(links)} URLs:")
                for u in links:
                    st.write(u)
                
                st.download_button(
                    label="Download URLs as TXT",
                    data="\n".join(links),
                    file_name="google_search_links.txt",
                    mime="text/plain"
                )
            else:
                st.warning("No URLs found in this search page.")
    except Exception as e:
        st.error(f"Error: {e}")



