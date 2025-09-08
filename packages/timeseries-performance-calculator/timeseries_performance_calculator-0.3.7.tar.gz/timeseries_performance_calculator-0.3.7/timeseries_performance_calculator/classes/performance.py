from functools import cached_property
import pandas as pd
from universal_timeseries_transformer import (
    PricesMatrix, 
    decompose_timeserieses_to_list_of_timeserieses, 
    plot_timeseries, 
    transform_timeseries, 
    extend_timeseries_by_all_dates,
    )
from timeseries_performance_calculator.tables.total import get_dfs_tables_year
from timeseries_performance_calculator.crosssectional_analysis import (
    get_crosssectional_total_performance, 
    get_crosssectional_total_performance_without_benchmark, 
    get_crosssectional_total_performance_with_benchmark,
    get_crosssectional_period_returns,
    get_crosssectional_yearly_returns,
    get_crosssectional_monthly_returns,
    get_crosssectional_yearly_relative,
    get_crosssectional_annualized_return_cagr,
    get_crosssectional_annualized_return_days,
    get_crosssectional_annualized_volatility,
    get_crosssectional_maxdrawdown,
    get_crosssectional_sharpe_ratio,
    get_crosssectional_beta,
    get_crosssectional_winning_ratio,
    get_crosssectional_information_ratio,
    get_crosssectional_tracking_error,
)
from timeseries_performance_calculator.crosssectional_analysis.parser import get_benchmark_price_in_prices, get_component_prices_in_prices
from .basis import get_table_seasonality


class Performance:
    def __init__(self, timeseries, benchmark_timeseries: pd.DataFrame = None, free_returns: pd.DataFrame = None):
        self.set_timeseries_and_benchmark(timeseries, benchmark_timeseries)
        self.free_returns = free_returns

    def set_timeseries_and_benchmark(self, timeseries, benchmark_timeseries):
        self.ordered_timeseries = timeseries.join(benchmark_timeseries, how='left').ffill()
        self.timeseries = self.ordered_timeseries.iloc[:, :-1]
        self.benchmark_timeseries = self.ordered_timeseries.iloc[:, [-1]]
        return None

    @cached_property
    def pm(self):
        return PricesMatrix(self.ordered_timeseries)
    
    @cached_property
    def prices(self):
        return self.pm.df

    @cached_property
    def pms(self):
        lst_of_prices = decompose_timeserieses_to_list_of_timeserieses(self.ordered_timeseries)
        return [PricesMatrix(df) for df in lst_of_prices]

    @cached_property
    def returns(self):
        lst_of_returns = [pm.returns for pm in self.pms]
        return pd.concat(lst_of_returns, axis=1)
    
    @cached_property
    def cumreturns(self):
        lst_of_cumreturns = [pm.cumreturns for pm in self.pms]
        return pd.concat(lst_of_cumreturns, axis=1)
    
    @cached_property
    def total_performance_for_benchmark(self):
        return get_crosssectional_total_performance_without_benchmark(prices=self.benchmark_timeseries, free_returns=self.free_returns)

    @cached_property
    def total_performance(self):
        df_port = get_crosssectional_total_performance(prices=self.timeseries, benchmark=self.benchmark_timeseries, free_returns=self.free_returns).T
        df_bm = self.total_performance_for_benchmark.T
        return df_port.join(df_bm, how='left').T
        
    @cached_property
    def total_performance_with_benchmark(self):
        return get_crosssectional_total_performance_with_benchmark(prices=self.timeseries, benchmark=self.benchmark_timeseries)

    @cached_property
    def period_returns(self):
        return get_crosssectional_period_returns(self.ordered_timeseries)
    
    @cached_property
    def yearly_returns(self):
        return get_crosssectional_yearly_returns(self.ordered_timeseries)
    
    @cached_property
    def monthly_returns(self):
        return get_crosssectional_monthly_returns(self.ordered_timeseries)
    
    @cached_property
    def yearly_relative(self):
        return get_crosssectional_yearly_relative(self.ordered_timeseries)
    
    @cached_property
    def annualized_return_cagr(self):
        return get_crosssectional_annualized_return_cagr(self.ordered_timeseries)
    
    @cached_property
    def annualized_return_days(self):
        return get_crosssectional_annualized_return_days(self.ordered_timeseries)
    
    @cached_property
    def annualized_volatility(self):
        return get_crosssectional_annualized_volatility(self.ordered_timeseries)
    
    @cached_property
    def maxdrawdown(self):
        return get_crosssectional_maxdrawdown(self.ordered_timeseries)
    
    @cached_property
    def sharpe_ratio(self):
        return get_crosssectional_sharpe_ratio(self.ordered_timeseries, free_returns=self.free_returns)
    
    @cached_property
    def beta(self):
        return get_crosssectional_beta(self.timeseries, self.benchmark_timeseries)
    
    @cached_property
    def winning_ratio(self):
        return get_crosssectional_winning_ratio(self.timeseries, self.benchmark_timeseries)
        
    @cached_property
    def information_ratio(self):
        return get_crosssectional_information_ratio(self.timeseries, self.benchmark_timeseries)

    @cached_property
    def tracking_error(self):
        return get_crosssectional_tracking_error(self.timeseries, self.benchmark_timeseries)

    @cached_property
    def return_ytd(self):
        return self.period_returns[['YTD']].rename(columns={'YTD': 'return_ytd'})
    
    @cached_property
    def return_total(self):
        return self.period_returns[['Since Inception']].rename(columns={'Since Inception': 'return_total'})

    def plot_cumreturns(
            self, 
            title=None, 
            option_last_name=False, 
            option_last_value=True, 
            option_main=False, 
            option_num_to_show=None,
            figsize=None
            ):
        timeseries_names = f'{list(self.timeseries.columns)[:3]} etc.' if len(list(self.timeseries.columns)) > 3 else list(self.timeseries.columns)
        benchmark_name = self.benchmark_timeseries.columns[0]
        return plot_timeseries(
            self.cumreturns.fillna(0), 
            title= title if title is not None else f"Cumreturns: {timeseries_names} (benchmark: {benchmark_name})",
            option_last_name=option_last_name, 
            option_last_value=option_last_value, 
            option_main=option_main, 
            option_num_to_show=option_num_to_show if option_num_to_show is not None else len(self.cumreturns.columns),
            figsize=figsize if figsize is not None else (10, 5)
            );

    def get_seasonality(self, index_name):
        return get_table_seasonality(self.monthly_returns, index_name)
    
    def get_relative_seasonality(self, index_name):
        df_port = get_table_seasonality(self.monthly_returns, index_name)
        benchmark_name = self.benchmark_timeseries.columns[0]
        df_bm = get_table_seasonality(self.monthly_returns, benchmark_name)
        df_relative = df_port - df_bm
        df_relative = df_relative.dropna(axis=0, how='all')
        return df_relative
