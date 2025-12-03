import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

st.title("Google Search Link Extractor")

st.write("Paste a Google search URL below, and this tool will extract all external links from the search results.")

# User input: Google search URL
search_url = st.text_input("Enter Google search URL:")

# Optionally, let the user upload an HTML file instead
html_file = st.file_uploader("Or upload a saved Google search HTML page", type=["html"])

if search_url or html_file:
    st.info("Extracting links...")
    try:
        # If user uploads a file, use its contents
        if html_file:
            html_content = html_file.read().decode("utf-8")
        else:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                              "(KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
            }
            response = requests.get(search_url, headers=headers)
            if response.status_code != 200:
                st.error(f"Failed to fetch page. Status code: {response.status_code}")
            html_content = response.text

        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")
        links = []

        for a in soup.find_all("a", href=True):
            href = a['href']
            if href.startswith("http"):
                links.append(href)
            elif href.startswith("/url?q="):
                parsed_url = parse_qs(urlparse(href).query).get("q")
                if parsed_url:
                    links.append(parsed_url[0])

        # Remove duplicates
        links = list(set(links))

        if links:
            st.subheader(f"Found {len(links)} URLs:")
            for u in links:
                st.write(u)

            # Download button
            st.download_button(
                label="Download URLs as TXT",
                data="\n".join(links),
                file_name="google_search_links.txt",
                mime="text/plain"
            )
        else:
            st.warning("No external links found.")

    except Exception as e:
        st.error(f"Error: {e}")





