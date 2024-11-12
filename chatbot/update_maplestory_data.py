# import asyncio
# import aiohttp
# import pinecone
# from openai import OpenAI
# from django.conf import settings

# # OpenAI 및 Pinecone 초기화
# client = OpenAI(api_key=settings.OPENAI_API_KEY)
# pinecone.init(api_key=settings.PINECONE_API_KEY, environment=settings.PINECONE_ENV)

# # Pinecone 인덱스 연결
# index = pinecone.Index("maplestory-index")

# BASE_URL = "https://open.api.nexon.com/maplestory/v1"
# API_KEY = settings.NEXON_API_KEY

# async def get_api_data(session, endpoint, params=None):
#     headers = {"x-nxopen-api-key": API_KEY}
#     url = f"{BASE_URL}{endpoint}"
#     async with session.get(url, headers=headers, params=params) as response:
#         if response.status == 200:
#             return await response.json()
#         return None

# async def fetch_character_data(session, character_name, date=None):
#     id_data = await get_api_data(session, "/id", {"character_name": character_name})
#     if not id_data or 'ocid' not in id_data:
#         return None

#     ocid = id_data['ocid']
#     params = {"ocid": ocid}
#     if date:
#         params["date"] = date

#     basic_info = await get_api_data(session, "/character/basic", params)
#     stat_info = await get_api_data(session, "/character/stat", params)
    
#     return {
#         "basic_info": basic_info,
#         "stat_info": stat_info,
#     }

# async def process_and_store_data(character_data):
#     if not character_data:
#         return

#     basic_info = character_data['basic_info']
#     stat_info = character_data['stat_info']

#     text = f"Character: {basic_info['character_name']}, Level: {basic_info['character_level']}, Job: {basic_info['character_class']}, "
#     text += f"Stat: STR {stat_info['str']}, DEX {stat_info['dex']}, INT {stat_info['int']}, LUK {stat_info['luk']}"

#     response = client.embeddings.create(input=[text], model="text-embedding-ada-002")
#     vector = response.data[0].embedding

#     index.upsert(vectors=[(basic_info['character_name'], vector, {"text": text})])

# async def update_maplestory_data():
#     try:
#         character_names = ["Character1", "Character2", "Character3"]  # 실제 캐릭터 이름 목록으로 대체해야 함
#         async with aiohttp.ClientSession() as session:
#             tasks = [fetch_character_data(session, name) for name in character_names]
#             character_data_list = await asyncio.gather(*tasks)

#         for character_data in character_data_list:
#             await process_and_store_data(character_data)

#         print("메이플스토리 데이터가 성공적으로 업데이트되었습니다.")
#     except Exception as e:
#         print(f"데이터 업데이트 중 오류 발생: {str(e)}")
