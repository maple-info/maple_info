from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings
import aiohttp
import asyncio
from django.template.defaultfilters import register

BASE_URL = "https://open.api.nexon.com/maplestory/v1"
API_KEY = settings.NEXON_API_KEY  # settings.py에서 API 키를 가져옵니다.

def home(request):
    if request.method == 'POST':
        character_name = request.POST.get('character_name')
        if character_name:
            return redirect(reverse('character_search') + f'?character_name={character_name}')
    return render(request, 'home.html')

async def get_api_data(session, endpoint, params=None):
    headers = {"x-nxopen-api-key": API_KEY}
    url = f"{BASE_URL}{endpoint}"
    try:
        async with session.get(url, headers=headers, params=params) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientError as e:
        print(f"API 요청 중 오류 발생: {e}")
        return None

async def get_character_info(character_name):
    async with aiohttp.ClientSession() as session:
        character_id_data = await get_api_data(session, "/id", {"character_name": character_name})
        if not character_id_data or 'ocid' not in character_id_data:
            return None

        ocid = character_id_data['ocid']

        # basic 정보만 가져오기
        basic_info = await get_api_data(session, "/character/basic", {"ocid": ocid})
        popularity_info = await get_api_data(session, "/character/popularity", {"ocid": ocid})
        


        return {
            "basic_info": basic_info,
            "popularity_info": popularity_info
        }

def character_search_view(request):
    query = request.GET.get('q')
    if query:
        character_info = asyncio.run(get_character_info(query))
        return render(request, 'character_search.html', {
            'character_info': character_info,
            'query': query
        })
    return render(request, 'character_search.html')

def character_info_view(request, character_name):
    character_info = asyncio.run(get_character_info(character_name))
    if character_info:
        return render(request, 'character_info.html', {'character_info': character_info})
    else:
        return render(request, 'error.html', {"message": "캐릭터를 찾을 수 없습니다."})