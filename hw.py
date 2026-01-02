import streamlit as st
import requests
import uuid

import streamlit as st

LANGFLOW_HOST = st.secrets["LANGFLOW_HOST"].rstrip("/")
FLOW_ID = st.secrets["LANGFLOW_FLOW_ID"]
LANGFLOW_API_KEY = st.secrets["LANGFLOW_API_KEY"]


st.set_page_config(page_title="PM Advisor Bot")
st.title("PM Methodology Advisor")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

user_input = st.chat_input("Zeptej se…")

if user_input:
    st.chat_message("user").write(user_input)

    payload = {
        "input_value": user_input,
        "input_type": "chat",
        "output_type": "chat",
        "session_id": st.session_state.session_id
    }

    r = requests.post(
        f"{LANGFLOW_HOST}/api/v1/run/{FLOW_ID}?stream=false",
        headers={
            "Content-Type": "application/json",
            "x-api-key": API_KEY
        },
        json=payload,
        timeout=60
    )

    if r.status_code != 200:
        st.error(r.text)
    else:
        data = r.json()
        answer = data["outputs"][0]["outputs"][0]["results"]["message"]["text"]
        st.chat_message("assistant").write(answer)
