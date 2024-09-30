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
        params = {"ocid": ocid}
        if date:
            params["date"] = date

        basic_info = await get_api_data(session, "/character/basic", params)
        stat_info = await get_api_data(session, "/character/stat", params)
        item_equipment_info = await get_api_data(session, "/character/item-equipment", params)
        ability_info = await get_api_data(session, "/character/ability", params)
        set_effect_info = await get_api_data(session, "/character/set-effect", params)
        link_skill_info = await get_api_data(session, "/character/link-skill", params)
        character_hexamatrix = await get_api_data(session, "/character/hexamatrix", params)

        return {
            "basic_info": basic_info,
            "stat_info": stat_info,
            "item_equipment_info": item_equipment_info,
            "ability_info": ability_info,
            "set_effect_info": set_effect_info,
            "link_skill_info": link_skill_info,
            "character_hexamatrix": character_hexamatrix
        }


def extract_final_stats(stat_info):
    # final_stat에서 원하는 정보 추출
    final_stats = {}
    for stat in stat_info.get('final_stat', []):
        # stat_name에서 띄어쓰기를 언더바로 변환
        stat_name = stat['stat_name'].replace(' ', '_')
        final_stats[stat_name] = stat['stat_value']
    
    return final_stats

def extract_item_equipment(item_equipment_info):
    if not isinstance(item_equipment_info, dict) or 'item_equipment' not in item_equipment_info:
        return {}
    
    equipment_data = {
        "preset_no": item_equipment_info.get("preset_no", "정보 없음"),
        "item_equipment": []
    }

    for item in item_equipment_info.get('item_equipment', []):
        equipment_item = {
            "part": item.get("item_equipment_part", "정보 없음"),
            "slot": item.get("item_equipment_slot", "정보 없음"),
            "name": item.get("item_name", "정보 없음"),
            "icon": item.get("item_icon", "정보 없음"),
            "description": item.get("item_description", "정보 없음"),
            "shape_name": item.get("item_shape_name", "정보 없음"),
            "shape_icon": item.get("item_shape_icon", "정보 없음"),
            "gender": item.get("item_gender", "정보 없음"),
            "total_option": item.get("item_total_option", {}),
            "base_option": item.get("item_base_option", {}),
            "potential_option_grade": item.get("potential_option_grade", "정보 없음"),
            "additional_potential_option_grade": item.get("additional_potential_option_grade", "정보 없음"),
            "potential_options": [
                item.get("potential_option_1"),
                item.get("potential_option_2"),
                item.get("potential_option_3")
            ],
            "additional_potential_options": [
                item.get("additional_potential_option_1"),
                item.get("additional_potential_option_2"),
                item.get("additional_potential_option_3")
            ],
            "exceptional_option": item.get("item_exceptional_option", {}),
            "add_option": item.get("item_add_option", {}),
            "starforce": item.get("starforce", "0"),
            "starforce_scroll_flag": item.get("starforce_scroll_flag", "정보 없음"),
            "scroll_upgrade": item.get("scroll_upgrade", "0"),
            "scroll_upgradeable_count": item.get("scroll_upgradeable_count", "0"),
            "cuttable_count": item.get("cuttable_count", "0"),
            "golden_hammer_flag": item.get("golden_hammer_flag", "정보 없음"),
            "scroll_resilience_count": item.get("scroll_resilience_count", "0"),
            "soul_name": item.get("soul_name", "정보 없음"),
            "soul_option": item.get("soul_option", "정보 없음"),
            "item_etc_option": item.get("item_etc_option", {}),
            "item_starforce_option": item.get("item_starforce_option", {})
        }
        equipment_data["item_equipment"].append(equipment_item)

    return equipment_data


def extract_ability_info(ability_info):
    if not isinstance(ability_info, dict):
        return {}

    ability_data = {
        "grade": ability_info.get("ability_grade", "정보 없음"),
        "abilities": []
    }
    
    for ability in ability_info.get("ability_info", []):
        ability_data["abilities"].append({
            "no": ability.get("ability_no", "정보 없음"),
            "grade": ability.get("ability_grade", "정보 없음"),
            "value": ability.get("ability_value", "정보 없음"),
        })
    
    return ability_data

def extract_set_effect(set_effect_info):
    if not isinstance(set_effect_info, list):
        set_effect_info = []
    
    set_effect_data = []
    for set_info in set_effect_info:
        set_data = {
            "set_name": set_info.get("set_name", "정보 없음"),
            "total_set_count": set_info.get("total_set_count", 0),
            "set_effects": []
        }
        for effect in set_info.get("set_effect_info", []):
            effect_data = {
                "set_count": effect.get("set_count", 0),
                "set_option": effect.get("set_option", "정보 없음")
            }
            set_data["set_effects"].append(effect_data)
        
        set_effect_data.append(set_data)

    return set_effect_data

def extract_link_skills(link_skill_info):
    if not isinstance(link_skill_info, dict):
        return {}

    extracted_skills = {}
    
    for preset_key, skills in link_skill_info.items():
        if preset_key.startswith('character_link_skill_preset_'):
            preset_number = preset_key.split('_')[-1]
            extracted_skills[f'preset_{preset_number}'] = []
            
            for skill in skills:
                skill_data = {
                    "name": skill.get("skill_name", "정보 없음"),
                    "description": skill.get("skill_description", "정보 없음"),
                    "level": skill.get("skill_level", 0),
                    "effect": skill.get("skill_effect", "정보 없음"),
                    "icon": skill.get("skill_icon", "정보 없음")
                }
                extracted_skills[f'preset_{preset_number}'].append(skill_data)
    
    return extracted_skills

def extract_hexa_stats(hexa_stat_info):
    if not isinstance(hexa_stat_info, list):
        return []

    extracted_stats = []
    for stat in hexa_stat_info:
        stat_data = {
            "slot_id": stat.get("slot_id", "정보 없음"),
            "main_stat_name": stat.get("main_stat_name", "정보 없음"),
            "sub_stat_name_1": stat.get("sub_stat_name_1", "정보 없음"),
            "sub_stat_name_2": stat.get("sub_stat_name_2", "정보 없음"),
            "main_stat_level": stat.get("main_stat_level", 0),
            "sub_stat_level_1": stat.get("sub_stat_level_1", 0),
            "sub_stat_level_2": stat.get("sub_stat_level_2", 0),
            "stat_grade": stat.get("stat_grade", 0)
        }
        extracted_stats.append(stat_data)

    return extracted_stats

async def character_info_view(request, character_name):
    character_info = await get_character_info(character_name)

    if character_info:
        # 각 데이터를 추출하는 함수들
        final_stats = extract_final_stats(character_info.get('stat_info', {}))
        equipment_data = extract_item_equipment(character_info.get('item_equipment_info', []))
        ability_data = extract_ability_info(character_info.get('ability_info', {}))
        set_effect_data = extract_set_effect(character_info.get('set_effect_info', []))
        link_skill_data = extract_link_skills(character_info.get('link_skill_info', []))
        hexa_stats = extract_hexa_stats(character_info.get('character_hexamatrix', []))

        # 템플릿으로 전달할 컨텍스트
        context = {
            'character_info': character_info,
            'final_stats': final_stats,
            'equipment_data': equipment_data,
            'ability_data': ability_data,
            'set_effect_data': set_effect_data,
            'link_skill_data': link_skill_data,
            'hexa_stats': hexa_stats,
            'preset_range': range(1, 4)
        }


        return render(request, 'character_info/info.html', context)
    else:
        return render(request, 'error.html', {"message": "캐릭터 정보를 찾을 수 없습니다."})