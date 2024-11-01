# character_info/views.py
import asyncio
import aiohttp
from django.shortcuts import render
from django.conf import settings
from asgiref.sync import async_to_sync
from django.utils.safestring import mark_safe 
import json

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
        hexamatrix_info = await get_api_data(session, "/character/hexamatrix", params)
        hexamatrix_stat_info = await get_api_data(session, "/character/hexamatrix-stat", params)
        symbol_equipment_info = await get_api_data(session, "/character/symbol-equipment", params)
        
        return {
            "basic_info": basic_info,
            "stat_info": stat_info,
            "item_equipment_info": item_equipment_info,
            "ability_info": ability_info,
            "set_effect_info": set_effect_info,
            "link_skill_info": link_skill_info,
            "hexamatrix_info": hexamatrix_info,
            "hexamatrix_stat_info" : hexamatrix_stat_info,
            "symbol_equipment_info" : symbol_equipment_info
        }


    
def extract_final_stats(stat_info):
    # final_stat에서 원하는 정보 추출
    final_stats = {}
    for stat in stat_info.get('final_stat', []):
        # stat_name에서 띄어쓰기를 언더바로 변환
        stat_name = stat['stat_name'].replace(' ', '_')
        final_stats[stat_name] = stat['stat_value']
    
    return final_stats


