import asyncio
import aiohttp
from django.shortcuts import render
from django.conf import settings

BASE_URL = "https://open.api.nexon.com/maplestory/v1"
API_KEY = settings.NEXON_API_KEY

async def get_api_data(session, endpoint, params=None):
    headers = {"x-nxopen-api-key": API_KEY}
    url = f"{BASE_URL}{endpoint}"
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

        basic_info = await get_api_data(session, "/character/basic", {"ocid": ocid})
        stat_info = await get_api_data(session, "/character/stat", {"ocid": ocid})
        item_equipment_info = await get_api_data(session, "/character/item-equipment", {"ocid": ocid})
        ability_info = await get_api_data(session, "/character/ability", {"ocid": ocid})
        set_effect_info = await get_api_data(session, "/character/set-effect", {"ocid": ocid})
        link_skill_info = await get_api_data(session, "/character/link-skill", {"ocid": ocid})
        hyper_stat_info = await get_api_data(session, "/character/hyper-stat", {"ocid": ocid})
        symbol_equipment_info = await get_api_data(session, "/character/symbol-equipment", {"ocid": ocid})
        hexamatrix_stat_info = await get_api_data(session, "/character/hexamatrix-stat", {"ocid": ocid})
        popularity_info = await get_api_data(session, "/character/popularity", {"ocid": ocid})

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

        return character_data


def extract_final_stats(stat_info):
    # final_stat에서 원하는 정보 추출
    final_stats = {}
    for stat in stat_info.get('final_stat', []):
        # stat_name에서 띄어쓰기를 언더바로 변환
        stat_name = stat['stat_name'].replace(' ', '_')
        final_stats[stat_name] = stat['stat_value']
    
    return final_stats

def extract_item_equipment(item_equipment_info):
    # 데이터가 리스트인지 확인하고, 아니면 빈 리스트로 처리
    if not isinstance(item_equipment_info, list):
        item_equipment_info = []
    
    equipment_data = {
        "equipped_items": [],
        "presets": []
    }

    # 장비 정보 추출
    for item in item_equipment_info:
        item_data = {
            "part": item.get("item_equipment_part", "정보 없음"),
            "slot": item.get("item_equipment_slot", "정보 없음"),
            "name": item.get("item_name", "정보 없음"),
            "icon": item.get("item_icon", "정보 없음"),
            "description": item.get("item_description", "정보 없음"),
            "total_option": item.get("item_total_option", {}),
            "base_option": item.get("item_base_option", {})
        }
        equipment_data["equipped_items"].append(item_data)

    return equipment_data

def extract_ability_info(ability_info):
    ability_data = {
        "grade": ability_info.get("ability_grade", "정보 없음"),
        "abilities": []
    }
    
    # 기본 어빌리티 추가
    for ability in ability_info.get("ability_info", []):
        ability_data["abilities"].append({
            "no": ability.get("ability_no", "정보 없음"),
            "grade": ability.get("ability_grade", "정보 없음"),
            "value": ability.get("ability_value", "정보 없음"),
        })
    
    # 프리셋 어빌리티 추가
    for preset_num in range(1, 4):
        preset_key = f"ability_preset_{preset_num}"
        preset_info = ability_info.get(preset_key, {})
        preset_data = {
            "preset_grade": preset_info.get("ability_preset_grade", "정보 없음"),
            "abilities": []
        }
        for ability in preset_info.get("ability_info", []):
            preset_data["abilities"].append({
                "no": ability.get("ability_no", "정보 없음"),
                "grade": ability.get("ability_grade", "정보 없음"),
                "value": ability.get("ability_value", "정보 없음"),
            })
        ability_data[preset_key] = preset_data
    
    return ability_data


# 캐릭터 정보 뷰
def character_info_view(request, character_name):
    character_info = asyncio.run(get_character_info(character_name))

    if character_info:
        # 기본 스탯 추출
        final_stats = extract_final_stats(character_info.get('stat_info', {}))
        
        # 장착 장비 정보 추출
        item_equipment_info = character_info.get('item_equipment_info', [])
        equipment_data = extract_item_equipment(item_equipment_info)

        # 어빌리티 정보 추출
        ability_info = character_info.get('ability_info', {})
        ability_data = extract_ability_info(ability_info)

        context = {
            'character_info': character_info,
            'final_stats': final_stats,
            'equipment_data': equipment_data,
            'ability_data': ability_data,
            'preset_range': range(1, 4)
        }

        return render(request, 'character_info/info.html', context)
    else:
        return render(request, 'error.html', {"message": "캐릭터 정보를 찾을 수 없습니다."})
    
    