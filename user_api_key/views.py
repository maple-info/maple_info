import json
import logging
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
import aiohttp
from django.conf import settings
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)
BASE_URL = "https://open.api.nexon.com/maplestory/v1"

async def get_api_data(session, endpoint, params=None, api_key=None):
    headers = {"x-nxopen-api-key": api_key}
    url = f"{BASE_URL}{endpoint}"
    try:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                logger.error(f"API 요청 실패: {url}, 상태 코드: {response.status}")
                return None
    except Exception as e:
        logger.error(f"API 요청 중 오류 발생: {url}, 오류: {str(e)}")
        return None

async def get_character_list(api_key):
    async with aiohttp.ClientSession() as session:
        return await get_api_data(session, "/character/list", api_key=api_key)

@require_http_methods(["GET", "POST"])
def input_user_api_key(request):
    if request.method == 'POST':
        api_key = request.POST.get('api_key')
        
        try:
            character_list = async_to_sync(get_character_list)(api_key)
            if character_list:
                return JsonResponse({'status': 'success', 'characters': character_list})
            else:
                return JsonResponse({'status': 'error', 'message': 'API 요청 실패'})
        except Exception as e:
            logger.error(f"캐릭터 리스트 조회 중 오류 발생: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return render(request, 'input_user_api_key.html')
