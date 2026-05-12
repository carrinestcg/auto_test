function toggleInput() {
    toggleAmount();
    toggleTicket();
    togglePromotion();
    togglePromotionTypeList();
    togglePlatform();
    toggleRoundID();
}

function toggleAmount(){
    const isChecked = id => document.getElementById(id)?.checked;
    const amountInputDiv = document.getElementById("amount-input-div");
    const requireamount = isChecked("frontend-checkbox_lott")||isChecked("frontend-checkbox")||isChecked("frontend-checkbox_manual")||isChecked("frontend-checkbox_member");
    if (!amountInputDiv) return
    amountInputDiv.classList.toggle("hidden", !requireamount);
}
function toggleTicket() {
    const ticket_select = document.getElementById("frontend-checkbox_select");
    const ticket_input = document.getElementById("ticket-input-div");
    const ticket_id_input = document.getElementById("ticket_id-input-div");
    const manual_cb = document.getElementById("frontend-checkbox_manual");
    const requireTicket_input = manual_cb && manual_cb.checked;
    const checkbox = document.getElementById("frontend-checkbox_ticket");
    const hasSelectTicket = ticket_select && Array.from(ticket_select.selectedOptions).length > 0;

    if (!ticket_select || !checkbox) return;
    ticket_select.classList.toggle("hidden", !checkbox.checked);
    ticket_input.classList.toggle("hidden", !(checkbox.checked && hasSelectTicket));
    if (ticket_id_input) ticket_id_input.classList.toggle("hidden", !requireTicket_input);
}
function togglePromotion() {
    const promotion_id_Input = document.getElementById("promotion_id-input-div");
    const requirePromotion_id = document.getElementById("frontend-checkbox_manual").checked ||document.getElementById('frontend-checkbox_7_Ticket').checked;
    
    promotion_id_Input.classList.toggle("hidden", !requirePromotion_id);

}
/** 勾選「創建活動」時顯示活動類型多選（#promotion-checkbox_select） */
function togglePromotionTypeList() {
    const wrap = document.getElementById("promotion-type-select-wrap");
    const promoSelect = document.getElementById("promotion-checkbox_select");
    const need =
        document.getElementById("auto_create_promotion") &&
        document.getElementById("auto_create_promotion").checked;
    if (!promoSelect) return;
    if (wrap) {
        wrap.classList.toggle("hidden", !need);
    }
    promoSelect.classList.toggle("hidden", !need);
}
function toggleRoundID(){
    const Compensation=document.getElementById("Compensation_api");
    const RoundID_input=document.getElementById("round_id-input-div");
    if (!Compensation || !RoundID_input) return;
    RoundID_input.classList.toggle("hidden", !Compensation.checked);
}
/** 任一測試腳本被勾選時顯示平台（API 皆會帶 platforms；未選時後端預設 gi8viet）。 */
function togglePlatform() {
    const manual_platform_select = document.getElementById("frontend-checkbox_manual_platform");
    if (!manual_platform_select) return;
    const anyScriptChecked = document.querySelector("input[name=\"script\"]:checked") !== null;
    manual_platform_select.classList.toggle("hidden", !anyScriptChecked);
}
const amountInput = document.getElementById("amount");
if (amountInput){
    amountInput.addEventListener("input",()=>{
        if (amountInput.value.trim()!==""){
        document.getElementById("amount_hint").style.display = "none";
    }});
}
function validateFormBeforeSubmit() {
    const pwd = document.getElementById("password");
    const usernameInputDiv = document.getElementById("username");
    const needUsername = document.getElementById("frontend-checkbox_new").checked ||
        document.getElementById("frontend-checkbox_lott").checked ||
        document.getElementById("frontend-checkbox").checked ||
        document.getElementById("frontend-checkbox_id").checked ||
        document.getElementById("frontend-checkbox_manual").checked ||
        document.getElementById("frontend-checkbox_7_Ticket").checked ||
        document.getElementById("frontend-player-rank").checked||
        document.getElementById('frontend-promo-batch').checked||
        document.getElementById('frontend-bonus-batch').checked||
        document.getElementById('frontend-ticket-batch').checked||
        document.getElementById('frontend-checkbox_member').checked;
        const amountDiv = document.getElementById("amount-input-div");
        const needAmount = amountDiv && !amountDiv.classList.contains("hidden");
        
    if (needAmount && (!amountInput || amountInput.value.trim() === "")) {
        document.getElementById("amount_hint").style.display = "inline";
        console.log("❌ 被 amount 擋");
        return false; 
    }else{
        document.getElementById("amount_hint").style.display = "none";
    };

    
    if (needUsername && !usernameInputDiv.value.trim()) {
        document.getElementById("username_hint").style.display = "inline";
        document.getElementById("password_hint").style.display = "inline";
        document.querySelector("button[type=submit]").disabled = false;
        document.querySelector("button[type=submit]").innerText = "開始測試";
        return false;
    } else {
        document.getElementById("username_hint").style.display = "none";
    };

    if (!pwd.value.trim()) {
        pwd.value = "123qwe";
    }

    const autoPromoCb = document.getElementById("auto_create_promotion");
    if (autoPromoCb && autoPromoCb.checked) {
        const promoSel = document.getElementById("promotion-checkbox_select");
        if (promoSel && Array.from(promoSel.selectedOptions).length === 0) {
            alert("請至少選擇一種活動類型（活動類型複選）");
            return false;
        }
    }

    return true;
}
['frontend-checkbox_select_platform', 'frontend-checkbox_manual_platform','frontend-checkbox_7_Ticket_select', 'promotion-checkbox_select']
    .forEach(id => {
        const el=document.getElementById(id);
        if (!el){
            return;
        }
        el.addEventListener('change', function() {
            if(!this.options){
                toggleInput();
                return;
            }
            const alloption = this.querySelector('option[value="ALL"]');
            const otheroption = Array.from(this.options).filter(option => option.value !== 'ALL');
            const anyOtherSelected = otheroption.some((o) => o.selected);

            // 「全部」與「只選部分類型」不可同時為 true；否則會誤觸發「全選其餘」分支（例如 HTML 曾預設 ALL selected）
            if (alloption && alloption.selected && anyOtherSelected) {
                alloption.selected = false;
            }

            if (alloption && alloption.selected) {
                otheroption.forEach(option => option.selected = true);
                alloption.selected = false;
            }
            toggleInput();
        });
    });

