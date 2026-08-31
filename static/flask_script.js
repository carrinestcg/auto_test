/** Checkbox helper — must be module-level; toggleDepositAmount / toggleExtraPromo use it. */
const isChecked = (id) => document.getElementById(id)?.checked;

/** 前台充值是否使用充值折抵券（type=3；後台審核需 requestType=D） */
function isDiscountCouponDepositMode() {
    return isChecked("frontend-deposit-coupon");
}

/** 後台批量審核：折抵券充值帶 "D"，一般充值不帶 */
function getDepositApproveRequestType() {
    return isDiscountCouponDepositMode() ? "D" : null;
}

const DEFAULT_FORM_AMOUNT = "1";
const DEFAULT_PROMOTION_ID = "4023101";
const PLATFORM_DEFAULT_PROMOTION_ID = {
    jkscus1: "4616092",
};

function getSelectedPlatforms() {
    const select = document.getElementById("frontend-checkbox_manual_platform");
    if (!select) return ["gi8viet"];
    const platforms = Array.from(select.selectedOptions).map((opt) => opt.value);
    return platforms.length ? platforms : ["gi8viet"];
}

function getDefaultPromotionIdForPlatform(platform) {
    return PLATFORM_DEFAULT_PROMOTION_ID[platform] || DEFAULT_PROMOTION_ID;
}

function getDefaultPromotionIdForSelection() {
    const platforms = getSelectedPlatforms();
    const primary = platforms[0] || "gi8viet";
    return getDefaultPromotionIdForPlatform(primary);
}

function getKnownPromotionDefaults() {
    return new Set([DEFAULT_PROMOTION_ID, ...Object.values(PLATFORM_DEFAULT_PROMOTION_ID)]);
}

function updatePromotionIdPlaceholder(defaultId = getDefaultPromotionIdForSelection()) {
    const input = document.getElementById("promotion_id");
    if (input) {
        input.placeholder = `留空將帶入 ${defaultId}`;
    }
}

function syncPromotionIdForPlatformSelection() {
    const input = document.getElementById("promotion_id");
    if (!input) return;

    const newDefault = getDefaultPromotionIdForSelection();
    const current = input.value.trim();
    const knownDefaults = getKnownPromotionDefaults();

    if (!current || knownDefaults.has(current)) {
        input.value = newDefault;
    }
    updatePromotionIdPlaceholder(newDefault);
}

function getFormPromotionIdValue() {
    const raw = document.getElementById("promotion_id")?.value;
    const trimmed = raw == null ? "" : String(raw).trim();
    return trimmed || getDefaultPromotionIdForSelection();
}

function getFormAmountValue() {
    const raw = document.getElementById("amount")?.value;
    const trimmed = raw == null ? "" : String(raw).trim();
    return trimmed || DEFAULT_FORM_AMOUNT;
}

const TEST_SCENARIOS = [
    {
        id: "manual_create_confirm",
        title: "創建個人＋審核",
        summary: "後台 · 個人審核",
        tab: "Backend",
        scripts: ["MANUAL_CREATE_SINGLE_CONFIRM"],
        fields: { promotion_id: DEFAULT_PROMOTION_ID, amount: DEFAULT_FORM_AMOUNT },
        platforms: ["gi8viet"],
        followUp: "填玩家帳號；票券 ID 依活動需要再補。",
    },
    {
        id: "customer_info",
        title: "查詢 customer_id",
        summary: "Customer_id",
        tab: "Player Management",
        scripts: ["Customer_id"],
        platforms: ["gi8viet"],
        followUp: "填玩家帳號後執行，結果顯示在彈窗。",
    },
    {
        id: "create_member",
        title: "創建玩家",
        summary: "新建代理帳號",
        tab: "Player Management",
        scripts: ["auto_create_player"],
        platforms: ["gi8viet"],
        followUp: "填玩家帳號作為新建代理帳號。",
    },
    {
        id: "deposit_frontend_backend",
        title: "充值＋審核",
        summary: "充值 → 審核",
        tab: "TestingTooLTab",
        scripts: ["FRONTEND_DEPOSIT", "DEPOSIT_API"],
        fields: { deposit_amount: "100", password: "123qwe" },
        followUp: "先填玩家帳號；依序跑前台充值再後台批量審核。",
    },
    {
        id: "create_qa_task",
        title: "建立 QA Task",
        summary: "QA Task",
        tab: "SanityTooLTab",
        scripts: ["create_qa_task"],
        followUp: "填 TCG 單號（可多筆，逗號分隔）後執行。",
    },
    {
        id: "change_password",
        title: "變更玩家密碼",
        summary: "重設為 123qwe",
        tab: "TestingTooLTab",
        scripts: ["Change_password"],
        platforms: ["gi8viet"],
        followUp: "填玩家帳號後執行，密碼將重設為 123qwe。",
    },
];

let activeScenarioId = null;

function getCheckedScriptValues() {
    return Array.from(document.querySelectorAll('input[name="script"]:checked')).map((el) => el.value);
}

function scriptsMatchScenario(scenario, checkedScripts) {
    if (!scenario?.scripts?.length || checkedScripts.length !== scenario.scripts.length) {
        return false;
    }
    const checkedSet = new Set(checkedScripts);
    return scenario.scripts.every((script) => checkedSet.has(script));
}

function clearScenarioSelection() {
    activeScenarioId = null;
    document.querySelectorAll('input[name="script"]').forEach((checkbox) => {
        checkbox.checked = false;
    });
    document.querySelectorAll(".scenario-card").forEach((card) => {
        card.classList.remove("is-active");
    });
    const followUp = document.getElementById("scenario-followup");
    if (followUp) {
        followUp.textContent = "";
        followUp.classList.add("hidden");
    }
    toggleInput();
}

function syncScenarioPanelWithSelection() {
    const checked = getCheckedScriptValues();
    const activeScenario = TEST_SCENARIOS.find((scenario) => scenario.id === activeScenarioId);

    if (!checked.length || !activeScenario || !scriptsMatchScenario(activeScenario, checked)) {
        activeScenarioId = null;
        document.querySelectorAll(".scenario-card").forEach((card) => {
            card.classList.remove("is-active");
        });
        const followUp = document.getElementById("scenario-followup");
        if (followUp) {
            followUp.textContent = "";
            followUp.classList.add("hidden");
        }
    }
}

function activateTab(tabId) {
    const navBtn = Array.from(document.querySelectorAll(".nav-item, .tab-version-btn")).find((btn) => {
        const onclick = btn.getAttribute("onclick") || "";
        return onclick.includes(`'${tabId}'`);
    });
    switchTab({ currentTarget: navBtn || document.body }, tabId);
}

function syncPlatformChipsFromSelect() {
    const select = document.getElementById("frontend-checkbox_manual_platform");
    const picker = document.getElementById("platform-chip-picker");
    if (!select || !picker) return;

    picker.querySelectorAll(".platform-chip").forEach((chip) => {
        const value = chip.dataset.value;
        const option = Array.from(select.options).find((opt) => opt.value === value);
        const selected = !!option?.selected;
        chip.classList.toggle("is-selected", selected);
        chip.setAttribute("aria-pressed", selected ? "true" : "false");
    });
}

function initPlatformChipPicker() {
    const select = document.getElementById("frontend-checkbox_manual_platform");
    const picker = document.getElementById("platform-chip-picker");
    if (!select || !picker || picker.dataset.initialized === "true") return;

    picker.dataset.initialized = "true";
    picker.innerHTML = "";

    Array.from(select.options).forEach((option) => {
        const chip = document.createElement("button");
        chip.type = "button";
        chip.className = "platform-chip";
        chip.dataset.value = option.value;
        chip.textContent = option.textContent.trim() || option.value;
        chip.setAttribute("aria-pressed", option.selected ? "true" : "false");
        if (option.selected) {
            chip.classList.add("is-selected");
        }
        chip.addEventListener("click", () => {
            option.selected = !option.selected;
            syncPlatformChipsFromSelect();
            syncPromotionIdForPlatformSelection();
            toggleInput();
        });
        picker.appendChild(chip);
    });
}

function setPlatformSelection(platforms) {
    const select = document.getElementById("frontend-checkbox_manual_platform");
    if (!select || !platforms?.length) return;
    Array.from(select.options).forEach((option) => {
        option.selected = platforms.includes(option.value);
    });
    syncPlatformChipsFromSelect();
    syncPromotionIdForPlatformSelection();
}

