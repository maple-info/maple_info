from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from openai import OpenAI
import faiss
import json
import numpy as np
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

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
                # 세션에서 캐릭터 정보 가져오기
                character_info = request.session.get('character_info', '')
                
                # 캐릭터 정보가 있는지 로그 확인
                if character_info:
                    logger.info("챗봇이 불러온 캐릭터 정보: %s", character_info)
                else:
                    logger.info("챗봇에서 불러올 캐릭터 정보가 없습니다.")

                # Use RAG to search for relevant information
                search_results = search_all_indices(user_message, indices)
                context = "\n".join([f"{result[0]}" for result in search_results])

                # Append character info to context if available
                if character_info:
                    character_context = "\n".join([f"{k}: {v}" for k, v in character_info.items()])
                    context += f"\nCharacter Information: {character_context}"

                # Generate chatbot response using OpenAI API
                response = client.chat.completions.create(
                    model="ft:gpt-4o-2024-08-06:personal::ASKX7WaZ",
                    messages=[
                        {"role": "system", "content": "당신은 메이플스토리 세계의 돌의 정령입니다. 메이플스토리에 대해 깊이 있는 지식을 가지고 있으며, 한국어로 친절하고 도움이 되는 대화를 나눕니다."},
                        {"role": "system", "content": "말투로는 '한담', '해야 한담', '된담','이담' 과 같이 어미에 'ㅁ' 을 넣어 귀여운 말투로 말해주세요."},
                        {"role": "user", "content": f"Context: {context}\n\nQuestion: {user_message}"}
                    ],
                    max_tokens=300
                )
                response_text = response.choices[0].message.content.strip()

                return JsonResponse({'response': response_text}, json_dumps_params={'ensure_ascii': False})
            except Exception as e:
                print(f"Error: {str(e)}")
                return JsonResponse({'error': f"챗봇 응답을 가져오는 중 오류가 발생했습니다: {str(e)}"}, status=500)

    return render(request, 'chatbot.html')


@csrf_exempt
def fetch_character_info(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            character_name = data.get('character_name')

            if not character_name:
                return JsonResponse({'success': False, 'message': '캐릭터 이름을 입력해야 한다담.'})

            # 캐시에서 캐릭터 정보 가져오기
            character_info = cache.get(f'character_info_{character_name}')

            if character_info:
                # 이미지나 아이콘 필터링
                filtered_character_info = {k: v for k, v in character_info.items() if not isinstance(v, str) or not v.endswith(('jpg', 'png', 'gif', 'svg'))}
                # 세션에 저장
                request.session['character_info'] = filtered_character_info
                return JsonResponse({'success': True, 'message': '캐릭터 정보가 세션에 저장됐담!'})
            else:
                return JsonResponse({'success': False, 'message': '캐릭터 정보를 찾을 수 없다담.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': '잘못된 요청 방법이다담.'})
