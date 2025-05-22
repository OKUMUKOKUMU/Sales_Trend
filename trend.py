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
    # Extended sample data with years 2022-2025
    data = [
        ["1-3-2022", "BCH-12201", "Gouda Portion 200g", "10000", "Online Subscription", -1, 301.72],
        ["1-4-2022", "BCH-16301", "Paneer 250g", "10000", "Online Subscription", -1, 344.83],
        ["1-5-2022", "BDY-20101", "Unsalted Butter 500g", "10000", "Online Subscription", -1, 603.45],
        ["1-6-2022", "BOG-50101", "Organic Whole Milk - 420mL", "10000", "Online Subscription", -4, 700],
        ["1-8-2022", "BOG-50227", "Vegan Berry Yoghurt 150ML", "10000", "Online Subscription", -1, 172.41],
        ["15-9-2022", "BOG-50228", "Vegan Plain Natural Sugar Yoghurt 150ML", "10000", "Online Subscription", -1, 172.41],
        ["1-10-2022", "BOG-50229", "Vegan Passion Fruit Yoghurt 150ML", "10000", "Online Subscription", -1, 172.41],
        ["1-11-2022", "DIC-30161", "Delia's Coffee bean Ice Cream 500mL", "10000", "Online Subscription", -1, 603.45],
        ["1-12-2022", "DIC-40101", "Delia's Customer Specific Ice-cream 500ml", "10000", "Online Subscription", -1, 603.45],
        ["1-1-2023", "BCH-10301", "Camembert 200g", "10000", "Online Subscription", -1, 448.28],
        ["1-2-2023", "BCH-14101", "Mozzarella 200g", "10000", "Online Subscription", -2, 620.68],
        ["1-3-2023", "BCH-14161", "String Cheese 180g", "10000", "Online Subscription", -2, 620.68],
        ["1-4-2023", "BCH-16201", "Halloumi 250g", "10000", "Online Subscription", -2, 844.82],
        ["1-5-2023", "BDY-20101", "Unsalted Butter 500g", "10000", "Online Subscription", -1, 603.45],
        ["1-6-2023", "BDY-20201", "Sour Cream 200g", "10000", "Online Subscription", -1, 431.03],
        ["1-7-2023", "BOI-60000", "Browns Other sale Items", "10000", "Online Subscription", -1, 344.83],
        ["1-8-2023", "BOI-60000", "Browns Other sale Items", "10000", "Online Subscription", -1, 431.03],
        ["1-9-2023", "BRC-12505", "Grated Parmesan 100g", "10000", "Online Subscription", -2, 775.86],
        ["1-10-2023", "DIC-30101", "Delia's Vanilla Bean Ice Cream 500mL", "10000", "Online Subscription", -1, 603.45],
        ["1-11-2023", "DIC-40101", "Delia's Customer Specific Ice-cream 500ml", "10000", "Online Subscription", -1, 603.45],
        ["1-12-2023", "BOG-50101", "Organic Whole Milk - 420mL", "10000", "Online Subscription", -4, 700],
        ["1-1-2024", "BFC-51101", "Margarita Pizza", "10000", "Online Subscription", -1, 775.86],
        ["1-2-2024", "BFC-51111", "Spinach & Pesto Pizza", "10000", "Online Subscription", -1, 775.86],
        ["1-3-2024", "BCH-12201", "Gouda Portion 200g", "10000", "Online Subscription", -1, 301.72],
        ["1-4-2024", "BCH-16301", "Paneer 250g", "10000", "Online Subscription", -1, 344.83],
        ["1-5-2024", "BDY-20101", "Unsalted Butter 500g", "10000", "Online Subscription", -1, 603.45],
        ["1-6-2024", "BOG-50101", "Organic Whole Milk - 420mL", "10000", "Online Subscription", -4, 700],
        ["1-7-2024", "BOG-50227", "Vegan Berry Yoghurt 150ML", "10000", "Online Subscription", -1, 172.41],
        ["1-8-2024", "BOG-50228", "Vegan Plain Natural Sugar Yoghurt 150ML", "10000", "Online Subscription", -1, 172.41],
        ["1-9-2024", "BOG-50229", "Vegan Passion Fruit Yoghurt 150ML", "10000", "Online Subscription", -1, 172.41],
        ["1-10-2024", "DIC-30161", "Delia's Coffee bean Ice Cream 500mL", "10000", "Online Subscription", -1, 603.45],
        ["1-11-2024", "DIC-40101", "Delia's Customer Specific Ice-cream 500ml", "10000", "Online Subscription", -1, 603.45],
        ["1-12-2024", "BCH-10301", "Camembert 200g", "10000", "Online Subscription", -1, 448.28],
        ["1-1-2025", "BCH-14101", "Mozzarella 200g", "10000", "Online Subscription", -2, 620.68],
        ["1-2-2025", "BCH-14161", "String Cheese 180g", "10000", "Online Subscription", -2, 620.68],
        ["1-3-2025", "BCH-16201", "Halloumi 250g", "10000", "Online Subscription", -2, 844.82],
    ]
    
    df = pd.DataFrame(data, columns=[
        'Posting Date', 'Item No', 'Description', 'Source No', 'Name', 'Invoiced Quantity', 'Sales Amount'
    ])
    
    return df

