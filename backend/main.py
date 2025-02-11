from fastapi import FastAPI
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

# 환경변수 로드
load_dotenv()

app = FastAPI()

class ChatInput(BaseModel):
    message: str
    session_id: str

class ChatResponse(BaseModel):
    message: str

DEFAULT_PROMPT = """당신은 전문 상담사입니다. 공감적 경청과 전문적 응답으로 내담자를 도와주세요."""

# Redis URL 생성 함수
def get_redis_url():
    return f"redis://{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}/{os.getenv('REDIS_DB')}"

# 프롬프트 로드 함수
def load_prompt():
    try:
        with open("prompts/counselor_prompt.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return DEFAULT_PROMPT

def get_message_history(session_id: str):
    return RedisChatMessageHistory(
        session_id=session_id,
        url=get_redis_url()
    )

# OpenAI 모델 초기화
chat = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
)

@app.post("/chat", response_model=ChatResponse)
async def chat_with_counselor(chat_input: ChatInput):
    print(f"Received input: {chat_input}")  # 입력 데이터 로깅
    try:
        # 프롬프트 템플릿 생성
        prompt = ChatPromptTemplate.from_messages([
            ("system", load_prompt()),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])
        
        # 체인 생성
        chain = prompt | chat
        
        # Runnable with history 생성
        chain_with_history = RunnableWithMessageHistory(
            chain,
            get_message_history,
            input_messages_key="input",
            history_messages_key="history",
        )
        
        # 대화 실행
        response = chain_with_history.invoke(
            {"input": chat_input.message},
            config={"configurable": {"session_id": chat_input.session_id}}
        )
        
        return ChatResponse(message=response.content)
    except Exception as e:
        print(f"Error: {str(e)}")  # 오류 로깅
        raise

@app.get("/health")
async def health_check():
    return {"status": "healthy"}