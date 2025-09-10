import numpy as np
import math
from datetime import datetime, timedelta

import os
from enum import Enum
import pandas as pd
import csv
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter, PercentFormatter
from matplotlib.gridspec import GridSpec
import seaborn as sns
from matplotlib.patches import Rectangle



# Set fonts for English
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False  # Fix minus sign display

# Set chart style - compatible solution
try:
    # Try using seaborn style
    sns.set_style("whitegrid")
    sns.set_palette("Set2")
except:
    # Fallback to matplotlib default style
    plt.style.use('ggplot')
    # Manual color palette
    mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', 
                                                    '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', 
                                                    '#bcbd22', '#17becf'])

class PerformanceMetrics:
    def __init__(self, total_assets_dict, init_cash, outpath, win_ratio=0.0, risk_free_rate=0.024, trading_days_per_year=252):
        """
        Initialize Performance Metrics Calculator
        
        :param total_assets_dict: Daily total assets dict {date string: total asset value}
        :param init_cash: Initial capital
        :param win_ratio: Win ratio (default 0)
        :param risk_free_rate: Annual risk-free rate (default 0.024)
        :param trading_days_per_year: Trading days per year (default 252)
        """
        self.init_cash = init_cash
        self.win_ratio = win_ratio
        self.risk_free_rate = risk_free_rate
        self.trading_days_per_year = trading_days_per_year
        self.outpath = outpath

        
    
        self.write_dict_to_csv(total_assets_dict, self.outpath + "net.csv")
        # Preprocess data: sort and extract asset sequence
        self.dates, self.assets = self._preprocess_data(total_assets_dict)
        
        if not self.assets:
            raise ValueError("资产数据为空，无法计算收益")
        
        # Calculate actual trading days
        self.total_days = len(self.dates)
        
        # Calculate actual time span in years
        self.time_span = self._calculate_time_span()
        
        # Calculate return sequence
        self.returns = self._calculate_returns()
        
        # Calculate cumulative return sequence
        self.cumulative_returns = self._calculate_cumulative_returns()
        
        # Calculate drawdown sequence
        self.drawdowns = self._calculate_drawdowns()
        
        # Calculate daily profits/losses
        self.daily_profits = self._calculate_daily_profits()
        
        # Calculate max drawdown details
        self.max_dd, self.max_dd_start, self.max_dd_end = self._calculate_max_drawdown_details()
        
        # Calculate all key metrics
        self.cum_ret = self.cumulative_return()
        self.ann_ret = self.annualized_return()
        self.ann_vol = self.annualized_volatility()
        self.sharpe = self.sharpe_ratio()
        self.max_dd_value = self.max_dd
        self.calmar = self.calmar_ratio()
        self.sortino = self.sortino_ratio()
        self.win_rate = self.winning_rate()
    def write_dict_to_csv(self, net_dic, filename="net.csv", date_col="交易日", value_col="数值"):
        """
        将字典写入CSV文件，键作为交易日，值作为数值
        
        参数:
        net_dic: 包含交易日和对应数值的字典
        filename: 输出的CSV文件名，默认为"output.csv"
        date_col: 日期列的列名，默认为"交易日"
        value_col: 数值列的列名，默认为"数值"
        """
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                # 创建CSV写入器
                writer = csv.writer(csvfile)
                
                # 写入列名
                writer.writerow([date_col, value_col])
                
                # 写入字典数据
                for date, value in net_dic.items():
                    writer.writerow([date, value])
                    
            #print(f"数据已成功写入 {filename}")
            return True
            
        except Exception as e:
            print(f"写入CSV文件时出错: {e}")
            return False
    
    def _preprocess_data(self, total_assets_dict):
        """Process asset data: sort dates and extract asset sequence"""
        # Convert date strings to date objects for sorting
        date_objects = [(datetime.strptime(d, '%Y.%m.%d'), d) for d in total_assets_dict]
        sorted_dates = sorted(date_objects, key=lambda x: x[0])
        
        # Extract sorted date strings and corresponding assets
        dates_sorted = [d[1] for d in sorted_dates]
        assets = [total_assets_dict[d] for d in dates_sorted]
        
        return dates_sorted, assets
    
    def _calculate_time_span(self):
        """Calculate actual time span in years"""
        if len(self.dates) < 2:
            return 0.0
            
        start_date = datetime.strptime(self.dates[0], '%Y.%m.%d')
        end_date = datetime.strptime(self.dates[-1], '%Y.%m.%d')
        days_between = len(self.dates)
        #days_between = len(self.assets)
        #days_between = (end_date - start_date).days

        
        # Avoid division by zero
        if days_between <= 0:
            return 1.0 / self.trading_days_per_year
            
        return days_between / 252.0
    
    def _calculate_returns(self):
        """Calculate daily return sequence"""
        returns = []
        
        # First trading day's return
        if self.init_cash != 0:
            first_return = (self.assets[0] - self.init_cash) / self.init_cash
            returns.append(first_return)
        else:
            # Avoid division by zero
            returns.append(0.0)
        
        # Subsequent trading days' returns
        for i in range(1, len(self.assets)):
            if self.assets[i-1] != 0:  # Avoid division by zero
                daily_return = (self.assets[i] - self.assets[i-1]) / self.assets[i-1]
                returns.append(daily_return)
            else:
                returns.append(0.0)
                
        return returns
    
    def _calculate_cumulative_returns(self):
        """Calculate cumulative return sequence"""
        cumulative_returns = []
        current_value = 1.0  # Start at 1 (100%)
        
        for r in self.returns:
            current_value *= (1 + r)
            cumulative_returns.append(current_value - 1)  # Store as return rate, not multiplier
            
        return cumulative_returns
    
    def _calculate_drawdowns(self):
        """Calculate daily drawdown sequence"""
        peak = self.init_cash
        drawdowns = []
        
        # Consider initial capital as starting point
        all_assets = [self.init_cash] + self.assets
        
        for asset in all_assets:
            if asset > peak:
                peak = asset
            drawdown = (peak - asset) / peak
            drawdowns.append(drawdown)
        
        # Return drawdown sequence starting from first trading day
        return drawdowns[1:]
    
    def _calculate_max_drawdown_details(self):
        """Calculate max drawdown details (rate, start date, end date)"""
        if not self.assets or len(self.assets) < 2:
            return 0.0, None, None
            
        # Add initial capital to asset sequence
        all_assets = [self.init_cash] + self.assets
        all_dates = [self.dates[0]] + self.dates  # Use first trading day as initial capital date
        
        peak = all_assets[0]
        max_dd = 0.0
        max_dd_start = all_dates[0]
        max_dd_end = all_dates[0]
        current_dd_start = all_dates[0]
        
        for i, asset in enumerate(all_assets):
            if asset > peak:
                peak = asset
                current_dd_start = all_dates[i]  # New peak, reset drawdown start date
            
            dd = (peak - asset) / peak
            if dd > max_dd:
                max_dd = dd
                max_dd_start = current_dd_start
                max_dd_end = all_dates[i]
                
        return max_dd, max_dd_start, max_dd_end
    
    def _calculate_daily_profits(self):
        """Calculate daily profit/loss amounts"""
        profits = []
        prev_asset = self.init_cash
        
        for asset in self.assets:
            profit = asset - prev_asset
            profits.append(profit)
            prev_asset = asset
            
        return profits
    
    def cumulative_return(self):
        """Calculate cumulative return"""
        if self.init_cash == 0:
            return 0.0
        return (self.assets[-1] - self.init_cash) / self.init_cash
    
    def annualized_return(self):
        """Calculate annualized return"""
        cumulative_ret = self.cumulative_return()
        
        # If time span is less than one year, use trading days
        if self.time_span < 1.0:
            if self.total_days == 0:
                return 0.0
            return (1 + cumulative_ret) ** (self.trading_days_per_year / self.total_days) - 1
        
        # For time spans greater than one year, use actual years
        return (1 + cumulative_ret) ** (1 / self.time_span) - 1
    
    def annualized_volatility(self):
        """Calculate annualized volatility"""
        if len(self.returns) < 2:
            return 0.0
            
        # Adjust annualization factor based on time span
        if self.time_span < 1.0:
            annualization_factor = math.sqrt(self.trading_days_per_year)
        else:
            annualization_factor = math.sqrt(self.trading_days_per_year * self.time_span)
            
        return np.std(self.returns) * annualization_factor
    
    def sharpe_ratio(self):
        """Calculate Sharpe ratio"""
        if len(self.returns) < 2:
            return 0.0
            
        # Calculate daily risk-free rate
        daily_rf = (1 + self.risk_free_rate) ** (1/self.trading_days_per_year) - 1
        
        # Calculate excess returns
        excess_returns = [r - daily_rf for r in self.returns]
        
        # Calculate mean and std of excess returns
        avg_excess_return = np.mean(excess_returns)
        std_excess_return = np.std(excess_returns)
        
        if std_excess_return == 0:
            return 0.0
            
        # Annualized Sharpe ratio
        return (avg_excess_return / std_excess_return) * math.sqrt(self.trading_days_per_year)
    
    def max_drawdown(self):
        """Calculate maximum drawdown rate"""
        return self.max_dd
    
    def max_drawdown_period(self):
        """Return max drawdown start and end dates"""
        return self.max_dd_start, self.max_dd_end
    
    def calmar_ratio(self):
        """Calculate Calmar ratio (annualized return / max drawdown)"""
        max_dd = self.max_dd
        annual_ret = self.annualized_return()
        
        if max_dd == 0:
            # If max drawdown is zero and annual return is positive, return a large number
            if annual_ret > 0:
                return float('inf')
            return 0.0
            
        return annual_ret / max_dd
    
    def winratio(self):
        """Return win ratio"""
        return self.win_ratio

    def sortino_ratio(self):
        """Calculate Sortino ratio (only consider downside volatility)"""
        if len(self.returns) < 2:
            return 0.0
            
        # Calculate daily risk-free rate
        daily_rf = (1 + self.risk_free_rate) ** (1/self.trading_days_per_year) - 1
        
        # Calculate downside deviation
        downside_returns = []
        for r in self.returns:
            if r < daily_rf:
                downside_returns.append(r - daily_rf)
        
        if not downside_returns:
            return 0.0
            
        downside_dev = np.std(downside_returns)
        if downside_dev == 0:
            return 0.0
        
        # Calculate average excess return
        avg_return = np.mean(self.returns)
        
        # Annualized Sortino ratio
        return (avg_return - daily_rf) / downside_dev * math.sqrt(self.trading_days_per_year)
    
    def winning_rate(self):
        """Calculate win rate (percentage of profitable days)"""
        if not self.returns:
            return 0.0
            
        winning_days = sum(1 for r in self.returns if r > 0)
        return winning_days / len(self.returns)
    
    def profit_factor(self):
        """Calculate profit factor (total profit / total loss)"""
        total_profit = 0
        total_loss = 0
        
        for profit in self.daily_profits:
            if profit > 0:
                total_profit += profit
            else:
                total_loss += abs(profit)
        
        if total_loss == 0:
            # No loss but profit exists
            if total_profit > 0:
                return float('inf')
            # No profit and no loss
            return 0.0
            
        return total_profit / total_loss
    
    def plot_metrics_dashboard(self, title='Performance Metrics Dashboard', figsize=(12, 8), save_path=None, show=True):
        """
        Plot key metrics dashboard
        
        :param title: Chart title
        :param figsize: Chart size
        :param save_path: Save path (optional)
        :param show: Whether to display chart
        """
        # Create figure and grid layout
        fig = plt.figure(figsize=figsize)
        gs = GridSpec(3, 3, figure=fig)
        
        # Set background color
        fig.patch.set_facecolor('#f0f0f0')
        
        # 1. Title
        ax_title = fig.add_subplot(gs[0, :])
        ax_title.axis('off')
        ax_title.set_title(title, fontsize=24, fontweight='bold', pad=20)
        
        # 2. Main metrics area
        ax_metrics = fig.add_subplot(gs[1:, :])
        ax_metrics.axis('off')
        
        # Define metrics layout
        metrics = [
            ("Cumulative Return", f"{self.cum_ret:.2%}", "#4CAF50"),
            ("Annualized Return", f"{self.ann_ret:.2%}", "#2196F3"),
            ("Annualized Volatility", f"{self.ann_vol:.2%}", "#FF9800"),
            ("Sharpe Ratio", f"{self.sharpe:.4f}", "#9C27B0"),
            ("Max Drawdown", f"{self.max_dd_value:.2%}", "#F44336"),
            ("Calmar Ratio", f"{self.calmar:.4f}", "#009688"),
            ("Sortino Ratio", f"{self.sortino:.4f}", "#795548"),
            ("Win Rate", f"{self.win_rate:.2%}", "#E91E63"),
            ("Initial Capital", f"¥{self.init_cash:,.2f}", "#607D8B")
        ]
        
        # Create metric boxes
        box_size = 0.2
        box_padding = 0.05
        boxes_per_row = 3
        start_x = 0.05
        start_y = 0.7
        
        for i, (name, value, color) in enumerate(metrics):
            row = i // boxes_per_row
            col = i % boxes_per_row
            
            x = start_x + col * (box_size + box_padding)
            y = start_y - row * (box_size + box_padding)
            
            # Add metric box
            rect = Rectangle((x, y), box_size, box_size, 
                             facecolor=color, alpha=0.8, 
                             edgecolor='white', linewidth=2)
            ax_metrics.add_patch(rect)
            
            # Add metric name
            ax_metrics.text(x + box_size/2, y + box_size - 0.08, name, 
                           ha='center', va='center', fontsize=12, color='white', fontweight='bold')
            
            # Add metric value
            ax_metrics.text(x + box_size/2, y + box_size/2 - 0.02, value, 
                           ha='center', va='center', fontsize=16, color='white', fontweight='bold')
        
        # Add additional info
        ax_metrics.text(0.05, 0.05, 
                       f"Evaluation Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                       f"Period: {self.dates[0]} to {self.dates[-1]}\n"
                       f"Trading Days: {self.total_days}",
                       fontsize=12, ha='left', va='bottom')
        
        # Save or show
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=300, facecolor=fig.get_facecolor())
        if show:
            plt.show()
    
    # ... 前面的代码保持不变 ...

    def plot_all_charts(self, save_path='performance_summary.png', figsize=(12, 22)):
        """
        Plot all charts and save as a summary image (optimized vertical layout with increased spacing)
        
        :param save_path: Save path
        :param figsize: Chart size (width, height), default adjusted to be more compact
        """
        # Create large figure
        fig = plt.figure(figsize=figsize, constrained_layout=True)
        # Use 6 rows and 1 column grid layout (vertical arrangement) with increased spacing
        gs = GridSpec(6, 1, figure=fig, height_ratios=[12, 2, 2, 2, 2, 2], hspace=1)  # Increased spacing
        
        # 1. Key metrics dashboard (placed first)
        ax1 = fig.add_subplot(gs[0])
        self._plot_metrics_dashboard(ax1)
        
        # 2. Equity curve
        ax2 = fig.add_subplot(gs[1])
        self._plot_equity_curve(ax2)
        
        # 3. Drawdown curve
        ax3 = fig.add_subplot(gs[2])
        self._plot_drawdown(ax3)
        
        # 4. Cumulative returns curve
        ax4 = fig.add_subplot(gs[3])
        self._plot_cumulative_returns(ax4)
        
        # 5. Returns distribution
        ax5 = fig.add_subplot(gs[4])
        self._plot_returns_distribution(ax5)
        
        # 6. Monthly returns heatmap
        ax6 = fig.add_subplot(gs[5])
        self._plot_monthly_returns(ax6)
        
        # Set overall title (adjusted y-value to reduce top margin)
        fig.suptitle('Comprehensive Performance Analysis Report', fontsize=22, fontweight='bold', y=0.98)
        
        # Save chart (compact layout)
        plt.savefig(save_path, bbox_inches='tight', dpi=150)
        plt.close()

        # 保存各个子图
        self.save_individual_charts(self.outpath)
        
        print(f"All charts saved to: {save_path}")
   

    def save_individual_charts(self, output_dir='./'):
        """Save each chart individually with appropriate file names"""
        #os.makedirs(output_dir, exist_ok=True)
        
        # 1. 保存关键指标面板
        self.save_metrics_dashboard(self.outpath + 'key_metrics.png')
        
        # 2. 保存资产曲线
        self.save_equity_curve(self.outpath + 'equity_curve.png')
        
        # 3. 保存回撤曲线
        self.save_drawdown_chart(self.outpath + 'drawdown.png')
        
        # 4. 保存累计收益曲线
        self.save_cumulative_returns(self.outpath + 'cumulative_returns.png')
        
        # 5. 保存收益分布
        self.save_returns_distribution(self.outpath + 'returns_distribution.png')
        
        # 6. 保存月度收益热力图
        self.save_monthly_returns_heatmap(self.outpath + 'monthly_returns.png')
        
        print(f"All individual charts saved to: {self.outpath}")

    
    # 以下是各个图表的保存方法
    def save_metrics_dashboard(self, save_path, figsize=(10, 8)):
        """Save key metrics dashboard as individual image"""
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111)
        self._plot_metrics_dashboard(ax)
        fig.savefig(save_path, bbox_inches='tight', dpi=150)
        plt.close()
        print(f"Key metrics dashboard saved to: {save_path}")

    def save_equity_curve(self, save_path, figsize=(10, 6)):
        """Save equity curve as individual image"""
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111)
        self._plot_equity_curve(ax)
        fig.savefig(save_path, bbox_inches='tight', dpi=150)
        plt.close()
        print(f"Equity curve saved to: {save_path}")

    def save_drawdown_chart(self, save_path, figsize=(10, 5)):
        """Save drawdown chart as individual image"""
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111)
        self._plot_drawdown(ax)
        fig.savefig(save_path, bbox_inches='tight', dpi=150)
        plt.close()
        print(f"Drawdown chart saved to: {save_path}")

    def save_cumulative_returns(self, save_path, figsize=(10, 5)):
        """Save cumulative returns chart as individual image"""
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111)
        self._plot_cumulative_returns(ax)
        fig.savefig(save_path, bbox_inches='tight', dpi=150)
        plt.close()
        print(f"Cumulative returns chart saved to: {save_path}")

    def save_returns_distribution(self, save_path, figsize=(10, 6)):
        """Save returns distribution chart as individual image"""
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111)
        self._plot_returns_distribution(ax)
        fig.savefig(save_path, bbox_inches='tight', dpi=150)
        plt.close()
        print(f"Returns distribution saved to: {save_path}")

    def save_monthly_returns_heatmap(self, save_path, figsize=(10, 8)):
        """Save monthly returns heatmap as individual image"""
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111)
        self._plot_monthly_returns(ax)
        fig.savefig(save_path, bbox_inches='tight', dpi=150)
        plt.close()
        print(f"Monthly returns heatmap saved to: {save_path}")

    # Internal plotting methods for summary chart
    def _plot_equity_curve(self, ax):
        """Plot equity curve on specified axis"""
        # Convert to date objects
        date_objs = [datetime.strptime(d, '%Y.%m.%d') for d in self.dates]
        
        # Calculate baseline (initial capital)
        baseline = [self.init_cash] * len(self.assets)
        
        # Plot equity curve
        ax.plot(date_objs, self.assets, label='Total Assets', color='#1f77b4', linewidth=2)
        ax.plot(date_objs, baseline, label='Initial Capital', color='#ff7f0e', linestyle='--', linewidth=1)
        
        # Set title and labels
        ax.set_title('Equity Curve', fontsize=16)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Total Assets', fontsize=12)
        
        # Format Y-axis as currency
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: '¥{:,.0f}'.format(x)))
        
        # Set date format
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        
        # Add grid and legend
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend()
        
        # Add cumulative return annotation
        cum_return = self.cum_ret
        ax.annotate(f'Cumulative Return: {cum_return:.2%}',
                xy=(0.05, 0.95), xycoords='axes fraction',
                fontsize=12, bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))

    def _plot_drawdown(self, ax):
        """Plot drawdown curve on specified axis"""
        # Convert to date objects
        date_objs = [datetime.strptime(d, '%Y.%m.%d') for d in self.dates]
        
        # Plot drawdown curve
        ax.fill_between(date_objs, self.drawdowns, 0, 
                    where=np.array(self.drawdowns) > 0, 
                    facecolor='#d62728', alpha=0.3, label='Drawdown')
        
        # Mark max drawdown
        max_dd = self.max_dd_value
        max_dd_idx = np.argmax(self.drawdowns)
        
        
        # Set title and labels
        ax.set_title('Drawdown Curve', fontsize=16)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Drawdown Rate', fontsize=12)
        
        # Format Y-axis as percentage
        ax.yaxis.set_major_formatter(PercentFormatter(1.0))
        
        # Set date format
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        
        # Add grid and legend
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend()

    def _plot_cumulative_returns(self, ax):
        """Plot cumulative returns on specified axis"""
        # Convert to date objects
        date_objs = [datetime.strptime(d, '%Y.%m.%d') for d in self.dates]
        
        # Plot cumulative returns curve
        ax.plot(date_objs, self.cumulative_returns, label='Cumulative Returns', color='#1f77b4', linewidth=2)
        
        # Add zero line
        ax.axhline(y=0, color='gray', linestyle='--', alpha=0.7)
        
        # Set title and labels
        ax.set_title('Cumulative Returns', fontsize=16)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Cumulative Return', fontsize=12)
        
        # Format Y-axis as percentage
        ax.yaxis.set_major_formatter(PercentFormatter(1.0))
        
        # Set date format
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        
        # Add grid and legend
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend()
        
        # Add final cumulative return annotation
        final_return = self.cum_ret
        ax.annotate(f'Final Return: {final_return:.2%}',
                xy=(0.05, 0.95), xycoords='axes fraction',
                fontsize=12, bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))

    def _plot_returns_distribution(self, ax):
        """Plot returns distribution on specified axis"""
        # Calculate positive and negative returns
        positive_returns = [r for r in self.returns if r > 0]
        negative_returns = [r for r in self.returns if r < 0]
        
        # Plot histogram
        ax.hist(self.returns, bins=30, color='#1f77b4', edgecolor='black', alpha=0.7)
        
        # Add mean line
        mean_return = np.mean(self.returns)
        ax.axvline(mean_return, color='#ff7f0e', linestyle='dashed', linewidth=2, 
                label=f'Mean: {mean_return:.2%}')
        
        # Add median line
        median_return = np.median(self.returns)
        ax.axvline(median_return, color='#2ca02c', linestyle='dashed', linewidth=2, 
                label=f'Median: {median_return:.2%}')
        
        # Add positive/negative ratio annotation
        pos_ratio = len(positive_returns) / len(self.returns) if self.returns else 0
        neg_ratio = len(negative_returns) / len(self.returns) if self.returns else 0
        
        ax.annotate(f'Positive Days: {len(positive_returns)} ({pos_ratio:.2%})',
                xy=(0.65, 0.95), xycoords='axes fraction', fontsize=12)
        ax.annotate(f'Negative Days: {len(negative_returns)} ({neg_ratio:.2%})',
                xy=(0.65, 0.90), xycoords='axes fraction', fontsize=12)
        
        # Set title and labels
        ax.set_title('Returns Distribution', fontsize=16)
        ax.set_xlabel('Daily Return', fontsize=12)
        ax.set_ylabel('Frequency', fontsize=12)
        
        # Format X-axis as percentage
        ax.xaxis.set_major_formatter(PercentFormatter(1.0))
        
        # Add grid and legend
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend()

    def _plot_metrics_dashboard(self, ax):
        """Plot key metrics dashboard on specified axis"""
        ax.axis('off')
        
        # Set background color
        ax.set_facecolor('#f0f0f0')
        
        # Add title
        ax.text(0.5, 0.95, 'Key Performance Metrics Dashboard', 
            fontsize=20, fontweight='bold', 
            ha='center', va='center', transform=ax.transAxes)
        
        # Define metrics
        metrics = [
            ("Cumulative Return", f"{self.cum_ret:.2%}", "#4CAF50"),
            ("Annualized Return", f"{self.ann_ret:.2%}", "#2196F3"),
            ("Annualized Volatility", f"{self.ann_vol:.2%}", "#FF9800"),
            ("Sharpe Ratio", f"{self.sharpe:.4f}", "#9C27B0"),
            ("Max Drawdown", f"{self.max_dd_value:.2%}", "#F44336"),
            ("Calmar Ratio", f"{self.calmar:.4f}", "#009688"),
            ("Sortino Ratio", f"{self.sortino:.4f}", "#795548"),
            ("Win Rate", f"{self.win_rate:.2%}", "#E91E63"),
            ("Initial Capital", f"¥{self.init_cash:,.2f}", "#607D8B")
        ]
        
        # Create metric boxes
        box_size = 0.2
        box_padding = 0.05
        boxes_per_row = 3
        start_x = 0.05
        start_y = 0.7
        
        for i, (name, value, color) in enumerate(metrics):
            row = i // boxes_per_row
            col = i % boxes_per_row
            
            x = start_x + col * (box_size + box_padding)
            y = start_y - row * (box_size + box_padding)
            
            # Add metric box
            rect = Rectangle((x, y), box_size, box_size, 
                            facecolor=color, alpha=0.8, 
                            edgecolor='white', linewidth=2,
                            transform=ax.transAxes)
            ax.add_patch(rect)
            
            # Add metric name
            ax.text(x + box_size/2, y + box_size - 0.08, name, 
                ha='center', va='center', fontsize=12, 
                color='white', fontweight='bold', transform=ax.transAxes)
            
            # Add metric value
            ax.text(x + box_size/2, y + box_size/2 - 0.02, value, 
                ha='center', va='center', fontsize=16, 
                color='white', fontweight='bold', transform=ax.transAxes)
        
        # Add additional info
        ax.text(0.05, 0.05, 
            f"Evaluation Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Period: {self.dates[0]} to {self.dates[-1]}\n"
            f"Trading Days: {self.total_days}",
            fontsize=12, ha='left', va='bottom', transform=ax.transAxes)

    def _plot_monthly_returns(self, ax):
        """Plot monthly returns heatmap on specified axis"""
        # Create DataFrame of dates and returns
        dates = [datetime.strptime(d, '%Y.%m.%d') for d in self.dates]
        monthly_data = []
        
        for date, return_val in zip(dates, self.returns):
            year = date.year
            month = date.month
            monthly_data.append([year, month, return_val])
        
        # Create DataFrame
        import pandas as pd
        df = pd.DataFrame(monthly_data, columns=['Year', 'Month', 'Return'])
        
        # Create pivot table
        pivot_table = df.pivot_table(index='Year', columns='Month', values='Return', aggfunc='mean')
        
        # Order by month
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        pivot_table = pivot_table.reindex(columns=range(1, 13))
        
        # Create custom colormap
        from matplotlib.colors import LinearSegmentedColormap
        cmap = LinearSegmentedColormap.from_list('custom', ['#d62728', 'lightgray', '#2ca02c'], N=256)
        
        # Plot heatmap
        sns.heatmap(pivot_table, annot=True, fmt=".2%", cmap=cmap, 
                center=0, linewidths=0.5, cbar_kws={'label': 'Return', 'format': PercentFormatter(1.0)},
                annot_kws={"size": 9}, ax=ax)
        
        # Set title and labels
        ax.set_title('Monthly Returns Heatmap', fontsize=16)
        ax.set_xlabel('Month', fontsize=12)
        ax.set_ylabel('Year', fontsize=12)
        
        # Set month labels
        ax.set_xticks(np.arange(12) + 0.5)
        ax.set_xticklabels(month_names, rotation=0)
        
        # Adjust colorbar labels
        cbar = ax.collections[0].colorbar
        cbar.ax.tick_params(labelsize=10)
        cbar.set_label('Return', fontsize=12)

