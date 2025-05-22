import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Configure page
st.set_page_config(page_title="Sales Trend Analysis", layout="wide")

st.title("📈 Sales Trend Analysis Dashboard")
st.markdown("*Fiscal Year: July to June | Week: Friday to Thursday*")

# Sample data
@st.cache_data
def load_sample_data():
    data = [
        ["1-3-2022", "BCH-12201", "Gouda Portion 200g", "10000", "Online Subscription", -1, 301.72],
        ["1-3-2022", "BCH-16301", "Paneer 250g", "10000", "Online Subscription", -1, 344.83],
        ["1-3-2022", "BDY-20101", "Unsalted Butter 500g", "10000", "Online Subscription", -1, 603.45],
        ["1-3-2022", "BOG-50101", "Organic Whole Milk - 420mL", "10000", "Online Subscription", -4, 700],
        ["1-3-2022", "BOG-50227", "Vegan Berry Yoghurt 150ML", "10000", "Online Subscription", -1, 172.41],
        ["1-3-2022", "BOG-50228", "Vegan Plain Natural Sugar Yoghurt 150ML", "10000", "Online Subscription", -1, 172.41],
        ["1-3-2022", "BOG-50229", "Vegan Passion Fruit Yoghurt 150ML", "10000", "Online Subscription", -1, 172.41],
        ["1-3-2022", "DIC-30161", "Delia's Coffee bean Ice Cream 500mL", "10000", "Online Subscription", -1, 603.45],
        ["1-3-2022", "DIC-40101", "Delia's Customer Specific Ice-cream 500ml", "10000", "Online Subscription", -1, 603.45],
        ["1-4-2022", "BCH-10301", "Camembert 200g", "10000", "Online Subscription", -1, 448.28],
        ["1-4-2022", "BCH-14101", "Mozzarella 200g", "10000", "Online Subscription", -2, 620.68],
        ["1-4-2022", "BCH-14161", "String Cheese 180g", "10000", "Online Subscription", -2, 620.68],
        ["1-4-2022", "BCH-16201", "Halloumi 250g", "10000", "Online Subscription", -2, 844.82],
        ["1-4-2022", "BDY-20101", "Unsalted Butter 500g", "10000", "Online Subscription", -1, 603.45],
        ["1-4-2022", "BDY-20201", "Sour Cream 200g", "10000", "Online Subscription", -1, 431.03],
        ["1-4-2022", "BOI-60000", "Browns Other sale Items", "10000", "Online Subscription", -1, 344.83],
        ["1-4-2022", "BOI-60000", "Browns Other sale Items", "10000", "Online Subscription", -1, 431.03],
        ["1-4-2022", "BRC-12505", "Grated Parmesan 100g", "10000", "Online Subscription", -2, 775.86],
        ["1-4-2022", "DIC-30101", "Delia's Vanilla Bean Ice Cream 500mL", "10000", "Online Subscription", -1, 603.45],
        ["1-4-2022", "DIC-40101", "Delia's Customer Specific Ice-cream 500ml", "10000", "Online Subscription", -1, 603.45],
        ["1-5-2022", "BOG-50101", "Organic Whole Milk - 420mL", "10000", "Online Subscription", -4, 700],
        ["1-6-2022", "BFC-51101", "Margarita Pizza", "10000", "Online Subscription", -1, 775.86],
        ["1-6-2022", "BFC-51111", "Spinach & Pesto Pizza", "10000", "Online Subscription", -1, 775.86],
    ]
    
    df = pd.DataFrame(data, columns=[
        'Posting Date', 'Item No', 'Description', 'Source No', 'Name', 'Invoiced Quantity', 'Sales Amount'
    ])
    
    return df

def prepare_data(df):
    df['Date'] = pd.to_datetime(df['Posting Date'])
    df['Abs_Sales'] = abs(df['Sales Amount'])
    df['Fiscal_Year'] = df['Date'].apply(lambda x: x.year if x.month >= 7 else x.year - 1)

    def get_fiscal_week(date):
        days_since_friday = (date.weekday() + 3) % 7
        week_start = date - timedelta(days=days_since_friday)
        return week_start.strftime('%Y-%m-%d')
    
    df['Fiscal_Week'] = df['Date'].apply(get_fiscal_week)
    df['Month'] = df['Date'].dt.strftime('%B')
    df['Month_Num'] = df['Date'].dt.month
    
    return df

def classify_season(month_num):
    if month_num in [11, 12, 1]:
        return "High Season"
    elif month_num in [6, 7, 8]:
        return "Low Season"
    else:
        return "Moderate Season"

