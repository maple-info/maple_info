document.addEventListener('DOMContentLoaded', function() {
    const chatContainer = document.getElementById('chat-container');
    const messageInput = document.getElementById('message');
    const sendButton = document.getElementById('send');
    const characterSearchForm = document.getElementById('character-search-form');
    const characterInfoDiv = document.getElementById('character-info');

    function addMessage(text, isBot) {
        const messageElement = document.createElement('div');
        messageElement.className = isBot ? 'message bot-message' : 'message user-message';
        messageElement.textContent = text;
        chatContainer.prepend(messageElement);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function typeText(text) {
        const messageElement = document.createElement('div');
        messageElement.className = 'message bot-message';
        chatContainer.prepend(messageElement);
        
        let i = 0;
        function typing() {
            if (i < text.length) {
                messageElement.textContent += text[i];
                i++;
                chatContainer.scrollTop = chatContainer.scrollHeight;
                setTimeout(typing, 30);
            }
        }
        typing();
    }

    function showLoading() {
        const loadingElement = document.createElement('div');
        loadingElement.className = 'loading';
        loadingElement.textContent = '처리 중...';
        chatContainer.appendChild(loadingElement);
        chatContainer.scrollTop = chatContainer.scrollHeight;
        return loadingElement;
    }

    function showError(message) {
        const errorElement = document.createElement('div');
        errorElement.className = 'error';
        errorElement.textContent = message;
        chatContainer.appendChild(errorElement);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    async function sendMessage() {
        const userMessage = messageInput.value.trim();
        if (!userMessage) return;

        addMessage(userMessage, false);
        messageInput.value = '';
        sendButton.disabled = true;

        const loadingElement = showLoading();

        try {
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const response = await fetch('/chatbot/', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrftoken
                },
                body: new URLSearchParams({ 'message': userMessage })
            });

            loadingElement.remove();

            if (!response.ok) throw new Error("서버 응답 오류");

            const data = await response.json();
            if (!data || !data.response) {
                throw new Error("유효하지 않은 서버 응답");
            }

            typeText(data.response);
        } catch (error) {
            console.error("메시지 전송 오류:", error);
            showError("오류가 발생했습니다. 다시 시도해주세요.");
        } finally {
            sendButton.disabled = false;
        }
    }

    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keyup', (event) => {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });



    characterSearchForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const nickname = document.getElementById('nickname').value.trim();
        if (!nickname) {
            showError("닉네임을 입력해주세요.");
            return;
        }

        const loadingElement = showLoading();
        console.log(`Searching for nickname: ${nickname}`);

        try {
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const response = await fetch('/chatbot/search_character/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrftoken
                },
                body: 'nickname=' + encodeURIComponent(nickname)
            });

            loadingElement.remove();

            if (!response.ok) {
                throw new Error("서버 응답 오류");
            }

            const data = await response.json();
            console.log('Received data:', data);

            if (data.character_name) {
                displayCharacterInfo(data);
            } else {
                showError(data.error || "캐릭터를 찾을 수 없습니다.");
            }
        } catch (error) {
            console.error('Error:', error);
            showError("캐릭터 검색 중 오류가 발생했습니다.");
        }
    });

    function displayCharacterInfo(info) {
        console.log('Displaying character info:', info);

        if (!info.character_name || !info.character_level || !info.world_name || !info.character_class || !info.character_image) {
            showError("필수 캐릭터 정보가 누락되었습니다.");
            return;
        }
        
        characterInfoDiv.style.display = 'block';
        characterInfoDiv.innerHTML = `
            <h3>${info.character_name}</h3>
            <p>레벨: ${info.character_level}</p>
            <p>서버: ${info.world_name}</p>
            <p>직업: ${info.character_class}</p>
            <img src="${info.character_image}" alt="${info.character_name}" style="max-width: 100px; border-radius: 8px;">
        `;
    }

    // 초기 메시지 표시
    typeText("안녕하세요! 메이플스토리에 대해 무엇이든 물어보세요.");
});



async function searchCharacter(nickname) {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    try {
        const response = await fetch('/chatbot/search_character/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrftoken,
            },
            body: new URLSearchParams({ 'nickname': nickname }),
        });

        if (!response.ok) throw new Error('서버 응답 오류');

        const data = await response.json();
        if (data.character_name) {
            displayCharacterInfo(data);
        } else {
            showError(data.error || '캐릭터를 찾을 수 없습니다.');
        }
    } catch (error) {
        console.error('캐릭터 검색 오류:', error);
        showError('캐릭터 검색 중 문제가 발생했습니다.');
    }
}