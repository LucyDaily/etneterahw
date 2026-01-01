import os
import uuid
import requests
import streamlit as st

# =========================
# UI
# =========================
st.set_page_config(page_title="PM Methodology Advisor", layout="centered")
st.title("PM Methodology Advisor")
st.caption("Interní knowledge bot nad tvými PDF (Langflow RAG).")

# =========================
# Config (ENV / Streamlit Secrets)
# =========================
# LANGFLOW_HOST: např. https://nonprofitable-jolene-untriumphantly.ngrok-free.dev
# LANGFLOW_FLOW_ID: např. c778533b-9fe8-4337-b11e-f9a65e29c099
# LANGFLOW_API_KEY: tvůj Langflow x-api-key (ne OpenAI klíč)

def get_cfg(key: str, default: str = "") -> str:
    # Streamlit Cloud: st.secrets; lokálně: env vars
    if hasattr(st, "secrets") and key in st.secrets:
        return str(st.secrets[key])
    return os.getenv(key, default)

LANGFLOW_HOST = get_cfg("LANGFLOW_HOST", "").rstrip("/")
FLOW_ID = get_cfg("LANGFLOW_FLOW_ID", "")
LANGFLOW_API_KEY = get_cfg("LANGFLOW_API_KEY", "")

if not (LANGFLOW_HOST and FLOW_ID and LANGFLOW_API_KEY):
    st.error("Chybí konfigurace: LANGFLOW_HOST, LANGFLOW_FLOW_ID, LANGFLOW_API_KEY.")
    st.stop()

# =========================
# Session state
# =========================
if "session_id" not in st.session_state:
    st.session_state.session_id = f"chat-{uuid.uuid4()}"

if "messages" not in st.session_state:
    st.session_state.messages = []

# =========================
# Langflow call
# =========================
def call_langflow(user_text: str) -> str:
    """
    Calls Langflow Run Flow API:
    POST {LANGFLOW_HOST}/api/v1/run/{FLOW_ID}?stream=false
    """
    url = f"{LANGFLOW_HOST}/api/v1/run/{FLOW_ID}"
    params = {"stream": "false"}

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "x-api-key": LANGFLOW_API_KEY,
    }

    payload = {
        "input_value": user_text,
        "input_type": "chat",
        "output_type": "chat",
        "session_id": st.session_state.session_id,
    }

    r = requests.post(url, headers=headers, params=params, json=payload, timeout=90)
    r.raise_for_status()
    data = r.json()

    # Langflow response structure can vary by version/flow.
    # We'll try common shapes and fall back to raw JSON.
    # Typical: outputs[0].outputs[0].results.message.text
    try:
        return data["outputs"][0]["outputs"][0]["results"]["message"]["text"].strip()
    except Exception:
        pass

    # Alternative: data["result"] or similar
    for key in ["result", "message", "text", "output"]:
        if key in data and isinstance(data[key], str):
            return data[key].strip()

    return f"⚠️ Nečekaný formát odpovědi z Langflow:\n\n```json\n{data}\n```"

# =========================
# Render history
# =========================
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# =========================
# Input
# =========================
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
                # show useful response for debugging
                try:
                    answer = f"Chyba z Langflow API: {e.response.status_code} – {e.response.text}"
                except Exception:
                    answer = f"Chyba z Langflow API: {e}"
            except Exception as e:
                answer = f"Chyba: {e}"

            st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})

# =========================
# Small debug panel (optional)
# =========================
with st.expander("Debug (volitelné)", expanded=False):
    st.write("LANGFLOW_HOST:", LANGFLOW_HOST)
    st.write("FLOW_ID:", FLOW_ID)
    st.write("session_id:", st.session_state.session_id)
