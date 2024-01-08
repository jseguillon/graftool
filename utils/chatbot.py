import os
import streamlit as st
from openai import OpenAI

def chatbot(*kwargs):
    st.title("Kubernetes chatbot")

    with st.expander("💡Examples", True):
        tab1, tab2 = st.tabs(["Resources creation", "Troubleshoot"])
        with tab1: 
            st.markdown(
"""
This bot can help for creating Yaml files. Try copy paste this query:

```
Create a Deployment plus a Service for a streamlit app named graftool.
Also give Dockerfile template.
```
""")
        
        with tab2:
            st.markdown(
"""
This bot can help for troubleshooting Kubernetes. Copy paste this error:
```
Pod: alertmanager-main-1
Namespace: monitoring

Event: 
    Last State:  Terminated                                                                                                                                                                                  
      Reason:    Unknown                                                                                                                                                                                     
      Message:   93/-/reload\": dial tcp [::1]:9093: connect: connection refused"                                                                                                                            
level=error ts=2024-01-07T21:33:19.448616532Z caller=runutil.go:100 msg="function failed. Retrying in next tick" 
err="trigger reload: reload request failed: Post \"http://localhost:9093/-/reload\": dial tcp [::1]:9093: connect: connection refused
```
""")

    open_ai_api_key = None
    if "open_ai_api_key" in os.environ:
        open_ai_api_key = os.environ["open_ai_api_key"]
    else:
        open_ai_api_key = st.secrets.OPENAI_API_KEY
    
    client = OpenAI(api_key=open_ai_api_key)

    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-3.5-turbo"

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("How can I help?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            for response in client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[{"role": "system","content": 
""""
You are a helpful assistant specialiazed in helping user with Kubernetes.
Noticeably, you recommend kubectl commands to help troubleshoot and create yaml content.
Always output yaml in markdown yaml block code.
"""}]+ [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            ):
                full_response += (response.choices[0].delta.content or "")
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
