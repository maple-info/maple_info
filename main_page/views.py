import aiohttp
from django.shortcuts import render, redirect
from django.conf import settings
import logging
from datetime import timedelta


logger = logging.getLogger(__name__)
BASE_URL = "https://open.api.nexon.com/maplestory/v1"
API_KEY = settings.NEXON_API_KEY
CACHE_DURATION = timedelta(hours=1)  # 캐시 유효 기간

async def main_home(request):
    info = await get_info()  # API에서 공지 정보를 가져옴
    return render(request, 'main_page/home.html', info)  # 공지 정보를 템플릿에 전달

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

async def get_info():
    async with aiohttp.ClientSession() as session:
        # 추가된 API 경로에 대한 데이터 요청
        event_info = await get_api_data(session, "/notice-event")
        cashshop_info= await get_api_data(session, "/notice-cashshop")
        # ranking_info= await get_api_data(session, "ranking/overall")


        return {
            "event_info": event_info,
            "cashshop_info": cashshop_info,
            # "ranking_info" : ranking_info,

        }

def google_login(request):
    if request.method == 'POST':
        redirect_uri = request.build_absolute_uri('/complete/google/')
        return redirect(f'https://accounts.google.com/o/oauth2/auth?client_id={settings.GOOGLE_CLIENT_ID}&redirect_uri={redirect_uri}&response_type=code&scope=email profile')
    else:
        # GET 요청에 대한 처리 (예: 로그인 페이지로 리디렉션)
        return redirect('main_home')  # 또는 적절한 페이지로 리디렉션

async def chatbot_view(request):
    return render(request, 'chatbot/chatbot.html')  # chatbot 앱의 템플릿 경로

async def character_info_view(request):
    # 챗봇 페이지에 대한 처리 로직 추가
    return render(request, 'character_info/info.html')  # 챗봇 템플릿 렌더링


