/**
 * flask_ux.js — UI/UX 增強層（載入於 flask_script.js 之後）
 * 不改動原本流程：只「搬移」既有節點、補上少量新節點，並包裝既有全域函式。
 * 所有原本的 id 都保留，flask_script.js 不需要任何修改。
 */
(function () {
    "use strict";

    const $ = (id) => document.getElementById(id);
    const setText = (id, text) => {
        const el = $(id);
        if (el) el.textContent = text;
    };
    const make = (tag, className, html) => {
        const node = document.createElement(tag);
        if (className) node.className = className;
        if (html != null) node.innerHTML = html;
        return node;
    };

    /* ---------- 1. 版面重組（只搬移、不複製） ---------- */
    function buildLayout() {
        const main = document.querySelector(".center-panel");
        const form = $("myForm");
        if (!main || !form || main.dataset.uxBuilt === "true") return;
        main.dataset.uxBuilt = "true";

        // 「常用場景」搬到表單上方，改名為「快速開始」
        const assist = $("operation-assist");
        if (assist) {
            assist.classList.add("strip");
            main.insertBefore(assist, form);
            setText("operation-assist-heading", "快速開始");
            const desc = assist.querySelector(".scenario-panel-desc");
            if (desc) desc.textContent = "一鍵套用常用組合：自動勾選項目、切換分頁、帶入預設值。";
        }

        buildScriptsHeader();
        buildConfigCard();
        buildRunDock(main);
    }

    // 測試功能選擇：標題旁加「已選 N」，右側加搜尋與清除
    function buildScriptsHeader() {
        const heading = $("scripts-heading");
        const header = heading && heading.closest(".card-header");
        if (!header) return;

        const group = make("div", "card-title-group");
        header.insertBefore(group, heading);
        group.appendChild(heading); // 保留同一個節點，switchTab 改 textContent 才不會壞
        const pill = make("span", "count-pill", "已選 0");
        pill.id = "selected-count-pill";
        pill.hidden = true;
        group.appendChild(pill);

        const tools = make("div", "card-tools", `
            <div class="search-field">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>
                <input type="text" id="script-search" autocomplete="off" aria-label="搜尋測試項目">
            </div>
            <button type="button" class="btn-ghost" id="clear-selection-btn" disabled>清除</button>`);
        tools.id = "scripts-tools";
        header.appendChild(tools);
        $("clear-selection-btn").addEventListener("click", () => {
            if (typeof window.clearScenarioSelection === "function") window.clearScenarioSelection();
        });

        const panels = document.querySelector(".tab-panels");
        if (panels) {
            const empty = make("p", "search-empty hidden", "找不到符合的測試項目，換個關鍵字試試。");
            empty.id = "search-empty";
            panels.appendChild(empty);
        }
    }

    // 帳號與參數：改名 + 尚未選擇時的空狀態
    function buildConfigCard() {
        setText("config-heading", "帳號與參數");
        const body = document.querySelector("#account-config-card .card-body");
        if (!body) return;
        const empty = make("div", "params-empty", `
            <span class="params-empty-icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>
            </span>
            <p class="params-empty-title">先從上方勾選測試項目</p>
            <p class="params-empty-desc">選好之後，這裡只會出現該項目需要填寫的欄位。</p>`);
        empty.id = "params-empty";
        body.insertBefore(empty, body.firstChild);
    }

    // 執行按鈕搬到底部固定列（按鈕、提示的 id 不變）
    function buildRunDock(main) {
        const row = document.querySelector(".account-run-row");
        if (!row) return;
        const actions = row.querySelector(".account-run-actions");
        const hint = $("run-test-hint");

        const dock = make("div", "run-dock");
        dock.id = "run-dock";
        const info = make("div", "run-dock-info");
        const summary = make("p", "run-dock-summary", "尚未選擇測試項目");
        summary.id = "dock-summary";
        info.appendChild(summary);
        if (hint) info.appendChild(hint);
        dock.appendChild(info);
        if (actions) dock.appendChild(actions);
        // 放進「帳號與參數」卡片底部：填完欄位，按鈕就在正下方
        const card = $("account-config-card");
        (card || main).appendChild(dock);
        row.remove();
    }

    /* ---------- 2. 已選項目 / 空狀態 / 執行列摘要 ---------- */
    function selectedLabels() {
        return Array.from(document.querySelectorAll('input[name="script"]:checked')).map((input) => {
            const label = input.closest("label");
            return (label ? label.textContent : input.value).replace(/\s+/g, " ").trim();
        });
    }

    function updateSelectionUI() {
        const labels = selectedLabels();
        const n = labels.length;

        $("account-config-card")?.classList.toggle("is-empty", n === 0);

        const pill = $("selected-count-pill");
        if (pill) {
            pill.hidden = n === 0;
            pill.textContent = `已選 ${n}`;
        }
        const clearBtn = $("clear-selection-btn");
        if (clearBtn) clearBtn.disabled = n === 0;

        let platform = "";
        try {
            platform = getSelectedPlatforms()[0] || "";
        } catch (e) {}
        const wrap = $("platform-select-wrap");
        const platformVisible = wrap && !wrap.classList.contains("hidden");
        setText(
            "dock-summary",
            n === 0 ? "尚未選擇測試項目" : `已選 ${n} 項` + (platformVisible && platform ? ` · 平台 ${platform}` : "")
        );
        renderOffTabSelection();
    }

    function tabTitle(tabId) {
        if (!tabId) return "";
        const btn = Array.from(document.querySelectorAll(".nav-item, .tab-version-btn")).find((node) => {
            const onclick = node.getAttribute("onclick") || "";
            return onclick.includes(`'${tabId}'`);
        });
        return (btn && btn.querySelector(".nav-label")?.textContent.trim()) || tabId;
    }

    function renderOffTabSelection() {
        const panels = document.querySelector(".tab-panels");
        if (!panels) return;
        let host = $("offtab-selection");
        if (!host) {
            host = make("div", "offtab-selection");
            host.id = "offtab-selection";
            host.hidden = true;
            panels.parentElement.insertBefore(host, panels);
        }

        const activePanel = document.querySelector(".tab-panels > .tabcontent.active");
        const missing = Array.from(document.querySelectorAll('input[name="script"]:checked')).filter(
            (input) => !activePanel || !activePanel.contains(input)
        );
        if (!missing.length) {
            host.hidden = true;
            host.replaceChildren();
            return;
        }

        host.hidden = false;
        host.replaceChildren();
        const title = make("p", "offtab-selection-title", "已選項目不在這個分類");
        host.appendChild(title);

        missing.forEach((input) => {
            const label = input.closest("label");
            const name = (label ? label.textContent : input.value).replace(/\s+/g, " ").trim();
            const panel = input.closest(".tabcontent");
            const row = make("div", "offtab-chip");
            const nameEl = make("span", "offtab-name");
            nameEl.textContent = name;
            const catEl = make("span", "offtab-cat");
            catEl.textContent = tabTitle(panel && panel.id);
            const jump = make("button", "btn-ghost offtab-jump", "前往分類");
            jump.type = "button";
            jump.addEventListener("click", () => {
                if (panel && typeof activateTab === "function") activateTab(panel.id);
            });
            const remove = make("button", "btn-ghost offtab-remove", "取消");
            remove.type = "button";
            remove.addEventListener("click", () => {
                input.checked = false;
                if (typeof toggleInput === "function") toggleInput();
            });
            row.append(nameEl, catEl, jump, remove);
            host.appendChild(row);
        });
    }

    /* ---------- 4. 搜尋測試項目（跨分頁） ---------- */
    function applySearch(raw) {
        const q = (raw || "").trim().toLowerCase();
        const section = $("scripts-section");
        const empty = $("search-empty");
        if (!section) return;

        section.classList.toggle("is-searching", !!q);

        let totalMatches = 0;
        document.querySelectorAll(".tab-panels > .tabcontent").forEach((panel) => {
            let matches = 0;
            panel.querySelectorAll(".script-grid label").forEach((label) => {
                if (label.classList.contains("hidden")) return;
                const hit = !q || label.textContent.toLowerCase().includes(q);
                label.classList.toggle("is-filtered", !hit);
                if (hit) matches += 1;
            });
            panel.querySelectorAll(".script-category").forEach((cat) => {
                const any = cat.querySelector(".script-grid label:not(.is-filtered)");
                cat.classList.toggle("no-match", !!q && !any);
            });
            panel.classList.toggle("no-match", !!q && matches === 0);
            totalMatches += q ? matches : 0;
        });

        if (empty) empty.classList.toggle("hidden", !(q && totalMatches === 0));
    }

    function initSearch() {
        const input = $("script-search");
        if (!input) return;
        input.addEventListener("input", () => applySearch(input.value));
        input.addEventListener("keydown", (e) => {
            if (e.key === "Escape") {
                input.value = "";
                applySearch("");
                input.blur();
            }
        });
        document.addEventListener("keydown", (e) => {
            if (e.key !== "/" || e.ctrlKey || e.metaKey || e.altKey) return;
            const t = e.target;
            if (t instanceof Element && t.closest("input, textarea, select, [contenteditable]")) return;
            e.preventDefault();
            input.focus();
            input.select();
        });
    }

    /* ---------- 5. 包裝既有全域函式 ---------- */
    function wrap(name, hooks) {
        const original = window[name];
        if (typeof original !== "function") return;
        window[name] = function () {
            try {
                hooks.before && hooks.before.apply(this, arguments);
            } catch (e) {
                console.warn("[flask_ux]", name, "before", e);
            }
            const result = original.apply(this, arguments);
            try {
                hooks.after && hooks.after.apply(this, arguments);
            } catch (e) {
                console.warn("[flask_ux]", name, "after", e);
            }
            return result;
        };
    }

    wrap("toggleInput", { after: updateSelectionUI });
    wrap("switchTab", {
        before: function (evt, tabId) {
            // 切換分頁先清掉搜尋，避免停在「全部分頁展開」
            const input = $("script-search");
            if (input && input.value) {
                input.value = "";
                applySearch("");
            }
            // Excel 分頁沒有可勾選項目，隱藏搜尋與清除
            const tools = $("scripts-tools");
            if (tools) tools.hidden = tabId === "ExcelTab";
        },
        after: updateSelectionUI,
    });

    function upgradeAppSelects() {
        document.querySelectorAll("select.app-select").forEach((select) => {
            if (select.dataset.upgraded === "true") return;
            select.dataset.upgraded = "true";
            const wrap = make("div", "app-select");
            select.parentNode.insertBefore(wrap, select);
            select.classList.remove("app-select");
            select.classList.add("app-select-native");
            select.tabIndex = -1;
            wrap.appendChild(select);

            const trigger = make("button", "app-select-trigger");
            trigger.type = "button";
            trigger.setAttribute("aria-haspopup", "listbox");
            const value = make("span", "app-select-value");
            const chevron = make("span", "app-select-chevron", `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>`);
            trigger.append(value, chevron);

            const menu = make("div", "jira-suggest-menu app-select-menu hidden");
            menu.setAttribute("role", "listbox");
            Array.from(select.options).forEach((option) => {
                const item = make("button", "jira-suggest-item", option.textContent);
                item.type = "button";
                item.dataset.value = option.value;
                item.setAttribute("role", "option");
                item.addEventListener("click", () => {
                    select.value = option.value;
                    select.dispatchEvent(new Event("change", { bubbles: true }));
                    close();
                });
                menu.appendChild(item);
            });

            function paint() {
                const current = select.options[select.selectedIndex];
                value.textContent = current ? current.textContent : "";
                menu.querySelectorAll(".jira-suggest-item").forEach((item) => {
                    const on = item.dataset.value === select.value;
                    item.classList.toggle("is-selected", on);
                    item.setAttribute("aria-selected", on ? "true" : "false");
                });
            }
            function close() {
                menu.classList.add("hidden");
                wrap.classList.remove("is-open");
                trigger.setAttribute("aria-expanded", "false");
            }
            trigger.addEventListener("click", () => {
                const open = menu.classList.contains("hidden");
                document.querySelectorAll(".app-select-menu").forEach((node) => node.classList.add("hidden"));
                document.querySelectorAll(".app-select.is-open").forEach((node) => node.classList.remove("is-open"));
                if (open) {
                    menu.classList.remove("hidden");
                    wrap.classList.add("is-open");
                    trigger.setAttribute("aria-expanded", "true");
                } else {
                    close();
                }
            });
            document.addEventListener("click", (event) => {
                if (!wrap.contains(event.target)) close();
            });
            select.addEventListener("change", paint);
            wrap.append(trigger, menu);
            paint();
        });
    }

    /* ---------- 6. 啟動 ---------- */
    function init() {
        buildLayout();
        upgradeAppSelects();
        initSearch();
        updateSelectionUI();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();