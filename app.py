import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import re
import time

st.title("ChatGPT Conversation URL Scraper")

conversation_url = st.text_input("Enter ChatGPT conversation URL (https://chat.openai.com/c/...)")

if conversation_url:
    st.write("Scraping URLs... (make sure you are logged in in your browser!)")
    
    # Set up Selenium Chrome WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--user-data-dir=selenium")  # Keeps your login session
    options.add_argument("--headless")  # Set to False if you want to see the browser
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        driver.get(conversation_url)
        time.sleep(5)  # Wait for page to load

        # Scroll down to load more messages if needed
        for _ in range(3):
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(1)

        # Extract all text elements in messages
        messages = driver.find_elements(By.CSS_SELECTOR, "div[class*='group'] p")
        text_content = " ".join([m.text for m in messages])

        # Extract URLs
        urls = re.findall(r"https?://[^\s]+", text_content)

        if urls:
            st.write(f"Found {len(urls)} URLs:")
            for u in urls:
                st.write(u)
            
            # Download button
            st.download_button(
                label="Download URLs as TXT",
                data="\n".join(urls),
                file_name="chatgpt_urls.txt",
                mime="text/plain"
            )
        else:
            st.write("No URLs found.")
    finally:
        driver.quit()

