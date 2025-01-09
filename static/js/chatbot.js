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
                        <!-- 왼쪽 이미지 박스 -->
                        <div class="character-image-container">
                            ${response.character_image 
                                ? `<img src="${response.character_image}" alt="${response.character_name}" class="character-image">`
                                : '<span class="no-image">이미지가 없습니다.</span>'}
                        </div>
                            
                        <!-- 오른쪽 텍스트 박스 -->
                        <div class="character-details">
                            <div class="character-detail"<span class="value nickname">${response.character_name}</span><div class="server-box"><span class="server">${response.world_name}</span></div></div>
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
            },
            error: function(xhr) {
                // 에러 처리
                if (xhr.status === 404) {
                    $('#search-results').html('<p style="color: red;">Character not found. Please try again.</p>');
                } else {
                    $('#search-results').html('<p style="color: red;">An error occurred. Please try again later.</p>');
                }
            }
        });
    });
});

document.addEventListener("DOMContentLoaded", function () {
    // 서버에서 전달된 message 값을 가져오기
    const messageInput = document.getElementById("message");
    const message = messageInput.value; // input 태그의 value에서 가져옴

    if (message) {
        // 메시지를 바로 처리 (예: 화면에 표시, 서버로 전송 등)
        processMessage(message);
    }
});

// 메시지 처리 함수
document.addEventListener("DOMContentLoaded", () => {
    // DOM 요소 가져오기
    const messageInput = document.getElementById("message");
    const sendButton = document.getElementById("send");
    const chatBox = document.getElementById("chat-box");
    const botMessageBox = document.querySelector(".bot-message .message-content"); // 봇 메시지 박스 가져오기

    // 초기 메시지 처리
    const initialMessage = messageInput.value.trim();
    if (initialMessage) {
        addUserMessage(initialMessage);
        processMessage(initialMessage);
    }

    // 전송 버튼 클릭 이벤트
    sendButton.addEventListener("click", async () => {
        const message = messageInput.value.trim();
        if (!message) {
            alert("메시지를 입력하세요!");
            return;
        }

        addUserMessage(message);
        messageInput.value = ''; // 입력 필드 초기화
        await processMessage(message);
    });

    // 사용자 메시지 추가
    function addUserMessage(message) {
        const userTemplate = document.getElementById("user-template");
        const userMessage = userTemplate.cloneNode(true);
        userMessage.style.display = "flex"; // 숨김 해제
        userMessage.querySelector(".message-content").textContent = message;
        chatBox.appendChild(userMessage);
        scrollToBottom(); // 채팅창 스크롤 유지
    }

    // 봇 메시지 내용 업데이트
    function updateBotMessage(message) {
        if (botMessageBox) {
            botMessageBox.textContent = message; // 봇 메시지 내용 업데이트
        } else {
            console.error("봇 메시지 박스가 없습니다!");
        }
    }

    // 메시지 처리 함수
    async function processMessage(message) {
        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

        try {
            const response = await fetch('/chat_with_bot/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken
                },
                body: `message=${encodeURIComponent(message)}`
            });

            if (!response.ok) {
                throw new Error(`서버 오류: ${response.statusText}`);
            }

            const data = await response.json();
            if (data.error) {
                throw new Error(data.error);
            }

            updateBotMessage(data.response); // 봇의 응답 표시 (내용만 업데이트)
        } catch (error) {
            console.error("메시지 처리 오류:", error);
            alert("메시지 처리 중 문제가 발생했습니다.");
        }
    }

    // 채팅창 스크롤 유지
    function scrollToBottom() {
        chatBox.scrollTop = chatBox.scrollHeight;
    }
});
