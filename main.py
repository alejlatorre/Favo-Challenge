# %% 0. Libraries
import dtale
import warnings
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from matplotlib.ticker import PercentFormatter

from src.utils import Plotly_Plots

# %% 1. Settings
warnings.filterwarnings('ignore')

option_settings = {
    'display.max_rows': False,
    'display.max_columns': None,
    'display.float_format': '{:,.4f}'.format
}
[pd.set_option(setting, option) for setting, option in option_settings.items()]

%matplotlib inline
plt.rcParams["figure.autolayout"] = True
sns.set_theme(style='darkgrid')

IN_PATH = 'data/in/'
OUT_PATH = 'data/out/'

# %% 2. Load data
dtypes_dict = {
    'store_id': 'str',
    'buyer_id': 'str',
    'sku': 'str',
    'order_number': 'str',
    'region_id': 'str'
}
filename = 'Estudio de caso - Base de ventas.xlsx'
data_ = pd.read_excel(IN_PATH + filename, engine='openpyxl', dtype=dtypes_dict)

# %% 3. Exploratory data analysis
d = dtale.show(data)
dtale.instances()

## Features description
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
data = data_.copy()

cols_to_drop = {
    'leader_status',
    'offer'
}
data.drop(columns=cols_to_drop, inplace=True)

# Granularidad nivel ordenes
data_orders = pd.pivot_table(
    data=data,
    index=['created_date', 'effective_date_time', 'order_number', 'region_id', 'store_id', 'buyer_id', 'payment_type', 'purchase_completed'],
    values=[
        'full_price', 'discount', 'discounted_price', 'quantity', 'coupon_discount', 
        'total_full_price', 'total_discounted_price'
    ],
    aggfunc={
        #'full_price': np.mean, # Full price promedio por producto => Calcular como sum(total_full_price) / sum(quantity)
        # 'discount_per_product': np.mean, # Descuento promedio por producto => Calcular como (sum(total_full_price) - sum(total_discounted_price)) / sum(quantity)
        # 'discounted_price': np.mean, # Discounted price promedio por producto => Calcular como sum(total_discounted_price) / sum(quantity) 
        'quantity': np.sum, # Total de unidades por pedido
        'discount': np.sum, # sum(discount) == distinct(coupon_discount) 
        'total_full_price': np.sum, # Venta full price de la orden
        'total_discounted_price': np.sum # Venta discounted price de la orden
    }
)
data_orders.reset_index(inplace=True)
rename_cols = {
    'order_number': 'order_id',
    'discount': 'total_discount'
}
data_orders.rename(columns=rename_cols, inplace=True)
data_orders['avg_full_price_per_product'] = data_orders['total_full_price'] / data_orders['quantity']
data_orders['avg_disc_price_per_product'] = data_orders['total_discounted_price'] / data_orders['quantity']
data_orders['avg_disc_per_product'] = data_orders['total_discount'] / data_orders['quantity']
to_map = {
    'Yes': 1,
    'No': 0
}
data_orders['purchase_completed'] = data_orders['purchase_completed'].map(to_map)
filename = 'data_orders.csv'
data_orders.to_csv(OUT_PATH + filename, sep=',', index=False)

# Granularidad nivel metodo de pago
payment_type_2 = pd.pivot_table(
    data=data_orders[data_orders['region_id'] == '2'],
    index='payment_type',
    values=['order_id', 'total_discounted_price'],
    aggfunc={
        'order_id': pd.Series.nunique,
        'total_discounted_price': np.sum
    }
)
payment_type_6 = pd.pivot_table(
    data=data_orders[data_orders['region_id'] == '6'],
    index='payment_type',
    values=['order_id', 'total_discounted_price'],
    aggfunc={
        'order_id': pd.Series.nunique,
        'total_discounted_price': np.sum
    }
)
payment_type_2.sort_values(by='total_discounted_price', ascending=False, inplace=True)
payment_type_6.sort_values(by='total_discounted_price', ascending=False, inplace=True)
payment_type_2['orders_cum_prc'] = payment_type_2['order_id'].cumsum() / payment_type_2['order_id'].sum() 
payment_type_6['orders_cum_prc'] = payment_type_6['order_id'].cumsum() / payment_type_6['order_id'].sum() 
payment_type_2['revenue_cum_prc'] = payment_type_2['total_discounted_price'].cumsum() / payment_type_2['total_discounted_price'].sum() 
payment_type_6['revenue_cum_prc'] = payment_type_6['total_discounted_price'].cumsum() / payment_type_6['total_discounted_price'].sum() 
payment_type_2.reset_index(inplace=True)
payment_type_6.reset_index(inplace=True)

