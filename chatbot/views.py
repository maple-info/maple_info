from django.conf import settings
from django.shortcuts import render
from .forms import ChatForm
from .models import ChatMessage
from openai import OpenAI
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI as LangChainOpenAI
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
import pinecone

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def chatbot_view(request):
    response_text = ""
    if request.method == 'POST':
        user_message = request.POST.get('message')
        if user_message:
            try:
                # RAG를 사용하여 관련 정보 검색
                retrieved_info = qa_chain.run(user_message)

                # OpenAI API 호출
                response = client.chat.completions.create(
                    model=fine_tuned_model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant knowledgeable about MapleStory. Use the following information to answer the question: " + retrieved_info},
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