function fillScenarioPastDateTime() {
    const input = document.getElementById("date_time");
    if (!input) return;
    const date = new Date();
    date.setDate(date.getDate() - 1);
    date.setHours(10, 0, 0, 0);
    const pad = (n) => String(n).padStart(2, "0");
    input.value = `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
}

function applyTestScenario(scenario) {
    if (!scenario) return;

    if (activeScenarioId === scenario.id) {
        clearScenarioSelection();
        return;
    }

    document.querySelectorAll('input[name="script"]').forEach((checkbox) => {
        checkbox.checked = false;
    });

    activateTab(scenario.tab);

    scenario.scripts.forEach((value) => {
        const checkbox = document.querySelector(`input[name="script"][value="${CSS.escape(value)}"]`);
        if (checkbox) checkbox.checked = true;
    });

    if (scenario.fields) {
        Object.entries(scenario.fields).forEach(([fieldId, value]) => {
            const input = document.getElementById(fieldId);
            if (input) input.value = value;
        });
    }

    if (scenario.fillPastDate) {
        fillScenarioPastDateTime();
    }

    setPlatformSelection(scenario.platforms);
    toggleInput();

    activeScenarioId = scenario.id;
    document.querySelectorAll(".scenario-card").forEach((card) => {
        card.classList.toggle("is-active", card.dataset.scenarioId === scenario.id);
    });

    const followUp = document.getElementById("scenario-followup");
    if (followUp) {
        followUp.textContent = scenario.followUp || "";
        followUp.classList.toggle("hidden", !scenario.followUp);
    }

    const username = document.getElementById("username");
    const usernameWrap = document.getElementById("username-input-div");
    if (username && usernameWrap && !usernameWrap.classList.contains("hidden")) {
        username.focus();
    }
}

function renderTestScenarios() {
    const root = document.getElementById("scenario-list");
    if (!root) return;

    root.innerHTML = "";
    TEST_SCENARIOS.forEach((scenario) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "scenario-card";
        button.dataset.scenarioId = scenario.id;
        button.innerHTML = `
            <span class="scenario-card-title">${scenario.title}</span>
            <span class="scenario-card-summary">${scenario.summary}</span>
        `;
        button.addEventListener("click", () => applyTestScenario(scenario));
        root.appendChild(button);
    });
}

function initScenarioPanel() {
    renderTestScenarios();
}

function askConfirm(message, options = {}) {
    return new Promise((resolve) => {
        const modal = document.getElementById("confirm-modal");
        const messageEl = document.getElementById("confirm-modal-message");
        const titleEl = document.getElementById("confirm-modal-title");
        const yesBtn = document.getElementById("confirm-yes-btn");
        const noBtn = document.getElementById("confirm-no-btn");
        if (!modal || !yesBtn || !noBtn) {
            resolve(false);
            return;
        }

        if (titleEl) {
            titleEl.textContent = options.title || "審核確認";
        }
        if (messageEl) {
            messageEl.textContent = message;
        }

        modal.classList.remove("hidden");
        modal.classList.remove("is-visible");
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                modal.classList.add("is-visible");
            });
        });

        const cleanup = (result) => {
            modal.classList.remove("is-visible");
            window.setTimeout(() => {
                modal.classList.add("hidden");
            }, 180);
            yesBtn.removeEventListener("click", onYes);
            noBtn.removeEventListener("click", onNo);
            resolve(result);
        };
        const onYes = () => cleanup(true);
        const onNo = () => cleanup(false);

        yesBtn.addEventListener("click", onYes);
        noBtn.addEventListener("click", onNo);
    });
}

function askSign(message, options = {}) {
    return new Promise((resolve) => {
        const modal = document.getElementById("sign-modal");
        const messageEl = document.getElementById("sign-modal-message");
        const titleEl = document.getElementById("sign-modal-title");
        const yesBtn = document.getElementById("sign-yes-btn");
        const noBtn = document.getElementById("sign-no-btn");
        const closeBtn = document.getElementById("sign-close-btn");
        if (!modal || !yesBtn || !noBtn) {
            resolve(null);
            return;
        }

        if (titleEl) {
            titleEl.textContent = options.title || "報名類型";
        }
        if (messageEl) {
            messageEl.textContent = message;
        }

        modal.classList.remove("hidden");
        modal.classList.remove("is-visible");
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                modal.classList.add("is-visible");
            });
        });

        const cleanup = (result) => {
            modal.classList.remove("is-visible");
            window.setTimeout(() => {
                modal.classList.add("hidden");
            }, 180);
            yesBtn.removeEventListener("click", onYes);
            noBtn.removeEventListener("click", onNo);
            closeBtn?.removeEventListener("click", onClose);
            resolve(result);
        };
        const onYes = () => cleanup(true);
        const onNo = () => cleanup(false);
        const onClose = () => cleanup(null);

        yesBtn.addEventListener("click", onYes);
        noBtn.addEventListener("click", onNo);
        closeBtn?.addEventListener("click", onClose);
    });
}

const PLAYER_INFO_GROUPS = [
    {
        title: "基本資訊",
        modifier: "basic",
        items: [
            { value: 1, label: "手機號碼", icon: "mobile" },
            { value: 2, label: "身分證", icon: "id" },
            { value: 3, label: "玩家名稱", icon: "user" },
            { value: 14, label: "上級代理", icon: "upline" },
            { value: 7, label: "地址", icon: "address" },
            { value: 11, label: "虛擬錢包", icon: "wallet" },
        ],
    },
    {
        title: "社群／通訊帳號",
        modifier: "social",
        items: [
            { value: 4, label: "WeChat", icon: "wechat" },
            { value: 5, label: "Line ID", icon: "line" },
            { value: 6, label: "Apple ID", icon: "apple" },
            { value: 8, label: "Twitter", icon: "twitter" },
            { value: 9, label: "Viber", icon: "viber" },
            { value: 10, label: "Telegram", icon: "telegram" },
            { value: 12, label: "WhatsAppId", icon: "whatsapp" },
            { value: 13, label: "Facebook ID", icon: "user" },
            { value: 15, label: "Zalo ID", icon: "zalo" },
        ],
    },
];

const PLAYER_INFO_TYPES = PLAYER_INFO_GROUPS.flatMap((group) => group.items);

const PLAYER_INFO_VALUE_FIELDS = {
    1: ["mobileNumber", "手機號碼"],
    2: ["IDNumber", "身分證號"],
    3: ["name", "玩家名稱"],
    4: ["wechatNumber", "WeChat"],
    5: ["lineNumber", "Line ID"],
    6: ["appleIDNumber", "Apple ID"],
    7: ["address", "地址"],
    8: ["twitterID", "Twitter"],
    9: ["viberID", "Viber"],
    10: ["telegramID", "Telegram"],
    11: ["virtualWalletID", "虛擬錢包"],
    12: ["whatsappID", "WhatsAppId"],
    13: ["facebookID", "Facebook ID"],
    14: ["upline", "Upline"],
    15: ["zaloID", "Zalo ID"]
};

const PLAYER_INFO_CHECK_SVG =
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><polyline points="20 6 9 17 4 12"/></svg>';

function getPlayerInfoIcon(iconName) {
    const icons = {
        mobile:
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" aria-hidden="true"><rect x="7" y="2" width="10" height="20" rx="2"/><line x1="12" y1="18" x2="12" y2="18.01"/></svg>',
        id: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="9" cy="11" r="2"/><path d="M15 9h2M15 13h2"/></svg>',
        user: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" aria-hidden="true"><circle cx="12" cy="8" r="3"/><path d="M6 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/></svg>',
        address:
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" aria-hidden="true"><path d="M12 21s7-4.5 7-11a7 7 0 1 0-14 0c0 6.5 7 11 7 11z"/><circle cx="12" cy="10" r="2.5"/></svg>',
        wechat:
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" aria-hidden="true"><path d="M21 11.5a8.4 8.4 0 0 0-3.5-6.9A8.6 8.6 0 0 0 12 3C7 3 3 6.6 3 11c0 2.4 1.1 4.5 2.9 6L5 21l4.2-1.2A10.8 10.8 0 0 0 12 19c5 0 9-3.6 9-7.5z"/></svg>',
        line: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" aria-hidden="true"><path d="M4 6h16M4 12h10M4 18h14"/></svg>',
        apple:
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" aria-hidden="true"><path d="M16 8c.7-1.2 2-2 3.5-2.1C19 8.2 18 11 16.4 12.4 15 13.6 13.5 13.5 12.8 12.2 12.1 10.9 13 9.2 14.4 8 15.2 7.3 15.7 6.5 16 5.6 16 4.5 15.2 3.2 13.8 2.5 12 2.5S8.8 3.2 8 4.5c-.3 1.1-.1 2.2.4 3.1C7 9.2 6.1 10.9 6.8 12.2 7.5 13.5 9 13.6 10.4 12.4 12 11 13 8.2 12.5 5.9 14 6 15.3 7 16 8 16z"/><path d="M12 14.5v7"/></svg>',
        twitter:
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" aria-hidden="true"><path d="M22 4s-.7 2.1-2 3.2c1.6 10-9.4 17.3-18 11.1 2.2.1 4.4-.6 6-2C3 15.5.5 9.6 3 5c2.2 2.6 5.6 4.1 9 4-.9-4 4-6.6 7-3.8 1.1 0 3-1.2 3-1.2z"/></svg>',
        viber:
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.3 1.8.5 2.6a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.5-1.5a2 2 0 0 1 2.1-.5c.8.2 1.7.4 2.6.5A2 2 0 0 1 22 16.9z"/></svg>',
        telegram:
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" aria-hidden="true"><path d="M22 2 11 13"/><path d="M22 2 15 22 11 13 2 9l20-7z"/></svg>',
        whatsapp:
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" aria-hidden="true"><path d="M22 4s-.7 2.1-2 3.2c1.6 10-9.4 17.3-18 11.1 2.2.1 4.4-.6 6-2C3 15.5.5 9.6 3 5c2.2 2.6 5.6 4.1 9 4-.9-4 4-6.6 7-3.8 1.1 0 3-1.2 3-1.2z"/></svg>',
        wallet:
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M8 12h8M12 8v8"/></svg>',
        facebook:
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" aria-hidden="true"><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v10h3V14h3l1-4h-4z"/></svg>',
        zalo:
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" aria-hidden="true"><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2zm0 18c-4.4 0-8-3.6-8-8s3.6-8 8-8c4.4 0 8 3.6 8 8s-3.6 8-8 8z"/><path d="M15.5 9h-7v6h7v-6z"/></svg>',
        upline:
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" aria-hidden="true"><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2zm0 18c-4.4 0-8-3.6-8-8s3.6-8 8-8c4.4 0 8 3.6 8 8s-3.6 8-8 8z"/><path d="M12 7v5l4.3 2.6"/></svg>'
    };
    return icons[iconName] || icons.user;
}

function renderPlayerInfoChoiceCard(item, isSelected) {
    return `
        <button
            type="button"
            class="player-info-card${isSelected ? " is-selected" : ""}"
            data-value="${item.value}"
            role="option"
            aria-selected="${isSelected ? "true" : "false"}"
        >
            <span class="player-info-card-check" aria-hidden="true">${PLAYER_INFO_CHECK_SVG}</span>
            <span class="player-info-card-icon">${getPlayerInfoIcon(item.icon)}</span>
            <span class="player-info-card-label">${escapeHtml(item.label)}</span>
        </button>`;
}

function renderPlayerInfoChoiceGroups(selectedValues = []) {
    const selectedSet = new Set(selectedValues);
    return PLAYER_INFO_GROUPS.map(
        (group) => `
        <section class="player-info-group player-info-group--${group.modifier}">
            <h3 class="player-info-group-title">${escapeHtml(group.title)}</h3>
            <div class="player-info-group-grid">
                ${group.items
                    .map((item) => renderPlayerInfoChoiceCard(item, selectedSet.has(item.value)))
                    .join("")}
            </div>
        </section>`
    ).join("");
}

function updatePlayerInfoSelectionUI(root, statusEl, applyBtn, selectedValues) {
    const selectedSet = new Set(selectedValues);
    root.querySelectorAll(".player-info-card").forEach((card) => {
        const value = Number(card.dataset.value);
        const isSelected = selectedSet.has(value);
        card.classList.toggle("is-selected", isSelected);
        card.setAttribute("aria-selected", isSelected ? "true" : "false");
    });
    const count = selectedSet.size;
    if (statusEl) {
        statusEl.textContent = `已選擇 ${count} 項`;
    }
    if (applyBtn) {
        applyBtn.disabled = count === 0;
    }
}

function askPlayerInfoType(defaultTypes = []) {
    return new Promise((resolve) => {
        const modal = document.getElementById("player-info-modal");
        const root = document.getElementById("player-info-choice-root");
        const cancelBtn = document.getElementById("player-info-cancel-btn");
        const applyBtn = document.getElementById("player-info-apply-btn");
        const statusEl = document.getElementById("player-info-selection-status");
        if (!modal || !root || !cancelBtn || !applyBtn) {
            resolve(Array.isArray(defaultTypes) ? defaultTypes : []);
            return;
        }

        let selectedValues = Array.isArray(defaultTypes) ? [...defaultTypes] : [];

        root.innerHTML = renderPlayerInfoChoiceGroups(selectedValues);
        updatePlayerInfoSelectionUI(root, statusEl, applyBtn, selectedValues);

        modal.classList.remove("hidden");
        modal.classList.remove("is-visible");
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                modal.classList.add("is-visible");
            });
        });

        const cleanup = (result) => {
            modal.classList.remove("is-visible");
            window.setTimeout(() => {
                modal.classList.add("hidden");
            }, 180);
            root.removeEventListener("click", onCardClick);
            cancelBtn.removeEventListener("click", onCancel);
            applyBtn.removeEventListener("click", onApply);
            resolve(result);
        };

        const onCardClick = (event) => {
            const card = event.target.closest(".player-info-card");
            if (!card || !root.contains(card)) return;
            const value = Number(card.dataset.value);
            if (!Number.isFinite(value)) return;
            if (selectedValues.includes(value)) {
                selectedValues = selectedValues.filter((item) => item !== value);
            } else {
                selectedValues = [...selectedValues, value];
            }
            updatePlayerInfoSelectionUI(root, statusEl, applyBtn, selectedValues);
        };

        const onApply = () => {
            if (selectedValues.length === 0) return;
            cleanup([...selectedValues].sort((a, b) => a - b));
        };

        const onCancel = () => cleanup(null);

        root.addEventListener("click", onCardClick);
        cancelBtn.addEventListener("click", onCancel);
        applyBtn.addEventListener("click", onApply);
    });
}

function toggleInput() {
    toggleAmount();
    toggleTicket();
    togglePromotion();
    togglePromotionTypeList();
    togglePlatform();
    toggleRoundID();
    toggleDepositAmount();
    toggleDepositCouponFields();
    toggleExtraPromo();
    toggleDateTime();
    toggleUsernamePassword();
    updateRunButtonState();
    toggleSecondUsername();
    toggleQATaskInput();
    toggleWorkdaysInput();
    syncScenarioPanelWithSelection();
}
/** 需要 username 的腳本清單（這些被勾選時一定要顯示 username/password） */
const SCRIPTS_NEED_USERNAME = [
    "auto_create_player",       // frontend-checkbox_new
    "LOTTERY_BET",              // frontend-checkbox_lott
    "FRONTEND_DEPOSIT",         // frontend-checkbox
    "FIXED_DEPOSIT",            // frontend-fix_deposit
    "Customer_id",              // frontend-checkbox_id
    "MANUAL_CREATE_SINGLE_CONFIRM", // frontend-checkbox_manual
    "SIGLE_PROMO_7_TICKET",     // frontend-checkbox_7_Ticket
    "PLAYER_RANK",              // frontend-player-rank
    "PROMOCODE_BATCH",          // frontend-promo-batch
    "BONUS_BATCH",              // frontend-bonus-batch
    "TICKET_BATCH",             // frontend-ticket-batch
    "create_member_player",     // frontend-checkbox_member
    "Extra_Reward_api",
    "LOTTERY_BET",
    "Codition_create_bonus",
    "QUEST_bonus",
    "Achievement_bonus",
    "Activity_bonus",
    "MANUAL_SIGN",
    "ALL_deposit_promotion",
    "SameTimeLogin",
    "APP_Download",
    "PostCard_api",
    "Change_password",
    "Customer_name",
    "Input_User_Info",
    "auto_create_ticket",
    "Single_Manual_create",
    "test_Extra_bonus",
    "MANUAL_SINGLE",
    "MANUAL_BATCH",
    "SameTime_ReceiveTicket"
];

/** 勾選這些腳本（且無其他需要 username 的腳本）時，隱藏 username / password */
const SCRIPTS_HIDE_USERNAME = [
    "Create_all_promotion",
    "Compensation_api",
    "Schedule_manual_bonus",
    "DEPOSIT_API",
    "create_qa_task",
    "calculate_workdays",
];
/** 勾選「創建活動」時顯示活動類型多選（#promotion-checkbox_select） */
function togglePromotionTypeList() {
    const wrap = document.getElementById("promotion-type-select-wrap");
    const promoSelect = document.getElementById("promotion-checkbox_select");
    const need = isChecked("Create_all_promotion");
    if (!promoSelect) return;
    if (wrap) {
        wrap.classList.toggle("hidden", !need);
    }
    promoSelect.classList.toggle("hidden", !need);
}
function toggleDepositAmount(){
    const extra_depositAmountDiv = document.getElementById("extra-deposit-amount-input-div");
    const requestDepositInput = isChecked("Extra_Reward_api");
    if (!extra_depositAmountDiv) return;
    extra_depositAmountDiv.classList.toggle("hidden", !requestDepositInput);
}
function toggleSecondUsername(){
    const extra_UserName = document.getElementById("username2-input-div");
    const requestSecondUserName = isChecked("SameTime_ReceiveTicket");
    if (!extra_UserName) return;
    extra_UserName.classList.toggle("hidden", !requestSecondUserName);
}

function toggleExtraPromo(){
    const extraPromoWrap = document.getElementById("extra_reward_promo_id-input-div");
    const requestExtraPromo = isChecked("Extra_Reward_api");
    if (!extraPromoWrap) return;
    extraPromoWrap.classList.toggle("hidden", !requestExtraPromo);
}

function toggleQATaskInput() {
    const div = document.getElementById("qa-task-input-div");
    if (!div) return;
    div.classList.toggle("hidden", !isChecked("create_qa_task"));
}

function toggleWorkdaysInput() {
    const div = document.getElementById("workdays-input-div");
    if (!div) return;
    div.classList.toggle("hidden", !isChecked("calculate_workdays"));
}

function formatWorkdaysIsoDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
}

function getWorkdaysPresetRange(preset) {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const end = formatWorkdaysIsoDate(today);

    if (preset === "today") {
        return { from: end, to: end };
    }

    const start = new Date(today);
    const dayOffsets = { "7d": 6, "30d": 29, "90d": 89 };
    const offset = dayOffsets[preset];
    if (offset == null) {
        return { from: "", to: "" };
    }
    start.setDate(start.getDate() - offset);
    return { from: formatWorkdaysIsoDate(start), to: end };
}

function getWorkdaysDraftDates() {
    return {
        from: document.getElementById("qa_stats_date_from_draft")?.value || "",
        to: document.getElementById("qa_stats_date_to_draft")?.value || "",
    };
}

function getWorkdaysAppliedDates() {
    return {
        from: document.getElementById("qa_stats_date_from")?.value || "",
        to: document.getElementById("qa_stats_date_to")?.value || "",
    };
}

function getWorkdaysEffectiveDates({ autoApply = false } = {}) {
    const draft = getWorkdaysDraftDates();
    const applied = getWorkdaysAppliedDates();
    const draftChanged =
        draft.from !== applied.from || draft.to !== applied.to;

    if ((draft.from || draft.to) && draftChanged) {
        if (autoApply) {
            if (!validateWorkdaysDateRange(draft.from, draft.to)) {
                return { from: "", to: "" };
            }
            applyWorkdaysDateRange({ silent: true });
            return getWorkdaysAppliedDates();
        }
        return draft;
    }

    return applied;
}

function setWorkdaysDraftDates(from, to) {
    const fromEl = document.getElementById("qa_stats_date_from_draft");
    const toEl = document.getElementById("qa_stats_date_to_draft");
    if (fromEl) fromEl.value = from || "";
    if (toEl) toEl.value = to || "";
}

function setWorkdaysAppliedDates(from, to) {
    const fromEl = document.getElementById("qa_stats_date_from");
    const toEl = document.getElementById("qa_stats_date_to");
    if (fromEl) fromEl.value = from || "";
    if (toEl) toEl.value = to || "";
}

function clearWorkdaysPresetActive() {
    document.querySelectorAll(".workdays-date-preset").forEach((btn) => {
        btn.classList.remove("is-active");
    });
}

function syncWorkdaysPresetHighlight() {
    const draft = getWorkdaysDraftDates();
    clearWorkdaysPresetActive();
    if (!draft.from && !draft.to) return;

    document.querySelectorAll(".workdays-date-preset").forEach((btn) => {
        const preset = btn.dataset.preset;
        const range = getWorkdaysPresetRange(preset);
        if (range.from === draft.from && range.to === draft.to) {
            btn.classList.add("is-active");
        }
    });
}

function updateWorkdaysAppliedHint() {
    const hint = document.getElementById("workdays-date-applied-hint");
    if (!hint) return;

    const applied = getWorkdaysAppliedDates();
    if (!applied.from && !applied.to) {
        hint.textContent = "";
        hint.classList.add("hidden");
        return;
    }

    hint.textContent = `已套用：${formatWorkdaysDateRange(applied.from, applied.to)}`;
    hint.classList.remove("hidden");
}

function validateWorkdaysDateRange(from, to) {
    if (from && to && from > to) {
        alert("開始日期不能晚於結束日期");
        return false;
    }
    return true;
}

function applyWorkdaysDateRange({ silent = false } = {}) {
    const draft = getWorkdaysDraftDates();
    if (!validateWorkdaysDateRange(draft.from, draft.to)) {
        return false;
    }

    setWorkdaysAppliedDates(draft.from, draft.to);
    updateWorkdaysAppliedHint();
    syncWorkdaysPresetHighlight();

    if (!silent) {
        const panel = document.getElementById("workdays-date-panel");
        panel?.classList.add("is-applied");
        window.setTimeout(() => panel?.classList.remove("is-applied"), 220);
    }
    return true;
}

function clearWorkdaysDateRange() {
    setWorkdaysDraftDates("", "");
    setWorkdaysAppliedDates("", "");
    clearWorkdaysPresetActive();
    updateWorkdaysAppliedHint();
}

function initWorkdaysDatePicker() {
    const panel = document.getElementById("workdays-date-panel");
    if (!panel) return;

    panel.querySelectorAll(".workdays-date-preset").forEach((btn) => {
        btn.addEventListener("click", () => {
            const range = getWorkdaysPresetRange(btn.dataset.preset);
            setWorkdaysDraftDates(range.from, range.to);
            clearWorkdaysPresetActive();
            btn.classList.add("is-active");
        });
    });

    ["qa_stats_date_from_draft", "qa_stats_date_to_draft"].forEach((id) => {
        const input = document.getElementById(id);
        input?.addEventListener("change", syncWorkdaysPresetHighlight);
        input?.addEventListener("input", syncWorkdaysPresetHighlight);
    });

    document.getElementById("workdays-date-clear-btn")?.addEventListener("click", clearWorkdaysDateRange);
    document.getElementById("workdays-date-apply-btn")?.addEventListener("click", () => {
        applyWorkdaysDateRange();
    });
}

function toggleAmount(){
    const amountInputDiv = document.getElementById("amount-input-div");
    const depositAmountDiv = document.getElementById("deposit-amount-input-div");
    const requireAmount =
        isChecked("frontend-checkbox_lott") ||
        isChecked("frontend-checkbox_manual") ||
        isChecked("frontend-checkbox_member") ||
        isChecked("Extra_Reward_api") ||
        isChecked("frontend-fix_deposit");
    const requireDepositAmount = isChecked("frontend-checkbox")||isChecked("backend-checkbox");

    if (amountInputDiv) {
        amountInputDiv.classList.toggle("hidden", !requireAmount);
    }
    if (depositAmountDiv) {
        depositAmountDiv.classList.toggle("hidden", !requireDepositAmount);
    }
}

function toggleDepositCouponFields() {
    const couponWrap = document.getElementById("deposit-coupon-wrap");
    const discountDiv = document.getElementById("discount-amount-input-div");
    const showCouponOption =
        isChecked("frontend-checkbox") || isChecked("DEPOSIT_API_script");
    const couponOn = isDiscountCouponDepositMode();

    if (couponWrap) couponWrap.classList.toggle("hidden", !showCouponOption);
    if (discountDiv) discountDiv.classList.toggle("hidden", !couponOn);
}

function toggleTicket() {
    const ticket_select = document.getElementById("frontend-checkbox_select");
    const ticket_input = document.getElementById("ticket-input-div");
    const ticket_wrap = document.getElementById("ticket-select-wrap");
    const ticket_id_input = document.getElementById("ticket_id-input-div");
    const manual_cb = document.getElementById("frontend-checkbox_manual");
    const checkbox = document.getElementById("frontend-checkbox_ticket");
    const requireTicket_input =
        (manual_cb && manual_cb.checked) ||
        isChecked("Extra_Reward_api") ||
        isChecked("Codition_create_bonus") ||
        isDiscountCouponDepositMode();
    const hasSelectTicket = ticket_select && Array.from(ticket_select.selectedOptions).length > 0;
    const showTicketSelect = !!(checkbox && checkbox.checked);

    if (ticket_wrap) ticket_wrap.classList.toggle("hidden", !showTicketSelect);
    if (ticket_select) ticket_select.classList.toggle("hidden", !showTicketSelect);
    if (ticket_input) ticket_input.classList.toggle("hidden", !(showTicketSelect && hasSelectTicket));
    if (ticket_id_input) ticket_id_input.classList.toggle("hidden", !requireTicket_input);
}
function togglePromotion() {
    const promotion_id_Input = document.getElementById("promotion_id-input-div");
    const requirePromotion_id = document.getElementById("frontend-checkbox_manual").checked ||document.getElementById('frontend-checkbox_7_Ticket').checked||document.getElementById('Extra_Reward_api').checked||document.getElementById('Achievement_bonus').checked||document.getElementById('MANUAL_SIGN').checked||document.getElementById('QUEST_bonus').checked||document.getElementById('Activity_bonus').checked||document.getElementById('Schedule_manual_bonus').checked || isDiscountCouponDepositMode();
    
    promotion_id_Input.classList.toggle("hidden", !requirePromotion_id);

}
function toggleRoundID(){
    const Compensation=document.getElementById("Compensation_api");
    const RoundID_input=document.getElementById("round_id-input-div");
    if (!Compensation || !RoundID_input) return;
    RoundID_input.classList.toggle("hidden", !Compensation.checked);
}
function toggleDateTime(){
    const Schedule_manual_bonus=document.getElementById("Schedule_manual_bonus");
    const DateTime_input=document.getElementById("date-input-div");
    if (!Schedule_manual_bonus || !DateTime_input) return;
    DateTime_input.classList.toggle("hidden", !Schedule_manual_bonus.checked);
}
/** 任一測試腳本被勾選時顯示平台（API 皆會帶 platforms；未選時後端預設 gi8viet）。 */
function togglePlatform() {
    const manual_platform_select = document.getElementById("platform-select-wrap");
    const select = document.getElementById("frontend-checkbox_manual_platform");
    if (!manual_platform_select || !select) return;

    const checkedScripts = Array.from(document.querySelectorAll('input[name="script"]:checked')).map(el => el.value);
    const excludePlatform = ["FRONTEND_DEPOSIT", "extra_promo_id", "Compensation_api", "frontend-checkbox_lott","create_member_player", "FIXED_DEPOSIT","Schedule_manual_bonus","create_qa_task","calculate_workdays","SameTime_ReceiveTicket"];  /*不需要選平台*/
    
    const needPlatform = checkedScripts.some(s => !excludePlatform.includes(s));
    manual_platform_select.classList.toggle("hidden", !needPlatform);
}
const amountInput = document.getElementById("amount");
if (amountInput){
    amountInput.addEventListener("input",()=>{
        if (amountInput.value.trim()!==""){
        document.getElementById("amount_hint").style.display = "none";
    }});
}
const depositAmountInput = document.getElementById("deposit_amount");
if (depositAmountInput) {
    depositAmountInput.addEventListener("input", () => {
        if (depositAmountInput.value.trim() !== "") {
            const hint = document.getElementById("deposit_amount_hint");
            if (hint) hint.style.display = "none";
        }
    });
}
function toggleUsernamePassword() {
    const userDiv = document.getElementById("username-input-div");
    const pwdWrap = document.getElementById("password-input-div");
    const userColumn = userDiv?.closest(".account-column");
    if (!userDiv || !pwdWrap) return;

    const checkedScripts = Array.from(
        document.querySelectorAll('input[name="script"]:checked')
    ).map(el => el.value);

    const anyNeedUsername = checkedScripts.some(s => SCRIPTS_NEED_USERNAME.includes(s));
    const shouldHide = !anyNeedUsername && checkedScripts.some(s => SCRIPTS_HIDE_USERNAME.includes(s));

    userDiv.classList.toggle("hidden", shouldHide);
    // pwdWrap.classList.toggle("hidden", shouldHide);  ← 刪掉這行，密碼欄位交給 HTML 上的 hidden 永久控制
    if (userColumn) {
        userColumn.classList.toggle("hidden", shouldHide);
    }

    updateRunButtonState();
}

let activeRunRequests = 0;

function isUsernameFieldRequired() {
    const userDiv = document.getElementById("username-input-div");
    if (!userDiv || userDiv.classList.contains("hidden")) return false;
    const userColumn = userDiv.closest(".account-column");
    if (userColumn?.classList.contains("hidden")) return false;
    return getCheckedScriptValues().some((s) => SCRIPTS_NEED_USERNAME.includes(s));
}

function getRunBlockReason() {
    const checked = getCheckedScriptValues();
    if (checked.length === 0) {
        return "請先勾選至少一項測試腳本";
    }
    if (isUsernameFieldRequired()) {
        const username = document.getElementById("username")?.value.trim();
        if (!username) {
            return "請填寫玩家帳號後再執行測試";
        }
    }
    if (isChecked("create_qa_task")) {
        const qaDiv = document.getElementById("qa-task-input-div");
        if (qaDiv && !qaDiv.classList.contains("hidden")) {
            const tcg = document.getElementById("tcg_keys_input")?.value.trim();
            if (!tcg) {
                return "請填寫 TCG 單號";
            }
        }
    }
    return null;
}

function updateRunButtonState() {
    const btn = document.getElementById("run-test-btn");
    const hint = document.getElementById("run-test-hint");
    if (!btn || btn.classList.contains("is-loading")) return;

    const reason = getRunBlockReason();
    const blocked = !!reason;
    btn.disabled = blocked;
    btn.dataset.blocked = blocked ? "true" : "false";
    if (hint) {
        hint.textContent = reason || "";
    }
}

function setRunButtonLoading(loading) {
    const btn = document.getElementById("run-test-btn");
    if (!btn) return;
    btn.classList.toggle("is-loading", loading);
    btn.setAttribute("aria-busy", loading ? "true" : "false");
    if (loading) {
        btn.disabled = true;
    } else {
        updateRunButtonState();
    }
}

function trackRunRequestStart() {
    activeRunRequests += 1;
    if (activeRunRequests === 1) {
        setRunButtonLoading(true);
        showLoading(true);
    }
}

function trackRunRequestEnd() {
    activeRunRequests = Math.max(0, activeRunRequests - 1);
    if (activeRunRequests === 0) {
        setRunButtonLoading(false);
        showLoading(false);
    }
}

function validateFormBeforeSubmit() {
    const pwd = document.getElementById("password");
    const usernameInputDiv = document.getElementById("username");
    const needUsername = isUsernameFieldRequired();
        const amountDiv = document.getElementById("amount-input-div");
        const needAmount = amountDiv && !amountDiv.classList.contains("hidden");
        const depositAmountDiv = document.getElementById("deposit-amount-input-div");
        const needDepositAmount = depositAmountDiv && !depositAmountDiv.classList.contains("hidden");
        const qaTaskDiv = document.getElementById("qa-task-input-div");
        const needQATaskInput = qaTaskDiv && !qaTaskDiv.classList.contains("hidden");
        
    if (needAmount) {
        document.getElementById("amount_hint").style.display = "none";
    }

    if (needDepositAmount && (!depositAmountInput || depositAmountInput.value.trim() === "")) {
        const depositHint = document.getElementById("deposit_amount_hint");
        if (depositHint) depositHint.style.display = "inline";
        return false;
    } else {
        const depositHint = document.getElementById("deposit_amount_hint");
        if (depositHint) depositHint.style.display = "none";
    }

    if (isDiscountCouponDepositMode() && isChecked("frontend-checkbox")) {
        const ticketIdEl = document.getElementById("ticket_id");
        if (!ticketIdEl || !ticketIdEl.value.trim()) {
            alert("使用充值折抵券時請填寫票券 ID（ticket_id）");
            return false;
        }
    }

    
    if (needUsername && !usernameInputDiv.value.trim()) {
        document.getElementById("username_hint").style.display = "inline";
        document.getElementById("password_hint").style.display = "inline";
        updateRunButtonState();
        return false;
    } else {
        document.getElementById("username_hint").style.display = "none";
    };

    if (!pwd.value.trim()) {
        pwd.value = "123qwe";
    }

    if (isChecked("Create_all_promotion")) {
        const promoSel = document.getElementById("promotion-checkbox_select");
        if (promoSel && Array.from(promoSel.selectedOptions).length === 0) {
            alert("請至少選擇一種活動類型（活動類型複選）");
            return false;
        }
    }

    if (isChecked("Codition_create_bonus")) {
        const tid = document.getElementById("ticket_id");
        if (!tid || !tid.value.trim()) {
            alert("條件派發請填寫票券 ID（ticket_id）");
            return false;
        }
    }

    if (isChecked("Schedule_manual_bonus")) {
        const dateEl = document.getElementById("date_time");
        if (!dateEl || !dateEl.value.trim()) {
            alert("請填寫日期時間（格式: 2026-06-22，需為過去時間）");
            return false;
        }
    }

    if (needQATaskInput) {
        const tcgKeysInput = document.getElementById("tcg_keys_input");
        if (!tcgKeysInput || !tcgKeysInput.value.trim()) {
            alert("請填寫 TCG 單號（可多個，用逗號或空格分隔）");
            return false;
        }
    }

    if (isChecked("calculate_workdays")) {
        const effective = getWorkdaysEffectiveDates({ autoApply: true });
        if (!validateWorkdaysDateRange(effective.from, effective.to)) {
            return false;
        }
    }

    return true;
}

const MULTI_SELECT_IDS = [
    "frontend-checkbox_select",
    "frontend-checkbox_select_platform",
    "frontend-checkbox_7_Ticket_select",
    "promotion-checkbox_select",
];

function restoreMultiSelectScroll(selectEl, scrollTop) {
    if (!selectEl) return;
    const apply = () => {
        selectEl.scrollTop = scrollTop;
    };
    apply();
    requestAnimationFrame(() => {
        apply();
        requestAnimationFrame(apply);
    });
}

function handleMultiSelectChange(selectEl) {
    const scrollTop = selectEl.scrollTop;

    if (!selectEl.options) {
        toggleInput();
        restoreMultiSelectScroll(selectEl, scrollTop);
        return;
    }

    const alloption = selectEl.querySelector('option[value="ALL"]');
    const otheroption = Array.from(selectEl.options).filter((option) => option.value !== "ALL");
    const anyOtherSelected = otheroption.some((o) => o.selected);

    // 「全部」與「只選部分類型」不可同時為 true；否則會誤觸發「全選其餘」分支（例如 HTML 曾預設 ALL selected）
    if (alloption && alloption.selected && anyOtherSelected) {
        alloption.selected = false;
    }

    if (alloption && alloption.selected) {
        otheroption.forEach((option) => {
            option.selected = true;
        });
        alloption.selected = false;
    }

    toggleInput();
    restoreMultiSelectScroll(selectEl, scrollTop);
}

MULTI_SELECT_IDS.forEach((id) => {
    const el = document.getElementById(id);
    if (!el) return;

    el.addEventListener("change", function onMultiSelectChange() {
        handleMultiSelectChange(this);
    });

    // 不用 Ctrl 即可複選；preventDefault 後需手動還原 scrollTop，否則點下方選項會跳回頂部
    el.addEventListener("mousedown", function onMultiSelectMouseDown(e) {
        const option = e.target;
        if (option.tagName !== "OPTION") return;
        e.preventDefault();
        const scrollTop = this.scrollTop;
        option.selected = !option.selected;
        handleMultiSelectChange(this);
        restoreMultiSelectScroll(this, scrollTop);
    });
});

document.addEventListener("DOMContentLoaded", function () {
    toggleInput();
    initVersionNotice();
    initFileUploadZones();
    initThemeToggle();
    updateRunButtonState();
    const usernameEl = document.getElementById("username");
    if (usernameEl) {
        usernameEl.addEventListener("input", updateRunButtonState);
    }
    const tcgEl = document.getElementById("tcg_keys_input");
    if (tcgEl) {
        tcgEl.addEventListener("input", updateRunButtonState);
    }
    initResultModal();
    initWorkdaysDatePicker();
    initScenarioPanel();
    initPlatformChipPicker();
    syncPlatformChipsFromSelect();
    syncPromotionIdForPlatformSelection();
});

function initFileUploadZones() {
    document.querySelectorAll(".file-upload-zone").forEach((zone) => {
        const input = zone.querySelector(".file-upload-input");
        const nameEl = zone.querySelector(".file-upload-name");
        const label = zone.querySelector(".file-upload-label");
        if (!input || !nameEl || !label) return;

        const syncName = () => {
            if (input.files && input.files.length > 0) {
                nameEl.textContent = input.files[0].name;
                zone.classList.add("has-file");
            } else {
                nameEl.textContent = "尚未選擇檔案";
                zone.classList.remove("has-file");
            }
        };

        input.addEventListener("change", syncName);

        ["dragenter", "dragover"].forEach((evt) => {
            label.addEventListener(evt, (e) => {
                e.preventDefault();
                zone.classList.add("dragover");
            });
        });

        ["dragleave", "drop"].forEach((evt) => {
            label.addEventListener(evt, (e) => {
                e.preventDefault();
                zone.classList.remove("dragover");
            });
        });

        label.addEventListener("drop", (e) => {
            const files = e.dataTransfer?.files;
            if (!files || !files.length) return;
            input.files = files;
            syncName();
        });
    });
}

const VERSION_STORAGE_KEY = "auto_test_last_seen_version";
const THEME_STORAGE_KEY = "auto_test_theme";

function initThemeToggle() {
    const toggle = document.getElementById("theme-toggle");
    if (!toggle) return;

    const savedTheme = localStorage.getItem(THEME_STORAGE_KEY);
    const isDark = savedTheme === "dark" || document.documentElement.getAttribute("data-theme") === "dark";
    applyTheme(isDark ? "dark" : "light", false);

    toggle.checked = isDark;
    toggle.setAttribute("aria-checked", isDark ? "true" : "false");

    toggle.addEventListener("change", () => {
        const nextTheme = toggle.checked ? "dark" : "light";
        applyTheme(nextTheme, true);
        toggle.setAttribute("aria-checked", toggle.checked ? "true" : "false");
    });
}

function applyTheme(theme, persist) {
    const isDark = theme === "dark";
    document.documentElement.setAttribute("data-theme", isDark ? "dark" : "light");
    if (persist) {
        localStorage.setItem(THEME_STORAGE_KEY, isDark ? "dark" : "light");
    }
}

function initVersionNotice() {
    const info = window.APP_VERSION;
    const badge = document.getElementById("version-badge");
    if (!info) return;

    if (!badge) return;

    const lastSeen = localStorage.getItem(VERSION_STORAGE_KEY);
    if (lastSeen !== info.version) {
        badge.classList.remove("hidden");
        badge.setAttribute("aria-hidden", "false");
    }
}

function markVersionSeen() {
    const info = window.APP_VERSION;
    const badge = document.getElementById("version-badge");
    if (!info) return;

    localStorage.setItem(VERSION_STORAGE_KEY, info.version);
    if (badge) {
        badge.classList.add("hidden");
        badge.setAttribute("aria-hidden", "true");
    }
}

function switchTab(evt, tabId) {
    document.querySelectorAll(".tabcontent").forEach((tab) => tab.classList.remove("active"));
    document.querySelectorAll(".nav-item, .tab-version-btn").forEach((btn) => {
        btn.classList.remove("active");
        if (btn.getAttribute("role") === "tab") {
            btn.setAttribute("aria-selected", "false");
        }
    });

    const panel = document.getElementById(tabId);
    const btn = evt.currentTarget;
    const isVersion = tabId === "VersionTab";
    const isExcel = tabId === "ExcelTab";

    if (!isVersion && panel) panel.classList.add("active");
    if (btn) {
        btn.classList.add("active");
        btn.setAttribute("aria-selected", "true");
    }

    const accountCard = document.getElementById("account-config-card");
    const scriptsSection = document.getElementById("scripts-section");
    const versionSection = document.getElementById("version-section");
    const scriptsHeading = document.getElementById("scripts-heading");

    if (accountCard) accountCard.classList.toggle("hidden", isExcel || isVersion);
    if (scriptsSection) scriptsSection.classList.toggle("hidden", isVersion);
    if (versionSection) versionSection.classList.toggle("hidden", !isVersion);
    if (scriptsHeading) {
        scriptsHeading.textContent = isExcel ? "Excel 比對" : "測試功能選擇";
    }

    if (isVersion) {
        markVersionSeen();
    }
}

function showLoading(show=true){
    const loading=document.getElementById('loading');
    if (!loading) return;
    loading.classList.toggle('show', show);
}

function parseProgressPercent(raw) {
    if (raw == null || raw === "") return null;
    if (typeof raw === "number") {
        if (raw <= 1 && raw >= 0) return Math.round(raw * 100);
        return Math.round(raw);
    }
    const text = String(raw).trim();
    if (!text) return null;
    const m = text.match(/^([\d.]+)\s*%?$/);
    if (!m) return null;
    const num = Number(m[1]);
    if (!Number.isFinite(num)) return null;
    return num <= 1 && text.indexOf("%") === -1 && num > 0 ? Math.round(num * 100) : Math.round(num);
}

function progressTierClass(pct) {
    if (pct == null) return "is-none";
    if (pct <= 0) return "is-zero";
    if (pct < 50) return "is-low";
    if (pct < 80) return "is-mid";
    return "is-high";
}

function formatProgressLabel(pct) {
    const clamped = Math.min(100, Math.max(0, Number(pct) || 0));
    return clamped <= 0 ? "未開始" : `${clamped}%`;
}

function renderSheetProgressBar(label, rate) {
    const pct = parseProgressPercent(rate);
    if (pct == null) {
        return `<div class="tp-progress tp-progress--sheet is-none">
            <div class="tp-progress-meta">
                <span class="tp-progress-label">${escapeHtml(label)}</span>
                <span class="tp-progress-pct is-none">—</span>
            </div>
            <div class="tp-progress-track is-none"><div class="tp-progress-fill" style="width:0"></div></div>
        </div>`;
    }
    const clamped = Math.min(100, Math.max(0, pct));
    const tier = progressTierClass(clamped);
    return `<div class="tp-progress tp-progress--sheet ${tier}" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${clamped}" aria-label="${escapeHtml(label)} 進度">
        <div class="tp-progress-meta">
            <span class="tp-progress-label">${escapeHtml(label)}</span>
            <span class="tp-progress-pct ${tier}">${escapeHtml(formatProgressLabel(clamped))}</span>
        </div>
        <div class="tp-progress-track ${tier}">
            <div class="tp-progress-fill ${tier}" style="width:${clamped}%"></div>
        </div>
    </div>`;
}

function renderExcelProgressTable(rows) {
    if (!rows || rows.length === 0) {
        return renderEmptyState("沒有 TCG 分頁", "試算表內找不到以 TCG- 開頭的分頁。");
    }
    const sorted = [...rows].sort((a, b) => String(a["分頁名稱"] || "").localeCompare(String(b["分頁名稱"] || "")));
    const bars = sorted
        .map((row) => renderSheetProgressBar(row["分頁名稱"] || "—", row["進度"]))
        .join("");
    return `<div class="result-task-list excel-progress-list">${bars}</div>`;
}

function renderExcelProgressReport(report) {
    const sheets = Array.isArray(report?.sheets) ? report.sheets : [];
    const totalCount = Number(report?.total_count ?? sheets.length);
    const withProgress = sheets.filter((row) => parseProgressPercent(row["進度"]) != null);
    const avgProgress =
        withProgress.length === 0
            ? null
            : Math.round(
                  withProgress.reduce((sum, row) => sum + parseProgressPercent(row["進度"]), 0) /
                      withProgress.length
              );

    const summary = renderStatsBar(
        [
            { label: "TCG 分頁", numeric: totalCount, suffix: "張", dimZero: true },
            { label: "有進度", numeric: withProgress.length, suffix: "張", dimZero: true },
            {
                label: "平均進度",
                value: avgProgress == null ? "—" : formatProgressLabel(avgProgress),
                valueClass: avgProgress == null ? "" : `tp-progress-pct ${progressTierClass(avgProgress)}`,
            },
        ],
        { columns: 3 }
    );

    if (sheets.length === 0) {
        return `${summary}${renderEmptyState(
            "沒有 TCG 分頁",
            "試算表內找不到以 TCG- 開頭的分頁。"
        )}`;
    }

    const overallProgress = avgProgress == null ? "" : renderProgressBar(avgProgress, "平均進度");
    return `${summary}${overallProgress}${renderExcelProgressTable(sheets)}`;
}

const EXCEL_SHEET_ID_STORAGE_KEY = "excelProgressSheetId";

const excelProgressBtn = document.getElementById("excelProgressBtn");
const googleSheetIdInput = document.getElementById("googleSheetIdInput");
if (googleSheetIdInput) {
    const savedSheetId = localStorage.getItem(EXCEL_SHEET_ID_STORAGE_KEY);
    if (savedSheetId) {
        googleSheetIdInput.value = savedSheetId;
    }
}
if (excelProgressBtn) {
    excelProgressBtn.addEventListener("click", async () => {
        const sheetId = googleSheetIdInput?.value?.trim() || "";
        if (!sheetId) {
            showResultPopup({
                success: false,
                message: "請輸入 Google Sheet ID 或試算表連結",
            });
            googleSheetIdInput?.focus();
            return;
        }

        showLoading(true);
        try {
            localStorage.setItem(EXCEL_SHEET_ID_STORAGE_KEY, sheetId);
            const response = await fetch(
                `/api/excel-progress?sheet_id=${encodeURIComponent(sheetId)}`
            );
            const raw = await response.text();
            let data;
            try {
                data = JSON.parse(raw);
            } catch (parseErr) {
                throw new Error(`回應不是合法 JSON：${raw.slice(0, 120)}`);
            }
            if (!response.ok || !data.success) {
                showResultPopup({
                    success: false,
                    message: data.message || `HTTP ${response.status}`,
                });
                return;
            }
            showResultPopup(data);
        } catch (err) {
            showResultPopup({
                success: false,
                message: err.message || String(err),
            });
        } finally {
            showLoading(false);
        }
    });
}

document.getElementById('uploadform').addEventListener('submit',async(e)=>{
    e.preventDefault();
    const formdata=new FormData();
    const fileInput=document.getElementById('fileInput');
    const uploadHint=document.getElementById('upload_hint');
    if (!fileInput.files.length){
        uploadHint.style.display="inline";
        alert('請選擇要上傳的 Excel 檔案');
        return;
    }else{
        uploadHint.style.display="none";
    };
    showLoading(true)
    formdata.append('file', fileInput.files[0]);
        try{
        const response=await fetch('/upload_excel',{
            method:'POST',
            body:formdata
        });
        const data=await response.json();
        document.getElementById('result').innerHTML = `<p>${data.message}</p>`;
        if (data.full_dupes){
            let html="<table border=1 cellpadding='5'<tr>";
            Object.keys(data.full_dupes[0]).forEach(k=>html+=`<th>${k}</th>`);
            html += "</tr>";

            data.full_dupes.forEach(row=>{
                html+="<tr>";
                Object.values(row).forEach(v => html+=`<td>${v ?? ''}</td>`);
                html += "</tr>";
            });
            html+="</table>";
            document.getElementById('result').innerHTML+=html;
        }
    }catch(err){
        alert("上傳失敗：" + err);
    }
    finally{
        showLoading(false)
    }
});
document.getElementById('Compare_Two_Excel').addEventListener('submit',async(e)=>{
    e.preventDefault();
    const formdata=new FormData();
    const fileInput_1=document.getElementById('fileInput_1');
    const fileInput_2=document.getElementById('fileInput_2');
    const uploadHint=document.getElementById('upload_hint_compare');
    if (!fileInput_1.files.length||!fileInput_2.files.length){
        uploadHint.style.display="inline";
        alert('請選擇要上傳的 Excel 檔案');
        return;
    }else{
        uploadHint.style.display="none";
    };
    showLoading(true)
    formdata.append('file1', fileInput_1.files[0]);
    formdata.append('file2', fileInput_2.files[0]);
        try{
        const response=await fetch('/Compare_Two_Excel',{
            method:'POST',
            body:formdata
        });
        const data=await response.json();
        document.getElementById('result').innerHTML = `<p>${data.message}</p>`;
        if (data.full_dupes){
            let html="<table border=1 cellpadding='5'<tr>";
            Object.keys(data.full_dupes[0]).forEach(k=>html+=`<th>${k}</th>`);
            html += "</tr>";

            data.full_dupes.forEach(row=>{
                html+="<tr>";
                Object.values(row).forEach(v => html+=`<td>${v ?? ''}</td>`);
                html += "</tr>";
            });
            html+="</table>";
            document.getElementById('result').innerHTML+=html;
        }
    }catch(err){
        alert("上傳失敗：" + err);
    }
    finally{
        showLoading(false)
    }
});

function runSelectScript(){
    console.log("clicked");

    if(!validateFormBeforeSubmit()){
        console.log("❌ validate 被擋");
        return;
    }
    
    const username=document.getElementById("username").value;
    const platformSelect=document.getElementById("frontend-checkbox_manual_platform")
    let platforms=Array.from(platformSelect.selectedOptions).map(opt=>opt.value)
    const checkSelectScript=Array.from(document.querySelectorAll('input[name="script"]:checked')).map(el=>el.value);
    let ticket_select = document.getElementById("frontend-checkbox_select");
    let ticket_types=Array.from(ticket_select.selectedOptions).map(opt=>opt.value)
    console.log("checkSelectScript:", checkSelectScript);
    console.log("ticket_types:", ticket_types);
    console.log("platforms:", platforms);
    if (platforms.length==0){
        platforms=["gi8viet"];
    }

    (async () => {
    for (const scriptName of checkSelectScript) {
        let extraData = {};
        /** 非 null 時覆寫預設 payload（username + platforms + extraData） */
        let requestPayload = null;

    switch (scriptName) {
        case "SIGLE_PROMO_7_TICKET":
            extraData = {
                promotion_id: getFormPromotionIdValue(),
            };
            break;

        case "SameTime_ReceiveTicket":
            extraData = {
                username2: document.getElementById("username2").value,
            };
            break;

        case "MANUAL_CREATE_SINGLE_CONFIRM":
            extraData = {
                promotion_id: getFormPromotionIdValue(),
                ticket_id: document.getElementById("ticket_id").value,
                amount: getFormAmountValue(),
            };
            break;

        case "auto_create_ticket":
            extraData = {
                ticket_type: ticket_types,
                ticket_input: document.getElementById("ticket_input").value,
            };
            break;

        /** 票券／活動：後台一鍵建立多類活動（Create_all_promotion.create_promotion(merchantCode)） */
        case "Create_all_promotion": {
            const promoSel = document.getElementById("promotion-checkbox_select");
            const promotion_types = promoSel
                ? Array.from(promoSel.selectedOptions).map((opt) => opt.value)
                : [];
            extraData = {
                merchantCode: platforms[0] || "gi8viet",
                promotion_types,
            };
            break;
        }

        /** 達成存款活動：後端需兩個前台帳號（無第二欄時傳兩次主帳號） */
        case "ALL_deposit_promotion": {
            const pwd =
                (document.getElementById("password") &&
                    document.getElementById("password").value.trim()) ||
                "123qwe";
            const u2El = document.getElementById("username_secondary");
            const u2 =
                u2El && u2El.value.trim() ? u2El.value.trim() : username.trim();
            extraData = {
                usernames: [username.trim(), u2],
                password: pwd,
            };
            break;
        }

        case "LOTTERY_BET":
            extraData = {
                amount: getFormAmountValue(),
            };
            break;

        case "DEPOSIT_API": {
            const requestType = getDepositApproveRequestType();
            extraData = requestType ? { requestType } : {};
            break;
        }

        case "create_member_player":
            extraData = {
                amount: getFormAmountValue(),
            };
            break;

        case "FRONTEND_DEPOSIT": {
            const username_list = username
                ? username.split(/[\s,]+/).filter(Boolean)
                : [];
            const deposit_amount = document.getElementById("deposit_amount").value;
            if (isDiscountCouponDepositMode()) {
                const ticketIdRaw = document.getElementById("ticket_id")?.value.trim() || "";
                const discountRaw = document.getElementById("discount_amount")?.value.trim();
                const promotionRaw = document.getElementById("promotion_id")?.value.trim();
                extraData = {
                    username_list,
                    deposit_amount,
                    type: 3,
                    ticket_id: ticketIdRaw,
                    discountAmount: discountRaw ? Number(discountRaw) : 100,
                };
                if (promotionRaw) {
                    extraData.promotion_id = promotionRaw;
                }
            } else {
                extraData = {
                    username_list,
                    deposit_amount,
                    type: 1,
                };
            }
            requestPayload = { username, ...extraData };
            break;
        }

        case "FIXED_DEPOSIT": {
            const deposit_list = username
                ? username.split(/[\s,]+/).filter(Boolean)
                : [];
            extraData = {
                deposit_list,
                amount: getFormAmountValue(),
                type: 2
            };
            requestPayload = { username, ...extraData };
            break;
        }
        case "BACKEND_DEPOSIT": {
            const username_list = username
                ? username.split(/[\s,]+/).filter(Boolean)
                : [];
            const deposit_amount = document.getElementById("deposit_amount").value;    
            extraData = {
                username_list,
                deposit_amount,
                type: 4,
                merchantCode: platforms[0] || "gi8viet",
            };
            requestPayload = { username, ...extraData };
            break;
        }

        case "Compensation_api":
            extraData = {
                round_id: document.getElementById("round_id").value,
            };
            break;

        case "Schedule_manual_bonus":
            extraData = {
                promotion_id: getFormPromotionIdValue(),
                date: document.getElementById("date_time").value.trim(),
            };
            break;

        case "MANUAL_SIGN": {
            const signChoice = await askSign("選擇報名類型？");
            if (signChoice === null) {
                continue;
            }
            extraData = {
                promotion_id: getFormPromotionIdValue(),
                requireType: signChoice ? "A" : "B",
            };
            break;
        }

        /** 領取郵寄碼：先詢問是否要審核，Y/N 帶給後端 requireType */
        case "PostCard_api": {
            const wantApprove = await askConfirm("是否要審核該筆郵寄碼？");
            extraData = {
                requireType: wantApprove ? "Y" : "N",
            };
            break;
        }

        case "create_qa_task":
            extraData = {
                tcg_keys: document.getElementById("tcg_keys_input").value
                    .split(/[\s,;]+/)
                    .filter(Boolean),
            };
            requestPayload = { ...extraData };
            break;

        case "calculate_workdays": {
            const tpRaw = document.getElementById("qa_stats_tp_key").value.trim();
            const tpKeys = tpRaw.split(/[\s,;]+/).filter(Boolean);
            const effectiveDates = getWorkdaysEffectiveDates({ autoApply: true });
            extraData = {
                assignee: document.getElementById("qa_stats_assignee").value.trim() || "carrine.s",
                tp_key: tpKeys[0] || "",
                date_from: effectiveDates.from,
                date_to: effectiveDates.to,
            };
            requestPayload = { ...extraData };
            break;
        }

        case "Extra_Reward_api": {
            const rawTickets = document.getElementById("ticket_id").value.trim();
            const ticket_id_list = rawTickets
                ? rawTickets.split(/[\s,]+/).filter(Boolean)
                : [];
            extraData = {
                ticket_id_list,
                amount: getFormAmountValue(),
                promotion_id: getFormPromotionIdValue(),
                "deposit-amount-id": document.getElementById("deposit-amount-id").value,
                extra_promo_id: document.getElementById("extra_promo_id").value,
            };
            break;
        }
        case "Customer_id":
            extraData = {
                    type: 1
                }
            break;

        case "Customer_name":
            extraData = {
                    type: 2
                }
        break;

        case "Codition_create_bonus": {
            const el = document.getElementById("ticket_id");
            extraData = {
                ticket_id: el ? el.value.trim() : "",
            };
            break;
        }

        case "Input_User_Info": {
            const requireTypes = await askPlayerInfoType();
            if (!requireTypes || requireTypes.length === 0) {
                continue;
            }
            extraData = { requireTypes };
            break;
        }

        case "Achievement_bonus":
            extraData = {
                promotion_id: getFormPromotionIdValue(),
                type: 1,
            };
            break;
        case "QUEST_bonus":
            extraData = {
                promotion_id: getFormPromotionIdValue(),
                type: 2,
            };
            break;
        case "Activity_bonus":
            extraData = {
                promotion_id: getFormPromotionIdValue(),
                type: 3,
            };
            break;

        case "auto_create_promotion": {
            const promoSel = document.getElementById("promotion-checkbox_select");
            const promotion_types = promoSel
                ? Array.from(promoSel.selectedOptions).map(opt => opt.value)
                : [];
            extraData = {
                promotion_types,  // 直接傳字串陣列，不再用 type 數字
            };
            break;
        
        }

        default:
            extraData = {};
            console.warn("[runSelectScript] 未定義腳本，使用空 extraData:", scriptName);
    }

    const payload = requestPayload ?? { username, platforms, ...extraData };
    await runScriptApi(scriptName, payload);
    }
    })();
}

async function runScriptApi(scriptName, payload) {
    trackRunRequestStart();
    try {
        const res = await fetch(`/api/${scriptName}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        const data = await res.json();
        console.log(scriptName, data);
        showResultPopup(data);
        return data;
    } catch (err) {
        showResultPopup({
            success: false,
            message: "API 呼叫失敗：" + err,
        });
        return { success: false, message: String(err) };
    } finally {
        trackRunRequestEnd();
    }
}

