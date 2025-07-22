import requests,logging,datetime
from datetime import datetime,timedelta
import time,random,yaml,os
from openpyxl import Workbook
from get_header import get_common_header
import yaml,os,itertools
from itertools import cycle
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
class B_end:
    def __init__(self,credential:dict):
        self.session=requests.Session()
        self.username=''
        self.password=''
        self.token=self.get_token(credential['operatorName'],credential['password'])
        self.credential=credential
        self.token_data=self.token
        self.record_data_list=''
    def get_token(self,operatorName,password):
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
    
    '''=====註冊任務====='''
    def REGISTER_TASK(self,ticket:int,ticket_type:str):
        start_time = datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)
        unix_starttime=int(start_time.timestamp()*1000)
        end_time = datetime.now().replace(hour=23,minute=59,second=59,microsecond=0)
        unix_starttime=int(end_time.timestamp()*1000)
        API_URL3=f"http://sit-admin2.tcg.com/tac/api/relay/post/promo-promotion-register-task-create"
        
        headers=get_common_header(self.token_data,referer=24780)
        cookies = {
            "language": "zh_CN"
        }
        payload={
                "promoId": 0,
                "promoName": "test_auto_new",
                "status": "A",
                "noExpiry": "Y",
                "startTime": unix_starttime,
                "endTime": unix_starttime,
                "remark": "test",
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
                        "ticketQuantity": 1,
                        "ticketTurnoverMultiple": None,
                        "ticketType": ticket_type,
                        "ticketTurnoverMultiplier": 0
                    }
                ],
                "message": {
                    "inbox": {
                        "active": "Y",
                        "defaultLanguage": "CN",
                        "messageList": [
                            {
                                "content": "<p>auto_create</p>\n",
                                "language": "CN",
                                "title": "auto_create"
                            }
                        ]
                    },
                    "notification": {
                        "active": "N"
                    }
                },
                "productType": "ALL",
                "promoType": "REGISTER_TASK"
            }
        try:
            response=requests.post(API_URL3, cookies=cookies,json=payload,headers=headers, verify=False)
            response.raise_for_status()

            response_data=response.json()
            print(response_data)
            if response_data.get("success") == True:
                return True  
            else:

                return False
        
        except Exception as e:
            logging.error(f"api錯誤{e}")

    '''=====新手任務====='''
    def new_register_misssion(self,ticket:int,ticket_type:str):
        start_time = datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)
        unix_starttime=int(start_time.timestamp()*1000)
        end_time = datetime.now().replace(hour=23,minute=59,second=59,microsecond=0)
        unix_starttime=int(end_time.timestamp()*1000)
        API_URL3=f"http://sit-admin2.tcg.com/tac/api/relay/post/mcs-internal-v3-registerPromotion-add"
        
        headers=get_common_header(self.token_data,referer=24781)
        cookies = {
            "language": "zh_CN"
        }
        payload={
            "id": "",
            "promotionId": "",
            "merchantCode": "gi8viet",
            "name": "carrine test",
            "budget": "999888",
            "description": "cccc",
            "startTime": unix_starttime,
            "endTime": unix_starttime,
            "startMemberRegTime": unix_starttime,
            "endMemberRegTime": unix_starttime,
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
            "claimMethod": "AUTO",
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
                        "content": "<p>新手任务奖励站內信</p>",
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
                str(ticket): {
                    "promotionId": "",
                    "ticketBudget": 0,
                    "ticketId": ticket,
                    "ticketName": "",
                    "ticketType": ticket_type
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
                    "promotionId": "",
                    "configId": "",
                    "forAllLabel": "Y",
                    "bonusAmount": 10,
                    "pointAmount": 10,
                    "turnoverMultiplier": 5,
                    "minRequiredTurnover": 1,
                    "registerPromotionConfigLabels": [],
                    "ticketId": ticket,
                    "ticketType": ticket_type,
                    "ticketName": None
                }
            ],
            "startTimeString": "2025-07-01 00:00:00",
            "endTimeString": "2025-07-01 23:59:59",
            "startMemberRegTimeString": "2025-07-01 00:00:00",
            "endMemberRegTimeString": "2025-07-01 23:59:59"
        }

        try:
            response=requests.post(API_URL3, cookies=cookies,json=payload,headers=headers, verify=False)
            response.raise_for_status()

            response_data=response.json()
            if response_data.get("success") == True:
                value=response_data.get("value",{})
                id=value.get("id")
                logging.info(f"創建新手任務成功 活動id:{id}")
                return True  
            else:
                logging.error("創建新手任務失敗")
                return False
        
        except Exception as e:
            logging.error(f"api錯誤{e}")
    def get_promo_code(self):
        URL="http://sit-admin2.tcg.com/tac/api/relay/get/mcs-promotion-promoCode-genCode?merchantCode=gi8viet"
        headers=get_common_header(self.token_data,referer=24784)
        cookies={
            "Cookie":"language=zh_CN"
        }
        params={
            "merchantCode":"gi8viet"
        }
        response=requests.get(URL,headers=headers,cookies=cookies,params=params,verify=False)
        response_data=response.json()
        print(response_data)
        try:
            if response_data.get("success")==True:
                value=response_data.get("value")
                logging.info(f"建立一組優惠碼{value}")
                return value
            else:
                logging.error(f"建立優惠碼失敗")
                return None
        except Exception as e:
            logging.error(f"建立優惠碼失敗{e}")
    def create_promoCdoe_promotion(self,code,ticket,ticket_type):
        start_time = datetime.now().replace(hour=0,minute=0,second=0,microsecond=0)
        unix_starttime=int(start_time.timestamp()*1000)
        end_time = datetime.now().replace(hour=23,minute=59,second=59,microsecond=0)
        unix_starttime=int(end_time.timestamp()*1000)
        URL="http://sit-admin2.tcg.com/tac/api/relay/post/mcs-promotion-promoCode-create"
        headers=get_common_header(self.token_data,referer=24784)
        cookies={
                    "Cookie":"language=zh_CN"
                }
        payload={
            "merchantCode": "gi8viet",
            "name": "test",
            "productType": "ALL",
            "promoCodes": [
                {
                    "promoCodeGenerateType": "RANDOM",
                    "promoCode": code
                }
            ],
            "startTime": unix_starttime,
            "endTime": unix_starttime,
            "excludeRebate": "N",
            "remark": "test",
            "description": "test",
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
                    "mobileNumHasAuthenticate": False
                },
                "claimMethod": "MANUAL",
                "claimConditions": [
                    "CUSTOMER"
                ]
            },
            "config": {
                "bonusAmt": 10,
                "pointAmt": 5,
                "ticketName": ticket_type,
                "ticketId": ticket,
                "turnoverMultiplier": 5,
                "minimumTurnover": 1,
                "maxClaimCount": "10",
                "maxClaimCountDaily": " 5",
                "configId": 0,
                "promotionSettingId": 0,
                "ticketQuantity": 1
            },
            "announcements": [],
            "status": "A",
            "promotionSettingId": None
        }
        response=requests.post(URL,headers=headers,cookies=cookies,json=payload,verify=False)
        response_data=response.json()
        print(response_data)
        try:
            if response_data.get("success")==True:
                value=response_data.get("value")
                logging.info(f"建立一組優惠碼{value}")
                return value
            else:
                logging.error(f"建立優惠碼失敗")
                return None
        except Exception as e:
            logging.error(f"建立優惠碼失敗{e}")

    def process_procedure(self):
        
        ticket_dict={
            1087007:"CASH_VOUCHER",
            1087008:"RAFFLE",
            1087006:"GOLDEN_EGG",
            1113014:"PRIZE_WHEEL",
            1100020:"GIFT_CODE",
            1120016:"FREE_SPIN",
            1120017:"TEMU"
        }
        ticketQuantity=3
        #ticket=1105015
        
        for _ in range(2):
            for ticket,ticket_type in itertools.cycle(ticket_dict.items()):
                #is_successs=self.REGISTER_TASK(ticket,ticket_type)
                #is_success=self.new_register_misssion(ticket,ticket_type)
                code=self.get_promo_code()
                is_success=self.create_promoCdoe_promotion(code,ticket,ticket_type)
                if is_success:
                    logging.info("創建活動成功")
                else:
                    logging.info("創建活動失敗")
    
            
        
if __name__ == "__main__":
    credential = {
        "operatorName": "carrine03",
        "password": "Test@1234"
    }
    try:
        b_end=B_end(credential)
        if b_end.token:
            b_end.process_procedure()
    except Exception as e:
        print("啟動時取得 token 發生錯誤:", e)

    #填入玩家帳號
    
    
    

   