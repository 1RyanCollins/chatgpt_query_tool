import streamlit as st
import requests
import json
import re

st.title("ChatGPT Conversation Event Stream Inspector")
st.write("Paste a ChatGPT conversation URL and extract search model queries, domains, URLs, and more.")

# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------

def extract_conversation_id(url: str):
    """Extract conversation ID from https://chatgpt.com/c/<ID>"""
    match = re.search(r"/c/([a-zA-Z0-9\-]+)", url)
    return match.group(1) if match else None


def fetch_eventstream(conversation_id: str):
    """Fetch raw SSE event stream."""
    endpoint = f"https://chatgpt.com/backend-api/f/conversation/{conversation_id}"

    headers = {
        "Accept": "text/event-stream",
        "User-Agent": "Mozilla/5.0",
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
    search_queries = []   # strings from search_model_queries
    search_results = []   # domain/url/title/snippet

    for ev in parsed_events:
        if not ev["data"]:
            continue

        # Try reading JSON
        try:
            payload = json.loads(ev["data"])
        except:
            continue

        # -------------------------------------------------
        # CASE A — Path-based metadata events
        # -------------------------------------------------
        p = payload.get("p")
        v = payload.get("v")

        # Extract search_model_queries from path events
        if p == "/message/metadata/search_model_queries":
            if isinstance(v, list):
                for item in v:
                    search_queries.append(item)

        # Extract search_result_groups from path events
        if p == "/message/metadata/search_result_groups":
            if isinstance(v, list):
                for group in v:
                    domain = group.get("domain")

                    for entry in group.get("entries", []):
                        search_results.append({
                            "domain": domain,
                            "url": entry.get("url"),
                            "title": entry.get("title"),
                            "snippet": entry.get("snippet"),
                        })

        # -------------------------------------------------
        # CASE B — Delta events (event: delta)
        # -------------------------------------------------
        if ev["event"] == "delta":
            try:
                message = payload["v"]["message"]
                metadata = message.get("metadata", {})
            except:
                continue

            # search_model_queries inside delta
            if "search_model_queries" in metadata:
                smq = metadata["search_model_queries"]
                if isinstance(smq, dict) and "queries" in smq:
                    for q in smq["queries"]:
                        search_queries.append(q)

            # search_result_groups inside delta
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
                                "snippet": entry.get("snippet"),
                            })

    return search_queries, search_results


# ---------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------

url = st.text_input("Paste ChatGPT Conversation URL")

if st.button("Process"):
    if not url:
        st.warning("Paste a URL first.")
        st.stop()

    conv_id = extract_conversation_id(url)
    if not conv_id:
        st.error("Cannot extract conversation ID.")
        st.stop()

    st.info(f"Conversation ID: {conv_id}")

    with st.spinner("Fetching event stream..."):
        raw = fetch_eventstream(conv_id)

    if not raw:
        st.error("Could not fetch eventstream.")
        st.stop()

    st.success("Event stream loaded successfully.")

    st.expander("Raw Eventstream").write(raw)

    parsed = parse_sse(raw)
    st.write(f"Parsed **{len(parsed)}** events.")

    search_queries, search_results = extract_search_metadata(parsed)

    # Display search_model_queries
    st.subheader("🔍 Search Model Queries")
    if search_queries:
        st.json(search_queries)
    else:
        st.write("None found.")

    # Display domain+URL results
    st.subheader("🌐 Extracted Search Result Domains & URLs")
    if search_results:
        st.dataframe(search_results)
    else:
        st.write("None found.")
