document.addEventListener('DOMContentLoaded', function() {
    const messageInput = document.getElementById('message');
    const sendButton = document.getElementById('send');
    const chatWindow = document.getElementById('chat-box');
    const searchForm = document.getElementById('character-search-form');
    const nicknameInput = document.getElementById('nickname');

    sendButton.addEventListener('click', function(event) {
        event.preventDefault();
        const userMessage = messageInput.value;
        if (userMessage.trim() !== '') {
            appendMessage('You', userMessage);
            sendMessageToChatbot(userMessage);
            messageInput.value = '';
        }
    });

    searchForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const nickname = nicknameInput.value;
        if (nickname.trim() !== '') {
            searchCharacter(nickname);
            nicknameInput.value = '';
        }
    });

    function appendMessage(sender, message) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message');
        messageElement.innerHTML = `<strong>${sender}:</strong> ${message}`;
        chatWindow.appendChild(messageElement);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    function sendMessageToChatbot(message) {
        fetch('/chatbot/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();  // JSON으로 직접 파싱
        })
        .then(data => {
            console.log(data);
            appendMessage('Chatbot', data.response);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
    

    function searchCharacter(nickname) {
        fetch('/search_character/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ nickname: nickname })
        })
        .then(response => response.text())  // 응답을 텍스트로 받음
        .then(data => {
            console.log(data);  // 응답을 콘솔에 출력
            try {
                const jsonData = JSON.parse(data);  // JSON 파싱 시도
                appendMessage('Search Result', jsonData.result);
            } catch (error) {
                console.error('JSON 파싱 에러:', error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
