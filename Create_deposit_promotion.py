import requests,logging,time,yaml,os
from datetime import datetime,timedelta
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from deposit_api import batch_approve

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
def unit_time():
    current_time=datetime.now()
    unit_time=str(int(current_time.timestamp()*1000))
    return unit_time
    
class Backend:
    
    def __init__(self,credential_be:str):
        self.session=requests.Session()
        self.credential_be=credential_be
        self.token_expire=None
        self.type=''
        self.token_backend=self.get_token_backend(credential_be['operatorName'],credential_be['password'])
        self.token=self.token_backend
    def header(self):
         return {
             
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "Authorization": self.token,
                "Content-Type": "application/json",
                "Connection": "keep-alive",
                "Language": "zh_CN",
                "Merchant": "gi8viet",
                "MerchantCode": "gi8viet",
                "Tac-Trace-Id":"OoL7ntxjBpmiQPeM",
                "Referer": f"http://sit-admin2.tcg.com/24782",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
                "environment": "TCG3",
                "notPending": "true",
                "platform": "TCG"
            
         }
    def header_new(self):
        return{
            "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "Authorization": self.token,
                "Content-Type": "application/json",
                "Connection": "keep-alive",
                "Language": "zh_CN",
                "Merchant": "gi8viet",
                "MerchantCode": "gi8viet",
                "Tac-Trace-Id":"OoL7ntxjBpmiQPeM",
                "Referer": f"http://sit-admin2.tcg.com/24780",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
                "environment": "TCG3",
                "notPending": "true",
                "platform": "TCG"
        }
    def get_token_backend(self,operatorName,password):
        login_url="http://sit-admin2.tcg.com/tac/api/login/password"
        payload={
            "operatorName": operatorName,
            "password": password
        }
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Authorization": "",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Merchant": "gi8viet",
            "MerchantCode": "gi8viet",
            "Origin": "http://sit-admin2.tcg.com",
            "Referer": "http://sit-admin2.tcg.com/",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "environment": "",
            "language": "zh_CN",
            "noErrorNotice": "true",
            "platform": ""
        }
        
        cookies = {
            "language": "zh_CN"
        }
        requests_data=requests.post(login_url,json=payload,headers=headers,cookies=cookies,verify=False)
        token_data=requests_data.json()
        token=token_data.get("token")
        logging.info(f"登入API回傳: {token}")
        return token
    def unitTime(self):
        start_time = datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)
        unix_starttime=int(start_time.timestamp()*1000)
        end_time = datetime.now().replace(hour=23,minute=59,second=59,microsecond=0)
        unix_endttime=int(end_time.timestamp()*1000)
        return unix_starttime, unix_endttime
    def create_fisrt_deposit_promotion(self,type):
        start_Time,endTime=self.unitTime()
        try: 
            url="http://sit-admin2.tcg.com/tac/api/relay/post/mcs-depositPromotion-add"
            header=self.header()
            payload={
                
            "id": "",
            "merchantCode": "gi8viet",
            "name": f"carrine {type} deposit",
            "status": "A",
            "budget": "999888",
            "pointBudget": "999888",
            "budgetStr": "999888",
            "pointBudgetStr": "999888",
            "promotionType": type,
            "txType": 3119,
            "allowFirstDeposit": "N",
            "depositParticipant": "A",
            "depositMethods": [],
            "depositChannels": [],
            "productType": "RNG_OR_LIVE",
            "noExpiry": "Y",
            "startTime": start_Time,
            "startTimeString": "2025-07-14 00:00:00",
            "endTime": endTime,
            "endTimeString": "2025-07-14 00:00:00",
            "isFixedTime": "N",
            "fixedTimeSettings": [],
            "excludeRebate": "N",
            "excludeValidBet": "N",
            "excludePoints": "N",
            "withdrawMoneyLock": "N",
            "remarks": [
                {
                    "promotionId": None,
                    "remark": "<p>test</p>",
                    "language": "CN"
                }
            ],
            "forAllLabel": "Y",
            "participant": "ALL",
            "agents": [],
            "agentNames": "",
            "operationLabels": [],
            "totalContactNumbers": 0,
            "fileDetailList": [],
            "contactNumFileName": "",
            "restrictionType": "N",
            "vendors": [],
            "uniqueIp": "N",
            "claimMethod": "MANUAL",
            "effectiveTime": 0,
            "dailyCountLimit": "",
            "weeklyCountLimit": "",
            "monthlyCountLimit": "",
            "promotionCountLimit": "",
            "maxClaimCount": 1,
            "maxClaimCountType": "PROMOTION",
            "maxBonusAmount": "10000",
            "maxDailyPointAmount": "10000",
            "mobileVerified": "N",
            "ticketClaimMethod": "MANUAL",
            "playerRemark": "5",
            "promotionTicketBudget": {
                "1087006": {
                    "promotionId": "",
                    "ticketId": 1087006,
                    "ticketName": "",
                    "ticketBudget": 0
                }
            },
            "depositPromotionConfigs": [
                {
                    "bonusType": "PERCENTAGE",
                    "configId": "",
                    "turnoverMultiplier": 100,
                    "principalAndBonus": "",
                    "promotionId": "",
                    "turnoverType": "BONUS",
                    "depositPromotionConfigLabels": [],
                    "configDetail": [
                        {
                            "configId": None,
                            "minDepositAmount": 1,
                            "bonusPercentage": 100,
                            "minBonusAmount": 5,
                            "maxBonusAmount": 100,
                            "pointPercentage": 150,
                            "minPointAmount": 150,
                            "maxPointAmount": 150,
                            "minimumTurnover": 10,
                            "maximumTurnover": 156,
                            "ticketId": 1087006,
                            "ticketType": None,
                            "ticketName": None
                        }
                    ]
                }
            ],
            "promotionMessage": {
                "id": 2151043,
                "promotionId": 4023094,
                "defaultLanguageInbox": "CN",
                "defaultLanguagePushNotif": "CN",
                "contentInbox": [],
                "contentPushNotif": [],
                "contentInboxOneTime": None,
                "contentPushNotifOneTime": None,
                "contentInboxCont": None,
                "contentPushNotifCont": None,
                "contentInboxReferred": None,
                "contentPushNotifReferred": None,
                "contentInboxBettingRebate": None,
                "contentPushNotifBettingRebate": None,
                "contentInboxAchievementReward": None,
                "contentPushNotifAchievementReward": None,
                "allowMessage": None,
                "allowPushNotif": None
            },
            "activeKeyInbox": "",
            "activeKeyPushNotif": "",
            "allowMessage": "N",
            "allowPushNotif": "N",
            "linkedAnnouncementList": [],
            "languageInbox": "",
            "languagePushNotif": "",
            "withdrawalAccountRequired": "N",
            "bankCardRequired": "N",
            "virtualWalletRequired": "N",
            "electronicWalletRequired": "N",
            "emailRequired": "N",
            "qqRequired": "N",
            "zaloRequired": "N",
            "payeeNameRequired": "N",
            "lineRequired": "N",
            "wechatRequired": "N",
            "facebookRequired": "N",
            "whatsappRequired": "N",
            "addressRequired": "N",
            "contactNumberRequired": "N",
            "telegramRequired": "N",
            "viberRequired": "N",
            "appleIdRequired": "N",
            "twitterRequired": "N",
            "idRequired": "N",
            "birthdayRequired": "N"
        
            }
            if type=='DEPOSIT_BET_BONUS':
                for config in payload.get("depositPromotionConfigs",[]):
                    config.pop("configDetail",None)
                    config["maximumTurnover"] = 50
                    config["minimumTurnover"] = 5
                    config["promotionJobDetails"]=[
                        {
                        "id": "",
                        "configId": "",
                        "bonusType": "PERCENTAGE",
                        "totalDepositAmount": 5000,
                        "totalValidBet": 0,
                        "bonusAmount": 100,
                        "pointAmount": 100,
                        "ticketId": 1042012,
                        "ticketType": "GOLDEN_EGG",
                        "ticketName": "就是一般的砸金蛋"
                        }
                    ]
                response=requests.post(url,json=payload,headers=header,verify=False)
                response_json=response.json()
                if response_json.get('success')==True:
                    logging.info(f"創建活動成功 {type}")
                else:
                    logging.error(f"創建活動失敗 {type}")
            elif type=='DEPOSIT':

                payload["dailyCountLimit"]=10
                payload["weeklyCountLimit"]=10
                payload["monthlyCountLimit"]=100
                payload["promotionCountLimit"]=100
                payload["maxClaimCountType"]="PROMOTION"
                payload["maxBonusAmount"]=100000
                payload["maxDailyPointAmount"]=100000

                response=requests.post(url,json=payload,headers=header,verify=False)
                response_json=response.json()
                if response_json.get('success')==True:
                    logging.info(f"創建活動成功 {type}")
                else:
                    logging.error(f"創建活動失敗 {type}")
            elif type=='DEPOSIT_COUNT':
                payload["depositPromotionConfigs"]=[
                    {
                    "bonusAmount": 5,
                    "bonusType": "PERCENTAGE",
                    "configId": "",
                    "depositCount": 1,
                    "depositPromotionConfigLabels": [],
                    "maximumTurnover": 55,
                    "minimumSingleDeposit": 10,
                    "minimumTurnover": 5,
                    "pointAmount": 5,
                    "turnoverMultiplier": 3,
                    "principalAndBonus": "",
                    "promotionId": None,
                    "ticketId": 1113014,
                    "ticketName": "流水轉盤",
                    "ticketType": "PRIZE_WHEEL",
                    "turnoverType": "BONUS"
                }
                ]
                response=requests.post(url,json=payload,headers=header,verify=False)
                response_json=response.json()
                if response_json.get('success')==True:
                    logging.info(f"創建活動成功 {type}")
                else:
                    logging.error(f"創建活動失敗 {type}")

            else:
                response=requests.post(url,json=payload,headers=header,verify=False)
                response_json=response.json()
                if response_json.get('success')==True:
                    logging.info(f"創建活動成功 {type}")
                else:
                    logging.error(f"創建活動失敗 {type}")
        except Exception as e:
             logging.error(f"呼叫api錯誤 {e}")

    def create_new_register_Promotion(self):
        start_Time,endTime=self.unitTime()
        URL="http://sit-admin2.tcg.com/tac/api/relay/post/mcs-internal-v3-registerPromotion-add"
        header=self.header_new()
        payload = {
            "id": "",
            "promotionId": "",
            "merchantCode": "gi8viet",
            "name": "carrine test",
            "budget": "999888",
            "description": "cccc",
            "startTime": start_Time,
            "endTime": endTime,
            "startMemberRegTime": start_Time,
            "endMemberRegTime": endTime,
            "requiredTurnover": 0,
            "minimumRequiredTurnover": 0,
            "bonusAmount": 0,
            "status": "A",
            "noExpiry": "Y",
            "noMemberRegExpiry": "Y",
            "promotionType": "REGISTER",
            "walletType": "2",
            "txType": 6131,
            "neverDeposit": "N",
            "excludeRebate": "N",
            "minimumClaimAmount": 0,
            "maximumClaimAmount": 0,
            "maxClaimCount": 1,
            "maxClaimCountType": "PROMOTION",
            "productType": "ALL",
            "excludeValidBet": "N",
            "uniqueIp": "N",
            "withdrawalAccountRequired": "N",
            "bankCardRequired": "N",
            "virtualWalletRequired": "N",
            "electronicWalletRequired": "N",
            "emailRequired": "N",
            "contactNumberRequired": "N",
            "qqRequired": "N",
            "zaloRequired": "N",
            "payeeNameRequired": "N",
            "claimMethod": "REQUEST",
            "appRequirement": "N",
            "contactNumberRequiredType": "A",
            "contactNumFileName": "",
            "fileDetailList": [],
            "participant": "ALL",
            "forAllLabel": "Y",
            "remark": "<p>cccc</p>",
            "linkedAnnouncementList": [],
            "agentNames": "",
            "websites": "",
            "operationLabels": [],
            "totalContactNumbers": 0,
            "pointBudget": "999888",
            "promotionMessage": {
                "id": "",
                "promotionId": "",
                "defaultLanguageInbox": "EN",
                "defaultLanguagePushNotif": "CN",
                "contentInbox": [
                    {
                        "promotionMessageId": 2151037,
                        "language": "EN",
                        "title": "新手任务奖励站內信",
                        "content": "<p>新手任务奖励站內信</p>\n",
                        "type": "INBOX"
                    }
                ],
                "contentPushNotif": [],
                "contentInboxOneTime": None,
                "contentPushNotifOneTime": None,
                "contentInboxCont": None,
                "contentPushNotifCont": None,
                "contentInboxReferred": None,
                "contentPushNotifReferred": None,
                "contentInboxBettingRebate": None,
                "contentPushNotifBettingRebate": None,
                "contentInboxAchievementReward": None,
                "contentPushNotifAchievementReward": None,
                "allowMessage": None,
                "allowPushNotif": None
            },
            "languageInbox": "",
            "languagePushNotif": "",
            "allowMessage": "Y",
            "allowPushNotif": "N",
            "promotionTicketBudget": {
                "1087006": {
                    "promotionId": 4022089,
                    "ticketBudget": 0,
                    "ticketId": 1087006,
                    "ticketName": "",
                    "ticketType": None
                }
            },
            "mobileVerified": "N",
            "budgetStr": "999888",
            "pointBudgetStr": "999888",
            "lineRequired": "N",
            "wechatRequired": "N",
            "facebookRequired": "N",
            "whatsappRequired": "N",
            "addressRequired": "N",
            "idRequired": "N",
            "telegramRequired": "N",
            "viberRequired": "N",
            "appleIdRequired": "N",
            "twitterRequired": "N",
            "birthdayRequired": "N",
            "ticketClaimMethod": "AUTO",
            "playerRemark": "j",
            "registerPromotionConfigs": [
                {
                    "promotionId": 4022089,
                    "configId": "",
                    "forAllLabel": "Y",
                    "bonusAmount": 10,
                    "pointAmount": 10,
                    "turnoverMultiplier": 5,
                    "minRequiredTurnover": 1,
                    "registerPromotionConfigLabels": [],
                    "ticketId": 1087006,
                    "ticketType": None,
                    "ticketName": None
                }
            ],
            "startTimeString": "2025-07-01 00:00:00",
            "endTimeString": "2025-07-01 23:59:59",
            "startMemberRegTimeString": "2025-07-01 00:00:00",
            "endMemberRegTimeString": "2025-07-01 23:59:59",
            "promotionPeriodFirstDepositRequired": "N"
            }
        response=requests.post(URL,json=payload,headers=header,verify=False)
        response_json=response.json()
        if response_json.get('success')==True:
            logging.info("創建新手任務成功")
        else:
            logging.error("創建新手任務失敗")
    def create_Register(self):
        start_Time,endTime=self.unitTime()
        URL="http://sit-admin2.tcg.com/tac/api/relay/post/mcs-internal-v3-newRegisterPromotion-add"
        header=self.header_new()
        payload={
                "id": "",
                "promotionId": "",
                "merchantCode": "gi8viet",
                "name": "test ",
                "budget": 999888,
                "description": "s",
                "startTime": start_Time,
                "endTime": endTime,
                "requiredTurnover": 0,
                "minimumRequiredTurnover": 0,
                "bonusAmount": 0,
                "status": "A",
                "noExpiry": "Y",
                "promotionType": "NEW_REGISTER",
                "walletType": "2",
                "txType": 3119,
                "excludeRebate": "N",
                "minimumClaimAmount": 0,
                "maximumClaimAmount": 0,
                "maxClaimCount": 1,
                "maxClaimCountType": "PROMOTION",
                "productType": "RNG_OR_LIVE",
                "excludeValidBet": "N",
                "uniqueIp": "N",
                "bankCardRequired": "N",
                "emailRequired": "N",
                "contactNumberRequired": "N",
                "qqRequired": "N",
                "zaloRequired": "N",
                "payeeNameRequired": "N",
                "claimMethod": "AUTO",
                "contactNumberRequiredType": "A",
                "contactNumFileName": "",
                "fileDetailList": [],
                "participant": "ALL",
                "forAllLabel": "Y",
                "remark": "sss",
                "linkedAnnouncementList": [],
                "agentNames": "",
                "websites": "",
                "operationLabels": [],
                "totalContactNumbers": 0,
                "pointBudget": 999888,
                "promotionMessage": {
                    "contentInbox": [],
                    "defaultLanguageInbox": "CN",
                    "contentPushNotif": [],
                    "defaultLanguagePushNotif": "CN"
                },
                "languageInbox": "",
                "languagePushNotif": "",
                "allowMessage": "N",
                "allowPushNotif": "N",
                "promotionTicketBudget": {
                    "1168014": {
                        "ticketBudget": 0,
                        "ticketId": 1168014,
                        "ticketName": "",
                        "ticketType": "CASH_VOUCHER"
                    }
                },
                "mobileVerified": "",
                "budgetStr": "999888",
                "pointBudgetStr": "999888",
                "lineRequired": "N",
                "wechatRequired": "N",
                "facebookRequired": "N",
                "whatsappRequired": "N",
                "addressRequired": "N",
                "telegramRequired": "N",
                "viberRequired": "N",
                "appleIdRequired": "N",
                "twitterRequired": "N",
                "idRequired": "N",
                "birthdayRequired": "N",
                "ticketClaimMethod": "MANUAL",
                "restrictionType": "N",
                "vendors": [],
                "playerRemark": "2",
                "newRegisterPromotionConfigs": [
                    {
                        "configId": "",
                        "newRegisterPromotionConfigLabels": [],
                        "bonusAmount": 10,
                        "pointAmount": 20,
                        "ticketType": "CASH_VOUCHER",
                        "ticketId": 1168014,
                        "ticketName": "",
                        "turnoverMultiplier": 1,
                        "minRequiredTurnover": 2,
                        "forAllLabel": "Y"
                    }
                ],
                "startTimeString": "2025-09-12 00:00:00",
                "endTimeString": "2025-09-12 23:59:59"
            }
        response=requests.post(URL,json=payload,headers=header,verify=False)
        response_json=response.json()
        if response_json.get('success')==True:
            logging.info("創建註冊送成功")
        else:
            logging.error("創建註冊送失敗")
    def create_app_download(self):
        start_Time,endTime=self.unitTime()
        URL="http://sit-admin2.tcg.com/tac/api/relay/post/mcs-internal-v3-appDownloadPromotion-add"
        header=self.header_new()
        payload={
            "id": "",
            "merchantCode": "gi8viet",
            "promotionType": "APP_DOWNLOAD",
            "name": "app download",
            "budget": 999888,
            "pointBudget": 999888,
            "ticketClaimMethod": "MANUAL",
            "productType": "RNG_OR_LIVE",
            "startTime": start_Time,
            "endTime": endTime,
            "requiredTurnover": 1,
            "minimumRequiredTurnover": 2,
            "noExpiry": "Y",
            "bonusAmount": 10,
            "pointAmount": 20,
            "remark": "c",
            "maxClaimCount": 1,
            "status": "A",
            "txType": 3119,
            "excludeRebate": "N",
            "claimMethod": "AUTO",
            "linkedAnnouncementList": [],
            "promotionMessage": {
                "contentInbox": [],
                "defaultLanguageInbox": "CN",
                "contentPushNotif": [],
                "defaultLanguagePushNotif": "CN"
            },
            "languageInbox": "",
            "languagePushNotif": "",
            "allowMessage": "N",
            "allowPushNotif": "N",
            "promotionTicketBudget": {
                "1168014": {
                    "ticketBudget": 0,
                    "ticketId": 1168014,
                    "ticketName": "",
                    "ticketType": "CASH_VOUCHER"
                }
            },
            "ticketId": 1168014,
            "ticketName": "",
            "ticketType": "CASH_VOUCHER",
            "budgetStr": "999888",
            "pointBudgetStr": "999888",
            "includePwaWebClip": False,
            "contactNumberRequired": "N",
            "withdrawalAccountRequired": "N",
            "bankCardRequired": "N",
            "virtualWalletRequired": "N",
            "electronicWalletRequired": "N",
            "emailRequired": "N",
            "qqRequired": "N",
            "zaloRequired": "N",
            "payeeNameRequired": "N",
            "lineRequired": "N",
            "wechatRequired": "N",
            "facebookRequired": "N",
            "whatsappRequired": "N",
            "addressRequired": "N",
            "telegramRequired": "N",
            "viberRequired": "N",
            "appleIdRequired": "N",
            "twitterRequired": "N",
            "idRequired": "N",
            "birthdayRequired": "N",
            "playerRemark": "1",
            "startTimeString": "2025-09-12 00:00:00",
            "endTimeString": "2025-09-12 23:59:59"
        }

        response=requests.post(URL,json=payload,headers=header,verify=False)
        response_json=response.json()
        if response_json.get('success')==True:
            logging.info("創建app下載成功")
        else:
            logging.error("創建app下載失敗")
    def create_app_download(self):
        URL="http://sit-admin2.tcg.com/tac/api/relay/post/mcs-internal-v3-saviorPromotion-add"
        header=self.header_new()
        payload={
            "id": "",
            "merchantCode": "gi8viet",
            "promotionType": "SAVIOR",
            "name": "test",
            "budget": 999888,
            "pointBudget": 999888,
            "ticketClaimMethod": "MANUAL",
            "productType": "RNG_OR_LIVE",
            "excludeValidBet": "N",
            "noExpiry": "Y",
            "startTime": 1757865600000,
            "endTime": 1757951999000,
            "forAllLabel": "Y",
            "participant": "ALL",
            "effectiveTime": 0,
            "maxClaimCount": "1",
            "maxClaimCountType": "DAILY",
            "remark": "ccc",
            "status": "A",
            "txType": 3119,
            "excludeRebate": "N",
            "agentNames": "",
            "operationLabels": [],
            "linkedAnnouncementList": [],
            "contactNumFileName": "",
            "fileDetailList": [],
            "totalContactNumbers": 0,
            "promotionMessage": {
                "contentInbox": [],
                "defaultLanguageInbox": "CN",
                "contentPushNotif": [],
                "defaultLanguagePushNotif": "CN"
            },
            "languageInbox": "",
            "languagePushNotif": "",
            "allowMessage": "N",
            "allowPushNotif": "N",
            "promotionTicketBudget": {
                "1168014": {
                    "ticketBudget": 0,
                    "ticketId": 1168014,
                    "ticketName": "",
                    "ticketType": "CASH_VOUCHER"
                }
            },
            "budgetStr": "999888",
            "pointBudgetStr": "999888",
            "contactNumberRequired": "N",
            "withdrawalAccountRequired": "N",
            "bankCardRequired": "N",
            "virtualWalletRequired": "N",
            "electronicWalletRequired": "N",
            "emailRequired": "N",
            "qqRequired": "N",
            "zaloRequired": "N",
            "payeeNameRequired": "N",
            "lineRequired": "N",
            "wechatRequired": "N",
            "facebookRequired": "N",
            "whatsappRequired": "N",
            "addressRequired": "N",
            "telegramRequired": "N",
            "viberRequired": "N",
            "appleIdRequired": "N",
            "twitterRequired": "N",
            "idRequired": "N",
            "birthdayRequired": "N",
            "claimMethod": "AUTO",
            "playerRemark": "z",
            "saviorPromotionConfigs": [
                {
                    "configId": "",
                    "saviorPromotionConfigLabels": [],
                    "saviorPromotionConfigDetails": [
                        {
                            "configId": "",
                            "deposit": 100,
                            "netLoss": 1,
                            "bonusPercentage": 100,
                            "pointPercentage": 100,
                            "ticketType": "CASH_VOUCHER",
                            "ticketId": 1168014,
                            "ticketName": ""
                        }
                    ],
                    "bonusType": "PERCENTAGE",
                    "minBonusAmount": 1,
                    "maxBonusAmount": 100,
                    "minPointAmount": 1,
                    "maxPointAmount": 100,
                    "turnoverMultiplier": 1,
                    "minRequiredTurnover": "",
                    "forAllLabel": "Y",
                    "minTurnoverAmount": 100
                }
            ],
            "startTimeString": "2025-09-15 00:00:00",
            "endTimeString": "2025-09-15 23:59:59"
        }


        response=requests.post(URL,json=payload,headers=header,verify=False)
        response_json=response.json()
        if response_json.get('success')==True:
            logging.info("創建app下載成功")
        else:
            logging.error("創建app下載失敗")

            
        

    
if __name__ == "__main__":

    credential_be = {
            "operatorName": "carrine03",
            "password": "Test@1234"
    }
    try:
        backend=Backend(credential_be)
        if backend.token:
            logging.info("backend class有成功運作")
            deposit_list=['DEPOSIT','FIRST_DEPOSIT','SECOND_DEPOSIT','THIRD_DEPOSIT','FOURTH_DEPOSIT','FIFTH_DEPOSIT','DEPOSIT_BET_BONUS','DEPOSIT_COUNT']
            for promo_type in deposit_list:
                backend.create_fisrt_deposit_promotion(promo_type)
            backend.create_new_register_Promotion()
            backend.create_Register()
            backend.create_app_download()
        else:
            logging.error(f"沒有拿到後台token:")        
            #backend.Bonus_record_page()  --之後再修改 
  
    except Exception as e:
            logging.error(f"啟動時發生錯誤: {e}")

    