function showResultPopup(data) {
    const modal = document.getElementById("result-modal");
    const contentEl = modal.querySelector(".result-modal-content");
    const eyebrow = document.getElementById("modal-eyebrow");
    const headerTitle = document.getElementById("modal-header-title");
    const statusWrap = document.getElementById("modal-status-wrap");
    const tabBar = document.getElementById("modal-tab-bar");
    const body = document.getElementById("modal-body");
    const isSuccess = !!data.success;
    const resultType = detectResultType(data);

    contentEl.classList.toggle("is-fail", !isSuccess);
    modal.classList.toggle("no-backdrop-close", !isSuccess);
    eyebrow.textContent = isSuccess ? "AUTOMATION · QUERY RESULT" : "AUTOMATION · ERROR";
    headerTitle.textContent = isSuccess
        ? (data.message || "執行成功")
        : (data.message || "執行失敗");

    if (statusWrap) {
        statusWrap.classList.toggle("hidden", !isSuccess);
        statusWrap.classList.remove("ping-once");
        if (isSuccess) {
            void statusWrap.offsetWidth;
            statusWrap.classList.add("ping-once");
        }
    }

    if (tabBar) {
        tabBar.classList.toggle("hidden", !isSuccess);
    }

    const summaryResultTypes = [
        "postcard",
        "manual_single_confirm",
        "verify_player_info",
        "verify_player_info_multi",
        "verify_mobile",
        "verify_id",
        "verify_name",
        "customer_id",
        "customer_name",
    ];
    const showSummaryPanel = isSuccess || summaryResultTypes.includes(resultType);

    body.innerHTML = showSummaryPanel
        ? renderFormattedResult(data, resultType)
        : renderFailureResult(data);

    setupResultModalInteractions(body);

    modal.classList.remove("hidden");
    modal.classList.remove("is-visible");
    requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            modal.classList.add("is-visible");
        });
    });
}

