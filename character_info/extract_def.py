import logging

# logger 정의 추가
logger = logging.getLogger(__name__)

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



def extract_final_stats(stat_info):
    # final_stat에서 원하는 정보 추출
    final_stats = {}
    for stat in stat_info.get('final_stat', []):
        # stat_name에서 띄어쓰를 언더바 변환
        stat_name = stat['stat_name'].replace(' ', '_')
        final_stats[stat_name] = stat['stat_value']
    
    return final_stats

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
    """
    캐릭터 스킬 정보를 추출하는 함수
    Args:
        skill_info (dict): API로부터 받은 스킬 정보
    Returns:
        dict: 정제된 스킬 정보
    """
    logger.debug(f"Extracting character skills from: {skill_info}")
    
    try:
        if not isinstance(skill_info, dict):
            logger.error("Invalid skill_info format: not a dictionary")
            return {
                "date": "정보 없음",
                "character_class": "정보 없음",
                "character_skill_grade": "정보 없음",
                "skills": []
            }

        return {
            "date": skill_info.get("date", "정보 없음"),
            "character_class": skill_info.get("character_class", "정보 없음"),
            "character_skill_grade": skill_info.get("character_skill_grade", "정보 없음"),
            "skills": [
                {
                    "skill_name": skill.get("skill_name", "정보 없음"),
                    "skill_description": skill.get("skill_description", "정보 없음"),
                    "skill_level": int(skill.get("skill_level", 0)),
                    "skill_effect": skill.get("skill_effect", "정보 없음"),
                    "skill_effect_next": skill.get("skill_effect_next", "정보 없음"),
                    "skill_icon": skill.get("skill_icon", "")
                }
                for skill in skill_info.get("character_skill", [])
            ]
        }

    except Exception as e:
        logger.exception(f"스킬 정보 처리 중 오류: {str(e)}")
        return {
            "date": "정보 없음",
            "character_class": "정보 없음",
            "character_skill_grade": "정보 없음",
            "skills": [],
            "error": f"스킬 정보 처리 중 오류 발생: {str(e)}"
        }

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



def extract_vmatrix(vmatrix_info):

    try:
        if not isinstance(vmatrix_info, dict):
            logger.error("Invalid vmatrix_info format: not a dictionary")
            return {
                "date": "정보 없음",
                "character_class": "정보 없음",
                "cores": [],
                "remain_points": 0
            }

        return {
            "date": vmatrix_info.get("date", "정보 없음"),
            "character_class": vmatrix_info.get("character_class", "정보 없음"),
            "cores": [
                {
                    "slot_id": core.get("slot_id", "정보 없음"),
                    "slot_level": int(core.get("slot_level", 0)),
                    "core_name": core.get("v_core_name", "정보 없음"),
                    "core_type": core.get("v_core_type", "정보 없음"),
                    "core_level": int(core.get("v_core_level", 0)),
                    "skill_1": core.get("v_core_skill_1", "정보 없음"),
                    "skill_2": core.get("v_core_skill_2", "정보 없음"),
                    "skill_3": core.get("v_core_skill_3", "정보 없음")
                }
                for core in vmatrix_info.get("character_v_core_equipment", [])
            ],
            "remain_points": int(vmatrix_info.get("character_v_matrix_remain_slot_upgrade_point", 0))
        }

    except Exception as e:
        logger.exception(f"V매트릭스 정보 처리 중 오류: {str(e)}")
        return {
            "error": f"V매트릭스 정보 처리 중 오류 발생: {str(e)}",
            "date": "정보 없음",
            "character_class": "정보 없음",
            "cores": [],
            "remain_points": 0
        }

     


def extract_symbols(symbol_equipment_info):
    """
    심볼 장비 정보를 추출하여 캐릭터의 심볼 장비 관련 정보를 정리
    """
    if not isinstance(symbol_equipment_info, dict):
        return {}

    symbol_data = {
        "date": symbol_equipment_info.get("date", "정보 없음"),
        "character_class": symbol_equipment_info.get("character_class", "정보 없음"),
        "symbol": []
    }

    for symbol in symbol_equipment_info.get("symbol", []):
        symbol_data["symbol"].append({
            "symbol_name": symbol.get("symbol_name", "정보 없음"),
            "symbol_icon": symbol.get("symbol_icon", "정보 없음"),
            "symbol_description": symbol.get("symbol_description", "정보 없음"),
            "symbol_force": symbol.get("symbol_force", "정보 없음"),
            "symbol_level": symbol.get("symbol_level", 0),
            "symbol_str": symbol.get("symbol_str", "정보 없음"),
            "symbol_dex": symbol.get("symbol_dex", "정보 없음"),
            "symbol_int": symbol.get("symbol_int", "정보 없음"),
            "symbol_luk": symbol.get("symbol_luk", "정보 없음"),
            "symbol_hp": symbol.get("symbol_hp", "정보 없음"),
            "symbol_drop_rate": symbol.get("symbol_drop_rate", "정보 없음"),
            "symbol_meso_rate": symbol.get("symbol_meso_rate", "정보 없음"),
            "symbol_exp_rate": symbol.get("symbol_exp_rate", "정보 없음"),
            "symbol_growth_count": symbol.get("symbol_growth_count", 0),
            "symbol_require_growth_count": symbol.get("symbol_require_growth_count", 0)
        })

    return symbol_data