def create_weekly_trend(df, customer_filter=None):
    filtered_df = df.copy()
    if customer_filter and customer_filter != "All":
        filtered_df = filtered_df[filtered_df['Name'] == customer_filter]

    weekly_data = filtered_df.groupby('Fiscal_Week').agg({
        'Abs_Sales': 'sum',
        'Invoiced Quantity': 'sum'
    }).reset_index()

    weekly_data['Fiscal_Week'] = pd.to_datetime(weekly_data['Fiscal_Week'])
    weekly_data = weekly_data.sort_values('Fiscal_Week')

    fig = px.line(weekly_data, x='Fiscal_Week', y='Abs_Sales', 
                  title='Weekly Sales Trend (Friday to Thursday)',
                  labels={'Abs_Sales': 'Sales Amount', 'Fiscal_Week': 'Week Starting'})
    fig.update_traces(line=dict(width=3))
    fig.update_layout(height=400)

    return fig, weekly_data

def create_monthly_trend(df, customer_filter=None):
    filtered_df = df.copy()
    if customer_filter and customer_filter != "All":
        filtered_df = filtered_df[filtered_df['Name'] == customer_filter]

    monthly_data = filtered_df.groupby(['Month', 'Month_Num']).agg({
        'Abs_Sales': 'sum',
        'Invoiced Quantity': 'sum'
    }).reset_index()

    monthly_data = monthly_data.sort_values('Month_Num')
    monthly_data['Season'] = monthly_data['Month_Num'].apply(classify_season)

    color_map = {'High Season': '#ff6b6b', 'Moderate Season': '#4ecdc4', 'Low Season': '#45b7d1'}

    fig = px.bar(monthly_data, x='Month', y='Abs_Sales', color='Season',
                 title='Monthly Sales Trend with Seasonal Classification',
                 labels={'Abs_Sales': 'Sales Amount'},
                 color_discrete_map=color_map)
    fig.update_layout(height=400)

    return fig, monthly_data

def create_yearly_trend(df, customer_filter=None):
    filtered_df = df.copy()
    if customer_filter and customer_filter != "All":
        filtered_df = filtered_df[filtered_df['Name'] == customer_filter]

    yearly_data = filtered_df.groupby(['Fiscal_Year', 'Month', 'Month_Num']).agg({
        'Abs_Sales': 'sum',
        'Invoiced Quantity': 'sum'
    }).reset_index()

    yearly_data = yearly_data.sort_values(['Fiscal_Year', 'Month_Num'])
    yearly_data['Season'] = yearly_data['Month_Num'].apply(classify_season)

    fig = px.line(yearly_data, x='Month', y='Abs_Sales', color='Fiscal_Year',
                  title='Yearly Trend by Month (Fiscal Year: July-June)',
                  labels={'Abs_Sales': 'Sales Amount'})
    fig.update_layout(height=400)

    return fig, yearly_data

def validate_data_structure(df):
    required_columns = ['Posting Date', 'Item No', 'Description', 
                        'Source No', 'Name', 'Invoiced Quantity', 'Sales Amount']
    return all(col in df.columns for col in required_columns)

# Main app logic
def main():
    df = load_sample_data()

    st.sidebar.header("📁 Data Upload (Excel Only)")
    uploaded_file = st.sidebar.file_uploader("Upload your sales data (Excel only)", type=['xlsx', 'xls'])

    if uploaded_file:
        try:
            uploaded_df = pd.read_excel(uploaded_file)
            if validate_data_structure(uploaded_df):
                df = uploaded_df
                st.sidebar.success("✅ File uploaded and validated successfully.")
            else:
                st.sidebar.error("❌ Uploaded file is missing required columns.")
                return
        except Exception as e:
            st.sidebar.error(f"❌ Error reading file: {e}")
            return

    df = prepare_data(df)
    customers = ["All"] + sorted(df['Name'].unique())
    selected_customer = st.sidebar.selectbox("Filter by Customer", customers)

    st.markdown(f"### 📊 Selected Customer: `{selected_customer}`")
    
    # Weekly Trend
    fig_weekly, _ = create_weekly_trend(df, selected_customer)
    st.plotly_chart(fig_weekly, use_container_width=True)

    # Monthly Trend
    fig_monthly, _ = create_monthly_trend(df, selected_customer)
    st.plotly_chart(fig_monthly, use_container_width=True)

    # Yearly Trend
    fig_yearly, _ = create_yearly_trend(df, selected_customer)
    st.plotly_chart(fig_yearly, use_container_width=True)

if __name__ == "__main__":
    main()