const JIRA_BROWSE_BASE = "https://jira.tc-gaming.co/jira/browse/";
const COPY_ICON_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>';
const EMPTY_ICON_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" aria-hidden="true"><path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="1"/><path d="M9 12h6M9 16h6"/></svg>';

function initResultModal() {
    const modal = document.getElementById("result-modal");
    if (!modal || modal.dataset.bound === "true") return;
    modal.dataset.bound = "true";

    modal.addEventListener("click", (event) => {
        if (event.target !== modal) return;
        if (modal.classList.contains("no-backdrop-close")) return;
        closeResultModal();
    });

    document.addEventListener("keydown", (event) => {
        if (event.key !== "Escape") return;
        if (modal.classList.contains("hidden") || !modal.classList.contains("is-visible")) return;
        if (modal.classList.contains("no-backdrop-close")) return;
        closeResultModal();
    });
}

function setupResultModalInteractions(body) {
    if (!body) return;

    body.querySelectorAll(".result-row-copy-btn").forEach((button) => {
        button.addEventListener("click", (event) => {
            event.preventDefault();
            event.stopPropagation();
            const text = button.dataset.copy || "";
            if (!text) return;

            navigator.clipboard
                .writeText(text)
                .then(() => {
                    button.classList.add("copied");
                    button.setAttribute("title", "已複製");
                    window.setTimeout(() => {
                        button.classList.remove("copied");
                        button.setAttribute("title", "複製單號");
                    }, 1200);
                })
                .catch(() => {
                    window.alert("複製失敗，請手動選取內容複製");
                });
        });
    });
}

