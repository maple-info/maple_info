from django.conf import settings
from django.shortcuts import render
from .forms import ChatForm
from .models import ChatMessage
from openai import OpenAI

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# 파인튜닝된 모델 이름 가져오기
job_id = "ftjob-wQuRs8aIa3dSGFAzsEf5mpTe"
job = client.fine_tuning.jobs.retrieve(job_id)
fine_tuned_model = job.fine_tuned_model

def chatbot_view(request):
    response_text = ""
    if request.method == 'POST':
        user_message = request.POST.get('message')
        if user_message:
            try:
                # 새로운 API 호출 방식 사용
                response = client.chat.completions.create(
                    model=fine_tuned_model,  # 파인튜닝된 모델 이름 사용
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant knowledgeable about MapleStory."},
                        {"role": "user", "content": user_message}
                    ],
                    max_tokens=150
                )
                response_text = response.choices[0].message.content.strip()
            except Exception as e:
                response_text = f"챗봇 응답을 가져오는 중 오류가 발생했습니다: {str(e)}"
    
    return render(request, 'chatbot.html', {'response_text': response_text})

def character_info_view(request):
    # 캐릭터 정보 처리 로직
    return render(request, 'character_info.html', {})