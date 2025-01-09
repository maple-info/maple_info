import asyncio
import aiohttp
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.cache import cache
from asgiref.sync import async_to_sync
import logging
from datetime import timedelta
from django.utils.safestring import mark_safe 
import json
import faiss
import numpy as np
import os
import hashlib
from django.urls import reverse
from .extract_def import *


logger = logging.getLogger(__name__)
BASE_URL = "https://open.api.nexon.com/maplestory/v1"
API_KEY = settings.NEXON_API_KEY
CACHE_DURATION = timedelta(hours=1)  # 캐시 유효 기간

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
            if response.status == 200:
                return await response.json()
            else:
                logger.error(f"API 요청 실패: {url}, 상태 코드: {response.status}")
                return None
    except Exception as e:
        logger.error(f"API 요청 중 오류 발생: {url}, 오류: {str(e)}")
    async with session.get(url, headers=headers, params=params) as response:
        if response.status == 200:
            return await response.json()
        return None

async def get_character_info(character_name, date=None):
    async with aiohttp.ClientSession() as session:
        id_data = await get_api_data(session, "/id", {"character_name": character_name})
        if not id_data or 'ocid' not in id_data:
            return None

        ocid = id_data['ocid']
        params = {"ocid": ocid}
        if date:
            params["date"] = date
        
        # 추가된 API 경로에 대한 데이터 요청
        cashitem_info = await get_api_data(session, "/character/cashitem-equipment", params)
        beauty_info = await get_api_data(session, "/character/beauty-equipment", params)
        android_info = await get_api_data(session, "/character/android-equipment", params)
        pet_info = await get_api_data(session, "/character/pet-equipment", params)
        basic_info = await get_api_data(session, "/character/basic", params)
        stat_info = await get_api_data(session, "/character/stat", params)
        item_equipment_info = await get_api_data(session, "/character/item-equipment", params)
        ability_info = await get_api_data(session, "/character/ability", params)
        set_effect_info = await get_api_data(session, "/character/set-effect", params)
        link_skill_info = await get_api_data(session, "/character/link-skill", params)
        hexamatrix_info = await get_api_data(session, "/character/hexamatrix", params)
        hexamatrix_stat_info = await get_api_data(session, "/character/hexamatrix-stat", params)
        symbol_equipment_info = await get_api_data(session, "/character/symbol-equipment", params)
        vmatrix_info = await get_api_data(session, "/character/vmatrix", params)
        hyper_stat_info = await get_api_data(session, "/character/hyper-stat", params)
        
        # 전직 차수별 스킬 정보 요청
        skill_info = {}
        for job_advancement in ["0", "1", "1.5", "2", "2.5", "3", "4", "hyperpassive", "hyperactive"]:
            skill_info[job_advancement] = await get_api_data(session, "/character/skill", {"ocid": ocid, "job_advancement": job_advancement})

        return {
            "basic_info": basic_info,
            "stat_info": stat_info,
            "item_equipment_info": item_equipment_info,
            "ability_info": ability_info,
            "set_effect_info": set_effect_info,
            "link_skill_info": link_skill_info,
            "hexamatrix_info": hexamatrix_info,
            "hexamatrix_stat_info": hexamatrix_stat_info,
            "symbol_equipment_info": symbol_equipment_info,
            "vmatrix_info": vmatrix_info,
            "skill_info": skill_info,  # 전직 차수별 스킬 정보
            "cashitem_info": cashitem_info,
            "beauty_info": beauty_info,
            "android_info": android_info,
            "pet_info": pet_info,
            "hyper_stat_info": hyper_stat_info,
        }





    


from asgiref.sync import sync_to_async


import hashlib

def character_info_view(request):
    character_name = request.GET.get('character_name')



async def character_info_view(request, character_name=None):
    if not character_name:
        character_name = request.GET.get('character_name')  # 쿼리 파라미터에서 캐릭터 이름 가져오기
        if not character_name:
            # 세션에서 캐릭터 이름 가져오기
            character_info = request.session.get('character_info')
            if character_info:
                character_name = character_info.get('character_name')
            if not character_name:
                return render(request, 'error.html', {'error': '캐릭터 이름을 입력해주세요.'})

    character_info = await get_character_info(character_name)

    if character_info:
        # 각 데이터를 추출하는 함수들
        final_stats = await sync_to_async(extract_final_stats)(character_info.get('stat_info', {}))
        equipment_data = await sync_to_async(extract_item_equipment)(character_info.get('item_equipment_info', []))
        ability_data = await sync_to_async(extract_ability_presets)(character_info.get('ability_info', {}))
        set_effect_data = await sync_to_async(extract_set_effect)(character_info.get('set_effect_info', []))
        link_skill_data = await sync_to_async(extract_link_skills)(character_info.get('link_skill_info', []))
        hexa_stats = await sync_to_async(extract_hexa_stats)(character_info.get('hexamatrix_stat_info', []))
        hexa_data = await sync_to_async(extract_hexa)(character_info.get('hexamatrix_info', []))
        symbol_data = await sync_to_async(extract_symbols)(character_info.get('symbol_equipment_info', []))
        vmatrix_data = await sync_to_async(extract_vmatrix)(character_info.get('vmatrix_info', {}))
        character_skill_data = await sync_to_async(extract_character_skills)(character_info.get('skill_info', {}))
        cash_item_data = await sync_to_async(extract_cash_item_equipment)(character_info.get('cashitem_info', {}))
        android_data = await sync_to_async(extract_android_info)(character_info.get('android_info', {}))
        pet_data = await sync_to_async(extract_pet_info)(character_info.get('pet_info', {}))
        beauty_data = await sync_to_async(extract_beauty_info)(character_info.get('beauty_info', {}))
        hyper_stat_data = await sync_to_async(extract_hyper_stats)(character_info.get('hyper_stat_info', {}))

        # 캐시 저장
        cache.set(f'character_info_{character_name}', character_info, timeout=600)

        # 세션에 캐릭터 정보 저장
        request.session['character_info'] = {
            'character_name': character_name,
            'character_info': character_info,
        }

        # 템플릿으로 전달할 컨텍스트
        context = {
            'character_name': character_name,
            'final_stats': final_stats,
            'equipment_data': equipment_data,
            'ability_data': ability_data,
            'set_effect_data': set_effect_data,
            'link_skill_data': link_skill_data,
            'hexa_stats': hexa_stats,
            'hexa_data': hexa_data,
            'symbol_data': symbol_data,
            'preset_range': range(1, 4),
            'vmatrix_data': vmatrix_data,
            'character_skill_data': character_skill_data,
            'cash_item_data': cash_item_data,  # 추가된 캐시 아이템 데이터
            'android_data': android_data,        # 추가된 안드로이드 데이터
            'pet_data': pet_data,                # 추가된 펫 데이터
            'beauty_data': beauty_data,          # 추가된 뷰티 데이터
            'hyper_stat_data': hyper_stat_data,
            'character_skill_data': character_skill_data,
        }

        return render(request, 'info.html', context)
    else:
        return render(request, 'error.html', {'error': '캐릭터 정보를 찾을 수 없습니다.'})