function renderIssueKey(key, options = {}) {
    const value = String(key || "").trim();
    if (!value) return "";
    if (options.plain) {
        return `<span class="result-task-key">${escapeHtml(value)}</span>`;
    }
    const url = `${JIRA_BROWSE_BASE}${encodeURIComponent(value)}`;
    return `<a class="result-task-key" href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer" title="在 Jira 開啟">${escapeHtml(value)}</a>`;
}

function renderCopyButton(copyText, label = "複製單號") {
    return `<button type="button" class="result-row-copy-btn" data-copy="${escapeHtml(copyText)}" aria-label="${escapeHtml(label)}" title="${escapeHtml(label)}">${COPY_ICON_SVG}</button>`;
}

function formatStatNumber(value, options = {}) {
    const numeric = Number(value);
    const hasNumber = Number.isFinite(numeric);
    const displayValue = hasNumber ? numeric.toLocaleString("zh-TW") : String(value ?? "—");
    const isZero = hasNumber && numeric === 0 && options.dimZero;
    const suffix = options.suffix ? ` ${options.suffix}` : "";
    const zeroClass = isZero ? " is-zero" : "";
    return `<span class="result-stat-value${zeroClass}">${escapeHtml(displayValue)}${escapeHtml(suffix)}</span>`;
}

