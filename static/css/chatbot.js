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

// 서버에 메시지를 전송하고 응답받기
async function sendMessage() {
    const userMessage = messageInput.value.trim();
    if (!userMessage) return;

    // 사용자 메시지 추가
    addUserMessage(userMessage);
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

        // 봇 메시지 업데이트
        typeBotText(data.response);
    } catch (error) {
        console.error("메시지 전송 오류:", error);
        typeBotText("서버 오류가 발생했습니다. 다시 시도해주세요.");
    }
}

// 이벤트 리스너 설정
sendButton.addEventListener('click', sendMessage);

messageInput.addEventListener('keyup', (event) => {
    if (event.key === 'Enter') {
        sendMessage();
    }
});

// 사이드바
// function toggleSidebar() {
//   const sidebar = document.getElementById('sidebar');
//   const toggleBtn = document.getElementById('toggle-btn').querySelector('img'); // 이미지 태그 가져오기
//   const isVisible = sidebar.style.left === '0px';

//   if (isVisible) {
//     // 사이드바 닫기
//     sidebar.style.left = '-250px';
//     toggleBtn.src = 'sidebar1.png'; // 닫힌 상태의 버튼 이미지
//   } else {
//     // 사이드바 열기
//     sidebar.style.left = '0px';
//     toggleBtn.src = 'sidebar2.png'; // 열린 상태의 버튼 이미지
//   }
// }
