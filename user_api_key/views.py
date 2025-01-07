from django.shortcuts import render, redirect

def input_user_api_key(request):
    if request.method == 'POST':
        user_api_key = request.POST.get('user_api_key')
        if not user_api_key:
            return render(request, 'user_api_key.html', {'error': 'user_api_key를 입력해주세요.'})
        
        if not request.user.is_authenticated:
            return render(request, 'warning.html', {'message': '구글 로그인을 해주세요.'})
        
        # user_api_key를 사용하여 캐릭터 정보와 구글 아이디 연동 처리 로직 추가
        # ...

        # 캐릭터 정보를 세션에 저장
        request.session['character_info'] = {
            'user_api_key': user_api_key,
            'character_name': request.POST.get('character_name'),  # 캐릭터 이름 추가
            # 추가적인 캐릭터 정보
            # ...
        }

        return redirect('character_info_view')  # 캐릭터 정보 뷰로 리디렉션
    return render(request, 'user_api_key.html')

