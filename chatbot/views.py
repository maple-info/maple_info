from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from openai import OpenAI
import faiss
import json
import numpy as np
import os

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# FAISS 인덱스와 메타데이터 로드
def load_faiss_index(index_path, metadata_path):
    index = faiss.read_index(index_path)
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    return index, metadata

# 모든 FAISS 인덱스 로드
def load_all_faiss_indices(folder_path):
    indices = []
    for file in os.listdir(folder_path):
        if file.endswith('.faiss'):
            index_path = os.path.join(folder_path, file)
            metadata_path = os.path.join(folder_path, file.replace('.faiss', '_metadata.json'))
            if os.path.exists(metadata_path):
                index, metadata = load_faiss_index(index_path, metadata_path)
                indices.append((index, metadata))
    return indices

# FAISS 인덱스 로드
faiss_folder = r"C:\Users\ccg70\OneDrive\desktop\넥슨 프로젝트\maple_db\faiss_index"
indices = load_all_faiss_indices(faiss_folder)

# 임베딩 생성 함수
def get_embedding(text):
    response = client.embeddings.create(input=[text], model="text-embedding-ada-002")
    return response.data[0].embedding

# 모든 인덱스에서 검색 수행
def search_all_indices(query, indices, k=5):
    query_embedding = get_embedding(query)
    results = []
    for index, metadata in indices:
        D, I = index.search(np.array([query_embedding]).astype('float32'), k)
        results.extend([(metadata[i], D[0][j]) for j, i in enumerate(I[0])])
    return sorted(results, key=lambda x: x[1])[:k]


def chatbot_view(request):
    if request.method == 'POST':
        user_message = request.POST.get('message')
        if user_message:
            try:
                # RAG를 사용하여 관련 정보 검색
                search_results = search_all_indices(user_message, indices)
                context = "\n".join([f"{result[0]}" for result in search_results])

                # OpenAI API 호출 (파인튜닝 모델 사용)
                response = client.chat.completions.create(
                    model="ft:gpt-3.5-turbo-0125:personal::APok7gr7",  # 파인튜닝된 모델 ID
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that answers questions about MapleStory game mechanics and statistics."},
                        {"role": "system", "content": "모든 응답은 한국어로 작성해 주세요."},
                        {"role": "user", "content": f"Context: {context}\n\nQuestion: {user_message}"}
                    ],
                    max_tokens=300
                )
                response_text = response.choices[0].message.content.strip()

                # JsonResponse에서 ensure_ascii=False로 설정
                return JsonResponse({'response': response_text}, json_dumps_params={'ensure_ascii': False})
            except Exception as e:
                print(f"Error: {str(e)}")  # 로그에 오류 메시지 출력
                return JsonResponse({'error': f"챗봇 응답을 가져오는 중 오류가 발생했습니다: {str(e)}"}, status=500)

    return render(request, 'chatbot.html')

def character_info_view(request):
    # 캐릭터 정보 처리 로직
    return render(request, 'character_info.html', {})
