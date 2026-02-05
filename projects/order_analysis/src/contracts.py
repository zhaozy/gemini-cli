import pandera as pa
from pandera.typing import Series
from datetime import datetime

class TransactionSchema(pa.DataFrameModel):
    """
    Schema for the raw transaction data after initial cleaning (column renaming).
    """
    date: Series[datetime] = pa.Field(alias="日期")
    store_id: Series[str] = pa.Field(alias="门店编码", coerce=True)
    order_id: Series[str] = pa.Field(alias="流水单号", coerce=True)
    sku_id: Series[str] = pa.Field(alias="商品编码", coerce=True)
    sku_name: Series[str] = pa.Field(alias="商品名称")
    
    quantity: Series[float] = pa.Field(alias="销售数量")
    list_gmv: Series[float] = pa.Field(alias="销售金额") # Original Sales Amount (Price * Qty)
    discount: Series[float] = pa.Field(alias="折扣金额")
    
    # Calculated/Derived fields should be handled in transformation, 
    # but we validate them if they exist in the raw dataframe passed to validation
    
    class Config:
        strict = False # Allow extra columns
