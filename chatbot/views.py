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
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.embeddings import OpenAIEmbeddings
from django.views.decorators.http import require_http_methods

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 임베딩 클라이언트 초기화
embeddings = OpenAIEmbeddings(
    openai_api_key=settings.OPENAI_API_KEY,
    model="text-embedding-ada-002"
)

# ChatOpenAI 클라이언트 초기화 시 특정 모델 지정
chat = ChatOpenAI(
    openai_api_key=settings.OPENAI_API_KEY,
    model_name="ft:gpt-4o-2024-08-06:personal::ASKX7WaZ"  # 채팅 모델로 설정
)

def hash_nickname(nickname):
    return hashlib.sha256(nickname.encode('utf-8')).hexdigest()[:8]



# 맥스 토큰 넘어가지 않게 제한
def truncate_text(text, max_tokens=8192):
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    return encoding.decode(tokens[:max_tokens]) if len(tokens) > max_tokens else text

def get_embedding(text):
    try:
        truncated_text = truncate_text(text)
        embedding = embeddings.embed_query(truncated_text)
        return embedding
    except Exception as e:
        logger.error(f"Error in get_embedding: {str(e)}")
        return None



#챗봇에게 메세지를 받아와 임베딩 변환 
def search_all_indices(query, indices, k=5):
    query_embedding = get_embedding(query)
    if not query_embedding: #빈 값이면 공백
        return []
    
    results = [] #검색 결과를 공백으로 초기화
    for index, metadata in indices:
        try:
            # FAISS 인덱스의 차원 확인
            if len(query_embedding) != index.d:
                logger.error(f"Embedding dimension {len(query_embedding)} does not match FAISS index dimension {index.d}")
                continue

            D, I = index.search(np.array([query_embedding]).astype('float32'), k)
            results.extend([(metadata[i], D[0][j]) for j, i in enumerate(I[0]) if i < len(metadata)])
        except Exception as e:
            logger.exception("Error searching index: ")
    
    return sorted(results, key=lambda x: x[1])[:k]

def find_character_info(nickname):
    json_file_path = os.path.join("C:\\Users\\ccg70\\OneDrive\\desktop\\nexon_project\\chatbot_project\\character_faiss", f"{hash_nickname(nickname)}_metadata.json")
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
    if request.method == 'POST':
        nickname = request.POST.get('nickname')
        logger.debug(f"Received nickname: {nickname}")

        # character_info를 가져오는 로직
        character_info = find_character_info(nickname)
        logger.debug(f"Raw character_info: {character_info}")

        # character_info가 리스트인 경우 첫 번째 항목을 사용
        if isinstance(character_info, list):
            character_info = character_info[0] if character_info else {}
            logger.debug(f"Processed character_info: {character_info}")

        # 'basic_info'가 존재하는지 확인하고, 필요한 필드 추출
        basic_info = character_info.get('basic_info', {}) if isinstance(character_info, dict) else {}
        logger.debug(f"Basic info: {basic_info}")

        context = {
            'character_name': basic_info.get('character_name', ''),
            'character_level': basic_info.get('character_level', ''),
            'world_name': basic_info.get('world_name', ''),
            'character_class': basic_info.get('character_class', ''),
            'character_image': basic_info.get('character_image', ''),
        }

        logger.debug(f"Response context: {context}")
        return JsonResponse(context)
    logger.error("Invalid request method received.")
    return JsonResponse({'error': 'Invalid request'}, status=400)

def load_faiss_indices(base_folder):
    indices = []
    
    # 하위 폴더를 재귀적으로 탐색하는 함수
    def search_faiss_indices(folder):
        for entry in os.listdir(folder):
            path = os.path.join(folder, entry)
            if os.path.isdir(path):
                search_faiss_indices(path)  # 하위 폴더 탐색
            elif entry.endswith('.faiss'):
                try:
                    index = faiss.read_index(path)
                    
                    # 메타데이터 파일 경로 설정
                    metadata_path = os.path.join("C:/Users/ccg70/OneDrive/desktop/nexon_project/maple_db/data/rag/metadata", entry.replace('.faiss', '_metadata.json'))
                    
                    # 메타데이터 파일 읽기
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    
                    logger.info(f"Loaded FAISS index from {path} with dimension {index.d}")
                    
                    # 768 및 1536 차원 인덱스 허용
                    if index.d in [768, 1536]:
                        indices.append((index, metadata))
                    else:
                        logger.error(f"Unsupported FAISS index dimension {index.d} for {path}")
                except FileNotFoundError:
                    logger.error(f"Metadata file not found: {metadata_path}")
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON in file: {metadata_path}")
                except Exception as e:
                    logger.exception(f"Error reading FAISS index {path}: {str(e)}")

    search_faiss_indices(base_folder)  # 기본 폴더에서 탐색 시작
    return indices


