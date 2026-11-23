from app.modules.handover.models import InventoryBalance

def test_available_stock_formula():
    balance=InventoryBalance(owner_id='retailer-a',sku_code='SKU',warehouse_id='WH',on_hand=100,reserved=25,unavailable=10)
    assert balance.on_hand - balance.reserved - balance.unavailable == 65
