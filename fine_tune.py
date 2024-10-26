from openai import OpenAI
from decouple import config 

# API 키 설정 (환경 변수로 설정하는 것이 더 안전합니다)
client = OpenAI(api_key = config('OPENAI_API_KEY'))

# jsonl 파일을 업로드
with open(r"C:\Users\ccg70\OneDrive\desktop\넥슨 프로젝트\chatbot_project\chat_formatted_game_qa_data.jsonl", "rb") as file:
    file_response = client.files.create(
        file=file,
        purpose="fine-tune"
    )

# 업로드된 파일 ID로 파인튜닝 요청
fine_tune_response = client.fine_tuning.jobs.create(
    training_file=file_response.id,
    model="gpt-3.5-turbo"
)

print(f"Fine-tune job started: {fine_tune_response.id}")