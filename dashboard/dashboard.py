import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
import urllib

st.title('E-Commerce Public Data Analysis')
sns.set(style='dark')

def create_sales_per_month(df):
    timeseries = df[df['order_status'] == 'delivered']
    timeseries = timeseries.resample(rule='D', on = 'order_approved_at').agg({
        'order_id' : 'nunique',
        'payment_value' : 'sum'
    })

    timeseries = timeseries.reset_index()
    timeseries.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)

    timeseries['year_month'] = timeseries['order_approved_at'].dt.to_period('M')
    return timeseries


def create_top_product(df):
    top_products = df.groupby("product_category_name_english")["payment_value"].sum().reset_index()
    top_products = top_products.rename(columns={"payment_value": "total_sales"})
    top_products = top_products.sort_values(by="total_sales", ascending=False)
    return top_products

def create_rating_product(df):
    average_scores = df.groupby("delivered_on_time")["review_score"].mean().reset_index()
    return average_scores

def plot_brazil_map(data):
    brazil = mpimg.imread(urllib.request.urlopen('https://i.pinimg.com/originals/3a/0c/e1/3a0ce18b3c842748c255bc0aa445ad41.jpg'),'jpg')
    fig, ax = plt.subplots(figsize=(10, 10))
    ax = data.plot(kind="scatter", x="geolocation_lng", y="geolocation_lat", alpha=0.3, s=0.3, c='maroon', ax=ax)
    ax.set_axis_off()
    ax.imshow(brazil, extent=[-73.98283055, -33.8, -33.75116944, 5.4])
    st.pyplot(fig)

all_df = pd.read_csv('all_data.csv.gz', compression='gzip')
datetime_cols = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]
for col in datetime_cols:
    all_df[col] = pd.to_datetime(all_df[col])

min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()

# Sidebar
with st.sidebar:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(' ')
    with col2:
        st.image("https://raw.githubusercontent.com/mhdhfzz/data-analyst-dicoding/main/dashboard/logo.png"
                 , width=100)
    with col3:
        st.write(' ')

    # Date Range
    start_date, end_date = st.date_input(
        label="Select Date Range",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

all_df = all_df[(all_df["order_approved_at"] >= str(start_date)) & 
                 (all_df["order_approved_at"] <= str(end_date))]

sales_per_month = create_sales_per_month(all_df)
top_products = create_top_product(all_df)
rating_product = create_rating_product(all_df)

st.subheader('Total Penjualan tiap Bulan')
col1, col2 = st.columns(2)

with col1:
    total_orders = sales_per_month.order_count.sum()
    st.metric("Total orders", value=total_orders)

with col2:
    total_revenue = format_currency(sales_per_month.revenue.sum(), "AUD", locale='es_CO') 
    st.metric("Total Revenue", value=total_revenue)


sales_per_month = sales_per_month.groupby('year_month')['revenue'].sum().reset_index()
sales_per_month['year_month'] = sales_per_month['year_month'].astype(str)


tick_positions = sales_per_month.index[::3].tolist()


if sales_per_month.index[-1] not in tick_positions:
    tick_positions.append(sales_per_month.index[-1])


tick_labels = sales_per_month["year_month"].iloc[tick_positions]

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    sales_per_month["year_month"],
    sales_per_month["revenue"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.set_xticks(tick_positions)
ax.set_xticklabels(tick_labels, rotation=45, fontsize=15)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)


st.subheader("Best & Worst Performing Product")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(45,25))

colors = ["#068DA9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="total_sales", y="product_category_name_english", data=top_products.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Produk penjualan tertinggi", loc="center", fontsize=80)
ax[0].ticklabel_format(axis='x', style='plain')
ax[0].tick_params(axis ='x', labelsize=50)
ax[0].tick_params(axis ='y', labelsize=50)
ax[0].set_xlabel('Total Penjualan (R$)', fontsize=70)

sns.barplot(x="total_sales", y="product_category_name_english", data=top_products.sort_values(by="total_sales", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Produk penjualan terendah", loc="center", fontsize=80)
ax[1].ticklabel_format(axis='x', style='plain')
ax[1].tick_params(axis='x', labelsize=50)
ax[1].tick_params(axis='y', labelsize=50)
ax[1].set_xlabel('Total Penjualan (R$)', fontsize=70)

st.pyplot(fig)



st.subheader("Impact of Delivery Timeliness on Review Scores")
fig, ax = plt.subplots(figsize=(16, 8))
sns.barplot(data=rating_product, x="delivered_on_time", y="review_score", palette=["#F44336", "#4CAF50"])
ax.set_xlabel('Delivery Status', fontsize=32)
ax.set_ylabel('Average Review Score', fontsize=32)
ax.tick_params(axis='x', labelsize=16)
ax.tick_params(axis='y', labelsize=16)
st.pyplot(fig)


st.subheader("Persebaran customer")
plot_brazil_map(all_df.drop_duplicates(subset='customer_id'))