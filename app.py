import streamlit as st
import requests
import json
import re

st.title("ChatGPT Conversation Event Stream Inspector")
st.write(
    """
This app extracts **search model queries** and **search result domains/URLs** 
from a ChatGPT conversation.

**Important:** You need your ChatGPT **session token** to access the private API.
"""
)

st.markdown("""
### How to get your ChatGPT session token:
1. Open [ChatGPT](https://chat.openai.com/) in your browser and log in.
2. Open Developer Tools:
   - Chrome / Edge: `Ctrl+Shift+I` or `Cmd+Option+I` (Mac)
   - Firefox: `F12`
3. Go to `Application` / `Storage` → `Cookies` → select `https://chat.openai.com`
4. Find the cookie named `__Secure-next-auth.session-token`
5. Copy the **Value** of that cookie and paste it below.
""")

# -----------------------------
# User Inputs
# -----------------------------
session_token = st.text_input("Paste your ChatGPT session token:", type="password")
url = st.text_input("Paste ChatGPT conversation URL:")

# -----------------------------
# Helper functions
# -----------------------------
def extract_conversation_id(url: str):
    """Extract conversation ID from https://chatgpt.com/c/<ID>"""
    match = re.search(r"/c/([a-zA-Z0-9\-]+)", url)
    return match.group(1) if match else None


def fetch_eventstream(conversation_id: str, token: str):
    """Fetch raw SSE event stream using session token."""
    endpoint = f"https://chatgpt.com/backend-api/f/conversation/{conversation_id}"

    headers = {
        "Accept": "text/event-stream",
        "User-Agent": "Mozilla/5.0",
        "Cookie": f"__Secure-next-auth.session-token={token}",
    }

    response = requests.get(endpoint, headers=headers, stream=True)

    if response.status_code != 200:
        st.error(f"Error fetching stream: {response.status_code}")
        return None

    raw_text = ""
    for chunk in response.iter_lines(decode_unicode=True):
        if chunk:
            raw_text += chunk + "\n"

    return raw_text


def parse_sse(raw_text: str):
    """Parse Server-Sent Events into structured objects."""
    events = []
    current = {"event": None, "data": ""}

    for line in raw_text.splitlines():
        if line.startswith("event:"):
            if current["event"] or current["data"]:
                events.append(current)
            current = {"event": line.replace("event:", "").strip(), "data": ""}

        elif line.startswith("data:"):
            current["data"] += line.replace("data:", "").strip()

        elif line == "":
            if current["event"] or current["data"]:
                events.append(current)
            current = {"event": None, "data": ""}

    return events


def extract_search_metadata(parsed_events):
    search_queries = []
    search_results = []

    for ev in parsed_events:
        if not ev["data"]:
            continue

        try:
            payload = json.loads(ev["data"])
        except:
            continue

        # -------- Path-based metadata --------
        p = payload.get("p")
        v = payload.get("v")

        if p == "/message/metadata/search_model_queries":
            if isinstance(v, list):
                for item in v:
                    search_queries.append(item)

        if p == "/message/metadata/search_result_groups":
            if isinstance(v, list):
                for group in v:
                    domain = group.get("domain")
                    for entry in group.get("entries", []):
                        search_results.append({
                            "domain": domain,
                            "url": entry.get("url"),
                            "title": entry.get("title"),
                            "snippet": entry.get("snippet")
                        })

        # -------- Delta events --------
        if ev["event"] == "delta":
            try:
                message = payload["v"]["message"]
                metadata = message.get("metadata", {})
            except:
                continue

            # search_model_queries
            if "search_model_queries" in metadata:
                smq = metadata["search_model_queries"]
                if isinstance(smq, dict) and "queries" in smq:
                    for q in smq["queries"]:
                        search_queries.append(q)

            # search_result_groups
            if "search_result_groups" in metadata:
                srg = metadata["search_result_groups"]
                if isinstance(srg, list):
                    for group in srg:
                        domain = group.get("domain")
                        for entry in group.get("entries", []):
                            search_results.append({
                                "domain": domain,
                                "url": entry.get("url"),
                                "title": entry.get("title"),
                                "snippet": entry.get("snippet")
                            })

    return search_queries, search_results


# -----------------------------
# Run Extraction
# -----------------------------
if st.button("Process"):
    if not session_token:
        st.warning("Paste your ChatGPT session token first.")
        st.stop()

    if not url:
        st.warning("Paste a conversation URL first.")
        st.stop()

    conv_id = extract_conversation_id(url)
    if not conv_id:
        st.error("Cannot extract conversation ID from URL.")
        st.stop()

    st.info(f"Conversation ID: {conv_id}")

    with st.spinner("Fetching event stream..."):
        raw = fetch_eventstream(conv_id, session_token)

    if not raw:
        st.error("Failed to load conversation event stream. Check your session token.")
        st.stop()

    st.success("Event stream loaded successfully.")

    st.expander("Raw Event Stream").write(raw)

    parsed = parse_sse(raw)
    st.write(f"Parsed **{len(parsed)}** events.")

    search_queries, search_results = extract_search_metadata(parsed)

    # Display search queries
    st.subheader("🔍 Search Model Queries")
    if search_queries:
        st.json(search_queries)
    else:
        st.write("None found.")

    # Display search results (domains, URLs)
    st.subheader("🌐 Extracted Search Result Domains & URLs")
    if search_results:
        st.dataframe(search_results)
    else:
        st.write("None found.")

