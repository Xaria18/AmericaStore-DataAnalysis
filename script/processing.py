import pandas as pd
import numpy as np

# 设置保存路径
out_dir="D:/AmericaStore-DataAnalysis/Python/processed_dir"

# 读取 CSV
df = pd.read_csv('cleaned_data.csv',encoding='gbk')

# 把折扣数据转化为小数类型
df['Discount'] = df['Discount'].str.rstrip('%').astype('float') / 100.0

# 把日期数据转换至日期类型
df['Order Date']=pd.to_datetime(df['Order Date'],format='%Y/%m/%d')
df['Ship Date']=pd.to_datetime(df['Ship Date'],format='%Y/%m/%d')

# 提取时间
df['YearMonth']=df['Order Date'].dt.to_period('M').astype(str)
df['Year']=df['Order Date'].dt.year
df['Month']=df['Order Date'].dt.month

# ①为 分析销售与利润趋势 做准备
trend_df=(
    df.groupby('YearMonth').agg({
        'Sales':'sum',
        'Profit':'sum',
        'Discount':'mean'
    }).reset_index()
)
trend_df['Profit Margin']=trend_df['Profit']/trend_df['Sales']
trend_df['Sales Growth']=trend_df['Sales'].pct_change()
trend_df['Profit Growth']=trend_df['Profit'].pct_change()

trend_df.to_csv(out_dir+"/sales_trend.csv",index=False)

# ②为 客户分析（RFM） 做准备
latest_date=df['Order Date'].max()

recency=df.groupby('Customer ID')['Order Date'].max().reset_index()
recency['Recency']=(latest_date-recency['Order Date']).dt.days

frequency = (
    df.groupby('Customer ID')['Order ID']
    .nunique()
    .reset_index()
    .rename(columns={'Order ID':'Frequency'})
)
monetary = (
    df.groupby('Customer ID')['Sales']
    .sum()
    .reset_index()
    .rename(columns={'Sales':'Monetary'})
)

rfm = recency.merge(frequency, on='Customer ID').merge(monetary, on='Customer ID')

# 评分
rfm['R_Score']=pd.qcut(rfm['Recency'],5,labels=[5,4,3,2,1])
rfm['F_Score']=pd.qcut(rfm['Frequency'].rank(method='first'),5,labels=[1,2,3,4,5])
rfm['M_Score']=pd.qcut(rfm['Monetary'],5,labels=[1,2,3,4,5])

rfm['RFM_Score']=rfm[['R_Score','F_Score','M_Score']].astype(int).sum(axis=1)

def rank(score):
    if score>=13:return 'VIP'
    elif score>=9:return 'Loyal'
    elif score>=6:return 'Potential'
    else:return 'Risk'
rfm['Rank']=rfm['RFM_Score'].apply(rank)

rfm.to_csv(out_dir+"/customer_rfm.csv",index=False)

# ③为 产品分析 做准备
product_df=(
    df.groupby(['Category','Sub-Category','Product Name']).agg({
        'Sales':'sum',
        'Profit':'sum',
        'Quantity':'sum',
        'Discount':'mean'
    }).reset_index()
)
product_df['Profit Margin']=product_df['Profit']/product_df['Sales']
total_sales=product_df['Sales'].sum()
product_df['Sales Share']=product_df['Sales']/total_sales

# 排名与分类
product_df['Sales Rank']=product_df['Sales'].rank(ascending=False)
product_df['Profit Rank']=product_df['Profit'].rank(ascending=False)

def classify(row):
    if row['Sales Rank']<=10 and row['Profit Rank']<=10:return 'Start Product'
    elif row['Sales Rank']<=10:return 'High Sales But Low Profit'
    elif row['Profit Rank']<10:return 'Low Sales But High Profit'
    else:return 'Problem Product'
product_df['Product Type']=product_df.apply(classify,axis=1)

product_df.to_csv(out_dir+"/product_performance.csv",index=False)

# ④为 地区分析 做准备
region_df=(
    df.groupby(['Region','State']).agg({
        'Sales':'sum',
        'Profit':'sum',
        'Quantity':'sum',
        'Discount':'mean'
    }).reset_index()
)
region_df['Profit Margin']=region_df['Profit']/region_df['Sales']
region_df['Order Count']=df.groupby(['Region','State'])['Order ID'].nunique().values

region_df.to_csv(out_dir+"/region_performance.csv",index=False)

# ⑤为 运输方式分析 做准备
df['Shipping Days']=(df['Ship Date']-df['Order Date']).dt.days

shipMode_df=(
    df.groupby('Ship Mode').agg({
        'Sales':'sum',
        'Profit':'sum',
        'Discount':'mean',
        'Order ID':'nunique',
        'Shipping Days':'mean'
    }).reset_index()
)
shipMode_df.rename(columns={'Order ID':'Order Count'},inplace=True)
shipMode_df['Profit Margin']=shipMode_df['Profit']/shipMode_df['Sales']
shipMode_df['Profit Per Order']=shipMode_df['Profit']/shipMode_df['Order Count']

shipMode_df.to_csv(out_dir+"/shipMode_Analysis.csv",index=False)