def create_faiss_index(embeddings, metadata, index_path, metadata_path):
    dimension = len(embeddings[0])
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings).astype('float32'))
    faiss.write_index(index, index_path)
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=4)
    logger.info(f"Created FAISS index at {index_path} with dimension {dimension}")


def chatbot_view(request):
    if request.method == 'POST':
        user_message = request.POST.get('message')
        if not user_message:
            return JsonResponse({'error': "메시지가 비어 있습니다."}, status=400)

        try:
            faiss_folders = "C:/Users/ccg70/OneDrive/desktop/nexon_project/maple_db/data/rag/indexes/"
            indices = load_faiss_indices(faiss_folders)
            if not indices:
                logger.error("No FAISS indices loaded")
                return JsonResponse({'error': "FAISS 인덱스를 로드할 수 없습니다."}, status=500)

            # AI 에이전트를 사용하여 질문의 도메인 파악
            domain = determine_domain(user_message)  # 도메인 결정 함수 추가
            relevant_indices = filter_indices_by_domain(indices, domain)  # 도메인에 따라 인덱스 필터링

            search_results = search_all_indices(user_message, relevant_indices, k=1)
            context = "\n".join([json.dumps(result[0], ensure_ascii=False) for result in search_results])

            # 캐릭터 정보를 시스템 메시지에 포함
            system_message = create_system_message(request.session.get('character_info', {}))

            # ChatOpenAI를 사용한 메시지 구성
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": context + "\n\nQuestion: " + user_message}
            ]

            # OpenAI API 호출
            response = chat.invoke(input=messages, max_tokens=300)
            response_text = response.content.strip()

            # "Answer: " 접두사 제거
            if response_text.startswith("Answer: "):
                response_text = response_text[len("Answer: "):].strip()

            return JsonResponse({'response': response_text}, json_dumps_params={'ensure_ascii': False})

        except Exception as e:
            logger.exception(f"Unexpected error: {str(e)}")
            return JsonResponse({'error': "예기치 못한 오류가 발생했습니다."}, status=500)

    character_info = request.session.get('character_info', {})
    character_image = character_info.get('basic_info', {}).get('character_image', '')
    return render(request, 'chatbot.html', {'character_image': character_image})


def determine_domain(user_message):
    keywords = [
        (["아이템", "장비",'템셋','엠블렘','보조','무기','해방','몇추','에디','잠재','22성','17성','18성'], "item"),
        (["보스", "검마",'진힐라','카벨','하드','카오스','듄켈'], "boss"),
        (["직업", "스킬", "하버",'추천','시그너스','모험가','도적','전사','법사','궁수','해적','영웅','레지','버닝'], "job"),
    ]
    for words, domain in keywords:
        if any(word in user_message for word in words):
            return domain
    return "general"


def filter_indices_by_domain(indices, domain):
    # 도메인에 따라 인덱스를 필터링하는 로직
    filtered_indices = []
    for index, metadata in indices:
        if domain in metadata.get('domain', []):  # 메타데이터에 도메인 정보가 포함되어 있어야 함
            filtered_indices.append((index, metadata))
    return filtered_indices

def create_system_message(character_info):
    # 시스템 메시지를 생성하는 로직
    return (
        f"당신은 메이플스토리 세계의 돌의정령이라는 NPC입니다. "
        "메이플스토리에 대해 깊이 있는 지식을 가지고 있으며, "
        "한국어로 친절하고 도움이 되는 대화를 나눕니다. "
        f"상대방은 {character_info.get('basic_info', {}).get('character_name', '알 수 없음')}이라는 용사님입니다. "
        f"상대방의 레벨은 {character_info.get('basic_info', {}).get('character_level', '알 수 없음')}입니다."
    )