function renderEmptyState(title, description) {
    return `
        <div class="result-empty-state">
            <span class="result-empty-icon">${EMPTY_ICON_SVG}</span>
            <p class="result-empty-title">${escapeHtml(title)}</p>
            <p class="result-empty-desc">${escapeHtml(description)}</p>
        </div>`;
}

function escapeHtml(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}

function getPromoTypeFromResult(data) {
    if (data.promoType != null && String(data.promoType).trim() !== "") {
        return String(data.promoType);
    }
    if (data.data?.promoType != null && String(data.data.promoType).trim() !== "") {
        return String(data.data.promoType);
    }
    return "—";
}

function detectResultType(data) {
    if ("postcardCode" in data) {
        return "postcard";
    }
    if (data.promoType != null || data.data?.promoType != null) {
        return "manual_single_confirm";
    }
    if (Array.isArray(data.results) && data.results.length > 0) {
        const first = data.results[0];
        if (first && ("requireType" in first || "verifyType" in first)) {
            return data.results.length === 1 ? "verify_player_info" : "verify_player_info_multi";
        }
    }
    const verifyType = Number(data.requireType ?? data.verifyType);
    if (verifyType >= 1 && verifyType in PLAYER_INFO_VALUE_FIELDS) {
        return "verify_player_info";
    }
    if (data.mobileNumber != null) {
        return "verify_mobile";
    }
    if (data.IDNumber != null) {
        return "verify_id";
    }
    if (data.name != null && data.name !== "") {
        return "verify_name";
    }
    const report = data.data;
    if (!report) return "generic";
    if (report.customer_id != null && String(report.customer_id).trim() !== "") {
        return Number(data.type) === 2 ? "customer_name" : "customer_id";
    }
    if (Array.isArray(report) && report.length > 0 && ("tcg_key" in report[0] || "new_key" in report[0])) {
        return "create_qa_task";
    }
    if (report.tasks && Array.isArray(report.tasks) && "total_count" in report) {
        return "calculate_workdays";
    }
    if (report.sheets && Array.isArray(report.sheets) && "total_count" in report) {
        return "excel_progress";
    }
    return "generic";
}

