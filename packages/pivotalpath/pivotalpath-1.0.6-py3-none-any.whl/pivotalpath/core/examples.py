
from . import main_library as mli
from . import important_tickers as it

"""
USE CASES AND EXAMPLES OF THE MAIN LIBRARY FUNCTIONS

This module provides practical examples demonstrating how to use the pivotalpath library.
Each function shows both the description and syntax for easy learning and reference.
"""


def example1():
    """Get important ticker symbols used throughout the library."""
    print("Example: Important ticker symbols")
    print("Syntax: [pp.important_tickers.market_ticker, pp.important_tickers.riskfree_ticker, pp.important_tickers.hedge_fund_composite_index_ticker]")
    return [it.market_ticker, it.riskfree_ticker, it.hedge_fund_composite_index_ticker]


def example2():
    """Retrieve the complete hedge fund index catalog."""
    print("Example: Hedge fund index catalog")
    print("Syntax: pp.get_catalog(asset_class='index')")
    return mli.get_catalog(asset_class="index")

def example3():
    """List all available hedge fund index tickers."""
    print("Example: Hedge fund index tickers")
    print("Syntax: pp.get_asset_list(asset_class='index')")
    return mli.get_asset_list(asset_class="index")


def example4():
    """List all available hedge fund index names."""
    print("Example: Hedge fund index names")
    print("Syntax: pp.get_asset_list(asset_class='index', select='name')")
    return mli.get_asset_list(asset_class="index", select="name")


def example5():
    """Retrieve historical market return data."""
    print("Example: Market returns")
    print("Syntax: pp.get_returns(ticker=pp.important_tickers.market_ticker)")
    return mli.get_returns(ticker=it.market_ticker)


def example6():
    """List all available statistical metrics (by ticker)."""
    print("Example: Available statistical metrics")
    print("Syntax: pp.get_stats_list()")
    return mli.get_stats_list()

def example7():
    """List all available statistical metrics (by name)."""
    print("Example: Statistical metric names")
    print("Syntax: pp.get_stats_list(select='name')")
    return mli.get_stats_list(select="name")
  
def example8():
    """Calculate basic statistics for the first 2 hedge fund indices."""
    print("Example: Statistics for hedge fund indices")
    print("Syntax: pp.get_stats(target=pp.get_asset_list(asset_class='index')[:2], base=pp.important_tickers.market_ticker, start='2020-01', end='2024-12', stat=['annret','annvol','sharpe'])")
    return mli.get_stats(
        target=mli.get_asset_list(asset_class="index")[:2],
        base=it.market_ticker,
        start="2020-01",
        end="2024-12",
        stat=['annret','annvol','sharpe']
        )


def example9():
    """Generate comprehensive statistics with custom asset labels."""
    print("Example: Statistics with custom labels")
    print("Syntax: pp.get_stats(target=pp.get_asset_list(asset_class='index')+['SP500'], base=pp.important_tickers.market_ticker, start='2020-01', end='2024-12', stat=pp.get_stats_list(), label_as='shortname')")
    return mli.get_stats(
        target=mli.get_asset_list(asset_class='index')+['SP500'],
        base=it.market_ticker,
        start="2020-01",
        end="2024-12",
        stat=mli.get_stats_list(),
        label_as="shortname",
        )

def example10():
    """Generate structured statistics with custom formatting and indexing."""
    print("Example: Structured statistics")
    print("Syntax: pp.get_stats(target=pp.get_asset_list(asset_class='index'), base=pp.important_tickers.market_ticker, start='2020-01', end='2024-12', stat=['sharpe','annvol'], label_as='name+period', index_as='name')")
    return mli.get_stats(
        target=mli.get_asset_list(asset_class='index'),
        base=it.market_ticker,
        start="2020-01",
        end="2024-12",
        stat=['sharpe','annvol'],
        label_as="name+period",
        index_as="name",
    )   

