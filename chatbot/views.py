import openai
from django.conf import settings
from django.shortcuts import render
from .forms import ChatForm
from .models import ChatMessage

def chatbot_view(request):
    response_text = ""
    if request.method == 'POST':
        user_message = request.POST.get('message')
        if user_message:
            openai.api_key = settings.OPENAI_API_KEY
            try:
                response = openai.Completion.create(
                    engine="text-davinci-003",  # 사용할 GPT 모델
                    prompt=user_message,
                    max_tokens=150
                )
                response_text = response.choices[0].text.strip()
            except Exception as e:
                response_text = "챗봇 응답을 가져오는 중 오류가 발생했습니다."
    
    return render(request, 'chatbot.html', {'response_text': response_text})


def character_info_view(request):
    # 캐릭터 정보 처리 로직
    return render(request, 'character_info.html', {})
