# %% 0. Libraries
import warnings
import numpy as np
import pandas as pd
import seaborn as sns 
import matplotlib.pyplot as plt

from datetime import datetime
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import MinMaxScaler

from yellowbrick.cluster import silhouette_visualizer

from src.models import RFM

# %% 1. Settings
warnings.filterwarnings('ignore')

option_settings = {
    'display.max_columns': None,
    'display.max_rows': False,
    'display.float_format': '{:,.4f}'.format
}
[pd.set_option(setting, option) for setting, option in option_settings.items()]

IN_PATH = 'data/in/'
OUT_PATH = 'data/out/'

# %% 2. Import data
filename = 'data_orders.csv'
data_trx = pd.read_csv(OUT_PATH + filename)
data_trx.head()

# %% 3. Model per region
results = {}
for region_id in data_trx['region_id'].unique():
    print(f'REGION {region_id}')
    df_ = data_trx[data_trx['region_id'] == region_id].copy() 

    # Get RFM variables and scores
    model = RFM()
    rfm_vars = model.get_vars(data=df_, user_col='buyer_id', date_col='effective_date_time', order_col='order_id', ticket_col='total_discounted_price')

    # Standardize
    raw_cols = ['frequency', 'monetary', 'recency']
    X = rfm_vars[raw_cols].copy()

    scaler = MinMaxScaler()
    norm_cols = ['norm_frequency', 'norm_monetary', 'norm_recency']
    rfm_vars[norm_cols] = scaler.fit_transform(X)
    print(rfm_vars.describe())

    # Get Elbow Method plot
    WCSS = []
    for i in range(1,11):
        model = KMeans(n_clusters = i, init = 'k-means++')
        model.fit(rfm_vars[norm_cols])
        WCSS.append(model.inertia_)
    fig = plt.figure(figsize = (8, 5))
    plt.plot(range(1,11), WCSS, linewidth=4, markersize=7, marker='o', color = 'green')
    plt.xticks(np.arange(11))
    plt.xlabel("Number of clusters")
    plt.ylabel("WCSS")
    plt.title('Elbow Method')
    plt.show()

    # Get Silhouette score plot for k-values
    print('Silhouette score for:')
    for i in range(3, 11):
        labels=KMeans(n_clusters=i, init='k-means++', random_state=0).fit(rfm_vars[norm_cols]).labels_
        score=silhouette_score(rfm_vars[norm_cols], labels, metric='euclidean', random_state=0)
        print(f'{i} clusters: {score}')
    silhouette_visualizer(KMeans(n_clusters=3, random_state=0), rfm_vars[norm_cols], colors='yellowbrick')
    plt.show()

    # KMeans
    kmeans = KMeans(n_clusters=3, random_state=0).fit(rfm_vars[norm_cols])
    rfm_vars['cluster'] = kmeans.predict(rfm_vars[norm_cols])

    # Mapping values
    new_values = {
        2: '1. High',
        1: '2. Mid',
        0: '3. Low'
    }
    rfm_vars['_cluster'] = rfm_vars['cluster'].map(new_values)
    results[f'region_{region_id}'] = rfm_vars

    # Boxplots
    fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(16, 7))
    sns.boxplot(x=rfm_vars['_cluster'], y=rfm_vars['recency'], ax=axes[0])
    sns.boxplot(x=rfm_vars['_cluster'], y=rfm_vars['frequency'], ax=axes[1])
    sns.boxplot(x=rfm_vars['_cluster'], y=rfm_vars['monetary'], ax=axes[2])
    fig.suptitle(f'Variables por cluster en Region {region_id}')
    axes[0].set(xlabel='Cluster', ylabel='Días desde la última compra', title='Recencia')
    axes[1].set(xlabel='Cluster', ylabel='Número de ordenes', title='Frecuencia')
    axes[2].set(xlabel='Cluster', ylabel='Ticket promedio', title='Valor monetario')
    plt.show()

# %%
