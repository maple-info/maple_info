from openai import OpenAI
from decouple import config 

# API 키 설정 
client = OpenAI(api_key=config('OPENAI_API_KEY'))

# jsonl 파일을 업로드
with open(r"C:\Users\ccg70\OneDrive\desktop\nexon_project\chatbot_project\chat_formatted_game_qa_data.jsonl", "rb") as file:
    file_response = client.files.create(
        file=file,
        purpose="fine-tune"
    )

# 파인튜닝 작업 생성
fine_tune_response = client.fine_tuning.jobs.create(
    training_file=file_response.id,
    model="gpt-4o-2024-08-06", 
    hyperparameters={
        "n_epochs": 4
    }
)

print(f"Fine-tune job started: {fine_tune_response.id}")