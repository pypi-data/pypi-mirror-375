# original code: QuantStats: Portfolio analytics for quants
# https://github.com/ranaroussi/quantstats Copyright 2019-2023 Ran Aroussi
# Licensed originally under the Apache License, Version 2.0: http://www.apache.org/licenses/LICENSE-2.0

import contextlib
from typing import Literal

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure
from pandas import DataFrame as _df  # noqa

from .. import stats as _stats
from . import core as _core


def plot_returns(
    returns: pd.Series | pd.DataFrame,
    benchmark: pd.Series | pd.DataFrame,
    grayscale: bool = False,
    figsize: tuple[int, int] = (10, 6),
    lw: float = 1.5,
    match_volatility: bool = False,
    compound: bool = True,
    cumulative: bool = True,
    resample=None,
    ylabel: str = "Cumulative Returns",
    subtitle: bool = True,
    savefig: dict | None = None,
    cutoff: pd.Timestamp | None = None,
):
    title = "Cumulative Returns" if compound else "Returns"
    if benchmark is not None:
        if isinstance(benchmark, str):
            title += " vs %s" % benchmark.upper()
        else:
            title += " vs Benchmark"
        if match_volatility:
            title += " (Volatility Matched)"

    return _core.plot_timeseries(
        returns,
        benchmark,
        title,
        ylabel=ylabel,
        match_volatility=match_volatility,
        log_scale=False,
        resample=resample,
        compound=compound,
        cumulative=cumulative,
        lw=lw,
        figsize=figsize,
        grayscale=grayscale,
        subtitle=subtitle,
        savefig=savefig,
        cutoff=cutoff,
    )


def plot_log_returns(
    returns: pd.Series | pd.DataFrame,
    benchmark: pd.Series | pd.DataFrame,
    grayscale: bool = False,
    figsize: tuple[int, int] = (10, 5),
    lw: float = 1.5,
    match_volatility: bool = False,
    compound: bool = True,
    cumulative: bool = True,
    resample=None,
    ylabel: str = "Cumulative Returns",
    subtitle: bool = True,
    savefig: dict | None = None,
    cutoff: pd.Timestamp | None = None,
) -> Figure:
    title = "Cumulative Returns" if compound else "Returns"
    if benchmark is not None:
        if isinstance(benchmark, str):
            title += " vs %s (Log Scaled" % benchmark.upper()
        else:
            title += " vs Benchmark (Log Scaled"
        if match_volatility:
            title += ", Volatility Matched"
    else:
        title += " (Log Scaled"
    title += ")"

    return _core.plot_timeseries(
        returns,
        benchmark,
        title,
        ylabel=ylabel,
        match_volatility=match_volatility,
        log_scale=True,
        resample=resample,
        compound=compound,
        cumulative=cumulative,
        lw=lw,
        figsize=figsize,
        grayscale=grayscale,
        subtitle=subtitle,
        savefig=savefig,
        cutoff=cutoff,
    )


def plot_daily_returns(
    returns: pd.Series | pd.DataFrame,
    benchmark: pd.Series | pd.DataFrame,
    grayscale: bool = False,
    figsize: tuple[int, int] = (10, 4),
    lw: float = 0.5,
    log_scale: bool = False,
    ylabel: str = "Returns",
    subtitle: bool = True,
    savefig: dict | None = None,
    active: bool = False,
    cutoff: pd.Timestamp | None = None,
) -> Figure:
    if active and benchmark is not None:
        returns = returns - benchmark

    plot_title = "Daily Active Returns" if active else "Daily Returns"

    return _core.plot_timeseries(
        returns,
        None,
        plot_title,
        ylabel=ylabel,
        match_volatility=False,
        log_scale=log_scale,
        resample="D",
        compound=False,
        lw=lw,
        figsize=figsize,
        grayscale=grayscale,
        subtitle=subtitle,
        savefig=savefig,
        cutoff=cutoff,
    )


def plot_series(
    series,
    title: str,
    grayscale: bool = False,
    figsize: tuple[int, int] = (10, 4),
    lw: float = 1.5,
    log_scale: bool = False,
    ylabel: str = "Returns",
    xlabel: str = "",
    subtitle: bool = True,
    savefig: bool | None = None,
    active: bool = False,
    percent: bool = False,
    cutoff: pd.Timestamp | None = None,
) -> Figure:
    return _core.plot_timeseries(
        series,
        None,
        title,
        ylabel=ylabel,
        xlabel=xlabel,
        match_volatility=False,
        log_scale=log_scale,
        resample=None,
        compound=False,
        lw=lw,
        figsize=figsize,
        grayscale=grayscale,
        subtitle=subtitle,
        savefig=savefig,
        percent=percent,
        marker="o",
        cutoff=cutoff,
    )


