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

        # 스킬 정보 요청
        skill_grades = ["0", "1", "1.5", "2", "2.5", "3", "4", "hyperpassive", "hyperactive", "5", "6"]
        skill_info = {}
        for grade in skill_grades:
            skill_params = params.copy()
            skill_params["character_skill_grade"] = grade
            grade_skill_info = await get_api_data(session, "/character/skill", skill_params)
            if grade_skill_info:
                skill_info[grade] = grade_skill_info
        
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
            "skill_info": skill_info,
            "cashitem_info": cashitem_info,  # 추가된 캐시 아이템 정보
            "beauty_info": beauty_info,        # 추가된 뷰티 아이템 정보
            "android_info": android_info,      # 추가된 안드로이드 정보
            "pet_info": pet_info                # 추가된 펫 정보
        }



    
def extract_final_stats(stat_info):
    # final_stat에서 원하는 정보 추출
    final_stats = {}
    for stat in stat_info.get('final_stat', []):
        # stat_name에서 띄어쓰를 언더바 변환
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
        "item_equipment": {}  # 슬롯로 저장할 딕셔너리로 변경
    }

    # 각 장비 아이템을 슬롯별로 분류하여 저장
    for item in item_equipment_info.get('item_equipment', []):
        # 한글 슬롯 이름을 가져오고 매핑 테이블을 통해 영어 이름으로 변환
        korean_slot = item.get("item_equipment_slot", "정보 없음")
        slot = SLOT_MAPPING.get(korean_slot, korean_slot)  # 매핑이 없을 경우 한글 이름 그대로 사용

        # 슬롯 이름을 키로 하여 데이터 저장
        equipment_data["item_equipment"][slot] = {
            "en_slot":item.get("item_equipment_slot", "정보 없음"),
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

def extract_ability_presets(ability_data):
    """
    어빌리티 프리셋 정보를 추출하여 프리셋별로 정리
    """
    if not isinstance(ability_data, dict):
        return {}

    extracted_presets = {}

    # 프리셋 데이터를 반복
    for preset_key, preset_value in ability_data.items():
        # 프리셋 키가 'ability_preset_'으로 시작하는 경우만 처리
        if preset_key.startswith('ability_preset_'):
            # 프리셋 번호 추출
            preset_number = preset_key.split('_')[-1]

            # 각 프리셋의 데이터 추출
            if preset_value is None:  # None 체크 추가
                logger.warning(f"프리셋 값이 None입니다: {preset_key}")
                continue  # None인 경우 건너뛰기

            preset_data = {
                "description": preset_value.get("description", "정보 없음"),
                "grade": preset_value.get("ability_preset_grade", "정보 없음"),
                "abilities": []
            }

            # 어빌리티 상세 정보를 abilities 리스트에 추가
            for ability in preset_value.get("ability_info", []):
                ability_data = {
                    "no": ability.get("ability_no", "정보 없음"),
                    "grade": ability.get("ability_grade", "정보 없음"),
                    "value": ability.get("ability_value", "정보 없음")
                }
                preset_data["abilities"].append(ability_data)

            # 프리셋 데이터를 저장
            extracted_presets[f"preset_{preset_number}"] = preset_data

    return extracted_presets

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




def extract_hyper_stats(hyper_stat_info):
    if not isinstance(hyper_stat_info, dict):
        return {}

    extracted_hyper_stats = {}

    for preset_key, stats in hyper_stat_info.items():
        if preset_key.startswith('hyper_stat_preset_'):
            preset_number = preset_key.split('_')[-1]
            # stats가 리스트가 아닌 경우 강제로 리스트로 변환
            if not isinstance(stats, list):
                stats = []
            extracted_hyper_stats[f'preset_{preset_number}'] = []

            for stat in stats:
                if isinstance(stat, dict):  # stat이 딕셔너리인지 확인
                    stat_data = {
                        "type": stat.get("stat_type", "정보 없음"),
                        "points": stat.get("stat_point", 0),
                        "level": stat.get("stat_level", 0),
                        "increase": stat.get("stat_increase", "정보 없음")
                    }
                    extracted_hyper_stats[f'preset_{preset_number}'].append(stat_data)
    return extracted_hyper_stats

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
    if not isinstance(hexamatrix_stat_info, dict) or not hexamatrix_stat_info:
        return None

    # 헥사 스탯 정보를 담을 기본 구조
    hexa_stat_data = {
        "character_hexa_stat_core": [],
        "preset_hexa_stat_core": []
    }

    if hexamatrix_stat_info.get("character_hexa_stat_core"):
        for stat in hexamatrix_stat_info["character_hexa_stat_core"]:
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

    if hexamatrix_stat_info.get("preset_hexa_stat_core"):
        for preset_stat in hexamatrix_stat_info["preset_hexa_stat_core"]:
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

    return hexa_stat_data if (hexa_stat_data["character_hexa_stat_core"] or hexa_stat_data["preset_hexa_stat_core"]) else None

def extract_hexa(hexamatrix_info):
    if not isinstance(hexamatrix_info, dict) or not hexamatrix_info:
        return None
    
    # 헥사 스킬 정보를 담을 기본 구조
    hexa_data = {
        "character_hexa_core_equipment" : []
    }

    if hexamatrix_info.get("character_hexa_core_equipment"):
        for hexa in hexamatrix_info["character_hexa_core_equipment"]:
            hexa_data["character_hexa_core_equipment"].append({
                "hexa_core_name": hexa.get("hexa_core_name", "정보 없음"),
                "hexa_core_level": hexa.get("hexa_core_level", "정보 없음"),
                "hexa_core_type": hexa.get("hexa_core_type", "정보 없음"),
            })

    return hexa_data if hexa_data["character_hexa_core_equipment"] else None

def extract_character_skills(skill_info):

    # 데이터 검증
    if not isinstance(skill_info, dict):
        return {"error": "유효하지 않은 데이터 형식입니다."}

    # 기본 데이터 구조 생성
    character_skill_data = {
        "character_class": skill_info.get("character_class", "정보 없음"),
        "skill_grade": skill_info.get("character_skill_grade", "정보 없음"),
        "skills": []
    }

        # 스킬 정보 추가
        
    for skill in skill_info.get("character_skill", []):
        character_skill_data["skills"].append({
            "skill_name": skill.get("skill_name", "정보 없음"),
            "skill_description": skill.get("skill_description", "정보 없음"),
            "skill_level": skill.get("skill_level", 0),
            "skill_effect": skill.get("skill_effect", "정보 없음"),
            "skill_effect_next": skill.get("skill_effect_next", "정보 없음"),
            "skill_icon": skill.get("skill_icon", "정보 없음")
        })

    return character_skill_data

def extract_vmatrix(vmatrix_info):
    if not isinstance(vmatrix_info, dict):
        return {}
    
    vmatrix_data = {
        "character_class": vmatrix_info.get("character_class", "정보 없음"),
        "v_cores": [],
        "remain_slot_upgrade_point": vmatrix_info.get("character_v_matrix_remain_slot_upgrade_point", 0)
    }

    for core in vmatrix_info.get("character_v_core_equipment", []):
        vmatrix_data["v_cores"].append({
            "slot_id": core.get("slot_id", "정보 없음"),
            "slot_level": core.get("slot_level", 0),
            "name": core.get("v_core_name", "정보 없음"),
            "type": core.get("v_core_type", "정보 없음"),
            "level": core.get("v_core_level", 0),
            "skill_1": core.get("v_core_skill_1", "정보 없음"),
            "skill_2": core.get("v_core_skill_2", "정보 없음"),
            "skill_3": core.get("v_core_skill_3", "정보 없음")
        })

    return vmatrix_data


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

def extract_character_skills(skill_info):
    if not isinstance(skill_info, dict):
        return {"error": "유효하지 않은 데이터 형식입니다."}

    extracted_skills = {}
    for grade, grade_info in skill_info.items():
        extracted_skills[grade] = {
            "date": grade_info.get("date", "정보 없음"),
            "character_class": grade_info.get("character_class", "정보 없음"),
            "character_skill_grade": grade_info.get("character_skill_grade", "정보 없음"),
            "skills": [
                {
                    "skill_name": skill.get("skill_name", "정보 없음"),
                    "skill_description": skill.get("skill_description", "정보 없음"),
                    "skill_level": skill.get("skill_level", 0),
                    "skill_effect": skill.get("skill_effect", "정보 없음"),
                    "skill_effect_next": skill.get("skill_effect_next", "정보 없음"),
                    "skill_icon": skill.get("skill_icon", "정보 없음")
                }
                for skill in grade_info.get("character_skill", [])
            ]
        }
    return extracted_skills

from asgiref.sync import sync_to_async

FAISS_INDEX_PATH = r'C:\Users\ccg70\OneDrive\desktop\nexon_project\chatbot_project\character_faiss'


import hashlib

def character_info_view(request):
    character_name = request.GET.get('character_name')

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
    

def encode_class(vector, character_class):
    class_mapping = {
        '히어로': 0,
        '아크메이지(불,독)': 1,
        '팔라딘': 2,
        '다크나이트': 3,
        '아크메이지(썬,콜)': 4,
        '비숍': 5,
        '신궁': 6,
        '보우마스터': 7,
        '패스파인더': 8,
        '듀얼블레이드': 9,
        '나이트로드': 10,
        '캡틴': 11,
        '캐논슈터': 12,
        '바이퍼': 13,
        '데몬어벤져': 14,
        '데몬슬레이어': 15,
        '일리움': 16,
        '섀도어': 17,
        '소울마스터': 18,
        '미하일': 19,
        '플레임위자드': 20,
        '윈드브레이커': 21,
        '배틀메이지': 22,
        '블래스터': 23,
        '메카닉': 24,
        '와일드헌터': 25,
        '제논': 26,
        '아란': 27,
        '에반': 28,
        '루미너스': 29,
        '카이저': 30,
        '호영': 31,
        '팬텀': 32,
        '메르세데스': 33,
        '엔젤릭버스터': 34,
        '카인': 35,
        '카데나': 36,
        '아델': 37,
        '일리움': 38,
        '아크': 39,
        '칼리': 40,
        '라라': 41,
        '키네시스': 42,
        '제로': 43,
        '은월': 44,
        '나이트워커': 45,
        '스트라이커': 46,
    }

    index = class_mapping.get(character_class)
    if index is not None:
        vector[index] = 1
    return vector

def encode_stats_clipping(vector, stats):
    stats_mapping = {
        'STR': 47,
        'DEX': 48,
        'INT': 49,
        'LUK': 50,
        'HP': 51,
        'MP': 52,
        '보스 몬스터 데미지': 53,
        '크리티컬 확률': 54,
        '크리티컬 데미지': 55,
        '방어율 무시': 56,
        '최종 데미지': 57,
        '메소 획득량': 58,
        '아이템 드롭률': 59,
        '재사용 대기시간 감소 (%)': 60,
        '버프 지속시간': 61,
        '공격력': 62,
        '마력': 63,
    }
    
    # 합리적인 상한선 설정
    clipping_values = {
        'STR': 200000,
        'DEX': 200000,
        'INT': 200000,
        'LUK': 200000,
        'HP': 10000000,
        'MP': 10000000,
        '보스 몬스터 데미지': 750,
        '크리티컬 확률': 100,
        '크리티컬 데미지': 150,
        '방어율 무': 100,
        '최종 데미지': 200,
        '메소 획득량': 400,
        '아이템 드롭률': 400,
        '재사용 대기시간 감소 (%)': 20,
        '버프 지속시간': 1000,
        '공격력': 100000,
        '마력': 100000,
    }
    
    for stat, index in stats_mapping.items():
        value = stats.get(stat, 0)
        clipped = min(value, clipping_values.get(stat, 1))
        normalized = clipped / clipping_values.get(stat, 1)
        vector[index] = normalized
    return vector

def encode_equipment(vector, equipment):
    equipment_mapping = {
        '무기': 64,
        '모자': 65,
        '상의': 66,
        '하의': 67,
        '귀고리': 68,
        '얼굴장식': 69,
        '신발': 70,
        '장갑': 22,
        '벨트': 71,
        '펜던트': 72,
        '펜던트2': 73,
        '망토': 74,
        '반지1': 75,
        '반지2': 76,
        '반지3': 77,
        '반지4': 78,
        '포켓 아이템': 79,
        '엠블렘': 80,
        '보조무기': 81,
        '뱃지': 82,
        '훈장': 83,
        '기계 심장': 84,

    }
    for equip_type, index in equipment_mapping.items():
        if equipment.get(equip_type, {}).get('name'):
            vector[index] = 1
    return vector

def encode_skills(vector, skills):
    skill_count = len(skills.get('skills', []))
    # 최대 스킬 수를 기준으로 정규화
    vector[18] = min(skill_count / 50, 1)
    # 정 스킬 레벨이나 효과를 추가로 인코딩할 수 있음
    return vector

def vectorize_character_data(character_info):
    vector = np.zeros(768)  # 벡터 차원을 768으로 설정

    # 기본 정보 인코딩
    basic_info = character_info.get('basic_info', {})
    character_class = basic_info.get('character_class', '정보 없음')
    level = basic_info.get('character_level', 1)
    vector[20] = min(level / 300, 1)  # 최대 레벨 300 가정

    vector = encode_class(vector, character_class)

    # 스탯 인코딩 (클리핑 기반 정규화 사용)
    stats = character_info.get('final_stats', {})
    vector = encode_stats_clipping(vector, stats)

    # 장비 인코딩 (세분화된 장비 유형 사용)
    equipment = character_info.get('equipment_data', {})
    vector = encode_equipment(vector, equipment)

    # 스킬 인코딩
    skills = character_info.get('skill_info', {})
    vector = encode_skills(vector, skills)

    # 추가적인 속성 인코딩 가능
    # 예: hexa_stats, hexa_data, vmatrix_data 등

    return vector



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

        # FAISS 인덱스 차원 설정 (128에서 1536으로 변경)
        dimension = 768  # 기존 인덱스 차원을 새로운 임베딩 차원에 맞춤
        logger.info(f"Setting FAISS index dimension to {dimension}")

        # FAISS 인덱스 생성 또는 로드
        if os.path.exists(faiss_file_path):
            index = faiss.read_index(faiss_file_path)
            logger.info(f"Loaded existing FAISS index from {faiss_file_path}")
            if index.d != dimension:
                logger.error(f"기존 FAISS 인덱스의 차원({index.d})이 새 벡터의 차원({dimension})과 일치하지 않습니다.")
                return
        else:
            index = faiss.IndexFlatL2(dimension)
            logger.info(f"Created new FAISS index with dimension {dimension}")

        # 캐릭터 데이터를 벡터로 변환
        vector = vectorize_character_data(character_info)
        logger.info(f"Vectorized character data for {character_name} 저장 완료")

        # 벡터 데이터 타입 변환 및 차원 맞추기
        if vector.dtype != np.float32:
            vector = vector.astype(np.float32)
            logger.info("Converted vector to float32")

        if vector.shape[0] > dimension:
            vector = vector[:dimension]
            logger.info(f"Truncated vector to {dimension} dimensions")
        elif vector.shape[0] < dimension:
            vector = np.pad(vector, (0, dimension - vector.shape[0]), 'constant')
            logger.info(f"Padded vector to {dimension} dimensions")

        # 벡터의 형상 확인
        logger.info(f"Final vector shape: {vector.shape}, dtype: {vector.dtype}")

        # FAISS 인덱스에 벡터 추가 및 저장
        vector = np.array([vector], dtype=np.float32)
        index.add(vector)
        faiss.write_index(index, faiss_file_path)
        logger.info(f"Added vector to FAISS index and saved to {faiss_file_path}")

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

        # 메타데이터 저장
        with open(metadata_file_path, 'w', encoding='utf-8') as f:
            json.dump(filtered_data, f, ensure_ascii=False, indent=4)
            logger.info(f"Saved metadata to {metadata_file_path}")

        logger.info(f"Saved {character_name} to FAISS 인덱스와 메타데이터 파일")

    except Exception as e:
        logger.exception(f"Error saving to FAISS for {character_name}: {str(e)}")

async def character_info_view(request, character_name):
    # URL에서 받은 character_name 인수 사용
    character_name = request.GET.get('character_name')  # 쿼리 파라미터에서 캐릭터 이름 가져오기
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

        # 캐가된 데이터 추출
        cash_item_data = await sync_to_async(extract_cash_item_equipment)(character_info.get('cashitem_info', {}))
        android_data = await sync_to_async(extract_android_info)(character_info.get('android_info', {}))
        pet_data = await sync_to_async(extract_pet_info)(character_info.get('pet_info', {}))
        beauty_data = await sync_to_async(extract_beauty_info)(character_info.get('beauty_info', {}))

        # 캐시 저장
        cache.set(f'character_info_{character_name}', character_info, timeout=600)

        # FAISS에 캐릭터 정보 저장
        await sync_to_async(save_to_faiss)(character_name, character_info)

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
        }

        return render(request, 'character_info/info.html', context)
    else:
        return render(request, 'character_info/error.html', {'error': '캐릭터 정보를 찾을 수 없습니다.'})
    

