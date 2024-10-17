import openai
from django.shortcuts import render
from .forms import ChatForm
from .models import ChatMessage

def chatbot_view(request):
    response_text = ""
    if request.method == 'POST':
        form = ChatForm(request.POST)
        if form.is_valid():
            user_message = form.cleaned_data['message']
            
            # OpenAI API 호출
            response = openai.Completion.create(
                engine="text-davinci-003",  # GPT 모델 설정
                prompt=user_message,
                max_tokens=150
            )
            bot_response = response.choices[0].text.strip()

            # 데이터베이스에 저장
            chat_message = ChatMessage(user_message=user_message, bot_response=bot_response)
            chat_message.save()

            # 응답 텍스트 설정
            response_text = bot_response
    else:
        form = ChatForm()

    return render(request, 'chatbot.html', {'form': form, 'response_text': response_text})