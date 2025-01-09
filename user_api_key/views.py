from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import CharacterInfo
import requests

@login_required
def input_user_api_key(request):
    if request.method == 'POST':
        character_name = request.POST.get('character_name')
        user_api_key = request.POST.get('user_api_key')

        # 입력값 검증
        if not character_name or not user_api_key:
            return render(request, 'user_api_key.html', {'error': '닉네임과 API 키를 모두 입력해주세요.'})

        try:
            # OCID 조회
            response = requests.get(
                "https://open.api.nexon.com/maplestory/v1/id",
                params={"character_name": character_name},
                headers={"x-nxopen-api-key": user_api_key},
            )
            response.raise_for_status()
            data = response.json()
            ocid = data.get("ocid")

            if not ocid:
                return render(request, 'user_api_key.html', {'error': 'OCID를 가져올 수 없습니다.'})

            # OCID 저장
            CharacterInfo.objects.update_or_create(
                user=request.user,
                defaults={"ocid": ocid, "character_name": character_name},
            )

            return redirect('character_info')

        except requests.RequestException as e:
            return render(request, 'user_api_key.html', {'error': f'API 요청 실패: {str(e)}'})

    return render(request, 'user_api_key.html')
