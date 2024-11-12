// `equipment-data` 스크립트 태그에서 JSON 데이터를 가져옴
const equipmentData = JSON.parse(document.getElementById('equipment-data').textContent);

// 툴팁 요소 선택
const tooltip = document.getElementById('tooltip');

const keyToKorean = {
    str: "STR",
    dex: "DEX",
    int: "INT",
    luk: "LUK",
    max_hp: "HP",
    max_mp: "MP",
    attack_power: "공격력",
    magic_power: "마력",
    armor: "방어력",
    speed: "이동속도",
    jump: "점프력",
    boss_damage: "보스 공격 시 데미지",
    ignore_monster_armor: "방어율 무시",
    all_stat: "올스탯",
    damage: "데미지",
    equipment_level_decrease: "착용 레벨 감소",
    max_hp_rate: "최대 HP",
    max_mp_rate: "최대 MP",
    // 필요한 다른 키들도 추가
};
const percentageKeys = [
    "boss_damage",
    "ignore_monster_armor",
    "all_stat",
    "damage",
    "equipment_level_decrease",
    "max_hp_rate",
    "max_mp_rate",
];
// 툴팁을 보여주는 함수
function showTooltip(event, slot) {
    const item = equipmentData.item_equipment[slot];

    if (item) {
        // 툴팁 내용 설정
        tooltip.innerHTML = `
            <div class='item-equipmet-container'>
                ${item.starforce >= 1 ? `
                <div class="item-starforce">
                    ⭐x${item.starforce}
                </div>` : ''}
                
                ${item.name ? `
                    <div class="item-name">${item.name}${item.scroll_upgrade >= 1 ? ` (${item.scroll_upgrade})` : ''}</div>` : ''}

                ${item.potential_option_grade ? `
                <div class="item-grade">(${item.potential_option_grade})</div>` : ''}
                
                <hr>
                <div class="item-icon">
                    <img src="${item.icon}" alt="${item.name}" />
                </div>
                <hr>
                <div class="item-slot">장비분류: ${item.en_slot}</div>
                <div class="attributes">
                ${Object.entries(item.total_option || {})
                    .filter(([key, value]) => value > 0) // 총합 값이 0보다 큰 경우만 출력
                    .map(([key, value]) => {
                        const koreanKey = keyToKorean[key] || key; // 매핑된 한글 키 또는 기본 키 사용
                    
                        // 덧셈 값 처리: 각 항목에 스타일 추가
                        const parts = [
                            { value: item.base_option[key] || 0, color: "" }, // 기본값, 색상 없음
                            { value: item.add_option[key] || 0, color: "#CCFF00" }, // add_option
                            { value: item.item_etc_option[key] || 0, color: "#AAAAFF" }, // item_etc_option
                            { value: item.item_starforce_option[key] || 0, color: "#FFCC00" }, // item_starforce_option
                        ]
                            .filter(part => part.value > 0) // 0인 값 제외
                            .map(part => `<span style="color: ${part.color}">${percentageKeys.includes(key) ? `${part.value}%` : part.value}</span>`);
                    
                        // 덧셈 항목 문자열 생성
                        const partsString = parts.length > 0 ? ` (${parts.join(" + ")})` : "";
                    
                        // 추가 옵션이 있는지 확인 (base_option 이외에 다른 값이 있는지)
                        const hasAdditionalOptions = [
                            item.add_option[key],
                            item.item_etc_option[key],
                            item.item_starforce_option[key],
                        ].some(optionValue => optionValue > 0); // 추가 옵션이 하나라도 있으면 true
                    
                        // 비율 처리
                        const valueWithUnit = percentageKeys.includes(key) ? `${value}%` : value;
                    
                        // <strong>과 총합 값 스타일 설정
                        const additionalStyle = hasAdditionalOptions ? 'style="color: #66FFFF"' : "";
                    
                        return `
                            <div>
                                <strong ${additionalStyle}>${koreanKey}</strong>: +
                                <span ${additionalStyle}>${valueWithUnit}</span>${partsString}
                            </div>
                        `;
                    }).join('')}
                </div>
                <hr>
                ${item.potential_option_grade ? `
                <p class="section-title potential-grade-${item.potential_option_grade}">잠재옵션</p>
                <div class="potential-options">
                    <p>
                        ${item.potential_options.filter(Boolean).map(option => `<div>${option}</div>`).join('')}
                    </p>
                </div>
                <hr>
                ` : ''}
                ${item.additional_potential_option_grade ? `
                <p class="section-title potential-grade-${item.additional_potential_option_grade}">에디셔널 잠재옵션</p>
                <div class="additional-potential-options">
                    <p>
                        ${item.additional_potential_options.filter(Boolean).map(option => `<div>${option}</div>`).join('')}
                    </p>
                </div>
                ` : ''}
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
document.addEventListener('DOMContentLoaded', () => {
    const tabButtons = document.querySelectorAll('.link-tab-button');
    const tabContents = document.querySelectorAll('.link-tab-content');

    // 각 버튼에 클릭 이벤트 추가
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // 모든 버튼과 탭 내용에서 'active' 클래스 제거
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // 클릭된 버튼에 'active' 클래스 추가
            button.classList.add('active');

            // 클릭된 버튼에 해당하는 탭 내용 표시
            const targetTab = button.getAttribute('data-link-tab');
            document.getElementById(targetTab).classList.add('active');
        });
    });
});

//어빌리티
document.addEventListener('DOMContentLoaded', () => {
    const tabButtons = document.querySelectorAll('.ability-tab-button');
    const tabContents = document.querySelectorAll('.ability-tab-content');

    // 각 버튼에 클릭 이벤트 추가
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // 모든 버튼과 탭 내용에서 'active' 클래스 제거
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // 클릭된 버튼에 'active' 클래스 추가
            button.classList.add('active');

            // 클릭된 버튼에 해당하는 탭 내용 표시
            const targetTab = button.getAttribute('data-ability-tab');
            document.getElementById(targetTab).classList.add('active');
        });
    });
});