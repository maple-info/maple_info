import aiohttp
from django.shortcuts import render, redirect
from django.conf import settings
import logging
from datetime import timedelta
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
import requests
from asgiref.sync import sync_to_async


logger = logging.getLogger(__name__)
BASE_URL = "https://open.api.nexon.com/maplestory/v1"
API_KEY = settings.NEXON_API_KEY
CACHE_DURATION = timedelta(hours=1)  # 캐시 유효 기간

async def main_home(request):
    """메인 페이지 뷰"""
    info = await get_info()  # API에서 공지 정보를 가져옴
    is_authenticated = await sync_to_async(lambda: request.user.is_authenticated)()
    context = {
        **info,
        'is_authenticated': is_authenticated,
    }
    return render(request, 'home.html', context)  # 공지 정보를 템플릿에 전달

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
        redirect_uri = settings.GOOGLE_REDIRECT_URI
        google_client_id = settings.GOOGLE_CLIENT_ID
        if not google_client_id:
            logger.error("GOOGLE_CLIENT_ID가 설정되지 않았습니다.")
            return redirect('main_home')  # 또는 적절한 에러 페이지로 리디렉션

        return redirect(f'https://accounts.google.com/o/oauth2/auth?client_id={google_client_id}&redirect_uri={redirect_uri}&response_type=code&scope=email profile')
    else:
        # GET 요청에 대한 처리 (예: 로그인 페이지로 리디렉션)
        return redirect('main_home')  # 또는 적절한 페이지로 리디렉션

def google_callback(request):
    code = request.GET.get('code')
    if not code:
        return redirect('main_home')

    # 토큰 요청
    token_url = 'https://oauth2.googleapis.com/token'
    token_data = {
        'code': code,
        'client_id': settings.GOOGLE_CLIENT_ID,
        'client_secret': settings.GOOGLE_CLIENT_SECRET,
        'redirect_uri': settings.GOOGLE_REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    token_response = requests.post(token_url, data=token_data)
    token_json = token_response.json()
    access_token = token_json.get('access_token')

    if not access_token:
        logger.error("액세스 토큰을 가져오지 못했습니다.")
        return redirect('main_home')

    # 사용자 정보 요청
    user_info_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    user_info_params = {'access_token': access_token}
    user_info_response = requests.get(user_info_url, params=user_info_params)
    user_info = user_info_response.json()

    # 사용자 정보로 로그인 처리
    email = user_info.get('email')
    if not email:
        logger.error("사용자 이메일을 가져오지 못했습니다.")
        return redirect('main_home')

    user, created = User.objects.get_or_create(username=email, defaults={'email': email})
    backend = 'django.contrib.auth.backends.ModelBackend'  # 사용 중인 인증 백엔드
    login(request, user, backend=backend)

    return redirect('main_home')

def google_logout(request):
    logout(request)
    return redirect('main_home')

async def chatbot_view(request):
    return render(request, 'chatbot.html')  # chatbot 앱의 템플릿 경로

async def character_info_view(request):
    # 챗봇 페이지에 대한 처리 로직 추가
    return render(request, 'info.html')  # 챗봇 템플릿 렌더링


