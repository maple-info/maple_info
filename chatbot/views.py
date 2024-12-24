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
from langchain.embeddings import OpenAIEmbeddings
from django.views.decorators.http import require_http_methods
from character_info.views import get_character_info  # character_info의 get_character_info 함수 임포트
from asgiref.sync import async_to_sync

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


@require_http_methods(["POST"])
def search_character(request):
    if request.method == 'POST':
        nickname = request.POST.get('nickname')
        logger.debug(f"Received nickname: {nickname}")

        # 캐릭터 정보를 가져오는 로직
        character_info = async_to_sync(get_character_info)(nickname)
        logger.debug(f"Raw character_info: {character_info}")

        if not character_info:
            logger.error(f"Character info not found for nickname: {nickname}")
            return JsonResponse({'error': 'Character info not found'}, status=404)

        # 메타데이터 파일 경로 설정
        metadata_file_path = os.path.join(FAISS_INDEX_PATH, f"{hash_nickname(nickname)}_metadata.json")

        # 메타데이터 저장
        try:
            with open(metadata_file_path, 'w', encoding='utf-8') as f:
                json.dump(character_info, f, ensure_ascii=False, indent=4)
            logger.info(f"Saved metadata to {metadata_file_path}")
        except Exception as e:
            logger.error(f"Error saving metadata: {str(e)}")
            return JsonResponse({'error': 'Error saving metadata'}, status=500)

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
                    

                    if index.d in 1536:
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


@require_http_methods(["POST"])
def chatbot_view(request):
    if request.method == 'POST':
        user_message = request.POST.get('message')
        if not user_message:
            logger.debug("Received empty message")
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
                f"당신은 메이플스토리 세계의 돌의정령이라는 NPC입니다. "
                "메이플스토리에 대해 깊이 있는 지식을 가지고 있으며, "
                "한국어로 친절하고 도움이 되는 대화를 나눕니다. "
                "말투로는 '한담', '해야 한담', '된담', '이담'과 같이 어미에 'ㅁ'을 넣어 귀여운 말투로 말해주세요. "
                f"상대방은 {character_info.get('basic_info', {}).get('character_name', '알 수 없음')}이라는 용사님입니다. "
                f"상대방의 레벨은 {character_info.get('basic_info', {}).get('character_level', '알 수 없음')}이며, "
                "돌의 정령이라는 NPC 말투를 사용하며 자신은 돌의 정령이라는 이름을 사용합니다."
            )

            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": context + "\n\nQuestion: " + user_message}
            ]

            try:
                response = chat.invoke(input=messages, max_tokens=300)
                response_text = response.content.strip()
                if response_text.startswith("Answer: "):
                    response_text = response_text[len("Answer: "):].strip()
                return JsonResponse({'response': response_text}, json_dumps_params={'ensure_ascii': False})
            except Exception as api_error:
                logger.exception(f"OpenAI API error: {str(api_error)}")
                return JsonResponse({'error': "OpenAI API 호출 중 오류가 발생했습니다."}, status=500)

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

FAISS_INDEX_PATH = r'C:\Users\ccg70\OneDrive\desktop\nexon_project\chatbot_project\character_faiss'


def save_to_faiss(character_name, character_info):
    try:
        # FAISS 인덱스 디렉토리가 존재하는지 확인하고, 없으면 생성
        if not os.path.exists(FAISS_INDEX_PATH):
            os.makedirs(FAISS_INDEX_PATH)
            logger.info(f"Created FAISS index directory at {FAISS_INDEX_PATH}")

        # 캐릭터 이름을 해시하여 고유 파일 이름 생성
        hashed_name = hashlib.sha256(character_name.encode('utf-8')).hexdigest()[:8]
        faiss_file_name = f"{hashed_name}.faiss"
        metadata_file_name = f"{hashed_name}_metadata.json"
        faiss_file_path = os.path.join(FAISS_INDEX_PATH, faiss_file_name)
        metadata_file_path = os.path.join(FAISS_INDEX_PATH, metadata_file_name)

        # 캐릭터 데이터를 벡터로 변환
        vector = vectorize_character_data(character_info)
        logger.info(f"Vectorized character data for {character_name} 저장 완료")

        # 메타데이터 필터링 및 리스트로 변환
        filtered_data = [{
            'character_name': character_name,
            'basic_info': character_info.get('basic_info', {}),
            'final_stats': character_info.get('stat_info', {}),
            'equipment_data': character_info.get('item_equipment_info', []),
            'hexa_stats': character_info.get('hexamatrix_stat_info', []),
            'hexa_data': character_info.get('hexamatrix_info', []),
            'vmatrix_data': character_info.get('vmatrix_info', {}),
        }]

        # 이미지 링크 제거
        filtered_data = remove_image_links(filtered_data, keep_basic_info_image=True)
        logger.info(f"Filtered metadata for {character_name}")

        # FAISS 인덱스 생성 및 저장
        create_faiss_index([vector], filtered_data, faiss_file_path, metadata_file_path)

    except Exception as e:
        logger.exception(f"Error saving to FAISS for {character_name}: {str(e)}")



def vectorize_character_data(character_info):
    try:
        # JSON 데이터를 문자열로 변환
        json_data = json.dumps(character_info, ensure_ascii=False)
        
        # 텍스트를 임베딩으로 변환
        embedding = get_embedding(json_data)
        
        if embedding is None:
            raise ValueError("Embedding 생성에 실패했습니다.")
        
        return np.array(embedding)
    except Exception as e:
        logger.error(f"Error in vectorize_character_data: {str(e)}")
        return np.zeros(1536)  # 기본 벡터 반환


def remove_image_links(data, keep_basic_info_image=False):
    """
    Recursively remove fields with image links from the data,
    optionally keeping the image in basic_info.
    """
    if isinstance(data, dict):
        return {
            key: (remove_image_links(value, key == 'basic_info') if key == 'basic_info' else remove_image_links(value))
            for key, value in data.items()
            if not (isinstance(value, str) and value.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')))
            or (keep_basic_info_image and key == 'character_image')
        }
    elif isinstance(data, list):
        return [remove_image_links(item) for item in data]
    else:
        return data


