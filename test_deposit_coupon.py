import Manual_create_single_with_confirm 
from deposit_api import batch_approve
import FRONTEND_DEPOSIT 
import Search_Report
import logging
import get_discount_ticket_detail

USERNAME='bnm888'
PROMOTIONID=4023101

'''沒有勾選並行充值送的票券'''
ticket_fixed=1480017 #滿1000折100
ticket_percentage=1481017 #滿1000折10%
ticket_percentageX=1467015 #折10%

'''有勾選並行充值送的票券'''
ticket_fixed_with_promo=1480018 #滿1000折100
ticket_percentage_with_promo=1467014 #滿1000折10%
ticket_percentageX_with_promo=1467015 #折10%

platform='gi8viet'
amount=1
deposit_amount=1000
promotion_id=4615099 #筆筆存 直接到帳

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def test_use_Fixed_coupon():
    deposit_amount = get_discount_ticket_detail.get_ticket_detail(ticket_fixed)
    Manual_create_single_with_confirm.main(USERNAME,PROMOTIONID,ticket_fixed,platform,amount)
    Search_Report.main(USERNAME, platform)
    FRONTEND_DEPOSIT.main([USERNAME], deposit_amount, type=3, ticket_id=ticket_fixed, discountAmount=100, promotion_id=None, depositAmount=None)
    batch_approve(platform)
    claim, status = Search_Report.main(USERNAME, platform)
    assert claim is not None and status == "USED", "折抵券狀態正確"
    
def test_use_percentage_coupon():
    deposit_amount = get_discount_ticket_detail.get_ticket_detail(ticket_fixed)
    Manual_create_single_with_confirm.main(USERNAME,PROMOTIONID,ticket_percentage,platform,amount)
    Search_Report.main(USERNAME, platform)
    FRONTEND_DEPOSIT.main([USERNAME], deposit_amount, type=3, ticket_id=ticket_percentage, discountAmount=100, promotion_id=None, depositAmount=None)
    batch_approve(platform)
    claim, status = Search_Report.main(USERNAME, platform)
    assert claim is not None and status == "USED", "折抵券狀態正確"

def test_use_percentageX_coupon():
    deposit_amount = get_discount_ticket_detail.get_ticket_detail(ticket_fixed)
    Manual_create_single_with_confirm.main(USERNAME,PROMOTIONID,ticket_percentageX,platform,amount)
    Search_Report.main(USERNAME, platform)
    FRONTEND_DEPOSIT.main([USERNAME], deposit_amount, type=3, ticket_id=ticket_percentageX, discountAmount=100, promotion_id=None, depositAmount=None)
    batch_approve(platform)
    claim, status = Search_Report.main(USERNAME, platform)
    assert claim is not None and status == "USED", "折抵券狀態正確"
    
'''測試充值送並行'''
def test_use_Fixed_coupon_with_deposit_Promotion():
    depositAmount = get_discount_ticket_detail.get_ticket_detail(ticket_fixed)
    result, promoType =Manual_create_single_with_confirm.main(USERNAME, PROMOTIONID, ticket_fixed_with_promo, platform, amount)
    if result:
        logging.info(f"成功派發紅利，活動類型為 {promoType}")
    claim, status = Search_Report.main(USERNAME, platform)
    assert claim is not None and status == "AVAILABLE", "折抵券狀態正確"
    
    succes_count = FRONTEND_DEPOSIT.main([USERNAME], deposit_amount, type=3, ticket_id=ticket_fixed_with_promo, discountAmount=100, promotion_id=promotion_id, depositAmount=depositAmount)
    batch_approve(platform)
    claim, status = Search_Report.main(USERNAME, platform)
    assert succes_count > 0 and status == "USED", "折抵券狀態正確"
    
def test_use_Fixed_coupon_with_deposit_Promotion_notAllowed():
    depositAmount = get_discount_ticket_detail.get_ticket_detail(ticket_fixed_with_promo)
    result, promoType =Manual_create_single_with_confirm.main(USERNAME,PROMOTIONID,ticket_fixed_with_promo,platform,amount)
    if result:
        logging.info(f"成功派發紅利，活動類型為 {promoType}")
    Search_Report.main(USERNAME, platform)
    succes_count = FRONTEND_DEPOSIT.main([USERNAME], deposit_amount, type=3, ticket_id=ticket_fixed, discountAmount=100, promotion_id=promotion_id, depositAmount=depositAmount)
    claim, status = Search_Report.main(USERNAME, platform)
    assert succes_count==0, "充值送活動未勾選，前端充值應該要失敗（success_count 應為 0）"
    assert claim is not None and status == "AVAILABLE", "折抵券狀態為未使用"
    
