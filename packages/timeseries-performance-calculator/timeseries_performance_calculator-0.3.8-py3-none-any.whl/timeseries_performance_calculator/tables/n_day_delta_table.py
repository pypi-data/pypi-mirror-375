import pandas as pd

def get_table_n_day_delta(prices, n, index_ref=-1):
    """Calculate n-day delta (price difference) for all assets."""
    start_idx = index_ref - n
    end_idx = index_ref
    
    delta = prices.iloc[end_idx] - prices.iloc[start_idx]
    result = delta.to_frame(f'{n}-delta')
    
    return result

def get_table_days_deltas(prices, days=[1, 7], index_ref=-1):
    dfs = [get_table_n_day_delta(prices, n, index_ref) for n in days]
    df = pd.concat(dfs, axis=1)
    return df