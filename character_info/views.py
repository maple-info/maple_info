from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
import requests
import os
import asyncio
import aiohttp
from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)

BASE_URL = "https://open.api.nexon.com/maplestory/v1"
API_KEY = settings.NEXON_API_KEY

# 공통적인 API 호출 로직
async def get_api_data(session, endpoint, params=None):
    headers = {"x-nxopen-api-key": API_KEY}
    url = f"{BASE_URL}{endpoint}"
    try:
        async with session.get(url, headers=headers, params=params) as response:
            response.raise_for_status()
            logger.info(f"API 요청 성공: {url}, 응답: {await response.json()}")
            return await response.json()
    except aiohttp.ClientError as e:
        logger.error(f"API 요청 중 오류 발생: {e}, URL: {url}, Params: {params}")
        return None

# 캐릭터 ID 조회 함수
async def get_character_id(session, character_name):
    return await get_api_data(session, "/id", {"character_name": character_name})

# 각 정보별 API 호출을 개별 함수로 분리
async def get_basic_info(session, ocid):
    return await get_api_data(session, "/character/basic", {"ocid": ocid})

async def get_stat_info(session, ocid):
    return await get_api_data(session, "/character/stat", {"ocid": ocid})

async def get_item_equipment_info(session, ocid):
    return await get_api_data(session, "/character/item-equipment", {"ocid": ocid})

async def get_ability_info(session, ocid):
    return await get_api_data(session, "/character/ability", {"ocid": ocid})

async def get_set_effect_info(session, ocid):
    return await get_api_data(session, "/character/set-effect", {"ocid": ocid})

async def get_link_skill_info(session, ocid):
    return await get_api_data(session, "/character/link-skill", {"ocid": ocid})

async def get_hyper_stat_info(session, ocid):
    return await get_api_data(session, "/character/hyper-stat", {"ocid": ocid})

async def get_symbol_equipment_info(session, ocid):
    return await get_api_data(session, "/character/symbol-equipment", {"ocid": ocid})

async def get_hexamatrix_stat_info(session, ocid):
    return await get_api_data(session, "/character/hexamatrix-stat", {"ocid": ocid})

async def get_popularity_info(session, ocid):
    return await get_api_data(session, "/character/popularity", {"ocid": ocid})


# 캐릭터 정보를 가져오는 메인 함수
async def get_character_info(character_name):
    async with aiohttp.ClientSession() as session:
        # 캐릭터 ID 조회
        character_id_data = await get_character_id(session, character_name)
        if not character_id_data or 'ocid' not in character_id_data:
            logger.warning(f"캐릭터 ID 조회 실패: {character_name}")
            return None

        ocid = character_id_data['ocid']
        logger.info(f"캐릭터 ID 조회 성공: {ocid}")

        # 각 정보를 개별적으로 비동기 처리
        basic_info = await get_basic_info(session, ocid)
        stat_info = await get_api_data(session, "/character/stat", {"ocid": ocid})
        item_equipment_info = await get_item_equipment_info(session, ocid)
        ability_info = await get_ability_info(session, ocid)
        set_effect_info = await get_set_effect_info(session, ocid)
        link_skill_info = await get_link_skill_info(session, ocid)
        hyper_stat_info = await get_hyper_stat_info(session, ocid)
        symbol_equipment_info = await get_symbol_equipment_info(session, ocid)
        hexamatrix_stat_info = await get_hexamatrix_stat_info(session, ocid)
        popularity_info = await get_popularity_info(session, ocid)

        # 각 정보별로 딕셔너리 구성
        character_data = {
            "basic_info": basic_info,
            "stat_info": stat_info,
            "item_equipment_info": item_equipment_info,
            "ability_info": ability_info,
            "set_effect_info": set_effect_info,
            "link_skill_info": link_skill_info,
            "hyper_stat_info": hyper_stat_info,
            "symbol_equipment_info": symbol_equipment_info,
            "hexamatrix_stat_info": hexamatrix_stat_info,
            "popularity_info": popularity_info
        }

        logger.info(f"Character data for {character_name}: {json.dumps(character_data, indent=2)}")
        return character_data


# 캐릭터 검색 뷰
def character_search_view(request):
    query = request.GET.get('q')
    if query:
        character_info = asyncio.run(get_character_info(query))
        return render(request, 'character_search.html', {
            'character_info': character_info,
            'query': query
        })
    return render(request, 'character_search.html')


# 캐릭터 정보 뷰
def character_info_view(request, character_name):
    character_info = asyncio.run(get_character_info(character_name))
    logger.info(f"Character info: {json.dumps(character_info, indent=2)}")

    if character_info:
        logger.info(f"Keys in character_info: {character_info.keys()}")
        if 'stat_info' in character_info:
            stat_info = character_info['stat_info']
            logger.info(f"Stat info: {json.dumps(stat_info, indent=2)}")
            if 'final_stat' in stat_info:
                final_stats = {stat['stat_name']: stat['stat_value'] for stat in stat_info['final_stat']}
                logger.info(f"Final stats: {json.dumps(final_stats, indent=2)}")
            else:
                logger.warning("No 'final_stat' in stat_info")
        else:
            logger.warning("No 'stat_info' in character_info")

        context = {
            'character_info': character_info,
            'final_stats': final_stats if 'final_stats' in locals() else {},
        }
        return render(request, 'character_info.html', context)
    else:
        logger.warning(f"No character info found for: {character_name}")
        return render(request, 'error.html', {"message": "캐릭터 정보를 찾을 수 없습니다."})
    