@st.cache_data
def prepare_data(df):
    # Convert date and basic calculations
    df = df.copy()
    df['Date'] = pd.to_datetime(df['Posting Date'], dayfirst=True)
    df['Abs_Sales'] = abs(df['Sales Amount'])
    
    # Correct fiscal year calculation: if month >= 7, it's the current year's fiscal year
    df['Fiscal_Year'] = df['Date'].apply(lambda x: x.year if x.month >= 7 else x.year - 1)
    
    # Calculate fiscal week start (Friday to Thursday)
    def get_fiscal_week_start(date):
        days_since_friday = (date.weekday() + 3) % 7
        week_start = date - timedelta(days=days_since_friday)
        return week_start
    
    df['Fiscal_Week_Start'] = df['Date'].apply(get_fiscal_week_start)
    df['Fiscal_Week_Str'] = df['Fiscal_Week_Start'].dt.strftime('%Y-%m-%d')
    
    # Calculate week number within fiscal year
    def get_week_number(date, fiscal_year):
        # Fiscal year starts July 1st
        fiscal_start = datetime(fiscal_year, 7, 1)
        
        # Find first Friday of fiscal year or before
        days_to_friday = (4 - fiscal_start.weekday()) % 7
        if days_to_friday == 0:
            first_friday = fiscal_start
        else:
            first_friday = fiscal_start + timedelta(days=days_to_friday)
        
        # If fiscal start is after Friday, go to previous Friday
        if fiscal_start.weekday() > 4:
            first_friday = fiscal_start - timedelta(days=(fiscal_start.weekday() - 4))
        
        # Calculate week start for the given date
        week_start = get_fiscal_week_start(date)
        
        # Calculate week number
        if week_start >= first_friday:
            week_number = ((week_start - first_friday).days // 7) + 1
        else:
            # Handle edge case for dates before first Friday
            week_number = 1
            
        return min(week_number, 53)  # Cap at 53 weeks max
    
    df['Week_Number'] = df.apply(lambda row: get_week_number(row['Date'], row['Fiscal_Year']), axis=1)
    
    # Add other date components
    df['Month'] = df['Date'].dt.strftime('%B')
    df['Month_Num'] = df['Date'].dt.month
    df['Year'] = df['Date'].dt.year
    
    return df

def classify_season(month_num):
    if month_num in [11, 12, 1]:
        return "High Season"
    elif month_num in [6, 7, 8]:
        return "Low Season"
    else:
        return "Moderate Season"

def get_filtered_data(df, customer_filter=None, year_filter=None, month_filter=None, fiscal_year_filter=None):
    """Apply all filters to the dataframe efficiently"""
    filtered_df = df.copy()
    
    if customer_filter and customer_filter != "All":
        filtered_df = filtered_df[filtered_df['Name'] == customer_filter]
    
    if year_filter and year_filter != "All":
        filtered_df = filtered_df[filtered_df['Year'] == int(year_filter)]
    
    if month_filter and month_filter != "All":
        filtered_df = filtered_df[filtered_df['Month'] == month_filter]
        
    if fiscal_year_filter and fiscal_year_filter != "All":
        filtered_df = filtered_df[filtered_df['Fiscal_Year'] == int(fiscal_year_filter)]
    
    return filtered_df

def create_weekly_trend(df, customer_filter=None, year_filter=None, month_filter=None, fiscal_year_filter=None):
    # Apply filters
    filtered_df = get_filtered_data(df, customer_filter, year_filter, month_filter, fiscal_year_filter)
    
    if filtered_df.empty:
        # Return empty chart if no data
        fig = px.line(title="No data available for selected filters")
        fig.update_layout(height=400)
        return fig, pd.DataFrame()

    # Group by fiscal week
    weekly_data = filtered_df.groupby(['Fiscal_Week_Str', 'Week_Number', 'Fiscal_Week_Start']).agg({
        'Abs_Sales': 'sum',
        'Invoiced Quantity': 'sum'
    }).reset_index()

    weekly_data = weekly_data.sort_values('Fiscal_Week_Start')
    
    # Create labels for x-axis
    weekly_data['Week_Label'] = weekly_data.apply(
        lambda row: f"Week {row['Week_Number']}<br>{row['Fiscal_Week_Start'].strftime('%b %d')}", 
        axis=1
    )

    # Build title with active filters
    title_parts = ['Weekly Sales Trend (Friday to Thursday)']
    if customer_filter and customer_filter != "All":
        title_parts.append(f'Customer: {customer_filter}')
    if fiscal_year_filter and fiscal_year_filter != "All":
        title_parts.append(f'FY: {fiscal_year_filter}')
    if year_filter and year_filter != "All":
        title_parts.append(f'Year: {year_filter}')
    if month_filter and month_filter != "All":
        title_parts.append(f'Month: {month_filter}')
    
    title = title_parts[0]
    if len(title_parts) > 1:
        title += f"<br><sub>{' | '.join(title_parts[1:])}</sub>"

    fig = px.line(weekly_data, x='Week_Label', y='Abs_Sales', 
                  title=title,
                  labels={'Abs_Sales': 'Sales Amount', 'Week_Label': 'Week'})
    
    fig.update_traces(line=dict(width=3), mode='lines+markers', marker=dict(size=8))
    fig.update_layout(
        height=400,
        xaxis_title='Week Number',
        xaxis={'tickangle': -45}
    )

    return fig, weekly_data

def create_monthly_trend(df, customer_filter=None):
    filtered_df = get_filtered_data(df, customer_filter)

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
    filtered_df = get_filtered_data(df, customer_filter)

    yearly_data = filtered_df.groupby(['Fiscal_Year', 'Month', 'Month_Num']).agg({
        'Abs_Sales': 'sum',
        'Invoiced_Quantity': 'sum'
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
    # Load and prepare data
    df = load_sample_data()

    # File upload section
    st.sidebar.header("📁 Data Upload")
    uploaded_file = st.sidebar.file_uploader("Upload Excel file", type=['xlsx', 'xls'])

    if uploaded_file:
        try:
            uploaded_df = pd.read_excel(uploaded_file)
            if validate_data_structure(uploaded_df):
                df = uploaded_df
                st.sidebar.success("✅ File uploaded successfully!")
            else:
                st.sidebar.error("❌ Missing required columns.")
                st.sidebar.info("Required: Posting Date, Item No, Description, Source No, Name, Invoiced Quantity, Sales Amount")
                return
        except Exception as e:
            st.sidebar.error(f"❌ Error: {str(e)}")
            return

    # Prepare data once
    df = prepare_data(df)
    
    # Extract filter options
    customers = ["All"] + sorted(df['Name'].unique().tolist())
    years = ["All"] + sorted([str(year) for year in df['Year'].unique()], reverse=True)
    fiscal_years = ["All"] + sorted([str(fy) for fy in df['Fiscal_Year'].unique()], reverse=True)
    months = ["All"] + ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    selected_customer = st.sidebar.selectbox("Customer", customers, key="customer")
    
    st.sidebar.subheader("Weekly Trend Filters")
    selected_fiscal_year = st.sidebar.selectbox("Fiscal Year", fiscal_years, key="fiscal_year")
    selected_year = st.sidebar.selectbox("Calendar Year", years, key="year")
    selected_month = st.sidebar.selectbox("Month", months, key="month")

    # Display current selection
    st.markdown(f"### 📊 Analysis for: **{selected_customer}**")
    
    # Weekly Trend Section
    st.markdown("### 📅 Weekly Sales Trend")
    
    # Show active filters
    active_filters = []
    if selected_customer != "All":
        active_filters.append(f"Customer: {selected_customer}")
    if selected_fiscal_year != "All":
        active_filters.append(f"Fiscal Year: {selected_fiscal_year}")
    if selected_year != "All":
        active_filters.append(f"Calendar Year: {selected_year}")
    if selected_month != "All":
        active_filters.append(f"Month: {selected_month}")
    
    if active_filters:
        st.info(f"🔍 Active filters: {' | '.join(active_filters)}")
    
    # Generate weekly chart
    with st.spinner("Loading weekly trend..."):
        fig_weekly, weekly_data = create_weekly_trend(
            df, selected_customer, selected_year, selected_month, selected_fiscal_year
        )
        st.plotly_chart(fig_weekly, use_container_width=True)
    
    # Show summary table if data exists
    if not weekly_data.empty:
        with st.expander("📋 Weekly Summary Table", expanded=False):
            summary_df = weekly_data[['Week_Number', 'Fiscal_Week_Str', 'Abs_Sales', 'Invoiced Quantity']].copy()
            summary_df.columns = ['Week #', 'Week Start', 'Sales Amount', 'Quantity']
            summary_df['Sales Amount'] = summary_df['Sales Amount'].round(2)
            st.dataframe(summary_df, use_container_width=True)

    # Monthly and Yearly trends (less frequent updates)
    st.markdown("### 📊 Monthly Sales Trend")
    fig_monthly, _ = create_monthly_trend(df, selected_customer)
    st.plotly_chart(fig_monthly, use_container_width=True)

    st.markdown("### 📈 Yearly Sales Trend")
    fig_yearly, _ = create_yearly_trend(df, selected_customer)
    st.plotly_chart(fig_yearly, use_container_width=True)

if __name__ == "__main__":
    main()