# Series de tiempo nivel dia
base_ts_2 = pd.pivot_table(
    data=data_orders[data_orders['region_id']=='2'],
    index='created_date',
    values=[
        'order_id', 'buyer_id', 'purchase_completed', 'quantity', 
        'total_discounted_price', 'total_full_price', 'total_discount', 
        'avg_full_price_per_product', 'avg_disc_per_product'
    ],
    aggfunc={
        'order_id': pd.Series.nunique,
        'buyer_id': pd.Series.nunique,
        'purchase_completed': np.sum,
        'quantity': np.mean,
        'total_full_price': np.sum,
        'total_discount': np.sum,
        'total_discounted_price': np.sum,
        'avg_full_price_per_product': np.mean,
        'avg_disc_per_product': np.mean
    }
).reset_index()
base_ts_2.set_index('created_date', inplace=True)
base_ts_2 = base_ts_2.resample('D').sum()
base_ts_2.reset_index(inplace=True)
base_ts_2['day_name'] = base_ts_2['created_date'].dt.day_name()

base_ts_6 = pd.pivot_table(
    data=data_orders[data_orders['region_id']=='6'],
    index='created_date',
    values=[
        'order_id', 'buyer_id', 'purchase_completed', 'quantity', 
        'total_discounted_price', 'total_full_price', 'total_discount', 
        'avg_full_price_per_product', 'avg_disc_per_product'
    ],
    aggfunc={
        'order_id': pd.Series.nunique,
        'buyer_id': pd.Series.nunique,
        'purchase_completed': np.sum,
        'quantity': np.mean,
        'total_full_price': np.sum,
        'total_discount': np.sum,
        'total_discounted_price': np.sum,
        'avg_full_price_per_product': np.mean,
        'avg_disc_per_product': np.mean
    }
).reset_index()
base_ts_6.set_index('created_date', inplace=True)
base_ts_6 = base_ts_6.resample('D').sum()
base_ts_6.reset_index(inplace=True)
base_ts_6['day_name'] = base_ts_6['created_date'].dt.day_name()

# Ranking de categorias
rnk_category_2 = pd.pivot_table(
    data=data[data['region_id'] == '2'],
    index='category',
    values=['order_number', 'quantity', 'total_discounted_price'],
    aggfunc={
        'order_number': pd.Series.nunique,
        'quantity': np.sum,
        'total_discounted_price': np.sum
    }
).sort_values(by='quantity', ascending=False)
rnk_category_6 = pd.pivot_table(
    data=data[data['region_id'] == '6'],
    index='category',
    values=['order_number', 'quantity', 'total_discounted_price'],
    aggfunc={
        'order_number': pd.Series.nunique,
        'quantity': np.sum,
        'total_discounted_price': np.sum
    }
).sort_values(by='quantity', ascending=False)
rnk_category_2['qty_cumperc'] = rnk_category_2['quantity'].cumsum() / rnk_category_2['quantity'].sum(axis=0) * 100
rnk_category_6['qty_cumperc'] = rnk_category_6['quantity'].cumsum() / rnk_category_6['quantity'].sum(axis=0) * 100

