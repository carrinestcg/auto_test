function toggleInput() {
    const amountInputDiv = document.getElementById("amount-input-div");
    const ticket_select = document.getElementById("frontend-checkbox_select");
    const ticket_input = document.getElementById("ticket-input-div");
    const promotion_id_Input = document.getElementById("promotion_id-input-div");
    const manual_platform_select = document.getElementById("frontend-checkbox_manual_platform");
    const ticket_id_input = document.getElementById("ticket_id-input-div");
    const customer_detail=document.getElementById("frontend-checkbox_id");
    const requireamount = document.getElementById("frontend-checkbox_lott").checked ||document.getElementById("frontend-checkbox").checked;
    const requirePromotion_id = document.getElementById("frontend-checkbox_manual").checked ||document.getElementById('frontend-checkbox_7_Ticket').checked;
    const requireTicket_input = document.getElementById("frontend-checkbox_manual").checked;
    const checkbox = document.getElementById("frontend-checkbox_ticket");
    const register_checkbox = document.getElementById("frontend-checkbox_new");
    const deposit_checkbox = document.getElementById('DEPOSIT_API_script');
    const manual_checkbox = document.getElementById("frontend-checkbox_manual");
    const APP_Download_CheckBox=document.getElementById("APP_Download_API");
    const ticket_select_checkbox = document.getElementById("frontend-checkbox_7_Ticket");
    const receive_reward = document.getElementById("frontend-bonus-batch");
    const receive_ticket = document.getElementById("frontend-ticket-batch");
    const Change_password=document.getElementById("Change_password");
    const hasSelectTicket = Array.from(ticket_select.selectedOptions).length > 0;
    const hasPlatformSelect = Array.from(manual_platform_select.selectedOptions).length > 0;
    

    amountInputDiv.classList.toggle("hidden", !requireamount);
    ticket_select.style.display = checkbox.checked ? "block" : "none";
    manual_platform_select.style.display = (register_checkbox.checked || deposit_checkbox.checked || manual_checkbox.checked||ticket_select_checkbox.checked||receive_reward.checked||receive_ticket.checked||customer_detail.checked||Change_password.checked||APP_Download_CheckBox.checked) ? "block" : "none";
    ticket_input.style.display = (checkbox.checked && hasSelectTicket) ? "block" : "none";
    promotion_id_Input.classList.toggle("hidden", !requirePromotion_id);
    ticket_id_input.classList.toggle("hidden", !requireTicket_input);
}

function checkpassword() {
    const pwd = document.getElementById("password");
    const usernameInputDiv = document.getElementById("username");
    const amount = document.getElementById("amount");
    const TicketName=document.getElementById("ticket_id")
    const needUsername = document.getElementById("frontend-checkbox_new").checked ||
        document.getElementById("frontend-checkbox_lott").checked ||
        document.getElementById("frontend-checkbox").checked ||
        document.getElementById("frontend-checkbox_id").checked ||
        document.getElementById("frontend-checkbox_manual").checked ||
        document.getElementById("frontend-checkbox_7_Ticket").checked ||
        document.getElementById("frontend-player-rank").checked||
        document.getElementById('frontend-promo-batch').checked||
        document.getElementById('frontend-bonus-batch').checked||
        document.getElementById('frontend-ticket-batch').checked;
    const needAmount = document.getElementById("frontend-checkbox").checked

    if (needAmount && (!amount.value || amount.value.trim() === "")) {
        document.getElementById("amount_hint").style.display = "inline";
        return false; 
    }else{
        document.getElementById("amount_hint").style.display = "none";
    };

    amount.addEventListener("input",()=>{
        if (amount.value.trim()!==""){
        document.getElementById("amount_hint").style.display = "none";
    }
    });

    
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
    };

    return true;
}

document.getElementById('selectALL').addEventListener('click', (e) => {
    e.preventDefault();
    const active_tab = document.querySelector('.tabcontent.active');
    const checkboxs = active_tab.querySelectorAll('input[type="checkbox"]');
    const select = active_tab.querySelectorAll('select');
    checkboxs.forEach(checkbox => checkbox.checked = true);
    toggleInput();
});