def chatbot_view(request):
    return render(request, 'character_info/info.html')  # 챗봇 템플릿 경로

def extract_cash_item_equipment(cash_item_info):
    """
    캐시 아이템 정보를 추출하여 기본 정보와 프리셋 정보를 정리
    """
    if not isinstance(cash_item_info, dict):
        return {}

    # 기본 정보 추출
    cash_item_data = {
        "date": cash_item_info.get("date", "정보 없음"),
        "character_gender": cash_item_info.get("character_gender", "정보 없음"),
        "character_class": cash_item_info.get("character_class", "정보 없음"),
        "character_look_mode": cash_item_info.get("character_look_mode", "정보 없음"),
        "preset_no": cash_item_info.get("preset_no", 0),
        "cash_item_equipment_base": [],
        "cash_item_equipment_presets": {}
    }

    # 기본 캐시 아이템 정보 추출
    for item in cash_item_info.get("cash_item_equipment_base", []):
        cash_item_data["cash_item_equipment_base"].append({
            "part": item.get("cash_item_equipment_part", "정보 없음"),
            "slot": item.get("cash_item_equipment_slot", "정보 없음"),
            "name": item.get("cash_item_name", "정보 없음"),
            "icon": item.get("cash_item_icon", "정보 없음"),
            "description": item.get("cash_item_description", "정보 없음"),
            "options": item.get("cash_item_option", []),
            "date_expire": item.get("date_expire", "정보 없음"),
            "date_option_expire": item.get("date_option_expire", "정보 없음"),
            "label": item.get("cash_item_label", "정보 없음"),
            "coloring_prism": item.get("cash_item_coloring_prism", {}),
            "item_gender": item.get("item_gender", "정보 없음")
        })

    # 프리셋 정보 추출
    for i in range(1, 4):
        preset_key = f"cash_item_equipment_preset_{i}"
        cash_item_data["cash_item_equipment_presets"][f"preset_{i}"] = [
            {
                "part": item.get("cash_item_equipment_part", "정보 없음"),
                "slot": item.get("cash_item_equipment_slot", "정보 없음"),
                "name": item.get("cash_item_name", "정보 없음"),
                "icon": item.get("cash_item_icon", "정보 없음"),
                "description": item.get("cash_item_description", "정보 없음"),
                "options": item.get("cash_item_option", []),
                "date_expire": item.get("date_expire", "정보 없음"),
                "date_option_expire": item.get("date_option_expire", "정보 없음"),
                "label": item.get("cash_item_label", "정보 없음"),
                "coloring_prism": item.get("cash_item_coloring_prism", {}),
                "item_gender": item.get("item_gender", "정보 없음")
            }
            for item in cash_item_info.get(preset_key, [])
        ]

    return cash_item_data

