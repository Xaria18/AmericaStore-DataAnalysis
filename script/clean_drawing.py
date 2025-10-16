import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 读取 CSV
df = pd.read_csv('cleaned_data.csv',encoding='gbk')

# 把日期数据转换至日期类型
df['Order Date']=pd.to_datetime(df['Order Date'],format='%Y/%m/%d')
df['Ship Date']=pd.to_datetime(df['Ship Date'],format='%Y/%m/%d')

# 查看数据基本信息
# print(df.info())
# print(df.describe())

# 画图 - 根据每年每月的销售额和利润画图
df['Year']=df['Order Date'].dt.year
df['Month']=df['Order Date'].dt.month
df['Year-Month']=df['Order Date'].dt.to_period('M')

# 按每年每月计算销售额和利润
monthly_sale=df.groupby('Year-Month').agg({
    'Sales':'sum',
    'Profit':'sum'
}).reset_index()

# 将时期转为字符串类型方便后续绘图
monthly_sale['Year-Month']=monthly_sale['Year-Month'].astype(str)
# print(monthly_sale.head(10))


# 绘制双 Y轴图标
fig,ax1=plt.subplots(figsize=(14,8))
ax1.set_xlabel('年月')
ax1.set_ylabel('销售额',color='tab:blue',fontsize=12)
bars=ax1.bar(monthly_sale['Year-Month'],monthly_sale['Sales'],
             color='tab:blue',alpha=0.7,label='销售额')
ax1.tick_params(axis='y',labelcolor='tab:blue')
ax1.tick_params(axis='x',rotation=45)

ax2=ax1.twinx()
ax2.set_ylabel('利润',color='tab:red',fontsize=12)
line=ax2.plot(monthly_sale['Year-Month'],monthly_sale['Profit'],
              color='tab:red',marker='o',linewidth=2,label='利润')
ax2.tick_params(axis='y',labelcolor='tab:red')

# 添加标题和图例
plt.title('每年每月销售额和利润趋势',fontsize=16,fontweight='bold')

# 合并图例
lines1,labels1=ax1.get_legend_handles_labels()
lines2,labels2=ax2.get_legend_handles_labels()
ax1.legend(lines1+lines2,labels1+labels2,loc='upper left')
plt.tight_layout()
plt.show()

# 画图 - 按地区汇总销售额和利润
state_sale=df.groupby('State').agg({
    'Sales':'sum',
    'Profit':'sum'
}).reset_index()
# 选销售额前 20的州作为展示
top_30_states=state_sale.nlargest(30,'Sales')
# 创建双折线图
plt.figure(figsize=(14,8))
plt.plot(top_30_states['State'],top_30_states['Sales'],
         marker='o',linewidth=2,markersize=8,label='销售额',color='yellow')
plt.plot(top_30_states['State'],top_30_states['Profit'],
         marker='s',linewidth=2,markersize=8,label='利润',color='green')
plt.xlabel('州',fontsize=12)
plt.ylabel('金额',fontsize=12)
plt.title('销售前30的各州销售额及利润对比',fontsize=16,fontweight='bold')
plt.legend(fontsize=12)
plt.grid(True,alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# 画图 - 按种类汇总销售额和利润
subcaegory_sales=df.groupby('Sub-Category').agg({
    'Sales':'sum',
    'Profit':'sum'
}).reset_index()

fig,ax=plt.subplots(figsize=(14,10))
y_pos=np.arange(len(subcaegory_sales))
bar_height=0.35
bars_sales=ax.barh(y_pos-bar_height/2,subcaegory_sales['Sales'],
                   bar_height,label='销售额',color='turquoise',alpha=0.7)
bars_profit=ax.barh(y_pos+bar_height/2,subcaegory_sales['Profit'],
                    bar_height,label='利润',color='royalblue',alpha=0.7)
ax.set_yticks(y_pos)
ax.set_yticklabels(subcaegory_sales['Sub-Category'])
ax.set_xlabel('金额',fontsize=12)
ax.set_title('种类销售额和利润对比',fontsize=16,fontweight='bold')
ax.legend()
# 在条形图上添加数值标签
def add_value_label(bars):
    for bar in bars:
        width=bar.get_width()
        ax.text(width+width*0.01,bar.get_y()+bar.get_height()/2,
                f'{width:,.0f}',ha='left',va='center',fontsize=9)
add_value_label(bars_sales)
add_value_label(bars_profit)
plt.tight_layout()
plt.show()
