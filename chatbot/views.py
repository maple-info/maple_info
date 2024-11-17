import logging
import json
import os
import numpy as np
import faiss
import tiktoken
import hashlib
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from openai import OpenAI
from django.views.decorators.http import require_http_methods

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.OPENAI_API_KEY)

FAISS_INDEX_PATH = r'C:\Users\ccg70\OneDrive\desktop\nexon_project\chatbot_project\character_faiss'

def hash_nickname(nickname):
    return hashlib.sha256(nickname.encode('utf-8')).hexdigest()[:8]

def truncate_text(text, max_tokens=8000):
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    return encoding.decode(tokens[:max_tokens]) if len(tokens) > max_tokens else text

def get_embedding(text):
    try:
        truncated_text = truncate_text(text)
        response = client.embeddings.create(input=[truncated_text], model="text-embedding-ada-002")
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Error in get_embedding: {str(e)}")
        return None

def search_all_indices(query, indices, k=5):
    query_embedding = get_embedding(query)
    if not query_embedding:
        return []
    
    results = []
    for index, metadata in indices:
        try:
            D, I = index.search(np.array([query_embedding]).astype('float32'), k)
            results.extend([(metadata[i], D[0][j]) for j, i in enumerate(I[0]) if i < len(metadata)])
        except Exception as e:
            logger.error(f"Error searching index: {str(e)}")
    
    return sorted(results, key=lambda x: x[1])[:k]

def find_character_info(nickname):
    json_file_path = os.path.join(FAISS_INDEX_PATH, f"{hash_nickname(nickname)}_metadata.json")
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.info(f"Character info not found for nickname: {nickname}")
        return None
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in file: {json_file_path}")
        return None

@require_http_methods(["POST"])
def search_character(request):
    nickname = request.POST.get('nickname')
    if not nickname:
        return JsonResponse({'error': '닉네임을 입력해주세요.'}, status=400)
    
    character_info = find_character_info(nickname)
    if character_info:
        request.session['character_info'] = character_info
        return JsonResponse({
            'success': True,
            'message': '캐릭터 정보를 찾았습니다.',
            'character_info': {
                'character_name': character_info.get('basic_info', {}).get('character_name', ''),
                'character_level': character_info.get('basic_info', {}).get('character_level', ''),
                'character_class': character_info.get('basic_info', {}).get('character_class', ''),
                'world_name': character_info.get('basic_info', {}).get('world_name', ''),
                'character_image': character_info.get('basic_info', {}).get('character_image', ''),
            }
        })
    else:
        return JsonResponse({
            'success': False,
            'message': '캐릭터 정보를 찾을 수 없습니다.'
        })


def load_faiss_indices(folders):
    indices = []
    for folder in folders:
        if not os.path.exists(folder):
            logger.error(f"Folder not found: {folder}")
            continue
        for file_name in os.listdir(folder):
            if file_name.endswith('.faiss'):
                try:
                    index_path = os.path.join(folder, file_name)
                    index = faiss.read_index(index_path)
                    metadata_path = index_path.replace('.faiss', '_metadata.json')
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    indices.append((index, metadata))
                except Exception as e:
                    logger.error(f"Error reading FAISS index {index_path}: {str(e)}")
    return indices

def chatbot_view(request):
    if request.method == 'POST':
        user_message = request.POST.get('message')
        if not user_message:
            return JsonResponse({'error': "메시지가 비어 있습니다."}, status=400)

        try:
            faiss_folders = [
                "C:/Users/ccg70/OneDrive/desktop/nexon_project/maple_db/faiss_index/",
                "C:/Users/ccg70/OneDrive/desktop/nexon_project/chatbot_project/character_faiss/"
            ]
            indices = load_faiss_indices(faiss_folders)
            if not indices:
                logger.error("No FAISS indices loaded")
                return JsonResponse({'error': "FAISS 인덱스를 로드할 수 없습니다."}, status=500)

            search_results = search_all_indices(user_message, indices, k=1)
            context = "\n".join([json.dumps(result[0], ensure_ascii=False) for result in search_results])

            character_info = request.session.get('character_info', {})
            if character_info:
                character_query = " ".join(str(v) for v in character_info.values())
                character_results = search_all_indices(character_query, indices, k=1)
                character_context = "\n".join([json.dumps(result[0], ensure_ascii=False) for result in character_results])
                context += f"\n{character_context}"

            context = truncate_text(context, max_tokens=3000)

            system_message = (
                "당신은 메이플스토리 세계의 돌의 정령입니다. "
                "메이플스토리에 대해 깊이 있는 지식을 가지고 있으며, "
                "한국어로 친절하고 도움이 되는 대화를 나눕니다. "
                "말투로는 '한담', '해야 한담', '된담', '이담'과 같이 어미에 'ㅁ'을 넣어 귀여운 말투로 말해주세요."
            )

            user_message_with_context = f"Context: {context}\n\nQuestion: {user_message}"
            user_message_with_context = truncate_text(user_message_with_context, max_tokens=4000)

            try:
                response = client.chat.completions.create(
                    model="ft:gpt-4o-2024-08-06:personal::ASKX7WaZ",
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_message_with_context}
                    ],
                    max_tokens=300
                )
                response_text = response.choices[0].message.content.strip()
                return JsonResponse({'response': response_text}, json_dumps_params={'ensure_ascii': False})
            except Exception as api_error:
                logger.error(f"OpenAI API error: {str(api_error)}")
                return JsonResponse({'error': "OpenAI API 호출 중 오류가 발생했습니다."}, status=500)

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return JsonResponse({'error': "예기치 못한 오류가 발생했습니다."}, status=500)

    character_info = request.session.get('character_info', {})
    character_image = character_info.get('basic_info', {}).get('character_image', '')
    return render(request, 'chatbot.html', {'character_image': character_image})