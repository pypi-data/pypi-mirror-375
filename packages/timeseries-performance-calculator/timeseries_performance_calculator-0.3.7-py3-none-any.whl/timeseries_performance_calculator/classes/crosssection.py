from functools import cached_property
import os
import pandas as pd
from canonical_transformer import map_df_to_csv
from string_date_controller import get_today_nondashed
from timeseries_performance_calculator.crosssectional_analysis import (
    get_crosssectional_total_performance, 
    get_crosssectional_total_performance_without_benchmark, 
    get_crosssectional_total_performance_with_benchmark,
    get_crosssectional_annualized_return_cagr,
    get_crosssectional_period_returns,
    get_crosssectional_yearly_returns,
    get_crosssectional_annualized_return_days,
    get_crosssectional_annualized_volatility,
    get_crosssectional_maxdrawdown,
    get_crosssectional_sharpe_ratio,
    get_crosssectional_beta,
    get_crosssectional_winning_ratio,
    get_crosssectional_information_ratio,
    get_crosssectional_tracking_error,
    get_crosssectional_period_returns,
    get_crosssectional_yearly_returns,
    get_components_of_prices,
)

class CrossSection:
    def __init__(self, prices: pd.DataFrame, benchmark: pd.DataFrame, free_returns: pd.DataFrame = None):
        self.prices = prices
        self.benchmark = benchmark
        self.free_returns = free_returns
        self.components = get_components_of_prices(self.prices)

    @cached_property
    def prices_with_benchmark(self):
        return self.prices.join(self.benchmark, how='left').ffill()

    @cached_property
    def total_performance(self):
        return get_crosssectional_total_performance(self.prices_with_benchmark, free_returns=self.free_returns)

    @cached_property
    def total_performance_without_benchmark(self):
        return get_crosssectional_total_performance_without_benchmark(self.prices)

    @cached_property
    def total_performance_with_benchmark(self):
        return get_crosssectional_total_performance_with_benchmark(self.prices, self.benchmark)

    @cached_property
    def return_cagr(self):
        return get_crosssectional_annualized_return_cagr(self.prices)

    @cached_property
    def return_days(self):
        return get_crosssectional_annualized_return_days(self.prices)

    @cached_property
    def return_ytd(self):
        return get_crosssectional_period_returns(self.prices)

    @cached_property
    def return_total(self):
        return get_crosssectional_yearly_returns(self.prices)

    @cached_property
    def volatility(self):
        return get_crosssectional_annualized_volatility(self.prices)

    @cached_property
    def maxdrawdown(self):
        return get_crosssectional_maxdrawdown(self.prices)

    @cached_property
    def sharpe_ratio(self):
        return get_crosssectional_sharpe_ratio(self.prices, free_returns=self.free_returns)

    @cached_property
    def beta(self):
        return get_crosssectional_beta(self.prices)

    @cached_property
    def winning_ratio(self):
        return get_crosssectional_winning_ratio(self.prices)

    @cached_property
    def information_ratio(self):
        return get_crosssectional_information_ratio(self.prices, self.benchmark)

    @cached_property
    def tracking_error(self):
        return get_crosssectional_tracking_error(self.prices)

    def save(self, file_folder=None, file_name=None):
        LABEL_PRICES = f'{self.prices.columns[0]} etc.' if len(self.prices.columns) > 1 else f'{self.prices.columns[0]}'
        LABEL_BENCHMARK = f'{self.benchmark.columns[0]}'
        FILE_FOLDER_DEFAULT = os.path.join('data', 'dataset-result')
        FILE_NAME_DEFAULT = f'dataset-total_performance-{LABEL_PRICES}-{LABEL_BENCHMARK}-save{get_today_nondashed()}.csv'
        file_folder = file_folder if file_folder is not None else FILE_FOLDER_DEFAULT
        file_name = file_name if file_name is not None else FILE_NAME_DEFAULT
        map_df_to_csv(self.total_performance, file_folder=file_folder, file_name=file_name)

