import os
import uuid
import requests
import streamlit as st

st.set_page_config(page_title="PM Methodology Advisor", layout="centered")
st.title("PM Methodology Advisor")

# --- Config (dejte jako env vars / Streamlit Secrets) ---
LANGFLOW_HOST = os.getenv("LANGFLOW_HOST", "").rstrip("/")        # např. https://langflow.yourdomain.cz
FLOW_ID = os.getenv("LANGFLOW_FLOW_ID", "")                       # např. c778533b-...
LANGFLOW_API_KEY = os.getenv("LANGFLOW_API_KEY", "")              # Langflow API key (ne OpenAI key)

if not (LANGFLOW_HOST and FLOW_ID and LANGFLOW_API_KEY):
    st.error("Chybí konfigurace: LANGFLOW_HOST, LANGFLOW_FLOW_ID, LANGFLOW_API_KEY.")
    st.stop()

# --- Session setup ---
if "session_id" not in st.session_state:
    st.session_state.session_id = f"chat-{uuid.uuid4()}"

if "messages" not in st.session_state:
    st.session_state.messages = []

def call_langflow(user_text: str) -> str:
    """
    Calls Langflow Run Flow API:
    POST {LANGFLOW_HOST}/api/v1/run/{FLOW_ID}
    """
    url = f"{LANGFLOW_HOST}/api/v1/run/{FLOW_ID}"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": LANGFLOW_API_KEY,
        "accept": "application/json",
    }
    payload = {
        "input_value": user_text,
        "input_type": "chat",
        "output_type": "chat",
        "session_id": st.session_state.session_id,
        "tweaks": None,
    }

    r = requests.post(url, headers=headers, json=payload, timeout=90)
    r.raise_for_status()
    data = r.json()

    # Typical Langflow response shape: outputs[0].outputs[0].results.message.text
    try:
        return data["outputs"][0]["outputs"][0]["results"]["message"]["text"].strip()
    except Exception:
        # fallback: show something usable instead of dying
        return str(data)

# --- Render history ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- Input ---
prompt = st.chat_input("Napiš dotaz…")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Přemýšlím… (bohužel)"):
            try:
                answer = call_langflow(prompt)
            except requests.HTTPError as e:
                answer = f"Chyba z Langflow API: {e.response.status_code} – {e.response.text}"
            except Exception as e:
                answer = f"Chyba: {e}"

            st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
