const chatBox = document.getElementById('chat-box');
const messageInput = document.getElementById('message');
const sendButton = document.getElementById('send');
const botTemplate = document.getElementById('bot-template');
const botMessageContent = botTemplate.querySelector('.message-content');
let isSidebarOpen = false;

// 메시지를 추가하는 함수 (사용자 메시지)
function addUserMessage(text) {
    const userTemplate = document.getElementById('user-template');
    const messageElement = userTemplate.cloneNode(true);
    messageElement.querySelector('.message-content').textContent = text;
    messageElement.style.display = 'flex'; // 숨겨진 템플릿 표시
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight; // 스크롤을 최하단으로 이동
}

// 봇의 텍스트를 타이핑 효과로 표시
function typeBotMessage(text) {
    botMessageContent.textContent = ''; // 기존 텍스트 초기화
    let index = 0;
    const typingInterval = setInterval(() => {
        if (index < text.length) {
            botMessageContent.textContent += text[index];
            index++;
        } else {
            clearInterval(typingInterval);
        }
    }, 50);
}

// CSRF 토큰 가져오기
function getCSRFToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    if (!token) throw new Error("CSRF 토큰을 찾을 수 없습니다.");
    return token;
}

// 메시지 전송
async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) {
        alert("메시지를 입력하세요.");
        return;
    }

    try {
        addUserMessage(message); // 사용자 메시지 표시
        const csrfToken = getCSRFToken();

        const response = await fetch('/chat_with_bot/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: `message=${encodeURIComponent(message)}`
        });

        if (!response.ok) {
            throw new Error('서버 오류: ' + response.statusText);
        }

        const data = await response.json();
        if (data.error) throw new Error(data.error);

        typeBotMessage(data.response); // 봇의 응답 표시
        messageInput.value = ''; // 입력 필드 초기화
    } catch (error) {
        console.error('메시지 전송 오류:', error);
        alert('메시지 전송 중 문제가 발생했습니다.');
    }
}

// 사이드바 열고 닫기
function toggleSidebar() {
    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("overlay");
    isSidebarOpen = !isSidebarOpen;

    sidebar.style.right = isSidebarOpen ? "0" : "-500px";
    overlay.style.display = isSidebarOpen ? "block" : "none";
}

// 캐릭터 검색
function handleCharacterSearch(e) {
    e.preventDefault();
    const nickname = $('#nickname').val().trim();
    if (!nickname) {
        alert("캐릭터 닉네임을 입력하세요.");
        return;
    }

    const csrfToken = getCSRFToken();

    $.ajax({
        url: '/search_character/',
        type: 'POST',
        data: {
            nickname: nickname,
            csrfmiddlewaretoken: csrfToken
        },
        success: function (response) {
            $('#character-name').text(`이름: ${response.character_name || '알 수 없음'}`);
            $('#character-level').text(`레벨: ${response.character_level || '알 수 없음'}`);
            $('#world-name').text(`월드: ${response.world_name || '알 수 없음'}`);
            $('#character-class').text(`직업: ${response.character_class || '알 수 없음'}`);

            if (response.character_image) {
                $('#character-image').attr('src', response.character_image).show();
            } else {
                $('#character-image').hide();
            }
        },
        error: function (xhr) {
            const errorMessage = xhr.responseJSON?.error || '캐릭터 검색 중 문제가 발생했습니다.';
            alert(errorMessage);
        }
    });
}

// 이벤트 리스너 설정
function setupEventListeners() {
    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
    $('#search-form').on('submit', handleCharacterSearch);
}

// 초기화
$(document).ready(() => {
    setupEventListeners();
});
