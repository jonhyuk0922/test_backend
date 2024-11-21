import streamlit as st
import requests
import uuid

st.title("AI 상담사와의 대화")

# 세션 ID 생성 또는 가져오기
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# 대화 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 대화 기록 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력
if prompt := st.chat_input("메시지를 입력하세요"):
    # 사용자 메시지 표시
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        # AI 응답 생성
        response = requests.post(
            "http://backend:8000/chat",
            json={
                "message": prompt,
                "session_id": st.session_state.session_id
            }
        )
        
        if response.status_code == 200:
            # AI 응답 표시
            assistant_message = response.json()["message"]
            with st.chat_message("assistant"):
                st.markdown(assistant_message)
            st.session_state.messages.append({"role": "assistant", "content": assistant_message})
        else:
            st.error(f"서버 오류: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"연결 오류: {str(e)}")