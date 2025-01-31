const chatBox = document.getElementById('chat-box');
const messageInput = document.getElementById('message');
const userTemplate = document.getElementById('user-template');
const botTemplate = document.getElementById('bot-template');

// 사용자 메시지 추가
function addUserMessage(text) {
    const messageElement = userTemplate.cloneNode(true);
    messageElement.querySelector('.message-content').textContent = text;
    messageElement.style.display = 'flex'; // 숨겨진 템플릿 표시
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight; // 스크롤을 최하단으로 이동
}

// 봇 메시지 추가 (타이핑 효과)
function addBotMessage(text) {
    const messageElement = botTemplate.cloneNode(true);
    const botMessageContent = messageElement.querySelector('.message-content');
    messageElement.style.display = 'flex'; // 숨겨진 템플릿 표시
    chatBox.appendChild(messageElement);

    botMessageContent.textContent = ''; // 기존 텍스트 초기화
    let index = 0;
    const typingInterval = setInterval(() => {
        if (index < text.length) {
            botMessageContent.textContent += text[index];
            index++;
        } else {
            clearInterval(typingInterval);
            chatBox.scrollTop = chatBox.scrollHeight; // 스크롤을 최하단으로 이동
        }
    }, 50);
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
        messageInput.value = ''; // 입력 필드 초기화
        const csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]').value;

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

        addBotMessage(data.response); // 봇 메시지 표시
    } catch (error) {
        console.error('메시지 전송 오류:', error);
        alert('메시지 전송 중 문제가 발생했습니다.');
    }
}

// 버튼 클릭 및 엔터키 이벤트 리스너
document.getElementById('send').addEventListener('click', sendMessage);
messageInput.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') sendMessage();
});

// CSRF 토큰 가져오기
function getCSRFToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    if (!token) throw new Error("CSRF 토큰을 찾을 수 없습니다.");
    return token;
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
// 이벤트 리스너 설정
function setupEventListeners() {
    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
    $('#search-form').on('submit', handleCharacterSearch);
}

// 채팅 세션 불러오기
async function loadChatSessions() {
    try {
        const response = await fetch('/get_chat_sessions/');
        if (!response.ok) throw new Error('Failed to load chat sessions');
        const data = await response.json();
        const sessionList = document.getElementById('session-list');
        sessionList.innerHTML = '';
        data.sessions.forEach(session => {
            const li = document.createElement('li');
            li.textContent = `${session.created_at} - ${session.last_message}`;
            li.dataset.sessionId = session.id;
            li.addEventListener('click', () => loadSessionMessages(session.id));
            sessionList.appendChild(li);
        });
    } catch (error) {
        console.error('Error loading chat sessions:', error);
    }
}

// 채팅 세션 메시지 불러오기
async function loadSessionMessages(sessionId) {
    try {
        const response = await fetch(`/get_session_messages/${sessionId}/`);
        if (!response.ok) throw new Error('Failed to load session messages');
        const data = await response.json();
        chatBox.innerHTML = '';
        data.messages.forEach(msg => {
            if (msg.sender === 'user') {
                addUserMessage(msg.text);
            } else {
                addBotMessage(msg.text);
            }
        });
    } catch (error) {
        console.error('Error loading session messages:', error);
    }
}

// 초기화
$(document).ready(() => {
    setupEventListeners();
    loadChatSessions(); // 채팅 세션 불러오기
});

$(document).ready(function() {
    $('#search-form').on('submit', function(event) {
        event.preventDefault(); // 기본 동작 방지

        const nickname = $('#nickname').val().trim(); // 닉네임 가져오기
        const csrfToken = $('input[name=csrfmiddlewaretoken]').val(); // CSRF 토큰 가져오기
        const url = $(this).data('url'); // 렌더링된 URL 가져오기

        if (!nickname) {
            $('#search-results').html('<p style="color: red;">Please enter a nickname.</p>');
            return;
        }

        // AJAX 요청
        $.ajax({
            type: 'POST',
            url: url, // Django 뷰 URL
            data: {
                nickname: nickname,
                csrfmiddlewaretoken: csrfToken,
            },
            success: function(response) {
                // 성공 시 결과 표시
                $('#search-results').html(` 
                    <div class="character-box">
                        <div class="character-image-container">
                            ${response.character_image 
                                ? `<img src="${response.character_image}" alt="${response.character_name}" class="character-image">`
                                : '<span class="no-image">이미지가 없습니다.</span>'}
                        </div>
                        <div class="character-details">
                            <div class="character-detail"><span class="value nickname">${response.character_name}</span></div>
                            <hr class="detail-divider">
                            <div class="character-detail"><span class="label">레벨</span><span class="value">${response.character_level}</span></div>
                            <hr class="detail-divider">
                            <div class="character-detail"><span class="label">서버</span><span class="value">${response.world_name}</span></div>
                            <hr class="detail-divider">
                            <div class="character-detail"><span class="label">직업</span><span class="value">${response.character_class}</span></div>
                            <hr class="detail-divider">
                            <div class="character-detail"><span class="label">전투력</span><span class="value">${response.Combat_Power}</span></div>
                            <hr class="detail-divider">
                        </div>
                    </div>
                `);

                // 사용자 아이콘 업데이트
                const userIcon = document.getElementById('user-icon');
                if (response.character_image) {
                    userIcon.src = response.character_image; // 검색된 캐릭터 이미지로 변경
                } else {
                    userIcon.src = '/static/image/물의정령.png'; // 기본 이미지 사용
                }
            },
            error: function(xhr) {
                if (xhr.status === 404) {
                    $('#search-results').html('<p style="color: red;">Character not found. Please try again.</p>');
                } else {
                    $('#search-results').html('<p style="color: red;">An error occurred. Please try again later.</p>');
                }
            }
        });
    });
});