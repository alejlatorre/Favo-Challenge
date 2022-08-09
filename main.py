# %% 0. Libraries
import dtale
import warnings
import numpy as np
import pandas as pd 
import seaborn as sns
import matplotlib.pyplot as plt 

# %% 1. Settings
warnings.filterwarnings('ignore')

option_settings = {
    'display.max_rows': False,
    'display.max_columns': None,
    'display.float_format': '{:,.4f}'.format
}
[pd.set_option(setting, option) for setting, option in option_settings.items()]

IN_PATH = 'data/in/'
OUT_PATH = 'data/out/'

# %% 2. Load data
filename = 'Estudio de caso - Base de ventas.xlsx'
data = pd.read_excel(IN_PATH + filename, engine='openpyxl')

# %% 3. Exploratory data analysis
d = dtale.show(data)
dtale.instances()

## Feature description
# 1. store_id: Id from store
# 2. store_first_day: First day of store
# 3. leader_status: Is constant
# 4. buyer_id: Customer ID
# 5. sku: SKU code
# 6. order_number: Order ID
# 7. payment_type: Payment method
# 8. purchase_completed: 95.9% yes, 4.1% no (is the opposite of canceled)
# 9. canceled: 95.9% no, 4.1% yes (is the opposite of purchase_completed)
# 10. offer: Unknown
# 11. full_price: Unit price per SKU
# 12. discounted_price: Unit price discount per SKU
# 13. discount: Discount applied per SKU
# 14. quantity: Quantity of SKUs bought
# 15. order_quantity: Sum of quantity
# 16. order_subtotal: sum of discounted_price
# 17. coupon_discount: Coupon discount applied per SKU
# 18. total_full_price: full_price times quantity
# 19. total_discounted_price: discounted_price times quantity
# 20. region_id: Region ID
# 21. created_date: Order date
# 22. payment_confirmed_at: Payment confirmation timestamp
# 23. effective_date_time: Registered timestamp
# 24. brand: Brand
# 25. category: Category
# 26. subcategory: Subcategory 

# %% 4. Processing
cols_to_drop = {
    'leader_status'
}
data.drop(columns=cols_to_drop, inplace=True)


data['antiquity'] =

## Descripción

pd.pivot_table(
    data=data,
    index='order_number'
)