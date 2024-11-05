from openai import OpenAI
from decouple import config 

# API 키 설정 
client = OpenAI(api_key=config('OPENAI_API_KEY'))

# jsonl 파일을 업로드
with open(r"C:\Users\ccg70\OneDrive\desktop\넥슨 프로젝트\chatbot_project\chat_formatted_game_qa_data.jsonl", "rb") as file:
    file_response = client.files.create(
        file=file,
        purpose="fine-tune"
    )

# 파인튜닝 설정 파라미터
fine_tune_params = {
    "training_file": file_response.id,
    "model": "gpt-3.5-turbo",
    "n_epochs": 3,  # 학습할 에포크 수
    "batch_size": 2,  # 배치 크기
    "learning_rate_multiplier": 0.1,  # 학습률 조절 (기본값: 0.1)
    "prompt_loss_weight": 0.01,  # 프롬프트 손실 가중치 (생성 결과와 비교 시 손실의 비중)
    "compute_classification_metrics": False,  # 분류 성능 지표 계산 여부
    "classification_n_classes": None,  # 클래스 개수 (분류 문제에만 사용)
}

# 파인튜닝 작업 생성
fine_tune_response = client.fine_tuning.jobs.create(**fine_tune_params)

print(f"Fine-tune job started: {fine_tune_response.id}")
