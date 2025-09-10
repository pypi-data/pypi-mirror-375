"""
计算各类成交、持仓指标
"""

import yaml
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt



class ComputeIndex:

    def __init__(self):
        self.config = None  # config配置文件路径
        self.result_path = None  # 结果文件路径
        self.is_prompt = 1  # 是否将结果图片弹窗, 默认显示
        self.begin_period = None  # 期初权益
        self.yield_day_count = None  # 回测时间（总共有多少个交易日）
        self.yield_rate = None  # 回测收益率
        self.annual_yield_rate = None  # 年化收益率
        self.max_drawdown = None  # 最大回撤
        self.max_drawdown_date = None  # 最大回撤发生日期
        self.peak_date = None  # 最大回撤前高点日期
        self.peak_to_trough_days = None  # 最大回撤形成时长(交易日)
        self.recovery_date = None  # 回归前高日期
        self.recovery_days = None  # 回归时长(交易日)
        self.annualized_sharpe_ratio = None  # 夏普比率(年化)
        self.daily_sharpe_ratio = None  # 夏普比率(每日)
        self.calmar_ratio = None  # 卡玛比率
        self.annual_volatility = None  # 年化波动率

        self.longest_drawdown_days = None  # 最长回撤持续天数
        self.longest_drawdown_start = None  # 最长回撤开始日期
        self.longest_drawdown_end = None  # 最长回撤结束日期

        # # 设置matplotlib支持中文显示 - macOS系统兼容版本
        # plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # macOS系统默认支持的中文字体
        # plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

        # # 设置matplotlib支持中文显示 - 服务器兼容版本
        plt.rcParams['font.family'] = 'sans-serif'  # 设置全局字体
        # plt.rcParams['font.sans-serif'] = ['Noto Sans CJK JP']  # 添加多个字体选项，按顺序尝试
        plt.rcParams['font.sans-serif'] = ['SimSun']  # 添加多个字体选项，按顺序尝试
        plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

    # 读取yaml文件
    @staticmethod
    def read_yaml_file(filepath):
        """读取 YAML 文件"""
        with open(filepath, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)

    def _init_matplot(self):
        if self.is_prompt == 1:
            matplotlib.use('TkAgg')
        else:
            matplotlib.use('Agg')
        

    @staticmethod
    def read_csv_file(file_path):
        """
        读取csv文件
        :return:
        """
        # file_dir = os.listdir(file_path)
        #
        # # 筛选持仓数据文件
        # file_list = [file for file in file_dir if file.endswith('positions.csv')]
        # return file_list
        try:
            data = pd.DataFrame(pd.read_csv(file_path))
        except Exception as e:
            data = pd.DataFrame()
        return data


    def compute_begin_period(self, config_path):
        """
        计算期初权益（直接从config.yaml文件获取）
        """
        config_data = self.read_yaml_file(config_path)
        env_config = config_data.get("base", {})
        begin_period = env_config.get("accounts")
        return begin_period


    @staticmethod
    def compute_current_day_equity(data, begin_period):
        """
        计算当天权益
        当天权益 = 昨权益 + 今天实现盈亏(realized_pnl) + 今天未实现盈亏(unrealized_pnl)

        :return:
        """

        # 按交易日分组，计算每日总盈亏
        daily_pnl = data.groupby(["trading_day"]).sum()[["realized_pnl", "unrealized_pnl"]].reset_index()

        # 计算每日总盈亏
        daily_pnl['daily_total'] = daily_pnl['realized_pnl'] + daily_pnl['unrealized_pnl']

        # 计算累计权益 (从期初权益开始累加)
        daily_pnl['equity'] = begin_period + daily_pnl['daily_total'].cumsum()

        # 计算昨权益
        daily_pnl['yesterday_equity'] = daily_pnl['equity'].shift(1).fillna(begin_period)

        # 合并回原始数据
        result = data.merge(daily_pnl[['trading_day', 'equity', 'yesterday_equity']],
                            on='trading_day', how='left')

        return result


    def compute_current_day_yield_rate(self, data):
        """
        计算当天收益率
        当天收益率 = (当天权益 - 昨权益) / 期初权益

        :return:
        """
        data['yield_rate'] = (data['equity'] - data['yesterday_equity']) / self.begin_period

        return data

    def compute_yield_rate(self, data):
        """
        计算回测收益率
        回测收益率 = (回测最后交易日的当天权益 - 期初权益) / 期初权益
        :param data:
        :return:
        """
        # 回测最后交易日的当天权益
        end_equity = data['equity'].iloc[-1]
        self.yield_rate = (end_equity - self.begin_period) / self.begin_period
        # print("回测收益率: ", self.yield_rate)

        return data

    # 计算年华收益率
    def compute_annual_yield_rate(self, file_path):
        """
        计算年华收益率
        年化收益率 = (回测收益率 / 回测时间) * 252
        :return:
        """
        data = self.read_csv_file(file_path)
        yield_day_count = data.shape[0]
        # print("回测天数: ", yield_day_count)

        self.annual_yield_rate = (self.yield_rate / yield_day_count) * 252
        # print("年化收益率: ", self.annual_yield_rate)


    def compute_drawdown(self, data):
        """
        计算最大回撤
        最大回撤是衡量策略风险的重要指标，计算方法是在回测期内，任一交易日净值相对于之前最高点净值的最大跌幅

        计算公式：
        Drawdown_t = 0                                  if NET_t = min_{j≤t}NET_j
                     (NET_t - min_{j≤t}NET_j) / NET_t   else

        MaxDrawdown = max(Drawdown_t)

        :param data: 包含权益数据的DataFrame
        :return: 添加了回撤列的DataFrame和最大回撤值
        """
        # 按交易日分组，获取每日的权益数据
        daily_equity = data.groupby('trading_day')['equity'].first().reset_index()

        # 计算截至当前日期的最高权益
        daily_equity['max_equity'] = daily_equity['equity'].cummax()

        # 计算每日回撤
        daily_equity['drawdown'] = (daily_equity['max_equity'] - daily_equity['equity']) / daily_equity['max_equity']

        # 计算最大回撤
        self.max_drawdown = daily_equity['drawdown'].max()

        # 记录最大回撤发生的时间
        self.max_drawdown_date = daily_equity.loc[daily_equity['drawdown'] == self.max_drawdown, 'trading_day'].iloc[0]

        # 找到最大回撤前的最高点日期
        max_equity_before_drawdown = daily_equity.loc[daily_equity['trading_day'] <= self.max_drawdown_date]
        self.peak_date = max_equity_before_drawdown.loc[max_equity_before_drawdown['equity'] ==
                                                   max_equity_before_drawdown['max_equity'].max(), 'trading_day'].iloc[
            0]

        # 计算从最高点到最大回撤点的时间跨度（交易日数量）
        self.peak_to_trough_days = daily_equity[
                                  (daily_equity['trading_day'] >= self.peak_date) &
                                  (daily_equity['trading_day'] <= self.max_drawdown_date)
                                  ].shape[0] - 1  # 减1是因为不包括起始日

        # 查找最大回撤后回归到前高的日期
        recovery_data = daily_equity[daily_equity['trading_day'] > self.max_drawdown_date]
        recovery_date = None
        recovery_days = None

        if not recovery_data.empty:
            # 获取最大回撤时的最高权益值
            peak_equity = daily_equity.loc[daily_equity['trading_day'] == self.peak_date, 'equity'].iloc[0]

            # 查找回归到前高的日期
            recovery_dates = recovery_data[recovery_data['equity'] >= peak_equity]['trading_day']

            if not recovery_dates.empty:
                recovery_date = recovery_dates.iloc[0]
                # 计算从最大回撤到恢复的时间（交易日数量）
                recovery_days = daily_equity[
                                    (daily_equity['trading_day'] >= self.max_drawdown_date) &
                                    (daily_equity['trading_day'] <= recovery_date)
                                    ].shape[0] - 1  # 减1是因为不包括起始日

        # 将回撤数据合并回原始数据
        result = data.merge(daily_equity[['trading_day', 'drawdown']], on='trading_day', how='left')

        # 打印最大回撤相关信息
        # print(f"最大回撤: {self.max_drawdown:.4f}")
        # print(f"最大回撤发生日期: {self.max_drawdown_date}")
        # print(f"最大回撤前高点日期: {self.peak_date}")
        # print(f"最大回撤前高时间跨度(交易日天数): {self.peak_to_trough_days}")

        # if recovery_date is not None:
        #     print(f"回归前高日期: {recovery_date}")
        #     print(f"回归时长(交易日): {recovery_days}")
        # else:
        #     print("截至回测结束，尚未回归到前高")

        # 创建最大回撤信息字典
        drawdown_info = {
            'max_drawdown': self.max_drawdown,
            'max_drawdown_date': self.max_drawdown_date,
            'peak_date': self.peak_date,
            'peak_to_trough_days': self.peak_to_trough_days,
            'recovery_date': recovery_date,
            'recovery_days': recovery_days
        }

        return result, drawdown_info

    def compute_longest_drawdown_period(self, data):
        """
        计算最长回撤持续周期
        最长回撤持续周期是指从策略净值达到高点开始下跌，直到恢复到该高点所经历的最长时间段

        :param data: 包含权益数据的DataFrame
        :return: 最长回撤持续周期的信息字典
        """
        # 按交易日分组，获取每日的权益数据
        daily_equity = data.groupby('trading_day')['equity'].first().reset_index()

        # 初始化变量
        longest_period = 0
        longest_start = None
        longest_end = None
        longest_recovery = None

        # 遍历每个可能的高点
        for i in range(len(daily_equity) - 1):
            current_peak = daily_equity['equity'].iloc[i]
            current_peak_date = daily_equity['trading_day'].iloc[i]

            # 查找后续的低点和恢复点
            for j in range(i + 1, len(daily_equity)):
                # 如果找到一个新的高点，说明已经恢复并超过了之前的高点
                if daily_equity['equity'].iloc[j] >= current_peak:
                    recovery_date = daily_equity['trading_day'].iloc[j]
                    period_length = j - i

                    # 如果这个回撤持续周期比之前记录的更长，则更新记录
                    if period_length > longest_period:
                        longest_period = period_length
                        longest_start = current_peak_date
                        longest_recovery = recovery_date

                        # 找出这段时间内的最低点作为回撤底部
                        trough_idx = daily_equity['equity'].iloc[i:j + 1].idxmin()
                        longest_end = daily_equity['trading_day'].iloc[trough_idx - i]

                    break

        # 如果没有找到恢复点，说明截至回测结束，尚未从某些回撤中恢复
        # 这种情况下，我们可以考虑将最后一个交易日作为临时的恢复点
        if longest_period == 0 and len(daily_equity) > 1:
            # 找出整个回测期间的最高点
            peak_idx = daily_equity['equity'].idxmax()
            peak_date = daily_equity['trading_day'].iloc[peak_idx]
            peak_value = daily_equity['equity'].iloc[peak_idx]

            # 如果最高点不是最后一个交易日，且之后没有恢复到这个高点
            if peak_idx < len(daily_equity) - 1:
                longest_period = len(daily_equity) - 1 - peak_idx
                longest_start = peak_date
                longest_recovery = "未恢复"

                # 找出这段时间内的最低点作为回撤底部
                trough_idx = daily_equity['equity'].iloc[peak_idx:].idxmin()
                longest_end = daily_equity['trading_day'].iloc[trough_idx - peak_idx]

        # 保存最长回撤持续周期信息
        self.longest_drawdown_days = longest_period
        self.longest_drawdown_start = longest_start
        self.longest_drawdown_end = longest_end

        # 打印最长回撤持续周期相关信息
        # print(f"最长回撤持续天数: {self.longest_drawdown_days}")
        # print(f"最长回撤开始日期: {self.longest_drawdown_start}")
        # print(f"最长回撤最低点日期: {self.longest_drawdown_end}")
        # print(f"最长回撤恢复日期: {longest_recovery if longest_recovery != '未恢复' else '截至回测结束，尚未恢复'}")

        # 创建最长回撤持续周期信息字典
        longest_drawdown_info = {
            'longest_drawdown_days': self.longest_drawdown_days,
            'longest_drawdown_start': self.longest_drawdown_start,
            'longest_drawdown_end': self.longest_drawdown_end,
            'longest_drawdown_recovery': longest_recovery
        }

        return longest_drawdown_info


    def compute_sharpe_ratio(self, data, risk_free_rate=0.0, annualize_factor=252):
        """
        计算夏普比率
        夏普比率衡量超额收益与风险的比值，是策略风险调整后收益的重要指标

        计算公式：
        DailySharpeRatio = r_e / σ_e

        其中：
        r_e = (1/n) * Σ[r_p(i) - r_f(i)]  # 平均超额收益
        σ_e = sqrt[(1/(n-1)) * Σ[(r_p(i) - r_f(i) - r_e)??]]  # 超额收益的标准差

        年化夏普比率 = sqrt(252) * DailySharpeRatio

        :param data: 包含收益率数据的DataFrame
        :param risk_free_rate: 无风险利率，默认为0
        :param annualize_factor: 年化因子，默认为252（交易日）
        :return: 夏普比率
        """
        # 按交易日分组，获取每日的收益率数据
        daily_returns = data.groupby('trading_day')['yield_rate'].first().reset_index()

        # 计算每日超额收益（收益率减去无风险利率）
        # 这里假设risk_free_rate是年化的，需要转换为日收益率
        daily_risk_free_rate = risk_free_rate / 252  # 假设一年有252个交易日
        # daily_risk_free_rate = risk_free_rate
        daily_returns['excess_return'] = daily_returns['yield_rate'] - daily_risk_free_rate

        # 计算平均超额收益
        mean_excess_return = daily_returns['excess_return'].mean()

        # 计算超额收益的标准差
        std_excess_return = daily_returns['excess_return'].std(ddof=1)

        # 计算日夏普比率
        if std_excess_return == 0:
            self.daily_sharpe_ratio = 0  # 避免除以零
        else:
            self.daily_sharpe_ratio = mean_excess_return / std_excess_return

        # 计算年化夏普比率
        self.annualized_sharpe_ratio = self.daily_sharpe_ratio * (annualize_factor ** 0.5)  # sqrt(252)

        # print(f"日夏普比率: {self.daily_sharpe_ratio:.4f}")
        # print(f"年化夏普比率: {self.annualized_sharpe_ratio:.4f}")

        return self.annualized_sharpe_ratio

    def compute_calmar_ratio(self):
        """
        计算卡玛比率(Calmar Ratio)
        卡玛比率是年化收益率与历史最大回撤之间的比率，用于衡量单位最大回撤风险下的收益能力

        计算公式：
        Calmar Ratio = 年化收益率 / 最大回撤

        :return: 卡玛比率
        """
        # 检查最大回撤是否为0，避免除以0的错误
        if self.max_drawdown == 0 or self.max_drawdown is None:
            # print("最大回撤为0或未计算，无法计算卡玛比率")
            return 0

        # 计算卡玛比率
        self.calmar_ratio = self.annual_yield_rate / self.max_drawdown

        # print(f"卡玛比率: {self.calmar_ratio:.4f}")

        return self.calmar_ratio


    def compute_volatility(self, data):
        """
        计算年化波动率
        年化波动率是策略收益率的标准差，是最常用的风险度量，波动率越大，策略承担的风险越高

        计算公式：
        σ = sqrt(252 * Σ[(r_p(i) - r_p)??] / (n-1))

        其中：
        - n为回测期内交易日数目
        - r_p(i)表示第i个交易日策略所持投资组合的日收益率
        - r_p为回测期内策略日收益率的均值
        - 252为一年的交易日数量（用于年化）

        :param data: 包含收益率数据的DataFrame
        :return: 年化波动率
        """
        # 按交易日分组，获取每日的收益率数据
        daily_returns = data.groupby('trading_day')['yield_rate'].first().reset_index()

        # 计算日收益率的标准差
        daily_std = daily_returns['yield_rate'].std(ddof=1)  # ddof=1使用样本标准差

        # 计算年化波动率
        self.annual_volatility = daily_std * (252 ** 0.5)  # sqrt(252)

        # print(f"日波动率: {daily_std:.4f}")
        # print(f"年化波动率: {self.annual_volatility:.4f}")

        return self.annual_volatility

    def visualize_equity_curve(self, data):
        """
        可视化收益率曲线，并在图表上方显示指标数据
        横坐标：对应的交易日
        纵坐标：（当前交易日的总权益 - 期初权益）/期初权益
        """

        # 按交易日分组，获取每日的权益数据
        daily_equity = data.groupby('trading_day')['equity'].first().reset_index()
        daily_equity['return_rate'] = (daily_equity['equity'] - self.begin_period) / self.begin_period

        # 创建图表并调整布局
        fig, ax = plt.subplots(figsize=(12, 7))
        plt.subplots_adjust(top=0.78, bottom=0.15)  # 调整顶部边距，为回撤时间信息留出空间

        # 绘制收益率曲线
        ax.plot(range(len(daily_equity)), daily_equity['return_rate'], 'r-', label='收益率')

        # 标记最大回撤点（最低点）
        max_drawdown_idx = daily_equity['return_rate'].idxmin()
        max_drawdown_rate = daily_equity.loc[max_drawdown_idx, 'return_rate']
        ax.scatter(max_drawdown_idx, max_drawdown_rate, color='blue', s=100, marker='v', label='最大回撤点')

        # 标记前高点（最高点）
        peak_idx = daily_equity.loc[:max_drawdown_idx, 'return_rate'].idxmax()
        peak_rate = daily_equity.loc[peak_idx, 'return_rate']
        ax.scatter(peak_idx, peak_rate, color='green', s=100, marker='^', label='最大回撤前高点')

        # 设置x轴刻度和标签
        step = max(1, len(daily_equity) // 10)
        plt.xticks(
            range(0, len(daily_equity), step),
            daily_equity['trading_day'].iloc[::step],
            rotation=45
        )

        # 设置图表标签
        ax.set_xlabel('交易日', fontsize=12)
        ax.set_ylabel('收益率', fontsize=12)
        ax.grid(True)
        ax.legend(fontsize=10)

        # 格式化y轴为百分比
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: '{:.2%}'.format(y)))

        # 创建表格式的指标展示
        # 第一行指标
        row1_labels = ['策略收益率', '年化收益率', '最大回撤']
        row1_values = [f"{self.yield_rate:.2%}", f"{self.annual_yield_rate:.2%}", f"{self.max_drawdown:.2%}"]

        # 第二行指标
        row2_labels = ['夏普比率', '卡玛比率', '年化波动率']
        row2_values = [f"{self.daily_sharpe_ratio:.2f}", f"{self.calmar_ratio:.2f}", f"{self.annual_volatility:.2%}"]

        # 第三行指标 - 添加最大回撤时间范围信息
        row3_labels = ['最大回撤时间/最长回撤持续时间']
        row3_values = [f"MaxDD: {self.peak_date}-{self.max_drawdown_date}, {self.peak_to_trough_days}天",
                       f"MaxDDD: {self.longest_drawdown_start}-{self.longest_drawdown_end}, {self.longest_drawdown_days}天"]

        # 计算每列的宽度
        col_width = 0.33

        # 创建表格式布局
        for i in range(3):
            # 第一行标签和值
            plt.figtext(
                0.05 + i * col_width,  # x坐标
                0.95,  # 第一行y坐标
                row1_labels[i] + ":",
                ha='left',
                fontsize=14,
                weight='bold'
            )

            plt.figtext(
                0.05 + i * col_width + 0.12,  # x坐标（标签后面一点）
                0.95,  # 第一行y坐标
                row1_values[i],
                ha='left',
                fontsize=14,
                weight='bold',
                color='red' if i < 2 else 'black'  # 收益率相关指标用红色
            )

            # 第二行标签和值
            plt.figtext(
                0.05 + i * col_width,  # x坐标
                0.90,  # 第二行y坐标
                row2_labels[i] + ":",
                ha='left',
                fontsize=14,
                weight='bold'
            )

            plt.figtext(
                0.05 + i * col_width + 0.12,  # x坐标（标签后面一点）
                0.90,  # 第二行y坐标
                row2_values[i],
                ha='left',
                fontsize=14,
                weight='bold',
                color='black'
            )

        y_value3 = 0.85
        x_value3 = 0.03

        # 添加第三行 - 最大回撤时间范围信息（只在最大回撤列下方显示）
        plt.figtext(
            0.05 + 0 * col_width,  # 与最大回撤指标对齐
            y_value3,  # 位于第二行指标下方
            row3_labels[0] + ':',
            ha='left',
            fontsize=14,
            weight='bold'
        )
        for i in range(0, 2):
            plt.figtext(
                0.05 + 0 * col_width,  # 与最大回撤指标对齐
                y_value3 - x_value3,  # 位于标签下方
                row3_values[i],
                ha='left',
                fontsize=10,
                color='blue'  # 使用蓝色
            )
            x_value3 += 0.02

        # 保存和显示
        plt.savefig(self.result_path + '收益率.png', dpi=300, bbox_inches='tight')
        if self.is_prompt == 1:
            plt.show()
        
        # print("收益率曲线图已保存为 '收益率.png'")


    def compute_index(self, data, config_path, yield_file_path):
        """
        计算各类成交、持仓指标
        :return:
        """

        # 计算期初权益
        self.begin_period = self.compute_begin_period(config_path)

        # 计算当天权益
        data = self.compute_current_day_equity(data, self.begin_period)

        # 计算当天收益率
        data = self.compute_current_day_yield_rate(data)
        # print("当天收益率:\n", current_day_yield_rate[["trading_day", "instrument_id", "equity", "yesterday_equity"]].head(50))

        # 计算回测收益率
        self.compute_yield_rate(data)

        # 计算年化收益率
        self.compute_annual_yield_rate(yield_file_path)

        # self.compute_drawdown(current_day_yield_rate)
        # 计算最大回撤
        data, drawdown_info = self.compute_drawdown(data)
        # 将最大回撤信息添加为类属性
        self.max_drawdown = drawdown_info['max_drawdown']
        self.max_drawdown_date = drawdown_info['max_drawdown_date']
        self.peak_date = drawdown_info['peak_date']
        self.peak_to_trough_days = drawdown_info['peak_to_trough_days']
        self.recovery_date = drawdown_info['recovery_date']
        self.recovery_days = drawdown_info['recovery_days']

        # 计算最长回撤持续周期
        self.compute_longest_drawdown_period(data)


        # 计算夏普比率
        config_data = self.read_yaml_file(config_path)
        env_config = config_data.get("base", {})
        risk_free_rate = env_config.get("risk_free_rate")
        # self.calculate_sharpe_ratio(data["yield_rate"], risk_free_rate)
        self.compute_sharpe_ratio(data, risk_free_rate)

        # 计算卡玛比率
        self.calmar_ratio = self.compute_calmar_ratio()

        # 计算年华波动率
        self.compute_volatility(data)

        # 可视化权益曲线
        self.visualize_equity_curve(data)

        return data


    def run(self, config_path, position_file, yield_file_path, 
            result_path, is_prompt):
        self.result_path = result_path
        self.is_prompt = is_prompt

        self._init_matplot()

        # 读取持仓数据文件
        data = self.read_csv_file(position_file)
        if not data.empty:
            # 按交易日排序（方便后续计算）
            data = data.sort_values(by="trading_day")
            # print(data[["trading_day", "instrument_id", "realized_pnl", "unrealized_pnl"]])

            # 计算各类成交、持仓指标
            data = self.compute_index(data, config_path, yield_file_path)
            # print(data[["trading_day", "instrument_id", "equity", "yesterday_equity", "yield_rate"]])


# if __name__ == '__main__':
#     compute_index_obj = ComputeIndex()
#     compute_index_obj.run("config.yaml", "20250401_092406_min_1_positions.csv",
#                           "20250401_092406_min_1_daily_found_results.csv")



