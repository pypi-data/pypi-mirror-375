from functools import partial
import pandas as pd
from timeseries_performance_calculator.tables.period_returns_table import get_table_period_returns
from timeseries_performance_calculator.tables.monthly_returns_table import get_table_monthly_returns
from timeseries_performance_calculator.tables.yearly_returns_table import get_table_yearly_returns, get_table_yearly_relative
from timeseries_performance_calculator.tables.annualized_return_table import get_table_annualized_return_cagr, get_table_annualized_return_days
from timeseries_performance_calculator.tables.annualized_volatility_table import get_table_annualized_volatility
from timeseries_performance_calculator.tables.sharpe_ratio_table import get_table_sharpe_ratio
from timeseries_performance_calculator.tables.maxdrawdown_table import get_table_maxdrawdown
from timeseries_performance_calculator.tables.beta_table import get_table_beta_by_index
from timeseries_performance_calculator.tables.winning_ratio_table import get_table_winning_ratio_by_index
from timeseries_performance_calculator.tables.information_ratio_table import get_table_information_ratio_by_index
from timeseries_performance_calculator.tables.tracking_error_table import get_table_tracking_error_by_index
from .parser import get_components_of_prices
from .basis import get_crosssectional_performance, get_crosssectional_performance_with_benchmark


get_crosssectional_period_returns = partial(get_crosssectional_performance, get_table_period_returns)
get_crosssectional_yearly_returns = partial(get_crosssectional_performance, get_table_yearly_returns)
get_crosssectional_annualized_return_cagr = partial(get_crosssectional_performance, get_table_annualized_return_cagr)
get_crosssectional_annualized_return_days = partial(get_crosssectional_performance, get_table_annualized_return_days)
get_crosssectional_annualized_volatility = partial(get_crosssectional_performance, get_table_annualized_volatility)
get_crosssectional_maxdrawdown = partial(get_crosssectional_performance, get_table_maxdrawdown)

def get_crosssectional_sharpe_ratio(prices: pd.DataFrame, free_returns: pd.DataFrame= None) -> pd.DataFrame:
    kernel_table = partial(get_table_sharpe_ratio, free_returns=free_returns)
    return get_crosssectional_performance(kernel_table, prices)

get_crosssectional_monthly_returns = get_table_monthly_returns
def get_crosssectional_monthly_relative(prices: pd.DataFrame, benchmark: pd.DataFrame) -> pd.DataFrame:
    table_port = get_table_monthly_returns(prices)
    table_bm = get_table_monthly_returns(benchmark)

    df_merged = table_port.T.join(table_bm.T, how='left')
    cols = df_merged.columns[:-1]
    col_bm = df_merged.columns[-1]

    for col in cols:
        df_merged[col] = df_merged[col] - df_merged[col_bm]
    return df_merged.drop(columns=[col_bm]).T

def get_crosssectional_yearly_relative(prices: pd.DataFrame, benchmark: pd.DataFrame) -> pd.DataFrame:
    components = get_components_of_prices(prices)
    dfs = []
    for component in components:
        index_name = component.columns[0]
        df = get_table_yearly_relative(component.join(benchmark)).iloc[[-1]]
        df.index = [index_name]
        dfs.append(df)
    return pd.concat(dfs)

get_crosssectional_beta = partial(get_crosssectional_performance_with_benchmark, get_table_beta_by_index)
get_crosssectional_winning_ratio = partial(get_crosssectional_performance_with_benchmark, get_table_winning_ratio_by_index)
get_crosssectional_information_ratio = partial(get_crosssectional_performance_with_benchmark, get_table_information_ratio_by_index)
get_crosssectional_tracking_error = partial(get_crosssectional_performance_with_benchmark, get_table_tracking_error_by_index)


def get_crosssectional_total_performance_without_benchmark(prices: pd.DataFrame, free_returns: pd.DataFrame= None) -> pd.DataFrame:
    annualized_return_cagr = get_crosssectional_annualized_return_cagr(prices)
    annualized_return_days = get_crosssectional_annualized_return_days(prices)
    annualized_volatility = get_crosssectional_annualized_volatility(prices)
    maxdrawdown = get_crosssectional_maxdrawdown(prices)
    sharpe_ratio = get_crosssectional_sharpe_ratio(prices, free_returns=free_returns)
    return pd.concat([annualized_return_cagr, annualized_return_days, annualized_volatility, maxdrawdown, sharpe_ratio], axis=1)

def get_crosssectional_total_performance_with_benchmark(prices: pd.DataFrame, benchmark: pd.DataFrame) -> pd.DataFrame:
    beta = get_crosssectional_beta(prices, benchmark)
    winning_ratio = get_crosssectional_winning_ratio(prices, benchmark)
    information_ratio = get_crosssectional_information_ratio(prices, benchmark)
    tracking_error = get_crosssectional_tracking_error(prices, benchmark)
    return pd.concat([beta, winning_ratio, information_ratio, tracking_error], axis=1)

def get_crosssectional_total_performance(prices: pd.DataFrame, benchmark: pd.DataFrame, free_returns: pd.DataFrame= None) -> pd.DataFrame:
    total_performance_without_benchmark = get_crosssectional_total_performance_without_benchmark(prices, free_returns)
    total_performance_with_benchmark = get_crosssectional_total_performance_with_benchmark(prices, benchmark)
    return pd.concat([total_performance_without_benchmark, total_performance_with_benchmark], axis=1)