document.getElementById('unselectALL').addEventListener('click', (e) => {
    e.preventDefault();
    const active_tab = document.querySelector('.tabcontent.active');
    const checkboxs = active_tab.querySelectorAll('input[type="checkbox"]');
    const select = active_tab.querySelectorAll('select');
    checkboxs.forEach(checkbox => checkbox.checked = false);

    select.forEach(select => {
        Array.from(select.options).forEach(option => option.selected = false);
    });
    toggleInput();
});

['frontend-checkbox_select_platform', 'frontend-checkbox_manual_platform','frontend-checkbox_7_Ticket_select','frontend-checkbox_manual']
    .forEach(id => {
        document.getElementById(id).addEventListener('change', function() {
            const alloption = this.querySelector('option[value="ALL"]');
            const otheroption = Array.from(this.options).filter(option => option.value !== 'ALL');

            if (alloption && alloption.selected) {
                otheroption.forEach(option => option.selected = true);
                alloption.selected = false;
            }
            toggleInput();
        });
    });

['frontend-checkbox_select', 'frontend-checkbox_select_platform', 'frontend-checkbox_manual_platform','frontend-checkbox_7_Ticket_select','frontend-checkbox_manual']
    .forEach(id => {
        document.getElementById(id).addEventListener('mousedown', function(e) {
            e.preventDefault();
            const option = e.target;
            
            if (option.tagName === 'OPTION') {
                option.selected = !option.selected;
                this.dispatchEvent(new Event('change'));
            }
        });
    });

function switchTab(evt, tabId) {
    document.querySelectorAll('.tabcontent').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
    evt.currentTarget.classList.add('active');
}

window.addEventListener('load', () => {
    toggleInput();
    const loading=document.getElementById('loading');
    if(loading){
        loading.classList.remove('show');
    }
});
window.addEventListener('pageshow', (event) => {
    const loading = document.getElementById('loading');
    if (loading) {
        loading.classList.remove('show');
    }
});
let formState = {};
document.querySelectorAll('input, select').forEach(el => {
    el.addEventListener('input', () => {
        if (el.type === 'checkbox') {
            formState[el.name || el.id] = el.checked;
        } else {
            formState[el.name || el.id] = el.value;
        }
    });
});
const form=document.getElementById('myForm');
const loading =document.getElementById('loading');

let isSubmitting= false;
form.addEventListener('submit',function(e){
    if(isSubmitting){
        console.log('Form is submitting...');
        return true;
    }
    e.preventDefault();
    if(!checkpassword()){
        return false;
    }
    isSubmitting=true;

    loading.classList.add('show');
    setTimeout(()=>{
        console.log('Submitting form...');
        form.submit();
    },100);
    return false;
});

document.getElementById('uploadform').addEventListener('submit',async(e)=>{
    e.preventDefault();
    const formdata=new FormData();
    const fileInput=document.getElementById('fileInput');
    const loading=document.getElementById('loading');
    const uploadHint=document.getElementById('upload_hint');
    if (!fileInput.files.length){
        uploadHint.style.display="inline";
        alert('請選擇要上傳的 Excel 檔案');
        return;
    }else{
        uploadHint.style.display="none";
    };
    loading.classList.add('show');
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
        loading.classList.remove('show');
    }
});
document.getElementById('Compare_Two_Excel').addEventListener('submit',async(e)=>{
    e.preventDefault();
    const formdata=new FormData();
    const fileInput_1=document.getElementById('fileInput_1');
    const fileInput_2=document.getElementById('fileInput_2');
    const loading=document.getElementById('loading');
    const uploadHint=document.getElementById('upload_hint');
    if (!fileInput_1.files.length||!fileInput_2.files.length){
        uploadHint.style.display="inline";
        alert('請選擇要上傳的 Excel 檔案');
        return;
    }else{
        uploadHint.style.display="none";
    };
    loading.classList.add('show');
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
        loading.classList.remove('show');
    }
});
