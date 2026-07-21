import Manual_create_single_with_confirm 
from deposit_api import batch_approve
import FRONTEND_DEPOSIT 
import Search_Report

USERNAME='bnm985'
PROMOTIONID=4023101
ticket_fixed=1478017 #滿1000折100
ticket_percentage=1467014 #滿1000折10%
ticket_percentageX=1467015 #折10%
platform='gi8viet'
amount=1
deposit_amount=1000

def test_use_Fixed_coupon():
    Manual_create_single_with_confirm.main(USERNAME,PROMOTIONID,ticket_fixed,platform,amount)
    Search_Report.main(USERNAME, platform)
    FRONTEND_DEPOSIT.main([USERNAME], deposit_amount, type=3, ticket_id=ticket_fixed, discountAmount=100)
    batch_approve(platform)
    claim, status = Search_Report.main(USERNAME, platform)
    assert claim is not None and status == "USED", "折抵券狀態正確"
    
def test_use_percentage_coupon():
    Manual_create_single_with_confirm.main(USERNAME,PROMOTIONID,ticket_percentage,platform,amount)
    Search_Report.main(USERNAME, platform)
    FRONTEND_DEPOSIT.main([USERNAME], deposit_amount, type=3, ticket_id=ticket_percentage, discountAmount=100)
    batch_approve(platform)
    claim, status = Search_Report.main(USERNAME, platform)
    assert claim is not None and status == "USED", "折抵券狀態正確"

def test_use_percentageX_coupon():
    Manual_create_single_with_confirm.main(USERNAME,PROMOTIONID,ticket_percentageX,platform,amount)
    Search_Report.main(USERNAME, platform)
    FRONTEND_DEPOSIT.main([USERNAME], deposit_amount, type=3, ticket_id=ticket_percentageX, discountAmount=100)
    batch_approve(platform)
    claim, status = Search_Report.main(USERNAME, platform)
    assert claim is not None and status == "USED", "折抵券狀態正確"
    
    