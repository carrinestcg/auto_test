import requests
import logging
import random
from Customer_id import main

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def appDowload(CustomerId:str,CustomerName,Merchant,CustomerIP,uuid):
    URL="http://10.81.1.19:7001/tcg-mcs-fe/appDownloadPromotion/claimAppDownloadPromotion"

    header={
        "CustomerId":str(CustomerId),
        "CustomerName":CustomerName,
        "Merchant":Merchant,
        "CustomerIP":CustomerIP,
        "Language":"CN"
    }
    payload={ 
        "uuid": uuid 
        }
    print(CustomerId,CustomerName,Merchant,CustomerIP,uuid)
    resposne=requests.post(URL,headers=header,json=payload,verify=False)
    resposne_json=resposne.json()
    if resposne_json.get("success"):
        logging.info("app下載獎勵觸發完成")
        return True
    else:
        logging.error(f"觸發失敗{resposne.text}")
        return False

def app_download_main(Merchant,CustomerName):
    
    if Merchant=="gi8viet":
        
        CustomerId=(main(CustomerName, Merchant, 1))
        CustomerIP=".".join(str(random.randint(0,255)) for _ in range(4))
        uuid=random.randint(100000000, 999999999)
        
        isSuccess=appDowload(CustomerId,CustomerName,Merchant,CustomerIP,uuid)
        if isSuccess:
            return True
        else:
            return False
    elif Merchant=="huamei":
        
        CustomerId=(main(CustomerName, Merchant, 1))
        
        CustomerIP=".".join(str(random.randint(0,255)) for _ in range(4))
        uuid=random.randint(100000000, 999999999)
        
        isSuccess=appDowload(CustomerId,CustomerName,Merchant,CustomerIP,uuid)
        if isSuccess:
            return True
        else:
            return False
    elif Merchant=="tcgdemov3":
        
        CustomerId=(main(CustomerName, Merchant, 1))
        CustomerIP=".".join(str(random.randint(0,255)) for _ in range(4))
        uuid=random.randint(100000000, 999999999)
    
        isSuccess=appDowload(CustomerId,CustomerName,Merchant,CustomerIP,uuid)
        if isSuccess:
            return True
        else:
            return False
    elif Merchant=="lodibet":
        Merchant="lodibet"
        
        CustomerId=(main(CustomerName, Merchant, 1))
        
        CustomerIP=".".join(str(random.randint(0,255)) for _ in range(4))
        uuid=random.randint(100000000, 999999999)
    
        isSuccess=appDowload(CustomerId,CustomerName,Merchant,CustomerIP,uuid)
        if isSuccess:
            return True
        else:
            return False