def extract_beauty_info(beauty_info):
    """
    캐릭터의 뷰티 정보를 추출
    """
    if not isinstance(beauty_info, dict):
        return {}

    # 안전한 데이터 접근
    additional_hair = beauty_info.get("additional_character_hair", {}) or {}
    additional_face = beauty_info.get("additional_character_face", {}) or {}

    beauty_data = {
        "hair_name": additional_hair.get("hair_name", "정보 없음"),
        "hair_icon": additional_hair.get("hair_icon", "정보 없음"),
        "face_name": additional_face.get("face_name", "정보 없음"),
        "face_icon": additional_face.get("face_icon", "정보 없음"),
        "skin": beauty_info.get("skin", "정보 없음"),
        "skin_icon": beauty_info.get("skin_icon", "정보 없음"),
    }

    return beauty_data


def extract_android_info(android_info):
    """
    안드로이드 정보를 추출하여 캐릭터의 안드로이드 관련 정보를 정리
    """
    if android_info is None or not isinstance(android_info, dict):
        return {}

    android_data = {
        "date": android_info.get("date", "정보 없음"),
        "android_name": android_info.get("android_name", "정보 없음"),
        "android_nickname": android_info.get("android_nickname", "정보 없음"),
        "android_icon": android_info.get("android_icon", "정보 없음"),
        "android_description": android_info.get("android_description", "정보 없음"),
        "android_gender": android_info.get("android_gender", "정보 없음"),
        "android_grade": android_info.get("android_grade", "정보 없음"),
        "android_ear_sensor_clip_flag": android_info.get("android_ear_sensor_clip_flag", "정보 없음"),
        "android_non_humanoid_flag": android_info.get("android_non_humanoid_flag", "정보 없음"),
        "android_shop_usable_flag": android_info.get("android_shop_usable_flag", "정보 없음"),
        "preset_no": android_info.get("preset_no", 0),
        "android_hair": extract_nested_dict(android_info.get("android_hair")),
        "android_face": extract_nested_dict(android_info.get("android_face")),
        "android_skin": extract_nested_dict(android_info.get("android_skin")),
        "android_cash_item_equipment": [],
        "android_presets": {}
    }

    if "android_cash_item_equipment" in android_info and isinstance(android_info["android_cash_item_equipment"], list):
        for item in android_info["android_cash_item_equipment"]:
            android_data["android_cash_item_equipment"].append({
                "part": item.get("cash_item_equipment_part", "정보 없음"),
                "slot": item.get("cash_item_equipment_slot", "정보 없음"),
                "name": item.get("cash_item_name", "정보 없음"),
                "icon": item.get("cash_item_icon", "정보 없음"),
                "description": item.get("cash_item_description", "정보 없음"),
                "options": item.get("cash_item_option", []),
                "date_expire": item.get("date_expire", "정보 없음"),
                "date_option_expire": item.get("date_option_expire", "정보 없음"),
                "label": item.get("cash_item_label", "정보 없음"),
                "coloring_prism": item.get("cash_item_coloring_prism", {}),
                "android_item_gender": item.get("android_item_gender", "정보 없음")
            })

    for i in range(1, 4):
        preset_key = f"android_preset_{i}"
        preset_data = android_info.get(preset_key)
        if isinstance(preset_data, dict):
            android_data["android_presets"][f"preset_{i}"] = {
                "android_name": preset_data.get("android_name", "정보 없음"),
                "android_nickname": preset_data.get("android_nickname", "정보 없음"),
                "android_icon": preset_data.get("android_icon", "정보 없음"),
                "android_description": preset_data.get("android_description", "정보 없음"),
                "android_gender": preset_data.get("android_gender", "정보 없음"),
                "android_grade": preset_data.get("android_grade", "정보 없음"),
                "android_hair": extract_nested_dict(preset_data.get("android_hair")),
                "android_face": extract_nested_dict(preset_data.get("android_face")),
                "android_skin": extract_nested_dict(preset_data.get("android_skin")),
                "android_ear_sensor_clip_flag": preset_data.get("android_ear_sensor_clip_flag", "정보 없음"),
                "android_non_humanoid_flag": preset_data.get("android_non_humanoid_flag", "정보 없음"),
                "android_shop_usable_flag": preset_data.get("android_shop_usable_flag", "정보 없음"),
            }
        else:
            android_data["android_presets"][f"preset_{i}"] = {}

    return android_data


