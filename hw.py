import streamlit as st
import requests
import uuid

# --- KONFIGURACE ---
API_KEY = "YOUR_API_KEY_HERE"  # Doporučuji použít st.secrets pro produkci
API_URL = "https://langflow-production-dcd6.up.railway.app/api/v1/run/b455aef5-a951-44cf-9f48-dabbe70b4225"

st.set_page_config(page_title="Senior AI Project Coordinator", page_icon="📊")

st.title("📊 Senior AI Project Coordinator")
st.caption("Projektový asistent pro projekt ET (Jira + Confluence + Slack)")

# Inicializace session_id (aby agent věděl, s kým mluví)
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Inicializace historie zpráv
if "messages" not in st.session_state:
    st.session_state.messages = []

# Zobrazení historie zpráv z session_state
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Funkce pro volání Langflow API
def ask_agent(prompt):
    payload = {
        "output_type": "chat",
        "input_type": "chat",
        "input_value": prompt,
        "session_id": st.session_state.session_id
    }
    headers = {"x-api-key": API_KEY}
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Extrakce textové odpovědi z Langflow JSON struktury
        # Poznámka: Cesta v JSONu se může lišit podle verze Langflow, 
        # obvykle je to: outputs[0] -> outputs[0] -> results -> message -> text
        message_text = data['outputs'][0]['outputs'][0]['results']['message']['text']
        return message_text
    
    except Exception as e:
        return f"❌ Chyba při komunikaci s agentem: {str(e)}"

# Chat interface
if prompt := st.chat_input("Jaký je stav sprintu ET?"):
    # 1. Přidat zprávu uživatele do historie a zobrazit ji
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Získat odpověď od agenta
    with st.chat_message("assistant"):
        with st.spinner("Agent přemýšlí a kontroluje Jiru..."):
            response_text = ask_agent(prompt)
            st.markdown(response_text)
    
    # 3. Přidat odpověď asistenta do historie
    st.session_state.messages.append({"role": "assistant", "content": response_text})