class Direction(Enum):
    Long = 1
    Short = 2

class Side(Enum):
    Buy = 1
    Sell = 2
    Unknown = 3

class Offset(Enum):
    Open = 1
    Close = 2
    Unknown = 3

class TradeData:
    def __init__(self):
        self.datetime:str = ""
        self.instrument_id : str = ""
        self.price : float = 0.0
        self.side : Side = Side.Unknown
        self.commission : float = 0.0
        self.volume : int = 0
        self.trade_id : int = 0 
        self.offset : Offset = Offset.Unknown
        


class PositionData:
    def __init__(self):
        self.instrument_id : str = ""
        self.direction : Direction ={}
        self.volume : int = 0
        self.close_price : float = 0.0
        self.settlement_price : float = 0.0
        self.position_pnl : float = 0.0
        self.close_pnl : float = 0.0
        self.realized_pnl : float = 0.0
        self.unrealized_pnl : float = 0.0
        self.totalCount : int = 0
        self.winCount : int = 0 
        self.close_price : float = 0.0
        self.contract_multiplier : float = 0.0
        self.avg_open_price : float = 0.0

class FutureMethod:
    def __init__(self, trade_dates, dailyData, dailyDataLastSnap : dict, trade_csv : str, position_csv : str, init_cash : float, start : str = "", end : str = ""
                 , outpath = "", free_ratio = 0.0):
        self.dailyData = dailyData
        self.dailyDataLastSnap = dailyDataLastSnap
        self.outpath = outpath
        self.free_ratio = free_ratio
        # 多头持仓
        self.long_position : Direction[str,PositionData] = {}
        # 空头持仓
        self.short_position : Direction[str,PositionData] = {}
        # 成交列表
        self.trades : Direction[str, list[TradeData]] = {}
        # 交易日序列
        #self.trade_dates = []
        self.trade_dates = trade_dates
        # 合约乘数
        self.contract_multipliers = {}
        # 成交csv
        self.trade_csv = trade_csv
        # 持仓csv
        self.position_csv = position_csv
        # 净值
        self.netValue = {}
        # 价格信息
        self.price_cache = dailyData
        self.start_date =start
        self.end_date = end
        #self.trade_dates = []
        self.total_win = 0
        self.total_count = 0
        self.win_ratio = 0.0
        self.init_cash = init_cash
        # 净值数据
        self.net_value = {}
        
    def handle_date(self):
        self.ini_data()
        if not self.net_value:
            print("\n警告: 净值数据为空，跳过绩效计算")
            return
    
        pm = PerformanceMetrics(self.net_value,  self.init_cash, self.outpath, self.win_ratio, self.free_ratio)
        # 计算并打印各项指标
        print(f"累计收益率: {pm.cum_ret:.8f} ({pm.cum_ret*100:.8f}%)")
        print(f"年化收益率: {pm.ann_ret:.8f} ({pm.ann_ret*100:.8f}%)")
        print(f"年化波动率: {pm.ann_vol:.8f} ({pm.ann_vol*100:.8f}%)")
        print(f"夏普比率: {pm.sharpe:.8f}")
        print(f"最大回撤: {pm.max_dd_value:.8f} ({pm.max_dd_value*100:.8f}%)")
        
        # 获取最大回撤时间段
        max_dd_start, max_dd_end = pm.max_drawdown_period()
        print(f"最大回撤时间段: {max_dd_start} 至 {max_dd_end}")
        
        print(f"卡玛比率: {pm.calmar:.4f}")
        print(f"索提诺比率: {pm.sortino:.4f}")
        print(f"胜率: {pm.win_rate:.8f} ({pm.win_rate*100:.8f}%)")
        
        
        # 绘制并保存所有图表汇总
        pm.plot_all_charts(save_path="test_performance.png")
        print("报告已保存至 test_performance.png")
       

    def ini_data(self) :
        # 加载成交数据
        if  self.trade_csv and os.path.exists(self.trade_csv):
            # 可以选择返回或者抛出异常
            self.read_trades_from_csv(self.trade_csv)
        if  self.position_csv and os.path.exists(self.position_csv):
            # 加载合约乘数
            self.int_contract_multipliers(self.position_csv)
        self.parse_datas()

    def update_unrealized(self, date):
        for key, value in self.long_position.items():
            close = self.fetch_close_price(key, date)
            if close != 0.0:
                value.close_price = close
            self.intelupdate_unrealized(value)
            #net += (value.realized_pnl + value.unrealized_pnl)
        for key, value in self.short_position.items():
            close = self.fetch_close_price(key, date)
            if close != 0.0:
                value.close_price = close
            self.intelupdate_unrealized(value)
            #net += (value.realized_pnl + value.unrealized_pnl)
        

    def parse_datas(self):
        for time in self.trade_dates:
            if time not in self.trades:
                self.update_unrealized(time)
            else:
                for trade in self.trades[time]:
                    self.apply_trade(trade)
            self.update_daily_netvalue(time)

    def update_daily_netvalue(self, date : str):
        self.total_win = 0
        self.total_count = 0
        net = self.init_cash
        for key, value in self.long_position.items():
            net += (value.realized_pnl + value.unrealized_pnl)
            self.total_win += value.winCount
            self.total_count += value.totalCount
        for key, value in self.short_position.items():
            net += (value.realized_pnl + value.unrealized_pnl)
            self.total_win += value.winCount
            self.total_count += value.totalCount
        
        self.net_value[date] = net

        winratio = 0.0
        if self.total_count != 0:
            self.win_ratio = self.total_win / self.total_count
        #print(f"date:{date} net:{net} total_count:{self.total_count} total_win:{self.total_win} winratio:{self.win_ratio}")

    def read_trades_from_csv(self, file_path):
        templist = []
        # 指定编码为 utf-8-sig 以处理可能的 BOM 头
        with open(file_path, 'r', newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                trade = TradeData()
                trade.datetime = row['datetime']  # 移除可能的 \ufeff 前缀
                trade.instrument_id = row['order_book_id']
                trade.price = float(row['last_price'])
                if row['side'] == "BUY" or row['side'] == "Buy":
                    trade.side = Side.Buy
                elif row['side'] == "SELL" or row['side'] == "Sell":
                    trade.side = Side.Sell
                trade.commission = float(row['commission'])
                trade.volume = int(row['last_quantity'])
                trade.trade_id = int(row['exec_id'])
                if row['position_effect'] == "Open" or row['position_effect'] == "OPEN":
                    trade.offset = Offset.Open
                elif row['position_effect'] == "Close" or row['position_effect'] == "CLOSE":
                    trade.offset = Offset.Close
                else :
                    trade.offset = Offset.Unknown
                #self.trades[trade.datetime].append(trade)
                self.trades.setdefault(trade.datetime, []).append(trade)
                templist.append(trade)
        if self.start_date == "" and len(templist) != 0:
            self.start_date = templist[0].datetime
        if self.end_date == "" and len(templist) != 0:
            self.end_date = templist[-1].datetime
    # def read_trades_from_csv(self, file_path):
    #     with open(file_path, 'r', newline='') as csvfile:
    #         reader = csv.DictReader(csvfile)
    #         for row in reader:
    #             trade = TradeData()
    #             trade.datetime = row['\ufeffdatetime']
    #             trade.instrument_id = row['order_book_id']
    #             trade.price = float(row['last_price'])
    #             trade.side = Side[row['side']]
    #             trade.commission = float(row['commission'])
    #             trade.volume = int(row['last_quantity'])
    #             trade.trade_id = int(row['exec_id'])
    #             trade.offset = Offset[row['position_effect']]
    #             #self.trades[trade.datetime].append(trade)
    #             self.trades.setdefault(trade.datetime, []).append(trade)

    def fetch_close_price(self, contract, new_date):
        """通过API获取合约在指定日期的收盘价"""

        #date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

        # 格式化为新的日期字符串
        #new_date = date_obj.strftime("%Y.%m.%d")
        cache_key = f"{contract}_{new_date}"
        if cache_key in self.price_cache:
            return self.price_cache[cache_key]
        else:
            if contract in self.dailyDataLastSnap:
                return self.dailyDataLastSnap[contract]
            else:
                print("无法获取合约收盘价格")
                return 0.0

        # time.sleep(self.api_delay)  # 避免频繁调用API
        
        # try:
        #     # 调用API获取历史数据
        #     history_data = self.api.get_history_bars_by_period(
        #         instrument_id=contract,
        #         start_date=new_date,
        #         end_date=new_date,
        #         frequency='1d'
        #     )
            
        #     if not history_data.empty:
        #         # 提取收盘价（假设API返回数据包含close_price列）
        #         price = history_data['close_price'].iloc[0]
        #         self.price_cache[cache_key] = price
        #         return price
        #     else:
        #         print(f"无合约 {contract} 在 {new_date} 的收盘价数据")
        #         return 0.0
        # except Exception as e:
        #     print(f"获取收盘价失败 - 合约: {contract}, 日期: {new_date}, 错误: {str(e)}")
        #     return 0.0
    def int_contract_multipliers(self, csv_path):
        """
        从CSV文件中读取合约ID和对应的合约乘数，每个合约仅保留第一次出现的值
        
        参数:
        - csv_path: CSV文件路径
        
        返回:
        - 字典，格式为 {order_book_id: contract_multiple}
        """
        try:
        
            # 读取CSV文件
            df = pd.read_csv(csv_path)
            
            # 检查必要的列是否存在
            required_columns = ['date', 'order_book_id', 'contract_multiple']
            for col in required_columns:
                if col not in df.columns:
                    raise ValueError(f"CSV文件中缺少必要的列: {col}")
            
            # 按日期升序排序（确保先处理较早的日期）
            df = df.sort_values(by='date')
            
            # 每个合约只保留第一次出现的记录
            df_unique = df.drop_duplicates(subset='order_book_id', keep='first')
            
            # 提取合约乘数
            self.contract_multipliers = df_unique.set_index('order_book_id')['contract_multiple'].to_dict()
            
            print(f"成功加载 {len(self.contract_multipliers)} 个合约的乘数信息")
        except Exception as e:
            print(f"无持仓数据，无法计算指标")
            return 0.0
    def get_direction(self, side : Side, offset : Offset):
        if side == Side.Buy and offset == Offset.Open :
            return Direction.Long
        
        if (side == Side.Sell and offset == Offset.Close):
            return Direction.Long
        
        if (side == Side.Sell and offset == Offset.Open) :
            return Direction.Short
        
        if (side == Side.Buy and (offset == Offset.Close)) :
            return Direction.Short
        
    def get_position(self, instrument : str, direction : Direction):
        if direction == Direction.Long:
            if instrument not in self.long_position:
                return PositionData()
            else :
                return self.long_position[instrument]
        else:
            if instrument not in self.short_position:
                return PositionData()
            else :
                return self.short_position[instrument]

    def apply_quote(self, position : PositionData):
        pass 

    def apply_trade(self, trade : TradeData):
        direction = self.get_direction(trade.side, trade.offset)
        position = self.get_position(trade.instrument_id, direction)
        position.totalCount += 1

        close = self.fetch_close_price(trade.instrument_id, trade.datetime)
        if close != 0.0:
            position.close_price = self.fetch_close_price(trade.instrument_id, trade.datetime)
        position.contract_multiplier = self.contract_multipliers[trade.instrument_id]

        if trade.offset == Offset.Open:
            self.apply_open(position, trade)
        else :
            self.apply_close(position, trade)
        
        if direction == Direction.Long:
            position.direction = Direction.Long
            self.long_position[trade.instrument_id] = position
        else:
            position.direction = Direction.Short
            self.short_position[trade.instrument_id] = position
        
    def intelupdate_unrealized(self, position: PositionData):
        multiplier = position.contract_multiplier * ( 1 if position.direction == Direction.Long else  -1)
        price_diff = position.close_price - position.avg_open_price
        # 浮动盈亏
        position.unrealized_pnl = (price_diff * position.volume) * multiplier

        
    def apply_open(self, position : PositionData, trade : TradeData):
        position.avg_open_price = (position.avg_open_price * position.volume + trade.price * trade.volume) /(position.volume + trade.volume)
        position.volume += trade.volume
        # 扣除手续费
        position.realized_pnl -= trade.commission
        multiplier = position.contract_multiplier * ( 1 if position.direction == Direction.Long else  -1)
        price_diff = position.close_price - position.avg_open_price
        # 浮动盈亏
        position.unrealized_pnl = (price_diff * position.volume) * multiplier
         
    def apply_close(self, position : PositionData, trade : TradeData):

        position.volume -= trade.volume
        # 扣除手续费
        position.realized_pnl -= trade.commission

        # 更新胜率次数
        if trade.side == Side.Sell and trade.price > position.avg_open_price :
            position.winCount += 1
        elif trade.side == Side.Buy and trade.price < position.avg_open_price:
            position.winCount += 1
        
        # 更新实现盈亏
        realized_pnl = (trade.price - position.avg_open_price) * trade.volume * position.contract_multiplier
        if (position.direction == Direction.Short):
            realized_pnl = -realized_pnl
        
        position.realized_pnl += realized_pnl
        
        multiplier = position.contract_multiplier * ( 1 if position.direction == Direction.Long else  -1)
        price_diff = position.close_price - position.avg_open_price
        # 浮动盈亏
        position.unrealized_pnl = (price_diff * position.volume) * multiplier