['frontend-checkbox_select', 'frontend-checkbox_select_platform', 'frontend-checkbox_manual_platform','frontend-checkbox_7_Ticket_select', 'promotion-checkbox_select']
    .forEach(id => {
        const el=document.getElementById(id);
        if (!el){
            return;
        }
        el.addEventListener('mousedown', function(e) {
            const option = e.target;
            if (option.tagName === 'OPTION') {
                e.preventDefault();
                option.selected = !option.selected;
                this.dispatchEvent(new Event('change'));
            }
        });
    });

document.addEventListener("DOMContentLoaded", function () {
    toggleInput();
});

function switchTab(evt, tabId) {
    document.querySelectorAll('.tabcontent').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
    evt.currentTarget.classList.add('active');
}

function showLoading(show=true){
    const loading=document.getElementById('loading');
    if (!loading) return;
    loading.classList.toggle('show', show);
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
    checkSelectScript.forEach(scriptName=>{
        let extraData={}
    
    switch (scriptName) {
        case "SIGLE_PROMO_7_TICKET":
            extraData = {
                promotion_id: document.getElementById("promotion_id").value,
            };
            break;

        case "MANUAL_CREATE_SINGLE_CONFIRM":
            extraData = {
                promotion_id: document.getElementById("promotion_id").value,
                ticket_id: document.getElementById("ticket_id").value,
                amount: document.getElementById("amount").value,
            };
            break;

        case "auto_create_ticket":
            extraData = {
                ticket_type: ticket_types,
                ticket_input: document.getElementById("ticket_input").value,
            };
            break;

        case "auto_create_promotion": {
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
                amount: document.getElementById("amount").value,
            };
            break;

        case "create_member_player":
            extraData = {
                amount: document.getElementById("amount").value,
            };
            break;

        case "FRONTEND_DEPOSIT":
            extraData = {
                amount: document.getElementById("amount").value,
            };
            break;

        case "Compensation_api":
            extraData = {
                round_id: document.getElementById("round_id").value,
            };
            break;

        case "Extra_Reward_api": {
            const rawTickets = document.getElementById("ticket_id").value.trim();
            const ticket_id_list = rawTickets
                ? rawTickets.split(/[\s,]+/).filter(Boolean)
                : [];
            extraData = {
                ticket_id_list,
                amount: document.getElementById("amount").value,
                promotion_id: document.getElementById("promotion_id").value,
                "deposit-amount-id": document.getElementById("deposit-amount-id").value,
                extra_promo_id: document.getElementById("extra_promo_id").value,
            };
            break;
        }

        case "Verify_Mobile_No":
            extraData = { type: 1 };
            break;

        case "Verify_Personal_ID":
            extraData = { type: 2 };
            break;

        case "PROMOCODE_BATCH":
        case "BONUS_BATCH":
        case "TICKET_BATCH":
        case "MANUAL_SIGN":
        case "MANUAL_SINGLE":
        case "MANUAL_BATCH":
        case "Codition_create_bonus":
        case "PLAYER_RANK":
        case "auto_create_player":
        case "Customer_id":
        case "SameTimeLogin":
        case "DEPOSIT_API":
        case "APP_Download":
        case "PostCard_api":
        case "Change_password":
        case "Single_Manual_create":
        case "test_Extra_bonus":
            extraData = {};
            break;

        default:
            extraData = {};
            console.warn("[runSelectScript] 未定義腳本，使用空 extraData:", scriptName);
    }
    
    
    runScriptApi(scriptName,{username,platforms,...extraData})
})
}

function runScriptApi(scriptName,payload){
    showLoading(true);
    fetch(`/api/${scriptName}`,{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify(payload)
    })
    .then(res=>res.json())
    .then(data=>{
        console.log(scriptName,data);
        showResultPopup(data);
}).catch(err=>{
    showResultPopup({
        success:false,
        message: "API 呼叫失敗：" + err
    });
}).finally(()=>{
    showLoading(false);
});
}
function showResultPopup(data) {
    const modal=document.getElementById("result-modal");
    const header=document.getElementById("modal-header");
    const body=document.getElementById("modal-body");
    modal.classList.remove("hidden");

    if (data.success) {
        header.className = "modal-header success";
        header.innerText = "Action Success";
    }
    else {
        header.className = "modal-header fail";
        header.innerText = "Action Failed";
    }
    body.innerText=JSON.stringify(data,null,2);
        
}
function closeResultModal(){
    document.getElementById("result-modal").classList.add("hidden")
}

