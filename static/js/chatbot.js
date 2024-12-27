const chatBox = document.getElementById('chat-box');
const messageInput = document.getElementById('message');
const sendButton = document.getElementById('send');

// 봇 템플릿 (하단 고정)
const botTemplate = document.getElementById('bot-template');
const botMessageContent = botTemplate.querySelector('.message-content');

// 메시지를 채팅 창에 추가하는 함수 (사용자 메시지만 추가)
function addUserMessage(text) {
    const userTemplate = document.getElementById('user-template');
    const messageElement = userTemplate.cloneNode(true);

    // 텍스트 업데이트
    messageElement.querySelector('.message-content').textContent = text;
    messageElement.style.display = 'flex'; // 숨겨진 템플릿을 표시

    // 채팅창에 추가
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight; // 스크롤을 최하단으로 이동
}

// 글이 생성되는 것처럼 텍스트를 하나씩 표시하는 함수 (봇 메시지 업데이트)
function typeBotText(text) {
    let i = 0;
    botMessageContent.textContent = ''; // 기존 텍스트 초기화

    function typing() {
        if (i < text.length) {
            botMessageContent.textContent += text[i];
            i++;
            setTimeout(typing, 50); // 50ms마다 한 글자씩 추가
        }
    }
    typing();
}


// CSRF 토큰 가져오기
function getCSRFToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    if (!token) {
        console.error("CSRF 토큰을 찾을 수 없습니다.");
        throw new Error("CSRF 토큰을 찾을 수 없습니다.");
    }
    return token;
}

async function sendMessage() {
    const messageInput = document.getElementById('message');
    const message = messageInput?.value.trim();

    if (!message) {
        alert("메시지를 입력하세요.");
        return;
    }

    try {
        addUserMessage(message);

        const csrfToken = getCSRFToken();

        const response = await fetch('/chat_with_bot/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: `message=${encodeURIComponent(message)}`
        });

        const contentType = response.headers.get("content-type");
        if (contentType && contentType.includes("application/json")) {
            const data = await response.json();
            if (data.error) {
                throw new Error(data.error);
            }
            typeBotText(data.response);
        } else {
            console.error('Unexpected response:', await response.text());
            throw new Error('서버에서 JSON 응답을 받지 못했습니다.');
        }

        messageInput.value = '';
    } catch (error) {
        console.error('메시지 전송 오류:', error);
        alert('메시지 전송 중 오류가 발생했습니다. 콘솔 로그를 확인하세요.');
    }
}

// 이벤트 리스너 중복 제거 (한 번만 설정)
sendButton.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// 사이드바
let isSidebarOpen = false;

function toggleSidebar() {
    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("overlay");

    if (isSidebarOpen) {
        // 닫기
        sidebar.style.right = "-500px"; // 화면 밖으로 숨김
        overlay.style.display = "none"; // 오버레이 숨김
    } else {
        // 열기
        sidebar.style.right = "0"; // 화면 안으로 보임
        overlay.style.display = "block"; // 오버레이 표시
    }

    isSidebarOpen = !isSidebarOpen;
}


// 캐릭터 정보
// $(document).ready(function () {
//     const csrfToken = '{{ csrf_token }}'; // CSRF 토큰 설정

//     $('#search-form').on('submit', function (e) {
//         e.preventDefault(); // 기본 폼 제출 방지

//         const nickname = $('#nickname').val(); // 닉네임 가져오기

//         $.ajax({
//             url: '/chatbot/search_character/', // Django URL 매핑과 일치하도록 수정
//             type: 'POST',
//             data: {
//                 nickname: nickname,
//                 csrfmiddlewaretoken: csrfToken, // CSRF 토큰 전달
//             },
//             success: function (response) {
//                 // 성공적으로 응답을 받은 경우 데이터를 HTML에 렌더링
//                 $('#character-name').text('Name: ' + response.character_name);
//                 $('#character-level').text('Level: ' + response.character_level);
//                 $('#world-name').text('World: ' + response.world_name);
//                 $('#character-class').text('Class: ' + response.character_class);

//                 // 캐릭터 이미지 표시
//                 if (response.character_image) {
//                     $('#character-image').attr('src', response.character_image).show();
//                 } else {
//                     $('#character-image').hide();
//                 }
//             },
//             error: function (xhr) {
//                 // 에러 처리
//                 const errorMessage = xhr.responseJSON?.error || 'An error occurred';
//                 alert('Error: ' + errorMessage);
//             },
//         });
//     });
// });