# Ranking de subcategorias
rnk_subcategory_2 = pd.pivot_table(
    data=data[data['region_id'] == '2'],
    index='subcategory',
    values=['order_number', 'quantity', 'total_discounted_price'],
    aggfunc={
        'order_number': pd.Series.nunique,
        'quantity': np.sum,
        'total_discounted_price': np.sum
    }
).sort_values(by='quantity', ascending=False)
rnk_subcategory_6 = pd.pivot_table(
    data=data[data['region_id'] == '6'],
    index='subcategory',
    values=['order_number', 'quantity', 'total_discounted_price'],
    aggfunc={
        'order_number': pd.Series.nunique,
        'quantity': np.sum,
        'total_discounted_price': np.sum
    }
).sort_values(by='quantity', ascending=False)
rnk_subcategory_2['qty_cumperc'] = rnk_subcategory_2['quantity'].cumsum() / rnk_subcategory_2['quantity'].sum(axis=0) * 100
rnk_subcategory_6['qty_cumperc'] = rnk_subcategory_6['quantity'].cumsum() / rnk_subcategory_6['quantity'].sum(axis=0) * 100

# Ranking de marcas
rnk_brand_2 = pd.pivot_table(
    data=data[data['region_id'] == '2'],
    index='brand',
    values=['order_number', 'quantity', 'total_discounted_price'],
    aggfunc={
        'order_number': pd.Series.nunique,
        'quantity': np.sum,
        'total_discounted_price': np.sum
    }
).sort_values(by='quantity', ascending=False)
rnk_brand_6 = pd.pivot_table(
    data=data[data['region_id'] == '6'],
    index='brand',
    values=['order_number', 'quantity', 'total_discounted_price'],
    aggfunc={
        'order_number': pd.Series.nunique,
        'quantity': np.sum,
        'total_discounted_price': np.sum
    }
).sort_values(by='quantity', ascending=False)
rnk_brand_2['qty_cumperc'] = rnk_brand_2['quantity'].cumsum() / rnk_brand_2['quantity'].sum(axis=0) * 100
rnk_brand_6['qty_cumperc'] = rnk_brand_6['quantity'].cumsum() / rnk_brand_6['quantity'].sum(axis=0) * 100



# %% 5. Plots
mask_region_2 = data_orders['region_id'] == '2'
mask_region_6 = data_orders['region_id'] == '6'

# Lineplot: Trx evolution
fig, ax1 = plt.subplots(1, 1, figsize=(10, 4))
ax2 = ax1.twinx()
ax1.plot(base_ts_2[['created_date', 'order_id']].set_index('created_date'), color='g')
ax2.plot(base_ts_6[['created_date', 'order_id']].set_index('created_date'), color='b')
ax1.set_xlabel('Día')
ax1.set_ylabel('Ordenes (Region 2)')
ax2.set_ylabel('Ordenes (Region 6)')
fig.legend(['Region 2', 'Region 6'])
fig.suptitle('Evolución de ordenes diarias por region')
fig.autofmt_xdate(rotation=45)
plt.show()

# Barplot: Avg trx per day
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
sns.barplot(
    x='day_name', 
    y='order_id',
    data=base_ts_2.groupby(['day_name'])['order_id'].mean().sort_values(ascending=False).reset_index(),
    ax=axes[0]
)
sns.barplot(
    x='day_name', 
    y='order_id',
    data=base_ts_6.groupby(['day_name'])['order_id'].mean().sort_values(ascending=False).reset_index(),
    ax=axes[1]
)
axes[0].set(xlabel='Dia de la semana', ylabel='Ordenes promedio', title='Region 2')
axes[1].set(xlabel='Dia de la semana', ylabel='Ordenes promedio', title='Region 6')
fig.suptitle('Promedio de ordenes por dia de la semana', fontsize=15)
plt.show()

# Countplot: Qty of trx
fig, axes = plt.subplots(2, 1, figsize=(10, 10))
sns.countplot(
    y='payment_type', 
    data=data_orders[mask_region_2],
    order=data_orders.loc[mask_region_2, 'payment_type'].value_counts().index,
    ax=axes[0]
)
sns.countplot(
    y='payment_type', 
    data=data_orders[mask_region_6],
    order=data_orders.loc[mask_region_6, 'payment_type'].value_counts().index,
    ax=axes[1]
)
fig.suptitle('Número de ordenes por tipo de pago y región', fontsize=20)
axes[0].set(xlabel='Numero de ordenes', ylabel='Tipo de pago', title='Region 2')
axes[1].set(xlabel='Numero de ordenes', ylabel='Tipo de pago', title='Region 6')
plt.show()

