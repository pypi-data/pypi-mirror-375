def get_n_day_returns(prices, n, index_ref=-1):
    indices_for_nday_returns = [index_ref-n, index_ref]
    df = prices.iloc[indices_for_nday_returns, :]
    df = df.pct_change(fill_method=None)*100
    df = df.iloc[[-1]].T
    df.columns = [f'{n}-day']
    return df