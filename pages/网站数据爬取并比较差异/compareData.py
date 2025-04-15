# 数据对比
import pandas as pd
from datetime import date

from datetime import datetime, timedelta

# 获取当前日期和时间
today = datetime.now()

# 计算昨天的日期（当前日期减去 1 天）
yesterday = today - timedelta(days=1)

# 提取日期部分（去掉时间）
yesterday_date = yesterday.date()

yesterday_df = pd.read_csv(f'{yesterday_date}用户数据.csv')
today_df = pd.read_csv(f'{date.today()}用户数据.csv')

# 合并数据，方便对比
merged_df = pd.merge(yesterday_df, today_df, on='云手机ID', suffixes=('_yesterday', '_today'), how='outer')

# 获取所有需要对比的列名（假设第一个文件包含所有列）
columns_to_compare = [col for col in yesterday_df.columns if col != '云手机ID']

# 生成对比报告
comparison_report = []

for user_id, row in merged_df.iterrows():
    user_report = {'user_id': user_id, 'changes': {}}

    for col in columns_to_compare:
        yesterday_col = f"{col}_yesterday"
        today_col = f"{col}_today"

        # 处理缺失值
        yesterday_value = row[yesterday_col] if pd.notna(row[yesterday_col]) else "无数据"
        today_value = row[today_col] if pd.notna(row[today_col]) else "无数据"

        # 记录变化
        user_report['changes'][col] = {
            'yesterday': yesterday_value,
            'today': today_value,
            'changed': yesterday_value != today_value
        }

    comparison_report.append(user_report)

# 打印对比报告
for report in comparison_report:
    print(f"用户ID: {report['user_id']}")
    for field, data in report['changes'].items():
        status = "✅ 未变化" if not data['changed'] else "⚠️ 已变化"
        print(f"  字段: {field} | {status} | 昨天: {data['yesterday']} → 今天: {data['today']}")
    print("-" * 50)
