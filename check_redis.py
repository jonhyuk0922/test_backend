import os
import csv
from datetime import datetime
from dotenv import load_dotenv
from redis import Redis
from langchain_community.chat_message_histories import RedisChatMessageHistory

# 환경변수 로드
load_dotenv()

def get_redis_url():
    return f"redis://{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}/{os.getenv('REDIS_DB')}"

def export_redis_messages_to_csv():
    # Redis 연결
    redis_client = Redis.from_url(get_redis_url())
    
    # CSV 파일명 생성 (현재 시간 포함)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"chat_history_{timestamp}.csv"
    
    # CSV 파일 생성
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # 헤더 작성
        writer.writerow(['Session ID', 'Message Type', 'Content', 'Timestamp'])
        
        # 모든 키 가져오기
        all_keys = redis_client.keys("message_store:*")
        
        # 각 세션의 메시지 저장
        for key in all_keys:
            session_id = key.decode('utf-8').replace("message_store:", "")
            
            # LangChain의 RedisChatMessageHistory 사용
            message_history = RedisChatMessageHistory(
                session_id=session_id,
                url=get_redis_url()
            )
            
            # 메시지 저장
            for msg in message_history.messages:
                writer.writerow([
                    session_id,
                    msg.type,  # 'human' 또는 'ai'
                    msg.content,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 현재 시간 기록
                ])
    
    print(f"대화 내역이 {csv_filename}에 저장되었습니다.")
    return csv_filename

if __name__ == "__main__":
    export_redis_messages_to_csv()