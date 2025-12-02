import streamlit as st
import requests
import pandas as pd
import json

st.title("ChatGPT Conversation Analyzer (API Key)")

api_key = st.text_input("Enter your OpenAI API Key", type="password")
conversation_url = st.text_input("Enter ChatGPT Conversation URL")

def fetch_conversation(url, api_key):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    # Assuming the conversation ID is the last part of the URL
    conversation_id = url.rstrip("/").split("/")[-1]
    api_endpoint = f"https://api.openai.com/v1/conversations/{conversation_id}/events"

    response = requests.get(api_endpoint, headers=headers)
    if response.status_code != 200:
        st.error(f"Failed to fetch conversation: {response.status_code}")
        return None

    return response.json()

def parse_events(events):
    queries, domains, urls, titles, snippets = [], [], [], [], []

    for event in events.get("events", []):
        delta = event.get("delta", {})
        if "search_model_queries" in delta:
            queries.append(delta["search_model_queries"])
        if "domains" in delta:
            domains.append(delta["domains"])
        if "URLs" in delta:
            urls.append(delta["URLs"])
        if "titles" in delta:
            titles.append(delta["titles"])
        if "snippets" in delta:
            snippets.append(delta["snippets"])

    df = pd.DataFrame({
        "search_model_queries": queries if queries else [None],
        "domains": domains if domains else [None],
        "URLs": urls if urls else [None],
        "titles": titles if titles else [None],
        "snippets": snippets if snippets else [None],
    })
    return df

if st.button("Fetch and Parse"):
    if not api_key or not conversation_url:
        st.warning("Please enter both API key and conversation URL")
    else:
        events = fetch_conversation(conversation_url, api_key)
        if events:
            df = parse_events(events)
            st.subheader("Extracted Data")
            st.dataframe(df)

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download CSV",
                data=csv,
                file_name="chatgpt_conversation_data.csv",
                mime="text/csv"
            )