function getFailureGuidance(message) {
    const msg = String(message || "").toLowerCase();
    if (msg.includes("帳號") || msg.includes("密碼") || msg.includes("password") || msg.includes("401")) {
        return {
            cause: "帳號或密碼可能有誤",
            next: "請確認玩家帳號與密碼是否正確，或聯絡管理員確認權限。",
        };
    }
    if (msg.includes("tp") || msg.includes("tcg") || msg.includes("單號") || msg.includes("jira")) {
        return {
            cause: "查詢或單號條件可能有誤",
            next: "請確認 TP / TCG 單號與 Jira 帳號是否填寫正確。",
        };
    }
    if (msg.includes("timeout") || msg.includes("連線") || msg.includes("network")) {
        return {
            cause: "網路或服務連線異常",
            next: "請稍後再試，或確認 VPN / 內網連線是否正常。",
        };
    }
    return {
        cause: "執行過程發生未預期錯誤",
        next: "請將錯誤訊息截圖給開發人員協助排查。",
    };
}

function renderFailureResult(data) {
    const guidance = getFailureGuidance(data.message);
    return `
        <div class="result-error-panel">
            <p class="result-error-message">${escapeHtml(data.message || "未知錯誤")}</p>
            <div class="result-error-guide">
                <div>
                    <p class="result-error-guide-label">可能原因</p>
                    <p class="result-error-guide-text">${escapeHtml(guidance.cause)}</p>
                </div>
                <div>
                    <p class="result-error-guide-label">建議處理</p>
                    <p class="result-error-guide-text">${escapeHtml(guidance.next)}</p>
                </div>
            </div>
        </div>`;
}

function formatShortDate(dateStr) {
    if (!dateStr) return "—";
    const parts = String(dateStr).split("-");
    if (parts.length >= 3) {
        return `${parts[1]}-${parts[2]}`;
    }
    return dateStr;
}

function formatWorkdaysDays(workdays) {
    const value = Number(workdays);
    if (Number.isNaN(value)) return "0d";
    return `${value}d`;
}

const DONE_STATUS_TOKENS = new Set(["done", "closed", "resolved"]);

function tokenizeStatus(status) {
    return String(status || "")
        .toLowerCase()
        .split(/[\s/_-]+/)
        .filter(Boolean);
}

function isDoneStatus(status) {
    return tokenizeStatus(status).some((token) => DONE_STATUS_TOKENS.has(token));
}

function getStatusModifier(status) {
    if (isDoneStatus(status)) return "closed";
    const normalized = String(status || "").toLowerCase();
    if (normalized.includes("open")) return "open";
    if (normalized.includes("progress")) return "in-progress";
    if (normalized.includes("fail")) return "fail";
    return "default";
}

function renderStatusBadge(status) {
    const modifier = getStatusModifier(status);
    return `<span class="result-task-status"><span class="status-dot status-${modifier}" aria-hidden="true"></span><span>${escapeHtml(status)}</span></span>`;
}

function renderStatsBar(cards, options = {}) {
    const colsClass =
        options.columns === 6 ? " is-cols-6" : options.columns === 4 ? " is-cols-4" : "";
    const items = cards
        .map(
            (card, index) => `
        <div class="result-stat${index === 0 ? " result-stat-primary" : ""}">
            <span class="result-stat-label">${escapeHtml(card.label)}</span>
            ${
                card.numeric != null
                    ? formatStatNumber(card.numeric, { suffix: card.suffix, dimZero: card.dimZero })
                    : `<span class="result-stat-value${card.valueClass ? ` ${card.valueClass}` : ""}">${escapeHtml(card.value)}</span>`
            }
        </div>`
        )
        .join("");
    return `<div class="result-stats-bar${colsClass}">${items}</div>`;
}

function formatWorkdaysDateRange(dateFrom, dateTo) {
    if (dateFrom && dateTo) return `${dateFrom} ~ ${dateTo}`;
    if (dateFrom) return `${dateFrom} 起`;
    if (dateTo) return `至 ${dateTo}`;
    return "全部";
}

function renderProgressBar(rate, label = "QA Task 完成率") {
    const pct = Math.min(100, Math.max(0, Number(rate) || 0));
    const tier = progressTierClass(pct);
    return `<div class="tp-progress tp-progress--overall ${tier}" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${pct}" aria-label="${escapeHtml(label)}">
        <div class="tp-progress-meta">
            <span class="tp-progress-label">${escapeHtml(label)}</span>
            <span class="tp-progress-pct ${tier}">${escapeHtml(formatProgressLabel(pct))}</span>
        </div>
        <div class="tp-progress-track ${tier}">
            <div class="tp-progress-fill ${tier}" style="width:${pct}%"></div>
        </div>
    </div>`;
}

