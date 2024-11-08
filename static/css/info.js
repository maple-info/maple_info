// `equipment-data` 스크립트 태그에서 JSON 데이터를 가져옴
const equipmentData = JSON.parse(document.getElementById('equipment-data').textContent);

// 툴팁 요소 선택
const tooltip = document.getElementById('tooltip');

// 툴팁을 보여주는 함수
function showTooltip(event, slot) {
    const item = equipmentData.item_equipment[slot];

    if (item) {
        // 툴팁 내용 설정
        tooltip.innerHTML = `
            <div class='item-equipmet-container'>
                <div class="item-starforce">
                ⭐x${item.starforce}
                    </div>
                <div class="item-name">${item.name} (${item.scroll_upgrade})</div>
                <div class="item-grade">(${item.potential_option_grade})</div>
                <hr>
                <div class="item-icon">
                    <img src="${item.icon}" alt="${item.name}" />
                </div>
                <hr>
                <div class="item-slot">장비분류: ${item.en_slot}</div>
                <div class="attributes">
                    <strong>STR</strong>: ${item.total_option.str} (${item.base_option.str || 0} + ${item.add_option.str || 0})<br>
                    <strong>DEX</strong>: ${item.total_option.dex} (${item.base_option.dex || 0} + ${item.add_option.dex || 0})<br>
                    <strong>INT</strong>: ${item.total_option.int} (${item.base_option.int || 0} + ${item.add_option.int || 0})<br>
                    <strong>LUK</strong>: ${item.total_option.luk} (${item.base_option.luk || 0} + ${item.add_option.luk || 0})<br>
                    <strong>HP</strong>: ${item.total_option.max_hp} (${item.base_option.max_hp || 0} + ${item.add_option.max_hp || 0})<br>
                    <strong>MP</strong>: ${item.total_option.max_mp} (${item.base_option.max_mp || 0} + ${item.add_option.max_mp || 0})<br>
                    <strong>공격력</strong>: ${item.total_option.attack_power} (${item.base_option.attack_power || 0} + ${item.add_option.attack_power || 0})<br>
                    <strong>방어력</strong>: ${item.total_option.armor} (${item.base_option.armor || 0} + ${item.add_option.armor || 0})
                </div>
                <hr>
                <p class="section-title potential-grade-${item.potential_option_grade}">잠재옵션</p>
                <div class="potential-options">
                    <p>
                        ${item.potential_options.filter(Boolean).map(option => `<div>${option}</div>`).join('')}
                    </p>
                </div>
                <hr>
                <p class="section-title potential-grade-${item.additional_potential_option_grade}">에디셔널 잠재옵션</p>
                <div class="additional-potential-options">
                    <p>
                        ${item.additional_potential_options.filter(Boolean).map(option => `<div>${option}</div>`).join('')}
                    </p>
                </div>
            </div>
        `;

        // 툴팁 위치 설정
        tooltip.style.display = 'block';
        tooltip.style.left = `${event.pageX + 10}px`;
        tooltip.style.top = `${event.pageY + 10}px`;
        
        // 마우스가 요소에서 나가면 툴팁 숨기기
        event.target.addEventListener('mouseleave', hideTooltip);
    } else {
        tooltip.innerHTML = "장비 정보 없음";
    }

}

// 툴팁을 숨기는 함수
function hideTooltip() {
    tooltip.style.display = 'none';
    tooltip.innerHTML = ""; // 내용 초기화
}

//심볼 툴팁


// symbol-item 요소에 마우스 이벤트 추가
document.querySelectorAll('.symbol-item').forEach(item => {
    item.addEventListener('mouseenter', event => {
        const symbolName = event.currentTarget.getAttribute('data-name');
        tooltip.innerHTML = symbolName; // 툴팁 내용 설정
        tooltip.style.display = 'block'; // 툴팁 표시
    });

    item.addEventListener('mousemove', event => {
        // 마우스 위치에 따라 툴팁 위치 설정
        tooltip.style.left = `${event.pageX + 10}px`;
        tooltip.style.top = `${event.pageY + 10}px`;
    });

    item.addEventListener('mouseleave', () => {
        tooltip.style.display = 'none'; // 마우스가 벗어날 때 툴팁 숨기기
    });
});


//링크
