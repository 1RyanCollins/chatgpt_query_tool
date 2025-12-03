import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import time

st.title("Google AI Overview Link Scraper")

st.write("Paste a Google search URL, and this tool will extract all AI overview links.")

search_url = st.text_input("Enter Google search URL:")

# Optional keyword filter
keyword_filter = st.text_input("Optional keyword filter (comma-separated)", value="AI,Artificial-Intelligence")

# Optional domain filter
domain_filter = st.text_input("Optional domain filter (comma-separated, e.g., .edu,.org)")

if search_url:
    st.info("Opening Google search results in a headless browser...")

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run Chrome in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(search_url)
        time.sleep(3)  # wait for page to load

        # Optional: scroll to load more results
        for _ in range(3):
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(1)

        html_content = driver.page_source
        soup = BeautifulSoup(html_content, "html.parser")

        links = []

        for a in soup.find_all("a", href=True):
            href = a['href']
            # Google redirect /url?q=
            if href.startswith("/url?q="):
                parsed_url = parse_qs(urlparse(href).query).get("q")
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
    finally:
        driver.quit()