function renderWorkdaysReport(report) {
    const totalCount = Number(report.total_count ?? 0);
    const totalWorkdays = Number(report.total_workdays ?? 0);
    const doneCount = Number(report.done_count ?? 0);
    const completionRate = Number(report.completion_rate ?? 0);
    const tpLabel = report.tp_key ? report.tp_key : "全部";
    const summary = renderStatsBar(
        [
            { label: "TP 單號", value: tpLabel },
            { label: "結案區間", value: formatWorkdaysDateRange(report.date_from, report.date_to) },
            { label: "共查到", numeric: totalCount, suffix: "筆", dimZero: true },
            { label: "總工作日", numeric: totalWorkdays, dimZero: true },
            { label: "已完成", numeric: doneCount, suffix: "張", dimZero: true },
            { label: "完成率", value: `${completionRate}%` },
        ],
        { columns: 6 }
    );

    if (!report.tasks || report.tasks.length === 0) {
        const rangeHint = formatWorkdaysDateRange(report.date_from, report.date_to);
        const emptyDesc = report.tp_key
            ? `TP 單號（${report.tp_key}）在結案日區間 ${rangeHint} 內沒有相關 QA Task。`
            : `Jira 帳號（${report.assignee || "—"}）在結案日區間 ${rangeHint} 內沒有指派的 QA Task。`;
        return `${summary}${renderEmptyState("目前沒有指派的 QA Task", emptyDesc)}`;
    }

    const progress = renderProgressBar(completionRate);
    const items = report.tasks
        .map((task) => {
            const parent = task.parent
                ? `<span class="result-task-parent">← ${renderIssueKey(task.parent)}</span>`
                : "";
            const copyText = [task.key, task.parent].filter(Boolean).join(" / ");
            const resolvedLabel = task.resolved_date
                ? formatShortDate(task.resolved_date)
                : "未結案";
            return `
        <article class="result-task-item">
            <div class="result-task-main">
                <div class="result-task-content">
                    <div class="result-task-row-top">
                        <div class="result-task-ids">
                            ${renderIssueKey(task.key)}
                            ${parent}
                        </div>
                        ${renderStatusBadge(task.status)}
                    </div>
                    <p class="result-task-summary">${escapeHtml(task.summary)}</p>
                </div>
                <div class="result-task-side">
                    <span class="result-task-date">
                        <span class="result-task-date-label">${resolvedLabel}</span>
                        <span class="result-task-date-sep" aria-hidden="true">·</span>
                        <span class="result-task-workdays${Number(task.workdays) === 0 ? " is-zero" : ""}">${formatWorkdaysDays(task.workdays)}</span>
                    </span>
                </div>
            </div>
            <div class="result-task-actions">
                ${renderCopyButton(copyText)}
            </div>
        </article>`;
        })
        .join("");

    return `${summary}${progress}<div class="result-task-list">${items}</div>`;
}

function renderCreateQaTaskResults(items) {
    const successCount = items.filter((item) => item.new_key).length;
    const failCount = items.length - successCount;
    const summary = renderStatsBar([
        { label: "處理筆數", numeric: items.length, suffix: "筆", dimZero: true },
        { label: "建立成功", numeric: successCount, suffix: "筆", dimZero: true },
        { label: "建立失敗", numeric: failCount, suffix: "筆", dimZero: true },
    ]);

    if (items.length === 0) {
        return `${summary}${renderEmptyState(
            "沒有可處理的 TCG 單號",
            "請確認已填寫 TCG 單號，並再次執行建立 QA Task。"
        )}`;
    }

    const listItems = items
        .map((item) => {
            const keyHtml = item.new_key
                ? `<a class="result-task-key" href="${escapeHtml(item.url)}" target="_blank" rel="noopener noreferrer" title="在 Jira 開啟">${escapeHtml(item.new_key)}</a>`
                : `<span class="result-task-key is-fail">建立失敗</span>`;
            const status = item.error ? "Failed" : "Created";
            const parent = item.tcg_key
                ? `<span class="result-task-parent">← ${renderIssueKey(item.tcg_key)}</span>`
                : "";
            const detail = item.error
                ? `<p class="result-task-note text-fail">${escapeHtml(item.error)}</p>`
                : "";
            const copyText = item.new_key || item.tcg_key || item.summary || "";
            return `
        <article class="result-task-item">
            <div class="result-task-main">
                <div class="result-task-content">
                    <div class="result-task-row-top">
                        <div class="result-task-ids">
                            ${keyHtml}
                            ${parent}
                        </div>
                        ${renderStatusBadge(status)}
                    </div>
                    <p class="result-task-summary">${escapeHtml(item.summary)}</p>
                    ${detail}
                </div>
                <div class="result-task-side">
                    <span class="result-task-date">${item.new_key ? "已建立" : "失敗"}</span>
                </div>
            </div>
            <div class="result-task-actions">
                ${copyText ? renderCopyButton(copyText) : ""}
            </div>
        </article>`;
        })
        .join("");

    return `${summary}<div class="result-task-list">${listItems}</div>`;
}

function renderPostCardResult(data) {
    const code =
        data.postcardCode != null && String(data.postcardCode).trim() !== ""
            ? String(data.postcardCode)
            : "—";
    const needsReview = data.requireType === "Y";
    return renderStatsBar([
        { label: "郵寄碼", value: code },
        { label: "是否審核", value: needsReview ? "是" : "否" },
        { label: "結果", value: data.success ? "領取成功" : "領取失敗" },
    ]);
}

function renderVerifyMobileResult(data) {
    const number =
        data.mobileNumber != null && String(data.mobileNumber).trim() !== ""
            ? String(data.mobileNumber)
            : "—";
    return renderStatsBar([
        { label: "手機號碼", value: number },
        { label: "驗證結果", value: data.success ? "成功" : "失敗" },
    ]);
}

function renderVerifyIdResult(data) {
    const number =
        data.IDNumber != null && String(data.IDNumber).trim() !== ""
            ? String(data.IDNumber)
            : "—";
    return renderStatsBar([
        { label: "身分證號", value: number },
        { label: "驗證結果", value: data.success ? "成功" : "失敗" },
    ]);
}

function renderVerifyNameResult(data) {
    const name =
        data.name != null && String(data.name).trim() !== ""
            ? String(data.name)
            : "—";
    return renderStatsBar([
        { label: "玩家名稱", value: name },
        { label: "填入結果", value: data.success ? "成功" : "失敗" },
    ]);
}

function getPlayerInfoResultLabel(verifyType) {
    const mapping = PLAYER_INFO_VALUE_FIELDS[verifyType];
    return mapping ? mapping[1] : "填入內容";
}

function getPlayerInfoResultValue(item) {
    const verifyType = Number(item.requireType ?? item.verifyType);
    const mapping = PLAYER_INFO_VALUE_FIELDS[verifyType];
    const field = mapping ? mapping[0] : null;
    if (!field || item[field] == null || String(item[field]).trim() === "") {
        return "—";
    }
    return String(item[field]);
}

function renderVerifyPlayerInfoResult(data) {
    const source = Array.isArray(data.results) && data.results.length === 1 ? data.results[0] : data;
    const verifyType = Number(source.requireType ?? source.verifyType);
    const label = getPlayerInfoResultLabel(verifyType);
    const value = getPlayerInfoResultValue(source);
    return renderStatsBar([
        { label, value },
        { label: "驗證結果", value: source.success ? "成功" : "失敗" },
    ]);
}

function renderVerifyPlayerInfoMultiResult(data) {
    const results = Array.isArray(data.results) ? data.results : [];
    const successCount = results.filter((item) => item.success).length;
    const summary = renderStatsBar(
        [
            { label: "共執行", numeric: results.length, suffix: "項" },
            { label: "成功", numeric: successCount, suffix: "項" },
            { label: "失敗", numeric: results.length - successCount, suffix: "項", dimZero: true },
        ],
        { columns: 3 }
    );

    const items = results
        .map((item) => {
            const verifyType = Number(item.requireType ?? item.verifyType);
            const label = getPlayerInfoResultLabel(verifyType);
            const value = getPlayerInfoResultValue(item);
            return `
        <article class="result-task-item result-player-info-item">
            <div class="result-task-main">
                <div class="result-task-content">
                    <div class="result-task-row-top">
                        <div class="result-task-ids">
                            ${renderIssueKey(label, { plain: true })}
                        </div>
                        ${renderStatusBadge(item.success ? "成功" : "失敗")}
                    </div>
                    <p class="result-task-summary">${escapeHtml(value)}</p>
                </div>
            </div>
        </article>`;
        })
        .join("");

    return `${summary}<div class="result-task-list">${items}</div>`;
}

function renderCustomerIdResult(data) {
    const customerId =
        data.data?.customer_id != null && String(data.data.customer_id).trim() !== ""
            ? String(data.data.customer_id)
            : "—";
    return renderStatsBar([
        { label: "玩家 ID", value: customerId },
        { label: "查詢結果", value: data.success ? "成功" : "失敗" },
    ]);
}

function renderCustomerNameResult(data) {
    const customerName =
        data.data?.customer_id != null && String(data.data.customer_id).trim() !== ""
            ? String(data.data.customer_id)
            : "—";
    return renderStatsBar([
        { label: "玩家帳號", value: customerName },
        { label: "查詢結果", value: data.success ? "成功" : "失敗" },
    ]);
}

function renderManualSingleConfirmResult(data) {
    return renderStatsBar([
        { label: "Promo Type", value: getPromoTypeFromResult(data) },
        { label: "結果", value: data.success ? "成功" : "失敗" },
    ]);
}

function renderFormattedResult(data, resultType) {
    if (resultType === "calculate_workdays") {
        return renderWorkdaysReport(data.data);
    }
    if (resultType === "excel_progress") {
        return renderExcelProgressReport(data.data);
    }
    if (resultType === "create_qa_task") {
        return renderCreateQaTaskResults(data.data);
    }
    if (resultType === "postcard") {
        return renderPostCardResult(data);
    }
    if (resultType === "manual_single_confirm") {
        return renderManualSingleConfirmResult(data);
    }
    if (resultType === "verify_mobile") {
        return renderVerifyMobileResult(data);
    }
    if (resultType === "verify_id") {
        return renderVerifyIdResult(data);
    }
    if (resultType === "verify_name") {
        return renderVerifyNameResult(data);
    }
    if (resultType === "verify_player_info") {
        return renderVerifyPlayerInfoResult(data);
    }
    if (resultType === "verify_player_info_multi") {
        return renderVerifyPlayerInfoMultiResult(data);
    }
    if (resultType === "customer_id") {
        return renderCustomerIdResult(data);
    }
    if (resultType === "customer_name") {
        return renderCustomerNameResult(data);
    }

    return `<p class="result-message">${escapeHtml(data.message || "操作已完成")}</p>`;
}

function closeResultModal() {
    const modal = document.getElementById("result-modal");
    if (!modal || modal.classList.contains("hidden")) return;

    modal.classList.remove("is-visible");
    window.setTimeout(() => {
        if (!modal.classList.contains("is-visible")) {
            modal.classList.add("hidden");
        }
    }, 180);
}