def plot_yearly_returns(
    returns: pd.Series | pd.DataFrame,
    benchmark: pd.Series | pd.DataFrame,
    grayscale: bool = False,
    hlw: float = 1.5,
    hlcolor: str = "red",
    hllabel: str = "",
    match_volatility: bool = False,
    log_scale: bool = False,
    figsize: tuple[int, int] = (10, 5),
    ylabel: bool = True,
    subtitle: bool = True,
    compounded: bool = True,
    savefig: dict | None = None,
) -> Figure:
    title = "EOY Returns"
    if benchmark is not None:
        title += "  vs Benchmark"
        benchmark = benchmark.resample("YE").apply(_stats.comp).resample("YE").last()

    if compounded:
        returns = returns.resample("YE").apply(_stats.comp)
    else:
        returns = returns.resample("YE").apply(_df.sum)
    returns = returns.resample("YE").last()

    return _core.plot_returns_bars(
        returns,
        benchmark,
        hline=returns.mean(),
        hlw=hlw,
        hllabel=hllabel,
        hlcolor=hlcolor,
        match_volatility=match_volatility,
        log_scale=log_scale,
        resample=None,
        title=title,
        figsize=figsize,
        grayscale=grayscale,
        ylabel=ylabel,
        subtitle=subtitle,
        savefig=savefig,
    )


def plot_distribution(
    returns: pd.Series | pd.DataFrame,
    grayscale: bool = False,
    ylabel: bool = True,
    figsize: tuple[int, int] = (10, 6),
    subtitle: bool = True,
    compounded: bool = True,
    savefig: dict | None = None,
    title: str | None = None,
) -> Figure:
    return _core.plot_distribution(
        returns,
        grayscale=grayscale,
        figsize=figsize,
        ylabel=ylabel,
        subtitle=subtitle,
        title=title,
        compounded=compounded,
        savefig=savefig,
    )


def plot_histogram(
    returns: pd.Series | pd.DataFrame,
    benchmark: pd.Series | pd.DataFrame,
    resample: Literal["W", "M", "Q", "A"] = "ME",
    grayscale: bool = False,
    figsize: tuple[int, int] = (10, 5),
    ylabel: bool = True,
    subtitle: bool = True,
    compounded: bool = True,
    savefig: dict | None = None,
) -> Figure:
    if resample == "W":
        title = "Weekly "
    elif resample == "ME":
        title = "Monthly "
    elif resample == "QE":
        title = "Quarterly "
    elif resample == "YE":
        title = "Annual "
    else:
        title = ""

    return _core.plot_histogram(
        returns,
        benchmark,
        resample=resample,
        grayscale=grayscale,
        title="Distribution of %sReturns" % title,
        figsize=figsize,
        ylabel=ylabel,
        subtitle=subtitle,
        compounded=compounded,
        savefig=savefig,
    )


def drawdown(
    returns: pd.Series | pd.DataFrame,
    grayscale: bool = False,
    figsize: tuple[int, int] = (10, 5),
    lw: float = 1,
    log_scale: bool = False,
    match_volatility: bool = False,
    compound: bool = False,
    ylabel: str = "Drawdown",
    resample: bool | None = None,
    subtitle: bool = True,
    savefig: dict | None = None,
    cutoff: pd.Timestamp | None = None,
) -> Figure:
    dd = _stats.to_drawdown_series(returns)

    return _core.plot_timeseries(
        dd,
        title="Underwater Plot",
        hline=dd.mean(),
        hlw=2,
        hllabel="Average",
        returns_label="Drawdown",
        compound=compound,
        match_volatility=match_volatility,
        log_scale=log_scale,
        resample=resample,
        fill=True,
        lw=lw,
        figsize=figsize,
        ylabel=ylabel,
        grayscale=grayscale,
        subtitle=subtitle,
        savefig=savefig,
        cutoff=cutoff,
    )


def plot_drawdowns_periods(
    returns: pd.Series | pd.DataFrame,
    periods: int = 5,
    lw: float = 1.5,
    log_scale: bool = False,
    grayscale: bool = False,
    title: str | None = None,
    figsize: tuple[int, int] = (10, 5),
    ylabel: bool = True,
    subtitle: bool = True,
    compounded: bool = True,
    savefig: dict | None = None,
    cutoff: pd.Timestamp | None = None,
) -> Figure:
    return _core.plot_longest_drawdowns(
        returns,
        periods=periods,
        lw=lw,
        log_scale=log_scale,
        grayscale=grayscale,
        title=title,
        figsize=figsize,
        ylabel=ylabel,
        subtitle=subtitle,
        compounded=compounded,
        savefig=savefig,
        cutoff=cutoff,
    )