##### 아이템 슬롯명 매핑 테이블
SLOT_MAPPING = {
    "반지1": "ring1",
    "반지2": "ring2",
    "반지3": "ring3",
    "반지4": "ring4",
    "펜던트": "pendant1",
    "펜던트2": "pendant2",
    "무기": "weapon",
    "모자": "hat",
    "상의": "top",
    "하의": "bottom",
    "신발": "shoes",
    "장갑": "gloves",
    "망토": "cape",
    "벨트": "belt",
    "어깨장식": "shoulder",
    "얼굴장식": "face",
    "눈장식": "eyes",
    "귀고리": "earring",
    "뱃지": "badge",
    "훈장": "medal",
    "보조무기": "secondary",
    "엠블렘": "emblem",
    "기계 심장": "heart",
    "안드로이드": "android",
    "포켓 아이템": "poket",
}
def extract_item_equipment(item_equipment_info):
    # 유효성 검사
    if not isinstance(item_equipment_info, dict) or 'item_equipment' not in item_equipment_info:
        return {}
    
    # 기본 구조 생성
    equipment_data = {
        "preset_no": item_equipment_info.get("preset_no", "정보 없음"),
        "item_equipment": {}  # 슬롯별로 저장할 딕셔너리로 변경
    }

    # 각 장비 아이템을 슬롯별로 분류하여 저장
    for item in item_equipment_info.get('item_equipment', []):
        # 한글 슬롯 이름을 가져오고 매핑 테이블을 통해 영어 이름으로 변환
        korean_slot = item.get("item_equipment_slot", "정보 없음")
        slot = SLOT_MAPPING.get(korean_slot, korean_slot)  # 매핑이 없을 경우 한글 이름 그대로 사용

        # 슬롯 이름을 키로 하여 데이터 저장
        equipment_data["item_equipment"][slot] = {
            "slot": slot,  # 슬롯 이름 저장
            "part": item.get("item_equipment_part", "정보 없음"),
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
    # set_effect_info가 딕셔너리인지 확인하고 'set_effect' 필드를 가져옴
    if not isinstance(set_effect_info, dict) or 'set_effect' not in set_effect_info:
        print("set_effect_info의 구조가 잘못되었습니다:", set_effect_info)
        return {}

    # 'set_effect' 리스트를 추출
    set_effects_list = set_effect_info.get('set_effect', [])
    if not isinstance(set_effects_list, list):
        return {}

    set_effect_data = {
        "set_effects": []
    }


    for set_effect in set_effects_list:
        set_data = {
            "set_name": set_effect.get("set_name", "정보 없음"),
            "total_set_count": set_effect.get("total_set_count", "정보 없음"),
            "set_effects": [],
            "set_option_full": []
        }

        # 세트 효과 정보 (set_effect_info)
        for effect in set_effect.get("set_effect_info", []):
            effect_data = {
                "set_count": effect.get("set_count", "정보 없음"),
                "set_option": effect.get("set_option", "정보 없음")
            }
            set_data["set_effects"].append(effect_data)

        # 전체 세트 옵션 정보 (set_option_full)
        for full_effect in set_effect.get("set_option_full", []):
            full_effect_data = {
                "set_count": full_effect.get("set_count", "정보 없음"),
                "set_option": full_effect.get("set_option", "정보 없음")
            }
            set_data["set_option_full"].append(full_effect_data)

        set_effect_data["set_effects"].append(set_data)


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

def extract_hexa_stats(hexamatrix_stat_info):
    if not isinstance(hexamatrix_stat_info, dict):
        return {}

    # 헥사 스탯 정보를 담을 기본 구조
    hexa_stat_data = {
        "character_hexa_stat_core": [],
        "preset_hexa_stat_core": []
    }

    # character_hexa_stat_core 정보 추출
    for stat in hexamatrix_stat_info.get("character_hexa_stat_core", []):
        hexa_stat_data["character_hexa_stat_core"].append({
            "slot_id": stat.get("slot_id", "정보 없음"),
            "main_stat_name": stat.get("main_stat_name", "정보 없음"),
            "sub_stat_name_1": stat.get("sub_stat_name_1", "정보 없음"),
            "sub_stat_name_2": stat.get("sub_stat_name_2", "정보 없음"),
            "main_stat_level": stat.get("main_stat_level", 0),
            "sub_stat_level_1": stat.get("sub_stat_level_1", 0),
            "sub_stat_level_2": stat.get("sub_stat_level_2", 0),
            "stat_grade": stat.get("stat_grade", 0)
        })

    # preset_hexa_stat_core 정보 추출
    for preset_stat in hexamatrix_stat_info.get("preset_hexa_stat_core", []):
        hexa_stat_data["preset_hexa_stat_core"].append({
            "slot_id": preset_stat.get("slot_id", "정보 없음"),
            "main_stat_name": preset_stat.get("main_stat_name", "정보 없음"),
            "sub_stat_name_1": preset_stat.get("sub_stat_name_1", "정보 없음"),
            "sub_stat_name_2": preset_stat.get("sub_stat_name_2", "정보 없음"),
            "main_stat_level": preset_stat.get("main_stat_level", 0),
            "sub_stat_level_1": preset_stat.get("sub_stat_level_1", 0),
            "sub_stat_level_2": preset_stat.get("sub_stat_level_2", 0),
            "stat_grade": preset_stat.get("stat_grade", 0)
        })

    return hexa_stat_data

def extract_hexa(hexamatrix_info):
    if not isinstance(hexamatrix_info, dict):
        return {}

    # 헥사 스킬 정보를 담을 기본 구조
    hexa_data = {
        "character_hexa_core_equipment" : []
    }

    # character_hexa_core_equipment 정보 추출
    for hexa in hexamatrix_info.get("character_hexa_core_equipment", []):
        hexa_data["character_hexa_core_equipment"].append({
            "hexa_core_name": hexa.get("hexa_core_name", "정보 없음"),
            "hexa_core_level": hexa.get("hexa_core_level", "정보 없음"),
            "hexa_core_type": hexa.get("hexa_core_type", "정보 없음"),
        })


    return hexa_data


def extract_symbols(symbol_equipment_info):
    if not isinstance(symbol_equipment_info, dict):
        return {}

    # 심볼 정보를 담을 기본 구조
    symbol_data = {
        "authentic_symbols": [],
        "arcane_symbols": []
    }

    # symbol 데이터가 존재할 때
    for symbol in symbol_equipment_info.get("symbol", []):
        symbol_name = symbol.get("symbol_name", "")

        # 어센틱 심볼 추출
        if "어센틱" in symbol_name:
            symbol_data["authentic_symbols"].append({
                "name": symbol_name,
                "icon": symbol.get("symbol_icon"),
                "description": symbol.get("symbol_description"),
                "force": symbol.get("symbol_force"),
                "level": symbol.get("symbol_level"),
                "stats": {
                    "str": symbol.get("symbol_str"),
                    "dex": symbol.get("symbol_dex"),
                    "int": symbol.get("symbol_int"),
                    "luk": symbol.get("symbol_luk"),
                    "hp": symbol.get("symbol_hp"),
                },
                "growth_count": symbol.get("symbol_growth_count"),
                "require_growth_count": symbol.get("symbol_require_growth_count")
            })

        # 아케인 심볼 추출
        elif "아케인" in symbol_name:
            symbol_data["arcane_symbols"].append({
                "name": symbol_name,
                "icon": symbol.get("symbol_icon"),
                "description": symbol.get("symbol_description"),
                "force": symbol.get("symbol_force"),
                "level": symbol.get("symbol_level"),
                "stats": {
                    "str": symbol.get("symbol_str"),
                    "dex": symbol.get("symbol_dex"),
                    "int": symbol.get("symbol_int"),
                    "luk": symbol.get("symbol_luk"),
                    "hp": symbol.get("symbol_hp"),
                },
                "growth_count": symbol.get("symbol_growth_count"),
                "require_growth_count": symbol.get("symbol_require_growth_count")
            })

    return symbol_data

def character_info_view(request):
    character_name = request.GET.get('character_name') 

async def character_info_view(request, character_name):
    # URL에서 받은 character_name 인수 사용
    character_info = await get_character_info(character_name)

    if character_info:
        # 각 데이터를 추출하는 함수들
        final_stats = extract_final_stats(character_info.get('stat_info', {}))
        equipment_data = extract_item_equipment(character_info.get('item_equipment_info', []))
        ability_data = extract_ability_info(character_info.get('ability_info', {}))
        set_effect_data = extract_set_effect(character_info.get('set_effect_info', []))
        link_skill_data = extract_link_skills(character_info.get('link_skill_info', []))
        hexa_stats = extract_hexa_stats(character_info.get('hexamatrix_stat_info', []))
        hexa_data = extract_hexa(character_info.get('hexamatrix_info', []))
        symbol_data = extract_symbols(character_info.get('symbol_equipment_info', []))

        # 템플릿으로 전달할 컨텍스트
        context = {
            'character_info': character_info,
            'final_stats': final_stats,
            'equipment_data': equipment_data,
            'ability_data': ability_data,
            'set_effect_data': set_effect_data,
            'link_skill_data': link_skill_data,
            'hexa_stats': hexa_stats,
            'hexa_data' : hexa_data,
            'symbol_data' : symbol_data,
            'preset_range': range(1, 4)
        }


        return render(request, 'character_info/info.html', context)
    else:
        return render(request, 'error.html', {"message": "캐릭터 정보를 찾을 수 없습니다."})
    

def chatbot_view(request):
    return render(request, 'character_info/info.html')  # 챗봇 템플릿 경로


##여기는 장비템위에 마우스 갖다대면 띄우는 툴팁을 위해 장비 정보를 안전하게 json파일로 보내기 위한 함수
def character_equipment_view(request):
    item_equipment_info = {
        "preset_no": 1,
        "item_equipment": [
            {"item_equipment_slot": "반지1", "item_name": "파워링", "item_icon": "path/to/ring1_icon.png"},
            {"item_equipment_slot": "반지2", "item_name": "매직링", "item_icon": "path/to/ring2_icon.png"},
            {"item_equipment_slot": "무기", "item_name": "불멸의 검", "item_icon": "path/to/weapon_icon.png"},
        ]
    }

    equipment_data = extract_item_equipment(item_equipment_info)
    
    # JSON으로 변환하여 템플릿에 전달
    equipment_data_json = mark_safe(json.dumps(equipment_data["item_equipment"]))  # JSON으로 변환하고 안전하게 마크
    
    return render(request, "character_equipment.html", {"equipment_data": equipment_data, "equipment_data_json": equipment_data_json})