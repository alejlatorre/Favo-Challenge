import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from pandas.api.types import is_datetime64_dtype, is_numeric_dtype 

class RFM():
    def __init__(self, n_features=3):
        self._n_features = n_features

    def get_vars(self, data, user_col, date_col, order_col, ticket_col):
        try:
            _data = data.copy()

            # Get max date, frequency and monetary value table
            _left = pd.pivot_table(
                data=_data,
                index=user_col,
                aggfunc={
                    date_col: pd.Series.max,
                    order_col: pd.Series.nunique,
                    ticket_col: np.sum
                }
            )

            # Get recency variable
            if is_datetime64_dtype(_data[date_col]) != True:
                _data[date_col] = pd.to_datetime(_data[date_col])
            max_user_date = _data.groupby([user_col])[date_col].max()
            max_date = _data[date_col].max()
            recency = (max_date - max_user_date).dt.days

            # Merge datasets
            _rfm = pd.merge(
                left=_left[[order_col, ticket_col]],
                right=recency,
                left_index=True,
                right_index=True,
                how='left'
            )
            _rfm.reset_index(inplace=True)
            col_names = [user_col, 'frequency', 'monetary', 'recency']
            _rfm.columns = col_names

            return _rfm
        except ValueError as vx:
            print(f'Value error: {vx}')
        except Exception as ex:
            print(f'Exception: {ex}')

    def get_scores(self, data, r_col, f_col, m_col, q=3):
        try:
            _rfm = data.copy()
            # Create RFM variables
            _rfm['r_score'] = pd.qcut(_rfm[r_col].values, q=q, duplicates='drop')
            _rfm['f_score'] = pd.qcut(_rfm[f_col].values, q=q, duplicates='drop')
            _rfm['m_score'] = pd.qcut(_rfm[m_col].values, q=q, duplicates='drop')

            r = len(_rfm['r_score'].unique())
            f = len(_rfm['f_score'].unique())
            m = len(_rfm['m_score'].unique())
            r_labels = sorted([str(i) for i in range(1, r+1)], reverse=True)
            f_labels = [str(i) for i in range(1, f+1)]
            m_labels = [str(i) for i in range(1, m+1)]
            _rfm['r_score'] = pd.Categorical(_rfm['r_score']).rename_categories(r_labels)
            _rfm['f_score'] = pd.Categorical(_rfm['f_score']).rename_categories(f_labels)
            _rfm['m_score'] = pd.Categorical(_rfm['m_score']).rename_categories(m_labels)
                    
            return _rfm
        except ValueError as vx:
            print(f'Value error: {vx}')
        except Exception as ex:
            print(f'Exception: {ex}')
        