def plot_rolling_beta(
    returns: pd.Series | pd.DataFrame,
    benchmark: pd.Series | pd.DataFrame,
    window1: int = 126,
    window1_label: str = "6-Months",
    window2: int = 252,
    window2_label: str = "12-Months",
    lw: float = 1.5,
    grayscale: bool = False,
    figsize: tuple[int, int] = (10, 3),
    ylabel: bool = True,
    subtitle: bool = True,
    savefig: dict | None = None,
    cutoff: pd.Timestamp | None = None,
) -> Figure:
    return _core.plot_rolling_beta(
        returns,
        benchmark,
        window1=window1,
        window1_label=window1_label,
        window2=window2,
        window2_label=window2_label,
        title="Rolling Beta to Benchmark",
        grayscale=grayscale,
        lw=lw,
        figsize=figsize,
        ylabel=ylabel,
        subtitle=subtitle,
        savefig=savefig,
        cutoff=cutoff,
    )


def plot_rolling_net_exposure(
    weights: pd.DataFrame,
    period: int = 5,
    period_label: str = "1 Week",
    lw: float = 1.5,
    grayscale: bool = False,
    figsize: tuple[int, int] = (10, 3),
    ylabel: str = "Rolling Net Exposure",
    subtitle: bool = True,
    savefig: dict | None = None,
    cutoff: pd.Timestamp | None = None,
) -> Figure:
    rolling_weights = weights.sum(axis="columns").rolling(period).mean()

    return _core.plot_rolling_stats(
        rolling_weights,
        hline=weights.sum(axis="columns").mean(),
        hlw=1.5,
        ylabel=ylabel,
        title="Rolling Net Exposure (%s)" % period_label,
        grayscale=grayscale,
        lw=lw,
        figsize=figsize,
        subtitle=subtitle,
        savefig=savefig,
        cutoff=cutoff,
    )


def plot_rolling_volatility(
    returns: pd.Series | pd.DataFrame,
    benchmark: pd.Series | pd.DataFrame,
    period: int = 126,
    period_label: str = "6-Months",
    periods_per_year: int = 252,
    lw: float = 1.5,
    grayscale: int = False,
    figsize: tuple[int, int] = (10, 3),
    ylabel: str = "Volatility",
    subtitle: bool = True,
    savefig: dict | None = None,
    cutoff: pd.Timestamp | None = None,
) -> Figure:
    returns = _stats.rolling_volatility(returns, period, periods_per_year)

    if benchmark is not None:
        benchmark = _stats.rolling_volatility(benchmark, period, periods_per_year)

    return _core.plot_rolling_stats(
        returns,
        benchmark,
        hline=returns.mean(),
        hlw=1.5,
        ylabel=ylabel,
        title="Rolling Volatility (%s)" % period_label,
        grayscale=grayscale,
        lw=lw,
        figsize=figsize,
        subtitle=subtitle,
        savefig=savefig,
        cutoff=cutoff,
    )


def plot_rolling_sharpe(
    returns: pd.Series | pd.DataFrame,
    benchmark: pd.Series | pd.DataFrame,
    rf: float = 0.0,
    period: int = 126,
    period_label: str = "6-Months",
    periods_per_year: int = 252,
    lw: float = 1.25,
    grayscale: bool = False,
    figsize: tuple[int, int] = (10, 3),
    ylabel: str = "Sharpe",
    subtitle: bool = True,
    savefig: dict | None = None,
    cutoff: pd.Timestamp | None = None,
) -> Figure:
    returns = _stats.rolling_sharpe(
        returns,
        rf,
        period,
        True,
        periods_per_year,
    )

    if benchmark is not None:
        benchmark = _stats.rolling_sharpe(benchmark, rf, period, True, periods_per_year)

    return _core.plot_rolling_stats(
        returns,
        benchmark,
        hline=returns.mean(),
        hlw=1.5,
        ylabel=ylabel,
        title="Rolling Sharpe (%s)" % period_label,
        grayscale=grayscale,
        lw=lw,
        figsize=figsize,
        subtitle=subtitle,
        savefig=savefig,
        cutoff=cutoff,
    )