def test_use_percentage_coupon_with_deposit_Promotion():
    depositAmount = get_discount_ticket_detail.get_ticket_detail(ticket_percentage_with_promo)
    result, promoType =Manual_create_single_with_confirm.main(USERNAME, PROMOTIONID, ticket_percentage_with_promo, platform, amount)
    if result:
        logging.info(f"成功派發紅利，活動類型為 {promoType}")
    claim, status = Search_Report.main(USERNAME, platform)
    assert claim is not None and status == "AVAILABLE", "折抵券狀態正確"
    
    succes_count = FRONTEND_DEPOSIT.main([USERNAME], deposit_amount, type=3, ticket_id=ticket_percentage_with_promo, discountAmount=100, promotion_id=promotion_id, depositAmount=depositAmount)
    batch_approve(platform)
    claim, status = Search_Report.main(USERNAME, platform)
    assert succes_count > 0 and status == "USED", "折抵券狀態正確"
    
def test_use_percentage_coupon_with_deposit_Promotion_notAllowed():
    depositAmount = get_discount_ticket_detail.get_ticket_detail(ticket_percentage_with_promo)
    result, promoType =Manual_create_single_with_confirm.main(USERNAME,PROMOTIONID,ticket_percentage_with_promo,platform,amount)
    if result:
        logging.info(f"成功派發紅利，活動類型為 {promoType}")
    Search_Report.main(USERNAME, platform)
    succes_count = FRONTEND_DEPOSIT.main([USERNAME], deposit_amount, type=3, ticket_id=ticket_fixed, discountAmount=100, promotion_id=promotion_id, depositAmount=depositAmount)
    claim, status = Search_Report.main(USERNAME, platform)
    assert succes_count==0, "充值送活動未勾選，前端充值應該要失敗（success_count 應為 0）"
    assert claim is not None and status == "AVAILABLE", "折抵券狀態為未使用"
   
def test_use_percentagX_coupon_with_deposit_Promotion():
    depositAmount = get_discount_ticket_detail.get_ticket_detail(ticket_percentageX_with_promo)
    result, promoType =Manual_create_single_with_confirm.main(USERNAME, PROMOTIONID, ticket_percentageX_with_promo, platform, amount)
    if result:
        logging.info(f"成功派發紅利，活動類型為 {promoType}")
    claim, status = Search_Report.main(USERNAME, platform)
    assert claim is not None and status == "AVAILABLE", "折抵券狀態正確"
    
    succes_count = FRONTEND_DEPOSIT.main([USERNAME], deposit_amount, type=3, ticket_id=ticket_percentageX_with_promo, discountAmount=100, promotion_id=promotion_id, depositAmount=depositAmount)
    batch_approve(platform)
    claim, status = Search_Report.main(USERNAME, platform)
    assert succes_count > 0 and status == "USED", "折抵券狀態正確"
    
def test_use_percentageX_coupon_with_deposit_Promotion_notAllowed():
    depositAmount = get_discount_ticket_detail.get_ticket_detail(ticket_percentageX_with_promo)
    result, promoType =Manual_create_single_with_confirm.main(USERNAME,PROMOTIONID,ticket_percentageX_with_promo,platform,amount)
    if result:
        logging.info(f"成功派發紅利，活動類型為 {promoType}")
    Search_Report.main(USERNAME, platform)
    succes_count = FRONTEND_DEPOSIT.main([USERNAME], deposit_amount, type=3, ticket_id=ticket_fixed, discountAmount=100, promotion_id=promotion_id, depositAmount=depositAmount)
    claim, status = Search_Report.main(USERNAME, platform)
    assert succes_count==0, "充值送活動未勾選，前端充值應該要失敗（success_count 應為 0）"
    assert claim is not None and status == "AVAILABLE", "折抵券狀態為未使用" 
    
'''測試充值送並行＆快捷充值送'''

