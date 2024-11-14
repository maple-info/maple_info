const chatBox = document.getElementById('chat-box');
const messageInput = document.getElementById('message');
const sendButton = document.getElementById('send');

// 메시지를 채팅 창에 추가하는 함수
function addMessage(text, isBot) {
    const messageElement = document.createElement('p');
    messageElement.className = isBot ? 'bot-message' : 'user-message';
    messageElement.textContent = text;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;  // 스크롤을 최하단으로 이동
}

// 글이 생성되는 것처럼 텍스트를 하나씩 표시하는 함수
function typeText(text) {
    let i = 0;
    const messageElement = document.createElement('p');
    messageElement.className = 'bot-message';
    chatBox.appendChild(messageElement);
    
    function typing() {
        if (i < text.length) {
            messageElement.textContent += text[i];
            i++;
            setTimeout(typing, 50);  // 50ms마다 한 글자씩 추가
        }
    }
    typing();
}

// 서버에 메시지를 전송하고 응답받기
async function sendMessage() {
    const userMessage = messageInput.value.trim();
    if (!userMessage) return;

    addMessage(userMessage, false);
    messageInput.value = '';

    try {
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const response = await fetch('/chat/', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken
            },
            body: new URLSearchParams({ 'message': userMessage })
        });

        if (!response.ok) throw new Error("서버 응답 오류");

        const data = await response.json();

        if (!data || !data.response) {
            throw new Error("유효하지 않은 서버 응답");
        }

        typeText(data.response);
    } catch (error) {
        console.error("메시지 전송 오류:", error);
        typeText("서버 오류가 발생했습니다. 다시 시도해주세요.");
    }
}


// 전송 버튼 클릭 이벤트
sendButton.addEventListener('click', sendMessage);

// Enter 키 입력 시 메시지 전송
messageInput.addEventListener('keyup', (event) => {
    if (event.key === 'Enter') {
        sendMessage();
    }
});