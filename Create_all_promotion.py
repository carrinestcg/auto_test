import requests
import logging
from datetime import datetime,timedelta,timezone
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
    
class Backend:
    
    def __init__(self,credential_be:str):
        self.session=requests.Session()
        self.credential_be=credential_be
        self.token_expire=None
        self.type=''
        self.token=self.get_token_backend(credential_be['operatorName'],credential_be['password'],credential_be['merchantCode'])
        
    def header(self,merchantCode,refer):
         return {
             
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "Authorization": self.token,
                "Content-Type": "application/json",
                "Connection": "keep-alive",
                "Language": "zh_CN",
                "Merchant": merchantCode,
                "MerchantCode": merchantCode,
                "Tac-Trace-Id":"OoL7ntxjBpmiQPeM",
                "Referer": f"http://sit-admin2.tcg.com/{refer}",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
                "environment": "TCG3",
                "notPending": "true",
                "platform": "TCG"
            
         }
        
    def get_token_backend(self,operatorName,password,merchantCode):
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
            "Merchant": merchantCode,
            "MerchantCode": merchantCode,
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
        now = datetime.now()

        start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = now.replace(hour=23, minute=59, second=59, microsecond=0)

        start_ts = int(start_time.timestamp() * 1000)
        end_ts = int(end_time.timestamp() * 1000)

        start_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
        end_str = end_time.strftime("%Y-%m-%d %H:%M:%S")

        return start_ts, end_ts, start_str, end_str
    def create_fisrt_deposit_promotion(self,type,ticket,merchantCode,refer=24782):
        start_Time, endTime, start_str, end_str = self.unitTime()
        try: 
            url="http://sit-admin2.tcg.com/tac/api/relay/post/mcs-depositPromotion-add"
            header=self.header(merchantCode,refer)
            payload={
                
            "id": "",
            "merchantCode": merchantCode,
            "name": f"測複製 {type} deposit",
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
            "productType": "ALL",
            "noExpiry": "Y",
            "startTime": start_Time,
            "startTimeString": start_str,
            "endTime": endTime,
            "endTimeString": end_str,
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
                ticket: {
                    "promotionId": "",
                    "ticketId": ticket,
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
                            "ticketId": ticket,
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
                        "ticketId": ticket,
                        "ticketType": "GOLDEN_EGG",
                        "ticketName": "就是一般的砸金蛋"
                        }
                    ]
                response=requests.post(url,json=payload,headers=header,verify=False)
                response_json=response.json()
                if response_json.get('success'):
                    logging.info(f"創建活動成功 {type}")
                else:
                    logging.error(f"創建活動失敗 {type}{response_json}")
                    
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
                if response_json.get('success'):
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
                    "ticketId": ticket,
                    "ticketName": "流水轉盤",
                    "ticketType": "PRIZE_WHEEL",
                    "turnoverType": "BONUS"
                }
                ]
                response=requests.post(url,json=payload,headers=header,verify=False)
                response_json=response.json()
                if response_json.get('success'):
                    logging.info(f"創建活動成功 {type}")
                else:
                    logging.error(f"創建活動失敗 {type}")

            else:
                response=requests.post(url,json=payload,headers=header,verify=False)
                response_json=response.json()
                if response_json.get('success'):
                    logging.info(f"創建活動成功 {type}")
                else:
                    logging.error(f"創建活動失敗 {type}")
        except Exception as e:
             logging.error(f"呼叫api錯誤 {e}")

    def create_new_register_Promotion(self,ticket,merchantCode,refer=24780):
        start_Time, endTime, start_str, end_str = self.unitTime()
        URL="http://sit-admin2.tcg.com/tac/api/relay/post/mcs-internal-v3-registerPromotion-add"
        header=self.header(merchantCode,refer)
        payload = {
            "id": "",
            "promotionId": "",
            "merchantCode": merchantCode,
            "name": " 測複製",
            "budget": "999888",
            "description": "cccc",
            "startTime": start_Time,
            "endTime": endTime,
            "startMemberRegTime": start_str,
            "endMemberRegTime": end_str,
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
                ticket: {
                    "promotionId": 4022089,
                    "ticketBudget": 0,
                    "ticketId": ticket,
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
                    "ticketId": ticket,
                    "ticketType": None,
                    "ticketName": None
                }
            ],
            "startTimeString": start_str,
            "endTimeString": end_str,
            "startMemberRegTimeString": start_str,
            "endMemberRegTimeString": end_str,
            "promotionPeriodFirstDepositRequired": "N"
            }
        response=requests.post(URL,json=payload,headers=header,verify=False)
        response_json=response.json()
        if response_json.get('success'):
            logging.info("創建新手任務成功")
        else:
            logging.error(f"創建新手任務失敗{response.text}")
    def create_Register(self,ticket,merchantCode,refer=24780):
        start_Time, endTime, start_str, end_str = self.unitTime()
        URL="http://sit-admin2.tcg.com/tac/api/relay/post/mcs-internal-v3-newRegisterPromotion-add"
        header=self.header(merchantCode,refer)
        payload={
                "id": "",
                "promotionId": "",
                "merchantCode": merchantCode,
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
                    ticket: {
                        "ticketBudget": 0,
                        "ticketId": ticket,
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
                        "ticketId": ticket,
                        "ticketName": "",
                        "turnoverMultiplier": 1,
                        "minRequiredTurnover": 2,
                        "forAllLabel": "Y"
                    }
                ],
                "startTimeString": start_str,
                "endTimeString": end_str
            }
        response=requests.post(URL,json=payload,headers=header,verify=False)
        response_json=response.json()
        if response_json.get('success'):
            logging.info("創建註冊送成功")
        else:
            logging.error("創建註冊送失敗")
    def create_app_download(self,ticket,merchantCode,refer=24780):
        start_Time, endTime, start_str, end_str = self.unitTime()
        URL="http://sit-admin2.tcg.com/tac/api/relay/post/mcs-internal-v3-appDownloadPromotion-add"
        header=self.header(merchantCode,refer)
        payload={
            "id": "",
            "merchantCode": merchantCode,
            "promotionType": "APP_DOWNLOAD",
            "name": "測複製",
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
                ticket: {
                    "ticketBudget": 0,
                    "ticketId": ticket,
                    "ticketName": "",
                    "ticketType": "CASH_VOUCHER"
                }
            },
            "ticketId": ticket,
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
            "startTimeString": start_str,
            "endTimeString": end_str
        }

        response=requests.post(URL,json=payload,headers=header,verify=False)
        response_json=response.json()
        if response_json.get('success'):
            logging.info("創建app下載成功")
        else:
            logging.error("創建app下載失敗")
    

            
    def create_Raffle(self,ticket,merchantCode,refer=24780):
        URL="http://sit-admin2.tcg.com/tac/api/relay/post/mcs-internal-promotion-rafflePromotion-add"
        start_Time, endTime, start_str, end_str = self.unitTime()
        header=self.header(merchantCode,refer)
        payload={
                "id": "",
                "merchantCode": merchantCode,
                "promotionType": "RAFFLE",
                "name": "test",
                "budget": 0,
                "productType": "ALL",
                "excludeValidBet": "N",
                "noExpiry": "Y",
                "startTime": start_Time,
                "endTime": endTime,
                "forAllLabel": "Y",
                "participant": "ALL",
                "effectiveTime": "",
                "remark": "c",
                "status": "A",
                "txType": 6131,
                "excludeRebate": "N",
                "maxClaimCount": 1,
                "maxClaimCountType": "DAILY",
                "agentNames": "",
                "operationLabels": [],
                "linkedAnnouncementList": [],
                "contactNumFileName": "",
                "fileDetailList": [],
                "totalContactNumbers": 0,
                "uniqueIp": "N",
                "roundClaiming": "ALL_PROMOTION",
                "claimMethod": "MANUAL",
                "claimDuration": 5,
                "scheduleType": "HOURLY",
                "rounds": 5,
                "countdownNotice": 5,
                "maxRaffleCount": 5,
                "amount": 5,
                "appRequirement": "N",
                "forDeletionList": [],
                "triggerOnline": "Y",
                "triggerDeposit": "N",
                "triggerBet": "N",
                "rafflePromotionConfigs": [
                    {
                        "configId": "",
                        "rafflePromotionConfigLabels": [],
                        "depositAmount": "",
                        "validBet": "",
                        "turnoverMultiplier": 1,
                        "forAllLabel": "Y"
                    }
                ],
                "rafflePromotionRoundSettings": [
                    {
                        "roundId": "",
                        "raffleTimeFrom": "00:00:00",
                        "raffleTimeTo": "00:00:00",
                        "fixedRaffleTime": "00:00:00"
                    }
                ],
                "prizeType": "TICKET",
                "ticketType": "RAFFLE",
                "ticketId": ticket,
                "ticketName": "",
                "raffleBudget": "999888",
                "quantity": 0,
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
                "kycRequired": "N",
                "ticketClaimMethod": "MANUAL",
                "playerRemark": "幸运抽奖 test",
                "startTimeString": start_str,
                "endTimeString": end_str
            }
        response=requests.post(URL,json=payload,headers=header,verify=False)
        response_json=response.json()
        if response_json.get('success'):
            logging.info("創建幸運抽獎成功")
        else:
            logging.error("創建幸運抽獎失敗")
    def create_lucky_bet(self,ticket,merchantCode,refer=24784):
        URL="http://sit-admin2.tcg.com/tac/api/relay/post/promo-promotion-lucky-bet-create"
        start_Time, endTime, start_str, end_str = self.unitTime()
        start_Time = start_Time + (5 * 60 * 1000)
        header=self.header(merchantCode,refer)
        payload={
            "status": "A",
            "promoName": "111",
            "gamingMappingEnabled": "N",
            "noExpiry": "Y",
            "startTime": start_Time,
            "scheduleType": "DAILY",
            "claimLimitFixedCount": 111,
            "claimLimitType": "FIXED",
            "totalClaimLimitEnabled": "N",
            "totalClaimLimitCount": None,
            "winningLimitAmtEnabled": "N",
            "minValidBetAmt": 1,
            "bonusType": "FIXED",
            "ruleType": "LAST_DIGIT",
            "rewardConfigs": [
                {
                    "rewardAmountLimit": None,
                    "winningRule": "1",
                    "bonus": 1,
                    "point": 1,
                    "turnoverMultiplier": 11,
                    "betAmountMultiplier": None,
                    "betNumCount": None,
                    "betNumTarget": None,
                    "ticketRewards": 
                        [{"ticketId": ticket, "ticketQuantity": 1}]

                },
                {
                    "rewardAmountLimit": None,
                    "winningRule": "2",
                    "bonus": 12,
                    "point": 12,
                    "turnoverMultiplier": 12,
                    "ticketRewards": None
                       

                }
            ],
            "excludeRebate": "N",
            "remark": "1",
            "description": "1",
            "endTime": endTime,
            "scheduleInterval": None,
            "claimLimitConfigs": [
                {
                    "amount": None,
                    "limitCount": 111
                }
            ],
            "participant": {
                "participant": "ALL",
                "claimMethod": "MANUAL"
            },
            "participantCondition": {
                "withdrawalAccountRequired": "N",
                "payeeNameRequired": "N",
                "contactNumberRequired": "N",
                "mobileVerified": None,
                "idRequired": "N",
                "idNumHasAuthenticateRequired": "N",
                "addressRequired": "N",
                "emailRequired": "N",
                "whatsappRequired": "N",
                "lineRequired": "N",
                "qqRequired": "N",
                "zaloRequired": "N",
                "wechatRequired": "N",
                "facebookRequired": "N",
                "depositRequired": "N",
                "depositAmtRequired": "N",
                "depositAmtDuration": None,
                "requiredDepositAmount": None,
                "depositCountRequired": "N",
                "depositCountDuration": None,
                "depositCount": None,
                "minTurnoverRequired": "N",
                "minTurnoverDuration": None,
                "minTurnoverAmt": None,
                "gameType": None,
                "gameVendor": None,
                "kycRequired": "N"
            },
            "announcementList": [],
            "message": {
                "inbox": {
                    "active": "N"
                },
                "notification": {
                    "active": "N"
                }
            }
        }
        print("start_Time:", start_Time)
        print("end_Time:", endTime)               
        response=requests.post(URL,json=payload,headers=header,verify=False)
        response_json=response.json()
        print(response_json)
        if response_json.get('success'):
            logging.info("創建幸運注單成功")
        else:
            logging.error("創建幸運注單失敗")

    def register_mission(self,ticket,merchantCode,refer=24780):
        URL="http://sit-admin2.tcg.com/tac/api/relay/post/promo-promotion-register-task-create"
        start_Time, endTime, start_str, end_str = self.unitTime()
        header=self.header(merchantCode,refer)
        payload={
            "promoId": 0,
            "promoName": "bbb",
            "status": "A",
            "noExpiry": "N",
            "startTime": start_Time,
            "endTime": endTime,
            "participant": {
                "participant": "ALL",
                "claimMethod": "AUTO",
                "customerNames": [],
                "websites": [],
                "contactFileIds": [],
                "uniqueIp": "N",
                "allowSameIpReclaimDays": 30
            },
            "rewardList": [
                {
                    "ticketId": ticket,
                    "ticketName": None,
                    "ticketQuantity": 1,
                    "ticketTurnoverMultiple": None,
                    "ticketType": "CASH_VOUCHER",
                    "ticketTurnoverMultiplier": 0
                }
            ],
            "message": {
                "inbox": {
                    "active": "N"
                },
                "notification": {
                    "active": "N"
                }
            },
            "productType": "ALL",
            "promoType": "REGISTER_TASK"
        }
        response=requests.post(URL,json=payload,headers=header,verify=False)
        response_json=response.json()
        if response_json.get('success'):
            logging.info("創建註冊任務成功")
        else:
            print(response_json)
            logging.error(f"創建註冊任務失敗{response.text}")
    def rescue_promotion(self,ticket,merchantCode,refer=24783):
        URL="http://sit-admin2.tcg.com/tac/api/relay/post/promo-promotion-savior-create"
        start_Time, endTime, start_str, end_str = self.unitTime()
        header=self.header(merchantCode,refer)
        payload={
            "status": "A",
            "promoName": "111111",
            "noExpiry": "Y",
            "startTime": start_Time,
            "endTime": endTime,
            "saviorRewardPeriodType": "DAILY",
            "weekStartDay": 0,
            "productType": "ALL",
            "excludeBonus": "N",
            "excludeBonusScope": None,
            "excludePlayerRebate": "N",
            "excludePlayerRebateScope": None,
            "excludePrevPeriodReward": "Y",
            "excludeRebate": "N",
            "internalRemark": "1",
            "description": "1",
            "requiredTurnover": 0,
            "minimumRequiredTurnover": 0,
            "participant": {
                "participant": "ALL",
                "labelIds": [],
                "customerNames": [],
                "contactFiles": [],
                "claimMethod": "AUTO"
            },
            "participantCondition": {
                "withdrawalAccountRequired": "N",
                "mobileVerified": "N",
                "idNumHasAuthenticateRequired": "N",
                "depositRequired": "N",
                "depositAmtRequired": "N",
                "depositCountRequired": "N",
                "minTurnoverRequired": "N",
                "gameType": None,
                "gameVendor": None,
                "minTurnoverDuration": None,
                "minTurnoverAmt": None,
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
            },
            "playerRemark": "救援金",
            "saviorPromotionConfigToList": [
                {
                    "configId": None,
                    "promotionId": None,
                    "bonusType": "FIXED",
                    "rewardType": "BONUS",
                    "minBonusAmount": 1,
                    "maxBonusAmount": 2,
                    "minPointAmount": 1,
                    "maxPointAmount": 2,
                    "minTurnoverAmount": 2,
                    "forAllLabel": "Y",
                    "saviorPromotionConfigLabelToList": None,
                    "saviorPromotionConfigDetailToList": [
                        {
                            "promotionId": None,
                            "configId": None,
                            "deposit": 1,
                            "netLoss": 1,
                            "turnoverMultiplier": 1,
                            "bonusPercentage": 1,
                            "pointPercentage": 1,
                            "ticketType": "RAFFLE",
                            "ticketId": ticket,
                            "ticketName": "",
                            "id": None
                        }
                    ]
                }
            ],
            "effectiveTime": 0,
            "announcementList": None,
            "message": {
                "inbox": {
                    "active": "N",
                    "defaultLanguage": "CN",
                    "messageList": None
                },
                "notification": {
                    "active": "N",
                    "defaultLanguage": "CN",
                    "messageList": None
                }
            },
            "txType": 6131
        }
        response=requests.post(URL,json=payload,headers=header,verify=False)
        response_json=response.json()
        if response_json.get('success'):
            logging.info("創建救援金成功")
        else:
            print(response_json)
            logging.error("創建救援金失敗")
    def mission(self,ticket,merchantCode,refer=24783):
        URL="http://sit-admin2.tcg.com/tac/api/relay/post/mcs-internal-v3-missionPromotion-create?pid=20542"
        start_Time, endTime, start_str, end_str = self.unitTime()
        header=self.header(merchantCode,refer)
        payload={
            "id": "",
            "promotionId": "",
            "merchantCode": merchantCode,
            "name": "test",
            "promotionName": "",
            "description": "111",
            "budget": "999888",
            "startTime": start_Time,
            "endTime": endTime,
            "requiredTurnover": 0,
            "status": "A",
            "sorting": 0,
            "noExpiry": "N",
            "milestones": [
                {
                    "id": "",
                    "milestoneNumber": 1,
                    "promotionId": "",
                    "minBet": 1,
                    "depositRequired": "N",
                    "depositAmount": 1,
                    "betCountRequired": "N",
                    "betCount": "",
                    "profitMultiplierRequired": "N",
                    "profitMultiplier": ""
                }
            ],
            "rewardDetails": [],
            "missionRewardConfigs": [
                {
                    "configId": "",
                    "type": "M",
                    "forAllLabel": "Y",
                    "merchantCode": merchantCode,
                    "playerRanks": [],
                    "missionRewardGroups": [
                        {
                            "configId": "",
                            "groupId": None,
                            "milestoneNumbers": [
                                {
                                    "value": 1,
                                    "label": "排名 1"
                                }
                            ],
                            "rewardDetails": [
                                {
                                    "configId": "",
                                    "groupId": "",
                                    "milestoneNumber": 1,
                                    "type": "M",
                                    "bonusAmount": 1,
                                    "pointAmount": 1,
                                    "ticketId": ticket,
                                    "turnoverMultiplier": 1,
                                    "minTurnover": 1
                                }
                            ],
                            "type": "M",
                            "bonusAmount": 1,
                            "pointAmount": 1,
                            "ticketId": ticket,
                            "turnoverMultiplier": 1,
                            "ticketType": "CASH_VOUCHER",
                            "minTurnover": 1
                        }
                    ]
                },
                {
                    "configId": "",
                    "type": "L",
                    "forAllLabel": "Y",
                    "merchantCode": merchantCode,
                    "playerRanks": [],
                    "missionRewardGroups": [
                        {
                            "configId": "",
                            "groupId": None,
                            "milestoneNumbers": [
                                {
                                    "value": 1,
                                    "label": "排名 1"
                                },
                                {
                                    "value": 2,
                                    "label": "排名 2"
                                },
                                {
                                    "value": 3,
                                    "label": "排名 3"
                                }
                            ],
                            "rewardDetails": [
                                {
                                    "configId": "",
                                    "groupId": "",
                                    "milestoneNumber": 1,
                                    "type": "L",
                                    "bonusAmount": 1,
                                    "pointAmount": 1,
                                    "ticketId": ticket,
                                    "turnoverMultiplier": 1,
                                    "minTurnover": 1
                                },
                                {
                                    "configId": "",
                                    "groupId": "",
                                    "milestoneNumber": 2,
                                    "type": "L",
                                    "bonusAmount": 1,
                                    "pointAmount": 1,
                                    "ticketId": ticket,
                                    "turnoverMultiplier": 1,
                                    "minTurnover": 1
                                },
                                {
                                    "configId": "",
                                    "groupId": "",
                                    "milestoneNumber": 3,
                                    "type": "L",
                                    "bonusAmount": 1,
                                    "pointAmount": 1,
                                    "ticketId": ticket,
                                    "turnoverMultiplier": 1,
                                    "minTurnover": 1
                                }
                            ],
                            "type": "L",
                            "bonusAmount": 1,
                            "pointAmount": 1,
                            "ticketId": ticket,
                            "turnoverMultiplier": 1,
                            "ticketType": "CASH_VOUCHER",
                            "minTurnover": 1
                        }
                    ]
                }
            ],
            "promotionType": "MISSION",
            "walletType": 2,
            "txType": 3119,
            "minimumClaimAmount": 0,
            "maximumClaimAmount": 0,
            "missionStartTime": start_Time,
            "duration": 1,
            "interval": 0,
            "milestoneEnabled": "N",
            "leaderBoardEnabled": "N",
            "missionType": "ML",
            "milestoneRequirement": "",
            "rankingRestriction": "N",
            "leaderBoardSize": "3",
            "productType": "RNG_OR_FISH",
            "forAllLabel": "Y",
            "participant": "ALL",
            "linkedAnnouncementList": [],
            "pointBudget": "999888",
            "promotionMessage": {
                "contentInboxMilestone": [],
                "contentInboxLeaderboard": [],
                "contentPushNotifMilestone": [],
                "contentPushNotifLeaderboard": [],
                "defaultLanguageInbox": "CN",
                "defaultLanguagePushNotif": "CN"
            },
            "languageInbox": "",
            "languagePushNotif": "",
            "activeKeyInbox": "",
            "activeKeyPushNotif": "",
            "allowMessage": "N",
            "allowPushNotif": "N",
            "promotionTicketBudget": {
                "1282015": {
                    "ticketBudget": 0,
                    "ticketId": ticket,
                    "ticketType": "CASH_VOUCHER"
                }
            },
            "mobileVerified": "N",
            "depositRequired": "N",
            "requiredDepositAmount": 0,
            "promoGameMapping": [],
            "leaderBoardType": "VALID_BET",
            "leaderBoardMilestoneId": 1,
            "rankRestrictions": [],
            "missionRuleEnabled": "N",
            "missionRule": {
                "defaultLanguage": "CN",
                "content": []
            },
            "agentNames": "",
            "operationLabels": [],
            "contactNumFileName": "",
            "totalContactNumbers": 0,
            "forDeletionList": [],
            "errorMap": [],
            "ticketClaimMethod": "MANUAL",
            "playerRemark": "排行榜+里程碑 test",
            "budgetStr": "999888",
            "pointBudgetStr": "999888",
            "validationMap": [],
            "claimMethod": "MANUAL",
            "effectiveTime": 0,
            "maxClaimCountType": "DAILY",
            "startTimeString": start_str,
            "endTimeString": end_str,
            "missionStartTimeString": start_str,
            "type": "MISSION",
            "language": ""
}
        response=requests.post(URL,json=payload,headers=header,verify=False)
        response_json=response.json()
        if response_json.get('success'):
            logging.info("創建比賽排行榜成功")
        else:
            print(response_json)
            logging.error("創建比賽排行榜失敗")
    def gen_code(self,merchantCode,refer=24784):
        URL="http://10.80.1.19:8083/promo-be/resources/promotion/promo_code/gen_code"
        params={
            "merchantCode":merchantCode
        }
        header=self.header(merchantCode,refer)
        
        response=requests.get(URL,params=params,headers=header,verify=False)
        response_json=response.json()
        if response_json.get("success"):
            promoCode=response_json.get("value")
            return promoCode
        else:
            return None
    def PromoCode(self,ticket,merchantCode,promoCode,refer=24784):
        URL="http://10.80.1.19:8083/promo-be/resources/promotion/promo_code"
        start_Time, endTime, start_str, end_str = self.unitTime()
        header=self.header(merchantCode,refer)
        payload={
                "merchantCode": merchantCode,
                "name": "11111",
                "productType": "ALL",
                "promoCodes": [
                    {
                        "promoCodeGenerateType": "RANDOM",
                        "promoCode": promoCode
                    }
                ],
                "startTime": start_Time,
                "endTime": endTime,
                "excludeRebate": "N",
                "remark": "1",
                "description": "1",
                "isPublicInPromoList": "Y",
                "restriction": {
                    "exchangeCondition": {
                        "condition": "ALL_MEMBER",
                        "afterCampaignStart": None,
                        "agentList": None,
                        "labelIdList": None,
                        "registerStartTime": None,
                        "registerEndTime": None,
                        "fileDetailList": None,
                        "registerUrls": None
                    },
                    "participateCondition": {
                        "conditions": [],
                        "depositTypes": None,
                        "idNumHasAuthenticate": False,
                        "mobileNumHasAuthenticate": False
                    },
                    "claimMethod": "MANUAL",
                    "claimConditions": [
                        "CUSTOMER"
                    ]
                },
                "config": {
                    "bonusAmt": 1,
                    "pointAmt": 1,
                    "ticketName": "CASH_VOUCHER",
                    "ticketId": ticket,
                    "turnoverMultiplier": 1,
                    "minimumTurnover": 11,
                    "maxClaimCount": "111",
                    "maxClaimCountDaily": "111",
                    "playerRemark": "优惠码 11111",
                    "configId": 0,
                    "promotionSettingId": 0,
                    "ticketQuantity": 1
                },
                "announcements": [],
                "status": "A",
                "promotionSettingId": None
            }
        response=requests.post(URL,json=payload,headers=header,verify=False)
        response_json=response.json()
        if response_json.get('success'):
            logging.info("創建優惠碼成功")
        else:
            print(response_json)
            logging.error("創建優惠碼失敗")
    def Manual_bonus(self,ticket,merchantCode,refer=24785):
        URL="http://sit-admin2.tcg.com/tac/api/relay/post/mcs-internal-v3-manualPromotionMgmt-add"
        start_Time, endTime, start_str, end_str = self.unitTime()
        header=self.header(merchantCode,refer)
        payload={
            "merchantCode": merchantCode,
            "name": "test",
            "description": "test",
            "startTime": start_Time,
            "startTimeString": start_str,
            "endTime": endTime,
            "endTimeString": end_str,
            "noExpiry": "Y",
            "remark": "xxx",
            "excludeRebate": "N",
            "productType": "ALL",
            "txType": 6131,
            "claimMethod": "AUTO",
            "effectiveTime": "0",
            "mobileVerifyRequired": "N",
            "restrictionType": "N",
            "vendors": [],
            "bonusAmount": 1,
            "minimumRequiredTurnover": 1,
            "pointAmount": 1,
            "requiredTurnover": 1,
            "ticketClaimMethod": "MANUAL",
            "ticketType": "CASH_VOUCHER",
            "ticketId": ticket,
            "ticketName": "cash123",
            "promotionTicketBudget": {
                ticket: {
                    "promotionId": "",
                    "ticketId": ticket,
                    "ticketBudget": 0,
                    "ticketName": "cash123"
                }
            },
            "allowMessage": "N",
            "allowPushNotif": "N",
            "promotionMessage": {
                "id": "",
                "promotionId": "",
                "defaultLanguageInbox": "",
                "defaultLanguagePushNotif": "",
                "contentInbox": [],
                "contentPushNotif": []
            },
            "pointBudget": "999888",
            "walletType": 2,
            "status": "A",
            "promotionType": "MANUAL",
            "budget": 999888,
            "linkedAnnouncementList": [],
            "bonusPointAmount": "",
            "languageInbox": "",
            "languagePushNotif": "",
            "playerRemark": ""
        }
        response=requests.post(URL,json=payload,headers=header,verify=False)
        response_json=response.json()
        if response_json.get('success'):
            logging.info("創建手動活動成功")
        else:
            print(response_json)
            logging.error("創建手動活動失敗")
    def search_exist_announcment(self,merchantCode,refer=27000):
        URL="http://sit-admin2.tcg.com/tac/api/relay/get/promo-announcement-list"
        
        header=self.header(merchantCode,refer)
        params={
            "page":1,
            "size":10,
            "sort":"id,desc"
        }
        response=requests.get(URL,params=params,headers=header,verify=False)
        response_json=response.json()
        if response_json.get("success"):
            value_list=response_json.get("value",[])
            if len(value_list) == 0:
                logging.info("沒有公告存在")
                return None
            else:
                logging.info("有公告存在")
                label_ID=value_list[0].get("id")
                return label_ID
        else:
            logging.error("查詢公告失敗")
            return None
    def search_Title_content(self,merchantCode,label_ID,refer=27000):
        URL=f"http://sit-admin2.tcg.com/tac/api/relay/get/promo-announcement-id?id={label_ID}"
        header=self.header(merchantCode,refer)
        
        response=requests.get(URL,headers=header,verify=False)
        response_json=response.json()
        if response_json.get("success"):
            title = response_json["value"]["sections"][0]["contents"][0]["title"]
            content = response_json["value"]["sections"][0]["contents"][0]["content"]
            print(title)
            print(content)
            return title, content
        else:
            return None, None

    def create_announcement(self,merchantCode,refer=27000):
        URL="http://sit-admin2.tcg.com/tac/api/relay/post/promo-announcement-create"
        start_Time, endTime, start_str, end_str = self.unitTime()
        header=self.header(merchantCode,refer)
        payload={
            "id": 3525721,
            "startDate": start_Time,
            "endDate": None,
            "noExpiry": True,
            "categories": [
                1454001,
                1454002,
                1454003,
                1454004,
                1454005,
                1454006,
                1454007,
                1454008,
                1454009,
                1454010,
                1454012,
                1454013,
                1454014,
                1454015,
                1454016,
                1454017
            ],
            "labels": [],
            "ranks": [],
            "agents": [],
            "agentType": None,
            "promotionId": None,
            "promoType": None,
            "remark": "",
            "redirect": None,
            "externalLink": None,
            "postedOnCreate": True,
            "sections": [
                {
                    "contents": [
                        {
                            "language": "EN",
                            "title": "x",
                            "content": "<p>x</p>\n",
                            "images": {
                                "M": [
                                    2347128,
                                    2347128
                                ],
                                "W": [
                                    2347128,
                                    2347128
                                ]
                            },
                            "contentM": None
                        }
                    ],
                    "sequence": 0
                }
            ],
            "platforms": [
                "W"
            ]
        }
        
        response=requests.post(URL,headers=header,json=payload,verify=False)
        response_json=response.json()
        if response_json.get("success"):
            logging.info("創建公告成功")
            return True
        else:
            print(response_json)
            logging.info("創建公告失敗")
            return False
    #def Manual_Sign_up(self,ticket,merchantCode,label_ID,title,content,refer=24785):
    def Manual_Sign_up(self,ticket,merchantCode,label_ID,title,content,refer=24785):
        URL="http://sit-admin2.tcg.com/tac/api/relay/post/mcs-signUpPromotion-create-create"
        start_Time, endTime, start_str, end_str = self.unitTime()
        header=self.header(merchantCode,refer)
        payload={
            "id": "",
            "promotionId": "",
            "merchantCode": merchantCode,
            "name": "ccccc",
            "budget": "999888",
            "description": "",
            "startTime": start_Time,
            "endTime": endTime,
            "signUpStartDate": start_str,
            "signUpEndDate": end_str,
            "effectiveTime": 11,
            "appRequirement": "N",
            "requiredTurnover": 0,
            "minimumRequiredTurnover": 0,
            "bonusAmount": 0,
            "status": "A",
            "noExpiry": "Y",
            "noExpirySignUp": "Y",
            "type": "SIGNUP",
            "promotionType": "SIGNUP",
            "walletType": "2",
            "txType": 6131,
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
            "claimMethod": "AUTO",
            "contactNumberRequiredType": "A",
            "contactNumFileName": "",
            "fileDetailList": [],
            "participant": "ALL",
            "forAllLabel": "Y",
            "remark": "1",
            "linkedAnnouncementList": [
                {
                    "value": 3608730,
                    "label": "sss",
                    "id": 3608730,
                    "title": "sss",
                    "content": None,
                    "contents": [
                        {
                        "sequence": 0,
                        "title": "c",
                        "content": f"<p>c</p>",
                        "language": "EN"
                    },
                    {
                        "sequence": 0,
                        "title": "c",
                        "content": f"<p>c</p>",
                        "language": "EN"
                    }
                ],
                    "merchantCode": merchantCode,
                    "createdBy": "carrine01",
                    "updatedBy": None,
                    "createdAt": start_Time,
                    "updatedAt": None,
                    "type": "PR",
                    "status": "A",
                    "startDate": start_Time,
                    "endDate": endTime,
                    "expiry": None,
                    "noExpiry": 1,
                    "priority": None,
                    "platform": "A",
                    "execution": None,
                    "photoUrl": None,
                    "category": "new_player",
                    "expired": None,
                    "priorityUpdatedFlag": False,
                    "startDateStr": None,
                    "endDateStr": None,
                    "labels": None,
                    "ranks": None,
                    "announcementImages": None,
                    "agents": None,
                    "agentNames": None,
                    "linkedPromotionId": None,
                    "linkedPromotionName": None,
                    "agentType": None,
                    "promotionType": None
                }
            ],
            "agentNames": "",
            "websites": "",
            "operationLabels": [],
            "totalContactNumbers": 0,
            "forDeletionList": [],
            "pointBudget": "999888",
            "promotionMessage": {
                "contentInbox": [],
                "defaultLanguageInbox": "CN",
                "contentPushNotif": [],
                "defaultLanguagePushNotif": "CN"
            },
            "languageInbox": "",
            "languagePushNotif": "",
            "activeKeyInbox": "",
            "activeKeyPushNotif": "",
            "allowMessage": "N",
            "allowPushNotif": "N",
            "promotionTicketBudget": {},
            "mobileVerified": "N",
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
            "kycRequired": "N",
            "requestRewardType": "O",
            "remarksRequired": "N",
            "pictureRequired": "N",
            "ticketClaimMethod": "MANUAL",
            "playerRemark": "",
            "startTimeString": start_str,
            "endTimeString": end_str,
            "signUpStartDateString": start_str,
            "signUpEndDateString": end_str,
            "restrictionType": None,
            "vendors": [],
            "signUpPromotionConfigs": [
                {
                    "configId": "",
                    "promotionId": 0,
                    "signUpPromotionConfigLabels": [],
                    "bonusAmount": 1,
                    "pointAmount": 1,
                    "ticketType": "CASH_VOUCHER",
                    "ticketId": ticket,
                    "ticketName": "",
                    "turnoverMultiplier": 1,
                    "minRequiredTurnover": "",
                    "forAllLabel": "Y",
                    "minRequiredTo": 1,
                    "ticketQuantity": 1
                }
            ]
        }
        response=requests.post(URL,json=payload,headers=header,verify=False)
        response_json=response.json()
        if response_json.get('success'):
            logging.info("創建手工報名成功")
        else:
            print(response_json)
            logging.error("創建手工報名失敗")
            
    def get_group_ID(self,merchantCode,refer=250001):
        URL="http://sit-admin2.tcg.com/tac/api/relay/get/mcs-v3-player-rank-search"
        header=self.header(merchantCode,refer)
        params={
            "merchantCode":merchantCode
        }
        response=requests.get(URL,params=params,headers=header,verify=False)
        response_json=response.json()
        if response_json.get('value'):
            value = response_json.get('value')
            group=value.get("group",[])
            if len(group)>0:
                groupId=group[0].get("groupId")
                logging.info(f"Group_ID:{groupId}")
                return groupId
            elif not group:
                logging.info("沒有Group_ID")
                return False
        else:
            print(response_json)
            logging.error("API響應錯誤")
    def Establish_rank(self,merchantCode,refer=250001):
        URL="http://sit-admin2.tcg.com/tac/api/relay/post/mcs-v3-player-rank-group-create"
        header=self.header(merchantCode,refer)
        payload={
            "merchantCode": merchantCode,
            "group": {
                "merchantCode": merchantCode,
                "groupName": "L5"
            },
            "playerRank": {
                "groupName": "Lv1"
            }
        }
        response=requests.post(URL,json=payload,headers=header,verify=False)
        response_json=response.json()
        if response_json.get("success"):
            logging.info("建立等級成功")
        else:
            logging.error("建立等級失敗")
            
    def get_current_label(self,merchantCode,groupId,refer=250001):
        
        URL="http://sit-admin2.tcg.com/tac/api/relay/get/mcs-v3-player-rank-details"
        header=self.header(merchantCode,refer)
        params={
            "groupId":groupId,
            "merchantCode":merchantCode
        }
        response=requests.get(URL,params=params,headers=header,verify=False)
        response_json=response.json()
        if response_json.get('value'):
            value = response_json.get('value')
            labelId=value[0].get("labelId")
            if labelId:
                logging.info(f"拿到labelID:{labelId}")
                return labelId
            else:
                logging.error("沒有拿到labelID")
                return None
        else:
            print(response_json)
            logging.error("API響應失敗")
            return None
    
    def UPGRADE_BONUS(self,ticket,merchantCode,refer=20346):
        start_Time, endTime, start_str, end_str = self.unitTime()
        URL="http://sit-admin2.tcg.com/tac/api/relay/post/mcs-internal-v3-playerRankPromotion-add"
        header=self.header(merchantCode,refer)
        print(merchantCode)
        payload={
            "id": "",
            "promotionId": "",
            "merchantCode": merchantCode,
            "name": "1111",
            "budget": 999888,
            "description": "",
            "startTime": start_Time,
            "endTime": endTime,
            "effectiveTime": 0,
            "requiredTurnover": 0,
            "minimumRequiredTurnover": 0,
            "bonusAmount": 0,
            "status": "A",
            "noExpiry": "N",
            "promotionType": "UPGRADE_BONUS",
            "walletType": "2",
            "txType": 6131,
            "excludeRebate": "N",
            "minimumClaimAmount": 0,
            "maximumClaimAmount": 0,
            "maxClaimCount": 1,
            "maxClaimCountType": "PROMOTION",
            "productType": "ALL",
            "excludeValidBet": "N",
            "uniqueIp": "N",
            "bankCardRequired": "N",
            "emailRequired": "N",
            "contactNumberRequired": "N",
            "qqRequired": "N",
            "payeeNameRequired": "N",
            "claimMethod": "AUTO",
            "contactNumberRequiredType": "A",
            "contactNumFileName": "",
            "fileDetailList": [],
            "participant": "ALL",
            "forAllLabel": "Y",
            "remark": "111",
            "linkedAnnouncementList": [],
            "agentNames": "",
            "operationLabels": [],
            "totalContactNumbers": 0,
            "forDeletionList": [],
            "groupName": "",
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
            "promotionTicketBudget": {},
            "budgetStr": "999888",
            "pointBudgetStr": "999888",
            "ticketClaimMethod": "MANUAL",
            "playerRemark": "升级奖励 1111",
            "playerRankPromotionConfigs": [
                {
                    "configId": "",
                    "playerRankPromotionConfigLabels": [],
                    "bonusAmount": 1,
                    "pointAmount": 1,
                    "ticketType": None,
                    "ticketId": ticket,
                    "ticketName": "",
                    "ticketQuantity": 1,
                    "turnoverMultiplier": 1,
                    "forAllLabel": "Y"
                }
            ],
            "startTimeString": start_str,
            "endTimeString": end_str
        }
        response=requests.post(URL,json=payload,headers=header,verify=False)
        response_json=response.json()
        print(response_json)
        if response_json.get('success'):
            logging.info("創建升級獎勵成功")
        else:
            print(response_json)
            logging.error("創建升級獎勵失敗")
    def VIP_BONUS(self,ticket,merchantCode,labelId,refer=20324):
        URL="http://sit-admin2.tcg.com/tac/api/relay/put/promo-rank-salary-edit"
        header=self.header(merchantCode,refer)
        payload={
            "promoName": "1",
            "dailyStatus": "A",
            "weeklyStatus": "A",
            "weeklyIsNextDayReward": "Y",
            "weeklyRewardDay": "MONDAY",
            "weeklyStartDay": "MONDAY",
            "monthlyStatus": "A",
            "monthlyIsNextDayReward": "Y",
            "monthlyRewardDay": 1,
            "claimMethod": "AUTO",
            "dailyPlayerRemark": "日俸禄 11",
            "weeklyPlayerRemark": "周俸禄 1",
            "monthlyPlayerRemark": "月俸禄 1",
            "configs": [
                {
                    "type": "DAILY",
                    "details": [
                        {
                            "configDetailId": None,
                            "labelIds": [
                                labelId
                            ],
                            "rewards": [
                                {
                                    "rewardId": None,
                                    "requiredDepositAmount": 1,
                                    "requiredBetAmount": 1,
                                    "turnoverMultiplier": 11,
                                    "bonusAmount": 1,
                                    "pointAmount": 1,
                                    "ticketId": ticket
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "WEEKLY",
                    "details": [
                        {
                            "configDetailId": None,
                            "labelIds": [
                                labelId
                            ],
                            "rewards": [
                                {
                                    "rewardId": None,
                                    "requiredDepositAmount": 1,
                                    "requiredBetAmount": 1,
                                    "turnoverMultiplier": 1,
                                    "bonusAmount": 1,
                                    "pointAmount": 1,
                                    "ticketId": ticket
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "MONTHLY",
                    "details": [
                        {
                            "configDetailId": None,
                            "labelIds": [
                                labelId
                            ],
                            "rewards": [
                                {
                                    "rewardId": None,
                                    "requiredDepositAmount": 1,
                                    "requiredBetAmount": 1,
                                    "turnoverMultiplier": 11,
                                    "bonusAmount": 1,
                                    "pointAmount": 1,
                                    "ticketId": ticket
                                }
                            ]
                        }
                    ]
                }
            ],
            "message": {
                "inbox": {
                    "active": "N"
                },
                "notification": {
                    "active": "N"
                }
            }
        }
        response=requests.put(URL,json=payload,headers=header,verify=False)
        response_json=response.json()
        if response_json.get('success'):
            logging.info("創建VIP俸祿成功")
        else:
            print(response_json)
            logging.error("創建VIP俸祿失敗")
    def Invite_Bonus(self,ticket,merchantCode,refer=240001):
        URL="http://10.80.1.20:7001/promo-be/resources/promotion/referral_settings/update"
        header=self.header(merchantCode,refer)
        payload={
            "merchantCode": merchantCode,
            "promotionId": 123,
            "status": "I",
            "name": "活動名稱",
            "referrerRemark": "基本設置 邀请人交易备注",
            "referredRemark": "受邀人交易备注",
            "referrerConditionFlag": "Y",
            "referralPromotionOperationLabels": None,
            "referralPromotionRankLabels": None,
            "mobileVerified": "N",
            "isUniqueIp": "Y",
            "ipCheckQualifiedDay": 30,
            "ipMaxQualifiedCount": 1,
            "depositRequired": "N",
            "requiredDepositAmount": 100,
            "depositCountRequired": "N",
            "depositCount": 10,
            "bettingRequired": "N",
            "requiredBettingAmount": 200,
            "idRequired": "N",
            "bankCardRequired": "N",
            "sameNameCheck": "N",
            "associationScoreRequired": "N",
            "associationScore": 260,
            "kycRequired": "N",
            "linkType": "direct",
            "linkedAgentId": 789,
            "linkedAgentName": "代理名称",
            "domainList": [],
            "maxAllowDay": 30,
            "reviewInvitationRewardEnabled": "AUTO",
            "reviewAchievementRewardEnabled": "MANUAL",
            "invitationRewardEnabled": "N",
            "invitationRewardLabelType": 5,
            "referralPromotionConfigGroupList": [
                {
                "groupName": "default",
                "rankLabels": [],
                "agentNames": [],
                "content": [
                    {
                    "id": 0,
                    "promotionId": 0,
                    "rangeFrom": 0,
                    "rangeTo": 0,
                    "bonusAmount": 0,
                    "pointAmount": 0,
                    "turnoverMultiplier": 0,
                    "referredBonusAmount": 0,
                    "referredPointAmount": 0,
                    "referredTurnoverMultiplier": 0,
                    "ticketId": 0,
                    "ticketType": "string",
                    "ticketName": "string",
                    "referredTicketId": 0,
                    "referredTicketType": "string",
                    "referredTicketName": "string",
                    "ticketTurnoverMultiplier": 0,
                    "referredTicketTurnoverMultiplier": 0
                    }
                ],
                "depositRequired": "Y",
                "requiredDepositAmount": 0,
                "depositCountRequired": "Y",
                "depositCount": 0,
                "bettingRequired": "Y",
                "requiredBettingAmount": 0,
                "requiredBettingGameType": "ALL",
                "turnoverGameType": "ALL",
                "sort": 0
                }
            ],
            "achievementRewardEnabled": "N",
            "achievementRewardResetTimeUnit": "Monthly",
            "achievementRewardEnableTime": "2024-01-01T00:00:00Z",
            "referralAchievementRewardConfigList": [
                {
                "id": 0,
                "turnoverMultiplier": 0,
                "depositUsers": 0,
                "bonusAmount": 0,
                "pointAmount": 0,
                "ticketId": 0,
                "ticketType": "string",
                "ticketName": "string",
                "ticketTurnoverMultiplier": 0
                }
            ],
            "depositRebateEnabled": "N",
            "referralDepositRebate": {
                "limitSetting": {
                "contDepositLimitEnabled": "Y",
                "limitType": "REFERRER_INCOME",
                "maxDepositBonusPerReferrer": 1.1,
                "dailyMaxDepositBonusPerReferrer": 1.2,
                "maxDepositBonusPerPlayer": 1.3,
                "dailyMaxDepositBonusPerPlayer": 1.4
                },
                "referralDepositRebateConfigs": [
                {
                    "rankSequence": 1,
                    "referralDepositRebateDetails": [
                    {
                        "id": 0,
                        "requiredLastDayDepositAmount": 1,
                        "depositRebatePercentage": 0.23,
                        "turnoverMultiplier": 0
                    }
                    ]
                }
                ]
            },
            "bettingRebateEnabled": "N",
            "referralBettingRebate": {
                "limitSetting": {
                "bettingRebateLimitEnabled": "N",
                "limitType": "REFERRER_INCOME",
                "gameLimits": [
                    {
                    "gameType": "RNG",
                    "maxReferrerDayReward": 999.9999,
                    "maxReferrerReward": 999.9999,
                    "maxInviteeDayRebate": 999.9999,
                    "maxInviteeRebate": 999.9999,
                    "updatedBy": "string",
                    "updateTime": 0
                    }
                ]
                },
                "referralBettingRebateConfigs": [
                {
                    "rankSequence": 1,
                    "referralBettingRebateDetails": [
                    {
                        "id": 0,
                        "rebateLevel": 1,
                        "lottRate": 0.27,
                        "sportsRate": 0.27,
                        "fishRate": 0.27,
                        "liveRate": 0.27,
                        "rngRate": 0.27,
                        "pvpRate": 0.27,
                        "elottRate": 0.27,
                        "turnoverMultiplier": 0
                    }
                    ]
                }
                ]
            },
            "linkedAnnouncementList": [
                {
                "id": 0,
                "title": "string"
                }
            ],
            "allowMessage": "N",
            "allowPushNotif": "N",
            "promotionMessage": {
                "id": 0,
                "promotionId": 0,
                "defaultLanguageInbox": "string",
                "defaultLanguagePushNotif": "string",
                "inboxAutoDeleteEnabled": "Y",
                "inboxRetentionDays": 0,
                "contentInboxOneTime": [
                {
                    "title": "string",
                    "content": "string",
                    "language": "string"
                }
                ],
                "contentPushNotifOneTime": [
                {
                    "title": "string",
                    "content": "string",
                    "language": "string"
                }
                ],
                "contentInboxReferred": [
                {
                    "title": "string",
                    "content": "string",
                    "language": "string"
                }
                ],
                "contentPushNotifReferred": [
                {
                    "title": "string",
                    "content": "string",
                    "language": "string"
                }
                ],
                "contentInboxAchievementReward": [
                {
                    "title": "string",
                    "content": "string",
                    "language": "string"
                }
                ],
                "contentPushNotifAchievementReward": [
                {
                    "title": "string",
                    "content": "string",
                    "language": "string"
                }
                ],
                "contentInboxCont": [
                {
                    "title": "string",
                    "content": "string",
                    "language": "string"
                }
                ],
                "contentPushNotifCont": [
                {
                    "title": "string",
                    "content": "string",
                    "language": "string"
                }
                ],
                "contentInboxBettingRebate": [
                {
                    "title": "string",
                    "content": "string",
                    "language": "string"
                }
                ],
                "contentPushNotifBettingRebate": [
                {
                    "title": "string",
                    "content": "string",
                    "language": "string"
                }
                ]
            },
            "referralRankSetting": {
                "id": 0,
                "totalQualifiedCountRequired": "Y",
                "totalDepositRequired": "Y",
                "totalBetRequired": "Y",
                "monthQualifiedCountRequired": "Y",
                "monthDepositRequired": "Y",
                "monthBetRequired": "Y",
                "lastMonthQualifiedCountRequired": "Y",
                "lastMonthDepositRequired": "Y",
                "lastMonthBetRequired": "Y",
                "upgradeConditionType": "AND",
                "downgradeConditionType": "OR",
                "upgradeMode": "MANUAL",
                "downgradeMode": "MANUAL",
                "downgradeType": "SINGLE"
            },
            "referralRankConfigList": [
                {
                "id": 0,
                "rankSequence": 1,
                "rankName": "返佣等級名稱",
                "requiredTotalQualifiedCount": 1,
                "requiredTotalDeposit": 123.45,
                "requiredTotalBet": 123.45,
                "requiredMonthQualifiedCount": 1,
                "requiredMonthDeposit": 123.45,
                "requiredMonthBet": 123.45,
                "requiredLastMonthQualifiedCount": 1,
                "requiredLastMonthDeposit": 123.45,
                "requiredLastMonthBet": 123.45
                }
            ],
            "imagePath": "string",
            "imagePathMobile": "string",
            "bannerImagePath": "string",
            "bannerImagePathMobile": "string",
            "requiredBettingGameType": "ALL"
            }
        response=requests.post(URL,json=payload,headers=header,verify=False)
        response_json=response.json()
        if response_json.get('success'):
            logging.info("修改邀請反佣成功")
        else:
            print(response_json)
            logging.error("修改邀請反佣失敗")
    def login_task(self,ticket,merchantCode, refer=24781):
        start_Time, endTime, start_str, end_str = self.unitTime()
        URL="http://sit-admin2.tcg.com/tac/api/relay/post/promo-promotion-login-task-create"
        header=self.header(merchantCode,refer)
        payload={
            "promoName": "xxxx",
            "startTime": start_Time,
            "endTime": endTime,
            "noExpiry": "Y",
            "remark": "x",
            "description": "",
            "status": "A",
            "participant": {
                "participant": "ALL",
                "customerNames": [],
                "websites": [],
                "operationLabelIds": [],
                "contactFileIds": []
            },
            "message": {
                "inbox": {
                    "active": "N"
                },
                "notification": {
                    "active": "N"
                }
            },
            "claimCountLimit": None,
            "claimIntervalHourLimit": None,
            "rewardGroupList": [
                {
                    "labelId": [],
                    "agentName": [],
                    "rewardList": [
                        {
                            "ticketId": ticket,
                            "ticketQuantity": 1
                        }
                    ]
                }
            ]
        }
        response=requests.post(URL,json=payload,headers=header,verify=False)
        response_json=response.json()
        if response_json.get('success'):
            logging.info("創建登入任務成功")
        else:
            print(response_json)
            logging.error("創建登入任務失敗")
            
    def Sign_in_task_week(self,ticket,merchantCode, refer=24781):
        start_Time, endTime, start_str, end_str = self.unitTime()
        URL="http://sit-admin2.tcg.com/tac/api/relay/post/mcs-internal-v3-mcsLoginPromotion-createLoginPromotionWithDetails"
        header=self.header(merchantCode,refer)
        payload={
            "id": "",
            "promotionId": "",
            "merchantCode": merchantCode,
            "name": "sss",
            "promotionName": "",
            "description": "<p>ss</p>\n",
            "budget": "999888",
            "type": "W",
            "startTime": start_Time,
            "endTime": endTime,
            "requiredTurnover": 0,
            "status": "A",
            "sorting": 0,
            "noExpiry": "Y",
            "allowCycle": "Y",
            "allowSkip": "Y",
            "triggerCondition": "",
            "triggerLogin": "Y",
            "triggerDeposit": "N",
            "triggerValidBet": "N",
            "loginPromotionConfigs": [
                {
                    "configId": "",
                    "promotionId": "",
                    "merchantCode": merchantCode,
                    "promotionName": "test0417",
                    "description": "",
                    "playerRanks": [],
                    "loginPromotionConfigDetails": [
                        {
                            "amount": 1,
                            "pointAmount": 1,
                            "ticketType": "CASH_VOUCHER",
                            "ticketId": ticket,
                            "ticketName": "",
                            "depositAmount": 0,
                            "validBetAmount": 0,
                            "dayNo": 1,
                            "id": "",
                            "configId": "",
                            "promotionId": ""
                        },
                        {
                            "amount": 1,
                            "pointAmount": 1,
                            "ticketType": "CASH_VOUCHER",
                            "ticketId": ticket,
                            "ticketName": "",
                            "depositAmount": 0,
                            "validBetAmount": 0,
                            "dayNo": 2,
                            "id": "",
                            "configId": "",
                            "promotionId": ""
                        },
                        {
                            "amount": 1,
                            "pointAmount": 1,
                            "ticketType": "CASH_VOUCHER",
                            "ticketId": ticket,
                            "ticketName": "",
                            "depositAmount": 0,
                            "validBetAmount": 0,
                            "dayNo": 3,
                            "id": "",
                            "configId": "",
                            "promotionId": ""
                        },
                        {
                            "amount": 1,
                            "pointAmount": 1,
                            "ticketType": None,
                            "ticketId": None,
                            "ticketName": "",
                            "depositAmount": 0,
                            "validBetAmount": 0,
                            "dayNo": 4,
                            "id": "",
                            "configId": "",
                            "promotionId": ""
                        },
                        {
                            "amount": 1,
                            "pointAmount": 1,
                            "ticketType": None,
                            "ticketId": None,
                            "ticketName": "",
                            "depositAmount": 0,
                            "validBetAmount": 0,
                            "dayNo": 5,
                            "id": "",
                            "configId": "",
                            "promotionId": ""
                        },
                        {
                            "amount": 1,
                            "pointAmount": 1,
                            "ticketType": None,
                            "ticketId": None,
                            "ticketName": "",
                            "depositAmount": 0,
                            "validBetAmount": 0,
                            "dayNo": 6,
                            "id": "",
                            "configId": "",
                            "promotionId": ""
                        },
                        {
                            "amount": 1,
                            "pointAmount": 1,
                            "ticketType": None,
                            "ticketId": None,
                            "ticketName": "",
                            "depositAmount": 0,
                            "validBetAmount": 0,
                            "dayNo": 7,
                            "id": "",
                            "configId": "",
                            "promotionId": ""
                        }
                    ],
                    "forAllLabel": "Y",
                    "currentPage": 1,
                    "id": ""
                }
            ],
            "registerDateType": "R",
            "daysAfterCount": 0,
            "promotionType": "LOGIN",
            "walletType": 2,
            "txType": 6131,
            "excludeRebate": "N",
            "minimumClaimAmount": 0,
            "maximumClaimAmount": 0,
            "participant": "ALL",
            "agentNames": "",
            "operationLabels": [],
            "forDeletionList": [],
            "fileDetailList": [],
            "totalContactNumbers": 0,
            "productType": "ALL",
            "forAllLabel": "Y",
            "linkedAnnouncementList": [],
            "promotionMessage": {
                "id": "",
                "contentInbox": [],
                "contentPushNotif": [],
                "defaultLanguageInbox": "",
                "defaultLanguagePushNotif": "",
                "promotionId": ""
            },
            "languageInbox": "",
            "languagePushNotif": "",
            "activeKeyInbox": "",
            "activeKeyPushNotif": "",
            "allowMessage": "N",
            "allowPushNotif": "N",
            "contactNumberRequired": "N",
            "telegramRequired": "N",
            "viberRequired": "N",
            "appleIdRequired": "N",
            "idRequired": "N",
            "birthdayRequired": "N",
            "kycRequired": "N",
            "twitterRequired": "N",
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
            "mobileVerified": "",
            "ticketClaimMethod": "MANUAL",
            "playerRemark": "周签到 sss",
            "budgetStr": "999888",
            "pointBudgetStr": "999888",
            "claimMethod": "AUTO",
            "maxClaimCountType": "DAILY",
            "startTimeString": start_str,
            "endTimeString": end_str,
            "registerStartDate": start_Time,
            "registerEndDate": endTime,
            "createdBy": "carrine01",
            "createdAt": None,
            "updatedBy": None,
            "updatedAt": None,
            "minimumRequiredTurnover": None,
            "pointBudget": 999888,
            "claimedAmount": None,
            "maxClaimCount": None,
            "claimedCount": None,
            "customerClaimedCount": None,
            "genNoExpiry": None,
            "remark": None,
            "bonusAmount": None,
            "effectiveTime": None,
            "excludeValidBet": None,
            "uniqueIp": "N",
            "operationLabelIds": None,
            "linkedAnnouncementStr": None,
            "agents": None,
            "contactNumFileName": None,
            "rankGroupId": None,
            "groupName": None,
            "registerStartDateString": start_Time,
            "registerEndDateString": endTime,
            "agentType": None,
            "mobileNumMatchType": "PRECISE",
            "contactFileIds": []
        }
        
        response=requests.post(URL,json=payload,headers=header,verify=False)
        response_json=response.json()
        if response_json.get('success'):
            logging.info("創建週簽到成功")
        else:
            print(response_json)
            logging.error("創建週簽到失敗")
    def Sign_in_task_new(self,ticket,merchantCode, refer=24781):
        start_Time, endTime, start_str, end_str = self.unitTime()
        URL="http://sit-admin2.tcg.com/tac/api/relay/post/mcs-internal-v3-mcsLoginPromotion-createLoginPromotionWithDetails"
        header=self.header(merchantCode,refer)
        payload={
            "id": "",
        "promotionId": "",
        "merchantCode": merchantCode,
        "name": "aaaa",
        "promotionName": "",
        "description": "<p>aaaaa</p>\n",
        "budget": "999888",
        "type": "N",
        "startTime": start_Time,
        "endTime": endTime,
        "requiredTurnover": 0,
        "status": "A",
        "sorting": 0,
        "noExpiry": "Y",
        "allowCycle": "Y",
        "allowSkip": "Y",
        "triggerCondition": "",
        "triggerLogin": "Y",
        "triggerDeposit": "N",
        "triggerValidBet": "N",
        "loginPromotionConfigs": [
            {
                "configId": "",
                "promotionId": "",
                "merchantCode": merchantCode,
                "promotionName": "test0417",
                "description": "",
                "playerRanks": [],
                "loginPromotionConfigDetails": [
                    {
                        "amount": 1,
                        "pointAmount": 1,
                        "ticketType": "CASH_VOUCHER",
                        "ticketId": ticket,
                        "ticketName": "",
                        "depositAmount": 0,
                        "validBetAmount": 0,
                        "dayNo": 1,
                        "id": "",
                        "configId": "",
                        "promotionId": ""
                    }
                ],
                "forAllLabel": "Y",
                "currentPage": 1,
                "id": ""
            }
        ],
        "registerDateType": "R",
        "daysAfterCount": 0,
        "promotionType": "LOGIN",
        "walletType": 2,
        "txType": 6131,
        "excludeRebate": "N",
        "minimumClaimAmount": 0,
        "maximumClaimAmount": 0,
        "participant": "ALL",
        "agentNames": "",
        "operationLabels": [],
        "forDeletionList": [],
        "fileDetailList": [],
        "totalContactNumbers": 0,
        "productType": "ALL",
        "forAllLabel": "Y",
        "linkedAnnouncementList": [],
        "promotionMessage": {
            "id": "",
            "contentInbox": [],
            "contentPushNotif": [],
            "defaultLanguageInbox": "",
            "defaultLanguagePushNotif": "",
            "promotionId": ""
        },
        "languageInbox": "",
        "languagePushNotif": "",
        "activeKeyInbox": "",
        "activeKeyPushNotif": "",
        "allowMessage": "N",
        "allowPushNotif": "N",
        "contactNumberRequired": "N",
        "telegramRequired": "N",
        "viberRequired": "N",
        "appleIdRequired": "N",
        "idRequired": "N",
        "birthdayRequired": "N",
        "kycRequired": "N",
        "twitterRequired": "N",
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
        "mobileVerified": "",
        "ticketClaimMethod": "MANUAL",
        "playerRemark": "新用户签到 aaaa",
        "budgetStr": "999888",
        "pointBudgetStr": "999888",
        "claimMethod": "MANUAL",
        "maxClaimCountType": "DAILY",
        "startTimeString": start_str,
        "endTimeString": end_str,
        "registerStartDate": start_str,
        "registerEndDate": end_str,
        "createdBy": "carrine01",
        "createdAt": None,
        "updatedBy": None,
        "updatedAt": None,
        "minimumRequiredTurnover": None,
        "pointBudget": 999888,
        "claimedAmount": None,
        "maxClaimCount": None,
        "claimedCount": None,
        "customerClaimedCount": None,
        "genNoExpiry": None,
        "remark": None,
        "bonusAmount": None,
        "effectiveTime": None,
        "excludeValidBet": None,
        "uniqueIp": "N",
        "operationLabelIds": None,
        "linkedAnnouncementStr": None,
        "agents": None,
        "contactNumFileName": None,
        "rankGroupId": None,
        "groupName": None,
        "registerStartDateString": start_str,
        "registerEndDateString": end_str,
        "agentType": None,
        "mobileNumMatchType": "PRECISE",
        "contactFileIds": []
            }
        response=requests.post(URL,json=payload,headers=header,verify=False)
        response_json=response.json()
        if response_json.get('success'):
            logging.info("創建新用戶遷到成功")
        else:
            print(response_json)
            logging.error("創建新用戶簽到失敗")
            
    def Sign_in_task_month(self,ticket,merchantCode, refer=24781):
        start_Time, endTime, start_str, end_str = self.unitTime()
        URL="http://sit-admin2.tcg.com/tac/api/relay/post/mcs-internal-v3-mcsLoginPromotion-createLoginPromotionWithDetails"
        header=self.header(merchantCode,refer)
        payload={
            "id": "",
    "promotionId": "",
    "merchantCode": merchantCode,
    "name": "111",
    "promotionName": "",
    "description": "<p>11</p>\n",
    "budget": "999888",
    "type": "M",
    "startTime": start_Time,
    "endTime": endTime,
    "requiredTurnover": 0,
    "status": "A",
    "sorting": 0,
    "noExpiry": "Y",
    "allowCycle": "Y",
    "allowSkip": "Y",
    "triggerCondition": "",
    "triggerLogin": "Y",
    "triggerDeposit": "N",
    "triggerValidBet": "N",
    "loginPromotionConfigs": [
        {
            "configId": "",
            "promotionId": "",
            "merchantCode": merchantCode,
            "promotionName": "test0417",
            "description": "",
            "playerRanks": [],
            "loginPromotionConfigDetails": [
                {
                    "amount": 1,
                    "pointAmount": 1,
                    "ticketType": "CASH_VOUCHER",
                    "ticketId": ticket,
                    "ticketName": "",
                    "depositAmount": 0,
                    "validBetAmount": 0,
                    "dayNo": 1,
                    "id": "",
                    "configId": "",
                    "promotionId": ""
                },
                {
                    "amount": "0",
                    "pointAmount": "0",
                    "ticketType": "",
                    "ticketId": "",
                    "ticketName": "",
                    "depositAmount": 0,
                    "validBetAmount": 0,
                    "dayNo": 2,
                    "id": "",
                    "configId": "",
                    "promotionId": ""
                },
                {
                    "amount": "0",
                    "pointAmount": "0",
                    "ticketType": "",
                    "ticketId": "",
                    "ticketName": "",
                    "depositAmount": 0,
                    "validBetAmount": 0,
                    "dayNo": 3,
                    "id": "",
                    "configId": "",
                    "promotionId": ""
                },
                {
                    "amount": "0",
                    "pointAmount": "0",
                    "ticketType": "",
                    "ticketId": "",
                    "ticketName": "",
                    "depositAmount": 0,
                    "validBetAmount": 0,
                    "dayNo": 4,
                    "id": "",
                    "configId": "",
                    "promotionId": ""
                },
                {
                    "amount": "0",
                    "pointAmount": "0",
                    "ticketType": "",
                    "ticketId": "",
                    "ticketName": "",
                    "depositAmount": 0,
                    "validBetAmount": 0,
                    "dayNo": 5,
                    "id": "",
                    "configId": "",
                    "promotionId": ""
                },
                {
                    "amount": "0",
                    "pointAmount": "0",
                    "ticketType": "",
                    "ticketId": "",
                    "ticketName": "",
                    "depositAmount": 0,
                    "validBetAmount": 0,
                    "dayNo": 6,
                    "id": "",
                    "configId": "",
                    "promotionId": ""
                },
                {
                    "amount": "0",
                    "pointAmount": "0",
                    "ticketType": "",
                    "ticketId": "",
                    "ticketName": "",
                    "depositAmount": 0,
                    "validBetAmount": 0,
                    "dayNo": 7,
                    "id": "",
                    "configId": "",
                    "promotionId": ""
                },
                {
                    "amount": "0",
                    "pointAmount": "0",
                    "ticketType": "",
                    "ticketId": "",
                    "ticketName": "",
                    "depositAmount": 0,
                    "validBetAmount": 0,
                    "dayNo": 8,
                    "id": "",
                    "configId": "",
                    "promotionId": ""
                },
                {
                    "amount": "0",
                    "pointAmount": "0",
                    "ticketType": "",
                    "ticketId": "",
                    "ticketName": "",
                    "depositAmount": 0,
                    "validBetAmount": 0,
                    "dayNo": 9,
                    "id": "",
                    "configId": "",
                    "promotionId": ""
                },
                {
                    "amount": "0",
                    "pointAmount": "0",
                    "ticketType": "",
                    "ticketId": "",
                    "ticketName": "",
                    "depositAmount": 0,
                    "validBetAmount": 0,
                    "dayNo": 10,
                    "id": "",
                    "configId": "",
                    "promotionId": ""
                },
                {
                    "amount": "0",
                    "pointAmount": "0",
                    "ticketType": "",
                    "ticketId": "",
                    "ticketName": "",
                    "depositAmount": 0,
                    "validBetAmount": 0,
                    "dayNo": 11,
                    "id": "",
                    "configId": "",
                    "promotionId": ""
                },
                {
                    "amount": "0",
                    "pointAmount": "0",
                    "ticketType": "",
                    "ticketId": "",
                    "ticketName": "",
                    "depositAmount": 0,
                    "validBetAmount": 0,
                    "dayNo": 12,
                    "id": "",
                    "configId": "",
                    "promotionId": ""
                },
                {
                    "amount": "0",
                    "pointAmount": "0",
                    "ticketType": "",
                    "ticketId": "",
                    "ticketName": "",
                    "depositAmount": 0,
                    "validBetAmount": 0,
                    "dayNo": 13,
                    "id": "",
                    "configId": "",
                    "promotionId": ""
                },
                {
                    "amount": "0",
                    "pointAmount": "0",
                    "ticketType": "",
                    "ticketId": "",
                    "ticketName": "",
                    "depositAmount": 0,
                    "validBetAmount": 0,
                    "dayNo": 14,
                    "id": "",
                    "configId": "",
                    "promotionId": ""
                },
                {
                    "amount": "0",
                    "pointAmount": "0",
                    "ticketType": "",
                    "ticketId": "",
                    "ticketName": "",
                    "depositAmount": 0,
                    "validBetAmount": 0,
                    "dayNo": 15,
                    "id": "",
                    "configId": "",
                    "promotionId": ""
                },
                {
                    "amount": "0",
                    "pointAmount": "0",
                    "ticketType": "",
                    "ticketId": "",
                    "ticketName": "",
                    "depositAmount": 0,
                    "validBetAmount": 0,
                    "dayNo": 16,
                    "id": "",
                    "configId": "",
                    "promotionId": ""
                },
                {
                    "amount": "0",
                    "pointAmount": "0",
                    "ticketType": "",
                    "ticketId": "",
                    "ticketName": "",
                    "depositAmount": 0,
                    "validBetAmount": 0,
                    "dayNo": 17,
                    "id": "",
                    "configId": "",
                    "promotionId": ""
                },
                {
                    "amount": "0",
                    "pointAmount": "0",
                    "ticketType": "",
                    "ticketId": "",
                    "ticketName": "",
                    "depositAmount": 0,
                    "validBetAmount": 0,
                    "dayNo": 18,
                    "id": "",
                    "configId": "",
                    "promotionId": ""
                },
                {
                    "amount": "0",
                    "pointAmount": "0",
                    "ticketType": "",
                    "ticketId": "",
                    "ticketName": "",
                    "depositAmount": 0,
                    "validBetAmount": 0,
                    "dayNo": 19,
                    "id": "",
                    "configId": "",
                    "promotionId": ""
                },
                {
                    "amount": "0",
                    "pointAmount": "0",
                    "ticketType": "",
                    "ticketId": "",
                    "ticketName": "",
                    "depositAmount": 0,
                    "validBetAmount": 0,
                    "dayNo": 20,
                    "id": "",
                    "configId": "",
                    "promotionId": ""
                },
                {
                    "amount": "0",
                    "pointAmount": "0",
                    "ticketType": "",
                    "ticketId": "",
                    "ticketName": "",
                    "depositAmount": 0,
                    "validBetAmount": 0,
                    "dayNo": 21,
                    "id": "",
                    "configId": "",
                    "promotionId": ""
                },
                {
                    "amount": "0",
                    "pointAmount": "0",
                    "ticketType": "",
                    "ticketId": "",
                    "ticketName": "",
                    "depositAmount": 0,
                    "validBetAmount": 0,
                    "dayNo": 22,
                    "id": "",
                    "configId": "",
                    "promotionId": ""
                },
                {
                    "amount": "0",
                    "pointAmount": "0",
                    "ticketType": "",
                    "ticketId": "",
                    "ticketName": "",
                    "depositAmount": 0,
                    "validBetAmount": 0,
                    "dayNo": 23,
                    "id": "",
                    "configId": "",
                    "promotionId": ""
                },
                {
                    "amount": "0",
                    "pointAmount": "0",
                    "ticketType": "",
                    "ticketId": "",
                    "ticketName": "",
                    "depositAmount": 0,
                    "validBetAmount": 0,
                    "dayNo": 24,
                    "id": "",
                    "configId": "",
                    "promotionId": ""
                },
                {
                    "amount": "0",
                    "pointAmount": "0",
                    "ticketType": "",
                    "ticketId": "",
                    "ticketName": "",
                    "depositAmount": 0,
                    "validBetAmount": 0,
                    "dayNo": 25,
                    "id": "",
                    "configId": "",
                    "promotionId": ""
                },
                {
                    "amount": "0",
                    "pointAmount": "0",
                    "ticketType": "",
                    "ticketId": "",
                    "ticketName": "",
                    "depositAmount": 0,
                    "validBetAmount": 0,
                    "dayNo": 26,
                    "id": "",
                    "configId": "",
                    "promotionId": ""
                },
                {
                    "amount": "0",
                    "pointAmount": "0",
                    "ticketType": "",
                    "ticketId": "",
                    "ticketName": "",
                    "depositAmount": 0,
                    "validBetAmount": 0,
                    "dayNo": 27,
                    "id": "",
                    "configId": "",
                    "promotionId": ""
                },
                {
                    "amount": "0",
                    "pointAmount": "0",
                    "ticketType": "",
                    "ticketId": "",
                    "ticketName": "",
                    "depositAmount": 0,
                    "validBetAmount": 0,
                    "dayNo": 28,
                    "id": "",
                    "configId": "",
                    "promotionId": ""
                }
            ],
            "forAllLabel": "Y",
            "currentPage": 1,
            "id": ""
        }
    ],
    "registerDateType": "R",
    "daysAfterCount": 0,
    "promotionType": "LOGIN",
    "walletType": 2,
    "txType": 6131,
    "excludeRebate": "N",
    "minimumClaimAmount": 0,
    "maximumClaimAmount": 0,
    "participant": "ALL",
    "agentNames": "",
    "operationLabels": [],
    "forDeletionList": [],
    "fileDetailList": [],
    "totalContactNumbers": 0,
    "productType": "ALL",
    "forAllLabel": "Y",
    "linkedAnnouncementList": [],
    "promotionMessage": {
        "id": "",
        "contentInbox": [],
        "contentPushNotif": [],
        "defaultLanguageInbox": "",
        "defaultLanguagePushNotif": "",
        "promotionId": ""
    },
    "languageInbox": "",
    "languagePushNotif": "",
    "activeKeyInbox": "",
    "activeKeyPushNotif": "",
    "allowMessage": "N",
    "allowPushNotif": "N",
    "contactNumberRequired": "N",
    "telegramRequired": "N",
    "viberRequired": "N",
    "appleIdRequired": "N",
    "idRequired": "N",
    "birthdayRequired": "N",
    "kycRequired": "N",
    "twitterRequired": "N",
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
    "mobileVerified": "",
    "ticketClaimMethod": "MANUAL",
    "playerRemark": "月签到 111",
    "budgetStr": "999888",
    "pointBudgetStr": "999888",
    "claimMethod": "MANUAL",
    "maxClaimCountType": "DAILY",
    "startTimeString": start_str,
    "endTimeString": end_str,
    "registerStartDate": start_str,
    "registerEndDate": end_str,
    "createdBy": "carrine01",
    "createdAt": None,
    "updatedBy": None,
    "updatedAt": None,
    "minimumRequiredTurnover": None,
    "pointBudget": 999888,
    "claimedAmount": None,
    "maxClaimCount": None,
    "claimedCount": None,
    "customerClaimedCount": None,
    "genNoExpiry": None,
    "remark": None,
    "bonusAmount": None,
    "effectiveTime": None,
    "excludeValidBet": None,
    "uniqueIp": "N",
    "operationLabelIds": None,
    "linkedAnnouncementStr": None,
    "agents": None,
    "contactNumFileName": None,
    "rankGroupId": None,
    "groupName": None,
    "registerStartDateString": start_Time,
    "registerEndDateString": endTime,
    "agentType": None,
    "mobileNumMatchType": "PRECISE",
    "contactFileIds": []
        }
        response=requests.post(URL,json=payload,headers=header,verify=False)
        response_json=response.json()
        if response_json.get('success'):
            logging.info("創建月遷到成功")
        else:
            print(response_json)
            logging.error("創建月簽到失敗")
    def Sign_in_task_choice(self,ticket,merchantCode, refer=24781):
        start_Time, endTime, start_str, end_str = self.unitTime()
        URL="http://sit-admin2.tcg.com/tac/api/relay/post/mcs-internal-v3-mcsLoginPromotion-createLoginPromotionWithDetails"
        header=self.header(merchantCode,refer)
        payload={
            "id": "",
        "promotionId": "",
        "merchantCode": merchantCode,
        "name": "111",
        "promotionName": "",
        "description": "<p>11</p>\n",
        "budget": "999888",
        "type": "C",
        "startTime": start_Time,
        "endTime": endTime,
        "requiredTurnover": 0,
        "status": "A",
        "sorting": 0,
        "noExpiry": "Y",
        "allowCycle": "Y",
        "allowSkip": "Y",
        "triggerCondition": "",
        "triggerLogin": "Y",
        "triggerDeposit": "N",
        "triggerValidBet": "N",
        "loginPromotionConfigs": [
            {
                "configId": "",
                "promotionId": "",
                "merchantCode": merchantCode,
                "promotionName": "test0417",
                "description": "",
                "playerRanks": [],
                "loginPromotionConfigDetails": [
                    {
                        "amount": 1,
                        "pointAmount": 1,
                        "ticketType": "CASH_VOUCHER",
                        "ticketId": ticket,
                        "ticketName": "",
                        "depositAmount": 0,
                        "validBetAmount": 0,
                        "dayNo": 1,
                        "id": "",
                        "configId": "",
                        "promotionId": ""
                    }
                ],
                "forAllLabel": "Y",
                "currentPage": 1,
                "id": ""
            }
        ],
        "registerDateType": "R",
        "daysAfterCount": 0,
        "promotionType": "LOGIN",
        "walletType": 2,
        "txType": 6131,
        "excludeRebate": "N",
        "minimumClaimAmount": 0,
        "maximumClaimAmount": 0,
        "participant": "ALL",
        "agentNames": "",
        "operationLabels": [],
        "forDeletionList": [],
        "fileDetailList": [],
        "totalContactNumbers": 0,
        "productType": "ALL",
        "forAllLabel": "Y",
        "linkedAnnouncementList": [],
        "promotionMessage": {
            "id": "",
            "contentInbox": [],
            "contentPushNotif": [],
            "defaultLanguageInbox": "",
            "defaultLanguagePushNotif": "",
            "promotionId": ""
        },
        "languageInbox": "",
        "languagePushNotif": "",
        "activeKeyInbox": "",
        "activeKeyPushNotif": "",
        "allowMessage": "N",
        "allowPushNotif": "N",
        "contactNumberRequired": "N",
        "telegramRequired": "N",
        "viberRequired": "N",
        "appleIdRequired": "N",
        "idRequired": "N",
        "birthdayRequired": "N",
        "kycRequired": "N",
        "twitterRequired": "N",
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
        "mobileVerified": "",
        "ticketClaimMethod": "MANUAL",
        "playerRemark": "自定义签到 111",
        "budgetStr": "999888",
        "pointBudgetStr": "999888",
        "claimMethod": "MANUAL",
        "maxClaimCountType": "DAILY",
        "startTimeString": start_str,
        "endTimeString": end_str,
        "registerStartDate": start_str,
        "registerEndDate": end_str,
        "createdBy": "carrine01",
        "createdAt": None,
        "updatedBy": None,
        "updatedAt": None,
        "minimumRequiredTurnover": None,
        "pointBudget": 999888,
        "claimedAmount": None,
        "maxClaimCount": None,
        "claimedCount": None,
        "customerClaimedCount": None,
        "genNoExpiry": None,
        "remark": None,
        "bonusAmount": None,
        "effectiveTime": None,
        "excludeValidBet": None,
        "uniqueIp": "N",
        "operationLabelIds": None,
        "linkedAnnouncementStr": None,
        "agents": None,
        "contactNumFileName": None,
        "rankGroupId": None,
        "groupName": None,
        "registerStartDateString": start_Time,
        "registerEndDateString": endTime,
        "agentType": None,
        "mobileNumMatchType": "PRECISE",
        "contactFileIds": []
            }
        response=requests.post(URL,json=payload,headers=header,verify=False)
        response_json=response.json()
        if response_json.get('success'):
            logging.info("創建自定義遷到成功")
        else:
            print(response_json)
            logging.error("創建自定義簽到失敗")
            
    def Extra_Reward(self,merchantCode,refer=24800):
        URL="http://sit-admin2.tcg.com/tac/api/relay/post/promo-promotion-extra-reward"
        start_Time, endTime, start_str, end_str = self.unitTime()
        new_start_time = datetime.now() + timedelta(minutes=3)
        new_start_ts = int(new_start_time.timestamp() * 1000)
        header=self.header(merchantCode,refer)
        
        payload={
            "name": "test",
            "startTime": new_start_ts,
            "endTime": endTime,
            "playerRemark": "c",
            "internalRemark": "",
            "hourValidity": 0,
            "minuteValidity": 30,
            "rewardType": "BONUS",
            "multiplierMode": "FIXED",
            "configReqs": [
                {
                    "requireMinRewardAmount": None,
                    "requireMaxRewardAmount": None,
                    "requireMinDepositAmount": 200,
                    "requireMaxDepositAmount": 200,
                    "rewardMultiplier": 5
                }
            ],
            "turnoverMultiplier": 5,
            "excludeRebate": "N"
        }
        response=requests.post(URL,json=payload,headers=header,verify=False)
        response_json=response.json()
        if response_json.get('success'):
            logging.info("創建翻倍獎勵成功")
        else:
            logging.error(response_json)
            logging.error("創建翻倍獎勵失敗")
        
def create_promotion(prom_type:int,merchantCode):
    #789tatlbf5 #7kkkf2 #789mxnf2 #grandfinf2 #gtppf3 #gvs5rvd #holly01
    credential_be = {
            "operatorName": "carrine03",
            "password": "Test@1234",
            "merchantCode": merchantCode 
    }
    try:
        backend=Backend(credential_be)
        if backend.token:
            logging.info("backend class有成功運作")
            deposit_list=['DEPOSIT','FIRST_DEPOSIT','SECOND_DEPOSIT','THIRD_DEPOSIT','FOURTH_DEPOSIT','FIFTH_DEPOSIT','DEPOSIT_BET_BONUS','DEPOSIT_COUNT']
            ticket_list=[1383014] #1315019 #1315022 #1313017 #1320014 #1320015
            
            match prom_type:
                case 1:
                    for promo_type in deposit_list:
                        for ticket in ticket_list:
                            backend.create_fisrt_deposit_promotion(promo_type,ticket,merchantCode)
                    
                case 2:
                    backend.create_Raffle(ticket_list[0],merchantCode,refer=24780)
                case 3:
                    backend.create_lucky_bet(ticket_list[0],merchantCode,refer=24780)
                case 4:
                    backend.create_new_register_Promotion(ticket_list[0],merchantCode,refer=24780)
                case 5:
                    backend.create_Register(ticket_list[0],merchantCode,refer=24780)
                case 6:
                    backend.create_app_download(ticket_list[0],merchantCode,refer=24780)
                case 7:
                    backend.register_mission(ticket_list[0],merchantCode,refer=24780)
                case 8:
                    backend.rescue_promotion(ticket_list[0],merchantCode,refer=24783)
                case 9:
                    code=backend.gen_code(merchantCode,refer=24784)
                    backend.PromoCode(ticket_list[0],merchantCode,code,refer=24784)
                case 10:
                    backend.mission(ticket_list[0],merchantCode,refer=24783)
                case 11:
                    backend.Manual_bonus(ticket_list[0],merchantCode,refer=24785)
                case 12:
                    label=backend.search_exist_announcment(merchantCode,refer=27000)
                    
                    if not label:
                        isSuccess=backend.create_announcement(merchantCode,refer=27000)
                        if not isSuccess:
                            logging.info("建立公告失敗")
                            raise RuntimeError("create_announcement failed")
                        label=backend.search_exist_announcment(merchantCode,refer=27000)
                    title,content=backend.search_Title_content(merchantCode,label,refer=27000)
                    
                    backend.Manual_Sign_up(ticket_list[0], merchantCode, label, title, content, refer=24785)
                    
                case 13:
                    
                    backend.UPGRADE_BONUS(ticket_list[0],merchantCode,refer=20346)
                    
                    group_ID=backend.get_group_ID(merchantCode,refer=250001)
                    if not group_ID:
                        backend.Establish_rank(merchantCode,refer=250001)
                        group_ID=backend.get_group_ID(merchantCode,refer=250001)
                        labelId=backend.get_current_label(merchantCode,group_ID,refer=250001)
                    labelId=backend.get_current_label(merchantCode,group_ID,refer=250001)
                case 14:
                    backend.Sign_in_task_choice(ticket_list[0],merchantCode,refer=24781)
                case 15:
                    backend.VIP_BONUS(ticket_list[0],merchantCode,labelId,refer=20324)
                    
                    #backend.Invite_Bonus(ticket_list[0],merchantCode,refer=240001
                case 16:
                    backend.login_task(ticket_list[0],merchantCode,refer=24781)
                case 17:
                    backend.Sign_in_task_week(ticket_list[0],merchantCode,refer=24781)
                case 18:    
                    backend.Sign_in_task_new(ticket_list[0],merchantCode,refer=24781)
                case 19:    
                    backend.Sign_in_task_month(ticket_list[0],merchantCode,refer=24781)
                case 20:
                    for promo_type in deposit_list:
                        for ticket in ticket_list:
                            backend.create_fisrt_deposit_promotion(promo_type,ticket,merchantCode)
                    
               
                    backend.create_Raffle(ticket_list[0],merchantCode,refer=24780)
                
                    backend.create_lucky_bet(ticket_list[0],merchantCode,refer=24780)
                
                    backend.create_new_register_Promotion(ticket_list[0],merchantCode,refer=24780)
                
                    backend.create_Register(ticket_list[0],merchantCode,refer=24780)
                
                    backend.create_app_download(ticket_list[0],merchantCode,refer=24780)
                
                    backend.register_mission(ticket_list[0],merchantCode,refer=24780)
                
                    backend.rescue_promotion(ticket_list[0],merchantCode,refer=24783)
                
                    code=backend.gen_code(merchantCode,refer=24784)
                    backend.PromoCode(ticket_list[0],merchantCode,code,refer=24784)
                
                    backend.mission(ticket_list[0],merchantCode,refer=24783)
                
                    backend.Manual_bonus(ticket_list[0],merchantCode,refer=24785)
                
                    label=backend.search_exist_announcment(merchantCode,refer=27000)
                    
                    if not label:
                        isSuccess=backend.create_announcement(merchantCode,refer=27000)
                        if not isSuccess:
                            logging.info("建立公告失敗")
                            raise RuntimeError("create_announcement failed")
                        label=backend.search_exist_announcment(merchantCode,refer=27000)
                    title,content=backend.search_Title_content(merchantCode,label,refer=27000)
                    
                    backend.Manual_Sign_up(ticket_list[0], merchantCode, label, title, content, refer=24785)
                    
              
                    
                    backend.UPGRADE_BONUS(ticket_list[0],merchantCode,refer=20346)
                    
                    group_ID=backend.get_group_ID(merchantCode,refer=250001)
                    if not group_ID:
                        backend.Establish_rank(merchantCode,refer=250001)
                        group_ID=backend.get_group_ID(merchantCode,refer=250001)
                        labelId=backend.get_current_label(merchantCode,group_ID,refer=250001)
                    labelId=backend.get_current_label(merchantCode,group_ID,refer=250001)
                
                    backend.create_Raffle(ticket_list[0],merchantCode,refer=24780)
               
                    backend.VIP_BONUS(ticket_list[0],merchantCode,labelId,refer=20324)
                    
                    #backend.Invite_Bonus(ticket_list[0],merchantCode,refer=240001
                
                    backend.login_task(ticket_list[0],merchantCode,refer=24781)
                
                    backend.Sign_in_task_week(ticket_list[0],merchantCode,refer=24781)
                   
                    backend.Sign_in_task_new(ticket_list[0],merchantCode,refer=24781)
                  
                    backend.Sign_in_task_month(ticket_list[0],merchantCode,refer=24781)
                
                    backend.Sign_in_task_choice(ticket_list[0],merchantCode,refer=24781)
                case 21:
                    backend.Extra_Reward(merchantCode,refer=24800)
            
        else:
            logging.error("沒有拿到後台token:")        
            #backend.Bonus_record_page()  --之後再修改 
  
    except Exception as e:
            logging.error(f"啟動時發生錯誤: {e}")#

    