def extract_nested_dict(data):
    """ 중첩된 딕셔너리를 안전하게 처리 """
    if not isinstance(data, dict):
        return {
            "hair_name": "정보 없음",
            "base_color": "정보 없음",
            "mix_color": "정보 없음",
            "mix_rate": "정보 없음"
        }
    return {
        "hair_name": data.get("hair_name", "정보 없음"),
        "base_color": data.get("base_color", "정보 없음"),
        "mix_color": data.get("mix_color", "정보 없음"),
        "mix_rate": data.get("mix_rate", "정보 없음")
    }



def extract_pet_info(pet_info):
    """
    펫 정보를 추출하여 캐릭터의 펫 관련 정보를 정리
    """
    if not isinstance(pet_info, dict):
        return {}

    pet_data = {}

    # 펫 1~3 정보 추출
    for i in range(1, 4):
        pet_key = f"pet_{i}"
        equipment_info = pet_info.get(f"{pet_key}_equipment", {}) or {}  # None이면 빈 딕셔너리로 대체
        auto_skill_info = pet_info.get(f"{pet_key}_auto_skill", {}) or {}  # None이면 빈 딕셔너리로 대체

        pet_data[pet_key] = {
            "name": pet_info.get(f"{pet_key}_name", "정보 없음"),
            "nickname": pet_info.get(f"{pet_key}_nickname", "정보 없음"),
            "icon": pet_info.get(f"{pet_key}_icon", "정보 없음"),
            "description": pet_info.get(f"{pet_key}_description", "정보 없음"),
            "equipment": {
                "item_name": equipment_info.get("item_name", "정보 없음"),
                "item_icon": equipment_info.get("item_icon", "정보 없음"),
                "item_description": equipment_info.get("item_description", "정보 없음"),
                "item_option": equipment_info.get("item_option", []),
                "scroll_upgrade": equipment_info.get("scroll_upgrade", 0),
                "scroll_upgradable": equipment_info.get("scroll_upgradable", 0),
                "item_shape": equipment_info.get("item_shape", "정보 없음"),
                "item_shape_icon": equipment_info.get("item_shape_icon", "정보 없음"),
            },
            "auto_skill": {
                "skill_1": auto_skill_info.get("skill_1", "정보 없음"),
                "skill_1_icon": auto_skill_info.get("skill_1_icon", "정보 없음"),
                "skill_2": auto_skill_info.get("skill_2", "정보 없음"),
                "skill_2_icon": auto_skill_info.get("skill_2_icon", "정보 없음"),
            },
            "pet_type": pet_info.get(f"{pet_key}_pet_type", "정보 없음"),
            "skills": pet_info.get(f"{pet_key}_skill", []),
            "date_expire": pet_info.get(f"{pet_key}_date_expire", "정보 없음"),
            "appearance": pet_info.get(f"{pet_key}_appearance", "정보 없음"),
            "appearance_icon": pet_info.get(f"{pet_key}_appearance_icon", "정보 없음"),
        }

    return pet_data
