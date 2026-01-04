import streamlit as st
import requests
import uuid

# --- KONFIGURACE ---
API_URL = "https://langflow-production-dcd6.up.railway.app/api/v1/run/b455aef5-a951-44cf-9f48-dabbe70b4225"
# API klíč doporučuji uložit do Streamlit Secrets (viz níže)
API_KEY = st.secrets.get("LANGFLOW_API_KEY", "TVŮJ_DOČASNÝ_KLÍČ_POKUD_NEMÁŠ_SECRETS")

st.set_page_config(page_title="Senior AI Project Coordinator", page_icon="🤖")

st.title("🤖 Senior AI Project Coordinator")
st.caption("Projekt ET - Jira & Confluence Support")

# --- SESSION STATE (PAMĚŤ) ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# Vykreslení historie chatu
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- FUNKCE PRO VOLÁNÍ API ---
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
        result = response.json()
        
        # Langflow vrací odpověď v různé struktuře podle verze, 
        # většinou je v: result['outputs'][0]['outputs'][0]['results']['message']['text']
        # Pro jistotu použijeme bezpečný přístup:
        return result['outputs'][0]['outputs'][0]['results']['message']['text']
    except Exception as e:
        return f"Chyba při komunikaci s agentem: {str(e)}"

# --- INPUT OD UŽIVATELE ---
if user_input := st.chat_input("Jaký je stav sprintu?"):
    # Přidání zprávy uživatele do historie
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Odpověď agenta
    with st.chat_message("assistant"):
        with st.spinner("Agent přemýšlí a kontroluje Jiru..."):
            response = ask_agent(user_input)
            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
