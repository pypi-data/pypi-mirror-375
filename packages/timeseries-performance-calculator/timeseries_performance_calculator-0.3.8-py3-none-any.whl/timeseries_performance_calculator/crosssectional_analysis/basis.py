from typing import Callable
import pandas as pd
from .parser import get_components_of_prices

def get_crosssectional_performance_by_components(kernel_performance: Callable, components: list[pd.DataFrame]) -> pd.DataFrame:
    dfs = [kernel_performance(component) for component in components]
    return pd.concat(dfs)

def get_crosssectional_performance_with_benchmark_by_components(kernel_performance: Callable, components: list[pd.DataFrame], benchmark: pd.DataFrame) -> pd.DataFrame:
    components_with_benchmark = [component.join(benchmark) for component in components]
    dfs = [kernel_performance(component_with_benchmark).iloc[[0], :] for component_with_benchmark in components_with_benchmark]
    return pd.concat(dfs)

def get_crosssectional_performance(kernel_performance: Callable, prices: pd.DataFrame) -> pd.DataFrame:
    components = get_components_of_prices(prices)
    return get_crosssectional_performance_by_components(kernel_performance, components)

def get_crosssectional_performance_with_benchmark(kernel_performance: Callable, prices: pd.DataFrame, benchmark: pd.DataFrame) -> pd.DataFrame:
    components = get_components_of_prices(prices)
    return get_crosssectional_performance_with_benchmark_by_components(kernel_performance, components, benchmark)