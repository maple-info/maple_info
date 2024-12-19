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
