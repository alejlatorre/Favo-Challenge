# %% Libraries
import time
import warnings
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from mlxtend.frequent_patterns import (
    apriori,
    association_rules
)

# %% Settings
warnings.filterwarnings('ignore')

option_settings = {
    'display.max_columns': None,
    'display.max_rows': False,
    'display.float_format': '{:,.4f}'.format
}
[pd.set_option(setting, option) for setting, option in option_settings.items()]

IN_PATH = 'data/in/'
OUT_PATH = 'data/out/'

# %% Import data
dtypes_dict = {
    'store_id': 'str',
    'buyer_id': 'str',
    'sku': 'str',
    'order_number': 'str',
    'region_id': 'str'
}
filename = 'Estudio de caso - Base de ventas.xlsx'
data_ = pd.read_excel(IN_PATH + filename, engine='openpyxl', dtype=dtypes_dict)

# %% Processing
data = data_.copy()

cols_to_drop = {
    'leader_status',
    'offer'
}
data.drop(columns=cols_to_drop, inplace=True)

# %% Algorithm
basket_per_order_2 = data[data['region_id'] == '2'].groupby(['order_number', 'sku'])['order_number'].nunique().unstack().reset_index().fillna(0).set_index('order_number')
frequent_itemsets_2 = apriori(basket_per_order_2, min_support=0.01, use_colnames=True)
rules_2 = association_rules(frequent_itemsets_2, metric='lift', min_threshold=1)
rules_2.sort_values(by=['antecedent support', 'lift'], ascending=False, inplace=True)
rules_2['qty_antecedents'] = rules_2['antecedents'].apply(lambda x: len(x))
rules_2['rn'] = rules_2.groupby(['antecedents'])['qty_antecedents'].rank(method='first')
filt_rules_2 = rules_2.loc[rules['rn'] <= 3,:].copy()

basket_per_order_6 = data[data['region_id'] == '6'].groupby(['order_number', 'sku'])['order_number'].nunique().unstack().reset_index().fillna(0).set_index('order_number')
frequent_itemsets_6 = apriori(basket_per_order_6, min_support=0.01, use_colnames=True)
rules_6 = association_rules(frequent_itemsets_6, metric='lift', min_threshold=1)
rules_6.sort_values(by=['antecedent support', 'lift'], ascending=False, inplace=True)
rules_6['qty_antecedents'] = rules_6['antecedents'].apply(lambda x: len(x))
rules_6['rn'] = rules_6.groupby(['antecedents'])['qty_antecedents'].rank(method='first')
filt_rules_6 = rules_6.loc[rules['rn'] <= 3,:].copy()

# %% Export
filename = 'association_rules_R2.xlsx'
filt_rules_2.to_excel(OUT_PATH + filename, index=False, engine='openpyxl')
filename = 'association_rules_R6.xlsx'
filt_rules_6.to_excel(OUT_PATH + filename, index=False, engine='openpyxl')

# %%
