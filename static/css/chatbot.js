const chatBox = document.getElementById('chat-box');
const messageInput = document.getElementById('message');
const sendButton = document.getElementById('send');

// 사용자와 봇 메시지 템플릿
const userTemplate = document.getElementById('user-template');
const botTemplate = document.getElementById('bot-template');

// 메시지를 채팅 창에 추가하는 함수
function addMessage(text, isBot) {
    // 템플릿 복제
    const template = isBot ? botTemplate : userTemplate;
    const messageElement = template.cloneNode(true);

    // 텍스트 업데이트
    messageElement.querySelector('.message-content').textContent = text;
    messageElement.style.display = 'flex'; // 숨겨진 템플릿을 표시

    // 채팅창에 추가
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight; // 스크롤을 최하단으로 이동
}

// 글이 생성되는 것처럼 텍스트를 하나씩 표시하는 함수
function typeText(text) {
    let i = 0;

    // 템플릿 복제
    const messageElement = botTemplate.cloneNode(true);
    const messageContent = messageElement.querySelector('.message-content');
    messageElement.style.display = 'flex';

    // 채팅창에 추가
    chatBox.appendChild(messageElement);

    function typing() {
        if (i < text.length) {
            messageContent.textContent += text[i];
            i++;
            setTimeout(typing, 50); // 50ms마다 한 글자씩 추가
        }
    }
    typing();
}

// 서버에 메시지를 전송하고 응답받기
async function sendMessage() {
    const userMessage = messageInput.value.trim();
    if (!userMessage) return;

    // 사용자 메시지 추가
    addMessage(userMessage, false);
    messageInput.value = ''; // 입력창 초기화

    try {
        // CSRF 토큰 가져오기
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

        if (!csrftoken) {
            throw new Error("CSRF 토큰을 찾을 수 없습니다.");
        }

        // 서버로 요청 전송
        const response = await fetch('/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken,
            },
            body: new URLSearchParams({ message: userMessage }),
        });

        if (!response.ok) {
            throw new Error(`서버 응답 오류: ${response.statusText}`);
        }

        const data = await response.json();

        if (!data || !data.response) {
            throw new Error("유효하지 않은 서버 응답");
        }

        // 봇의 응답을 추가
        typeText(data.response);
    } catch (error) {
        console.error("메시지 전송 오류:", error);
        typeText("서버 오류가 발생했습니다. 다시 시도해주세요.");
    }
}

// 이벤트 리스너 설정
sendButton.addEventListener('click', sendMessage);

messageInput.addEventListener('keyup', (event) => {
    if (event.key === 'Enter') {
        sendMessage();
    }
});