def plot_monthly_heatmap(
    returns: pd.Series | pd.DataFrame,
    benchmark: pd.Series | pd.DataFrame,
    annot_size: int = 10,
    figsize: tuple[int, int] = (10, 5),
    cbar: bool = True,
    square: bool = False,
    returns_label: str = "Strategy",
    compounded: bool = True,
    eoy: bool = False,
    grayscale: bool = False,
    ylabel: bool = True,
    savefig: dict | None = None,
    active: bool = False,
) -> Figure:
    # colors, ls, alpha = _core._get_colors(grayscale)
    cmap = "gray" if grayscale else "RdYlGn"

    returns = _stats.monthly_returns(returns, eoy=eoy, compounded=compounded) * 100

    fig_height = len(returns) / 2.5

    if figsize is None:
        size = list(plt.gcf().get_size_inches())
        figsize = (size[0], size[1])

    figsize = (figsize[0], max([fig_height, figsize[1]]))

    if cbar:
        figsize = (figsize[0] * 1.051, max([fig_height, figsize[1]]))

    fig, ax = plt.subplots(figsize=figsize)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)

    fig.set_facecolor("white")
    ax.set_facecolor("white")

    # _sns.set(font_scale=.9)
    if active and benchmark is not None:
        ax.set_title(
            f"{returns_label} - Monthly Active Returns (%)\n",
            fontsize=14,
            y=0.995,
            fontweight="bold",
            color="black",
        )
        benchmark = (
            _stats.monthly_returns(benchmark, eoy=eoy, compounded=compounded) * 100
        )
        active_returns = returns - benchmark

        ax = sns.heatmap(
            active_returns,
            ax=ax,
            annot=True,
            center=0,
            annot_kws={"size": annot_size},
            fmt="0.2f",
            linewidths=0.5,
            square=square,
            cbar=cbar,
            cmap=cmap,
            cbar_kws={"format": "%.0f%%"},
        )
    else:
        ax.set_title(
            f"{returns_label} - Monthly Returns (%)\n",
            fontsize=14,
            y=0.995,
            fontweight="bold",
            color="black",
        )
        ax = sns.heatmap(
            returns,
            ax=ax,
            annot=True,
            center=0,
            annot_kws={"size": annot_size},
            fmt="0.2f",
            linewidths=0.5,
            square=square,
            cbar=cbar,
            cmap=cmap,
            cbar_kws={"format": "%.0f%%"},
        )
    # _sns.set(font_scale=1)

    # align plot to match other
    if ylabel:
        ax.set_ylabel("Years", fontweight="bold", fontsize=12)
        ax.yaxis.set_label_coords(-0.1, 0.5)

    ax.tick_params(colors="#808080")
    plt.xticks(rotation=0, fontsize=annot_size * 1.2)
    plt.yticks(rotation=0, fontsize=annot_size * 1.2)

    with contextlib.suppress(Exception):
        plt.subplots_adjust(hspace=0, bottom=0, top=1)
    with contextlib.suppress(Exception):
        fig.tight_layout(w_pad=0, h_pad=0)

    if savefig:
        if isinstance(savefig, dict):
            plt.savefig(**savefig)
        else:
            plt.savefig(savefig)

    plt.close()
    return fig


def plot_component_heatmap(
    data: pd.DataFrame,
    annot_size: int = 10,
    figsize: tuple[int, int] = (10, 5),
    cbar: bool = True,
    square: bool = False,
    grayscale: bool = False,
    ylabel: bool = True,
    savefig: dict | None = None,
) -> Figure:
    # colors, ls, alpha = _core._get_colors(grayscale)
    cmap = "gray" if grayscale else "RdYlGn"

    fig_height = len(data) / 2.5

    if figsize is None:
        size = list(plt.gcf().get_size_inches())
        figsize = (size[0], size[1])

    figsize = (figsize[0], max([fig_height, figsize[1]]))

    if cbar:
        figsize = (figsize[0] * 1.051, max([fig_height, figsize[1]]))

    fig, ax = plt.subplots(figsize=figsize)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)

    fig.set_facecolor("white")
    ax.set_facecolor("white")

    ax.set_title(
        "Heatmap of Targets by Year",
        fontsize=14,
        y=0.995,
        fontweight="bold",
        color="black",
    )
    ax = sns.heatmap(
        data,
        ax=ax,
        annot=True,
        center=0,
        annot_kws={"size": annot_size},
        fmt="0.2f",
        linewidths=0.5,
        square=square,
        cbar=cbar,
        cmap=cmap,
        cbar_kws={"format": "%.0f%%"},
    )
    # _sns.set(font_scale=1)

    # align plot to match other
    if ylabel:
        ax.set_ylabel("Targets", fontweight="bold", fontsize=12)
        ax.yaxis.set_label_coords(-0.1, 0.5)

    ax.tick_params(colors="#808080")
    plt.xticks(rotation=0, fontsize=annot_size * 1.2)
    plt.yticks(rotation=0, fontsize=annot_size * 1.0)

    with contextlib.suppress(Exception):
        plt.subplots_adjust(hspace=0, bottom=0, top=1)
    with contextlib.suppress(Exception):
        fig.tight_layout(w_pad=0, h_pad=0)

    if savefig:
        if isinstance(savefig, dict):
            plt.savefig(**savefig)
        else:
            plt.savefig(savefig)

    plt.close()
    return fig