# Barplot: Total discounted price
fig, axes = plt.subplots(2, 1, figsize=(10, 10))
sns.barplot(
    y='payment_type', 
    x='total_discounted_price',
    data=payment_type_2,
    ax=axes[0]
)
sns.barplot(
    y='payment_type',
    x='total_discounted_price',
    data=payment_type_6,
    ax=axes[1]
)
fig.suptitle('Revenue por tipo de pago y región', fontsize=20)
axes[0].set(xlabel='Revenue', ylabel='Tipo de pago', title='Region 2')
axes[1].set(xlabel='Revenue', ylabel='Tipo de pago', title='Region 6')
plt.show()

# Pareto plot - Categoria en Region 2
fig, ax = plt.subplots(1, 1, figsize=(8, 4))
ax.bar(
    x=rnk_category_2.index, 
    height=rnk_category_2['quantity'], 
    color='darkcyan'
)
ax2 = ax.twinx()
ax2.plot(
    rnk_category_2.index, 
    rnk_category_2['qty_cumperc'], 
    color='chocolate', 
    marker='D', 
    ms=6
)
ax2.yaxis.set_major_formatter(PercentFormatter())
ax2.axhline(y=60, xmin=0.05, xmax=0.95, linestyle='--', color='red')
ax.tick_params(axis='x', rotation=70, labelsize=8)
ax.set(xlabel='Categorias', ylabel='Unidades vendidas')
ax2.set(xlabel='Categorias', ylabel='Unidades vendidas (%)')
plt.title('Pareto de unidades vendidas por categoria en Región 2', fontsize=15)
plt.show()

# Pareto plot - Categoria en Region 6
fig, ax = plt.subplots(1, 1, figsize=(8, 4))
ax.bar(
    x=rnk_category_6.index, 
    height=rnk_category_6['quantity'], 
    color='darkcyan'
)
ax2 = ax.twinx()
ax2.plot(
    rnk_category_6.index, 
    rnk_category_6['qty_cumperc'], 
    color='chocolate', 
    marker='D', 
    ms=6
)
ax2.yaxis.set_major_formatter(PercentFormatter())
ax2.axhline(y=60, xmin=0.05, xmax=0.95, linestyle='--', color='red')
ax.tick_params(axis='x', rotation=90, labelsize=8)
ax.set(xlabel='Categorias', ylabel='Unidades vendidas')
ax2.set(xlabel='Categorias', ylabel='Unidades vendidas (%)')
plt.title('Pareto de unidades vendidas por categoria en Región 6', fontsize=15)
plt.show()



# Frecuencia
data_orders.order_id.nunique() / data_orders.buyer_id.nunique()

# MAUs
data_orders.buyer_id.nunique()

# MRPU
data_orders.total_discounted_price.sum() / data_orders.buyer_id.nunique()

# Trx
data_orders.order_id.nunique()

# Ticket full price
base_ts_2.iloc[:, 1:].sum()[7] / base_ts_2.iloc[:, 1:].sum()[2]
base_ts_6.iloc[:, 1:].sum()[7] / base_ts_6.iloc[:, 1:].sum()[2]

# Ticket discounted price
base_ts_2.iloc[:, 1:].sum()[6] / base_ts_2.iloc[:, 1:].sum()[2]
base_ts_6.iloc[:, 1:].sum()[6] / base_ts_6.iloc[:, 1:].sum()[2]

# Efecto descuento
base_ts_2.iloc[:, 1:].sum()[5] / base_ts_2.iloc[:, 1:].sum()[2]
base_ts_6.iloc[:, 1:].sum()[5] / base_ts_6.iloc[:, 1:].sum()[2]

# Promedio de unidades por orden
base_ts_2.iloc[:, 1:].mean()[4]
base_ts_6.iloc[:, 1:].mean()[4]

# %%
