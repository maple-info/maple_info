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

function openPopup(url) {
    window.open(url, '구글 로그인', 'width=600,height=600');
}

function closePopupAndReload() {
    window.opener.location.reload();
    window.close();
}

document.addEventListener('DOMContentLoaded', function() {
    const toggleButton = document.querySelector('.toggle-button');

    toggleButton.addEventListener('click', function(event) {
        event.preventDefault(); // 기본 동작 방지
        this.classList.toggle('active'); // 클래스 토글
    });
});
// 챗봇 메시지 넘기기
document.addEventListener("DOMContentLoaded", function() {
    const sendButton = document.getElementById("send");
    const messageInput = document.getElementById("message");

    sendButton.addEventListener("click", function() {
        const message = messageInput.value.trim(); // 공백 제거한 메시지 저장
        if (message) {
            // message 값을 localStorage에 저장
            localStorage.setItem("message", message);
            // chatbot.html로 이동
            window.location.href = "chatbot.html"; // 실제 chatbot.html 경로 입력
        } else {
            alert("메시지를 입력하세요!"); // 빈 메시지 처리
        }
    });
});

// 이벤트 공지
let currentSlide = 0;

function moveSlide(direction) {
    const slides = document.querySelector('.slider');
    const totalSlides = document.querySelectorAll('.slider-item').length;

    // 현재 슬라이드 위치 갱신
    currentSlide += direction;

    // 마지막 슬라이드에서 첫 슬라이드로 돌아가거나 첫 슬라이드에서 마지막 슬라이드로 돌아가는 처리
    if (currentSlide < 0) {
        currentSlide = totalSlides - 1;
    } else if (currentSlide >= totalSlides) {
        currentSlide = 0;
    }

    // 슬라이드를 이동
    slides.style.transform = `translateX(-${currentSlide * 100}%)`;
}

let cashshopIndex = 0; // 현재 슬라이드 인덱스

// 캐시샵 슬라이드를 이동하는 함수
function moveCashshopSlide(direction) {
    const slides = document.querySelectorAll(".cashshop-slider .slider-item");
    const totalSlides = slides.length;

    // 현재 슬라이드 인덱스를 업데이트
    cashshopIndex += direction;

    // 슬라이드가 마지막 또는 첫 번째로 돌아가지 않도록 제한
    if (cashshopIndex < 0) {
        cashshopIndex = totalSlides - 1; // 마지막 슬라이드로 돌아가기
    } else if (cashshopIndex >= totalSlides) {
        cashshopIndex = 0; // 첫 번째 슬라이드로 돌아가기
    }

    // 슬라이드 위치를 이동 (슬라이더에 transform 적용)
    const slider = document.querySelector(".cashshop-slider");
    
    // transition을 통해 애니메이션 효과 추가
    slider.style.transition = "transform 0.5s ease-in-out";
    slider.style.transform = `translateX(-${cashshopIndex * 100}%)`; // 한 슬라이드 너비만큼 이동
}

// 페이지 로드 시 초기 슬라이드 애니메이션을 부드럽게 적용하기 위해
document.addEventListener("DOMContentLoaded", () => {
    const slider = document.querySelector(".cashshop-slider");
    slider.style.transition = "transform 0.5s ease-in-out"; // 초기 애니메이션 효과
});
