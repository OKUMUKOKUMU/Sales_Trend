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
    """Prepare data with proper date handling and fiscal calculations"""
    # Convert date
    df['Date'] = pd.to_datetime(df['Posting Date'])
    
    # Calculate absolute sales amount
    df['Abs_Sales'] = abs(df['Sales Amount'])
    
    # Add fiscal year (July to June)
    df['Fiscal_Year'] = df['Date'].apply(lambda x: x.year if x.month >= 7 else x.year - 1)
    
    # Add fiscal week (Friday to Thursday)
    def get_fiscal_week(date):
        # Find the Friday of the week
        days_since_friday = (date.weekday() + 3) % 7
        week_start = date - timedelta(days=days_since_friday)
        return week_start.strftime('%Y-%m-%d')
    
    df['Fiscal_Week'] = df['Date'].apply(get_fiscal_week)
    
    # Add month name for better display
    df['Month'] = df['Date'].dt.strftime('%B')
    df['Month_Num'] = df['Date'].dt.month
    
    return df

def classify_season(month_num):
    """Classify months into seasons based on sales patterns"""
    if month_num in [11, 12, 1]:  # Nov, Dec, Jan - Holiday season
        return "High Season"
    elif month_num in [6, 7, 8]:  # Jun, Jul, Aug - Summer/Low season
        return "Low Season"
    else:
        return "Moderate Season"

def create_weekly_trend(df, customer_filter=None):
    """Create weekly trend analysis"""
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
    """Create monthly trend analysis"""
    filtered_df = df.copy()
    if customer_filter and customer_filter != "All":
        filtered_df = filtered_df[filtered_df['Name'] == customer_filter]
    
    monthly_data = filtered_df.groupby(['Month', 'Month_Num']).agg({
        'Abs_Sales': 'sum',
        'Invoiced Quantity': 'sum'
    }).reset_index()
    
    monthly_data = monthly_data.sort_values('Month_Num')
    monthly_data['Season'] = monthly_data['Month_Num'].apply(classify_season)
    
    # Create color mapping for seasons
    color_map = {'High Season': '#ff6b6b', 'Moderate Season': '#4ecdc4', 'Low Season': '#45b7d1'}
    
    fig = px.bar(monthly_data, x='Month', y='Abs_Sales', color='Season',
                 title='Monthly Sales Trend with Seasonal Classification',
                 labels={'Abs_Sales': 'Sales Amount'},
                 color_discrete_map=color_map)
    fig.update_layout(height=400)
    
    return fig, monthly_data

def create_yearly_trend(df, customer_filter=None):
    """Create yearly trend analysis by month"""
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
    """Validate the uploaded Excel file has required columns"""
    required_columns = ['Posting Date', 'Item No', 'Description', 
                       'Source No', 'Name', 'Invoiced Quantity', 'Sales Amount']
    return all(col in df.columns for col in required_columns)

# Main app
def main():
    # Load and prepare data
    df = load_sample_data()
    
    # File upload option - Excel only
    st.sidebar.header("📁 Data Upload (Excel Only)")
    uploaded_file = st.sidebar.file_uploader(
        "Upload your sales data (Excel only)", 
        type=['xlsx', 'xls'],
        help="Only Excel files (.xlsx, .xls) are accepted"
    )
    
    if uploaded_file is not None:
        # Validate file extension
        file_extension = uploaded_file.name.split('.')[-1].lower()
        if file_extension not in ['xlsx', 'xls']:
            st.sidebar.error("Invalid file type. Please upload an Excel file (.xlsx or .xls)")
            st.stop()
        
        try:
            # Read Excel file
            with st.spinner('Loading Excel file...'):
                uploaded_file.seek(0)  # Reset file pointer
                engine = 'openpyxl' if file_extension == 'xlsx' else 'xlrd'
                df_loaded = pd.read_excel(uploaded_file, engine=engine)
            
            # Validate the loaded data structure
            if not validate_data_structure(df_loaded):
                missing = [col for col in ['Posting Date', 'Item No', 'Description', 
                                          'Source No', 'Name', 'Invoiced Quantity', 'Sales Amount'] 
                          if col not in df_loaded.columns]
                st.sidebar.error(f"Missing required columns in Excel file: {', '.join(missing)}")
                st.stop()
            
            df = df_loaded
            st.sidebar.success("Excel file uploaded and validated successfully!")
            
        except Exception as e:
            st.sidebar.error(f"Error reading Excel file: {str(e)}")
            st.stop()
    
    # Prepare data
    df = prepare_data(df)
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Customer filter
    customers = ["All"] + sorted(df['Name'].unique().tolist())
    selected_customer = st.sidebar.selectbox("Select Customer:", customers)
    
    # Date range filter
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    date_range = st.sidebar.date_input(
        "Select Date Range:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Filter data by date range
    if len(date_range) == 2:
        start_date, end_date = date_range
        df = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]
    
    # Main content
    col1, col2, col3, col4 = st.columns(4)
    
    # Summary metrics
    total_sales = df['Abs_Sales'].sum() if selected_customer == "All" else df[df['Name'] == selected_customer]['Abs_Sales'].sum()
    total_qty = abs(df['Invoiced Quantity'].sum()) if selected_customer == "All" else abs(df[df['Name'] == selected_customer]['Invoiced Quantity'].sum())
    unique_products = df['Item No'].nunique() if selected_customer == "All" else df[df['Name'] == selected_customer]['Item No'].nunique()
    avg_order = total_sales / len(df) if len(df) > 0 else 0
    
    with col1:
        st.metric("Total Sales", f"${total_sales:,.2f}")
    with col2:
        st.metric("Total Quantity", f"{total_qty:,.0f}")
    with col3:
        st.metric("Unique Products", f"{unique_products}")
    with col4:
        st.metric("Avg Order Value", f"${avg_order:.2f}")
    
    st.markdown("---")
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Weekly Trend", "📈 Monthly Trend", "📅 Yearly Trend", "📋 Data Table"])
    
    with tab1:
        st.subheader("Weekly Sales Trend (Friday to Thursday)")
        weekly_fig, weekly_data = create_weekly_trend(df, selected_customer)
        st.plotly_chart(weekly_fig, use_container_width=True)
        
        # Weekly summary table
        st.subheader("Weekly Summary")
        weekly_summary = weekly_data.copy()
        weekly_summary['Week Starting'] = weekly_summary['Fiscal_Week'].dt.strftime('%Y-%m-%d')
        weekly_summary['Sales Amount'] = weekly_summary['Abs_Sales'].apply(lambda x: f"${x:,.2f}")
        weekly_summary['Quantity'] = weekly_summary['Invoiced Quantity'].apply(lambda x: f"{abs(x):,.0f}")
        st.dataframe(weekly_summary[['Week Starting', 'Sales Amount', 'Quantity']], use_container_width=True)
    
    with tab2:
        st.subheader("Monthly Sales Trend with Seasonal Classification")
        monthly_fig, monthly_data = create_monthly_trend(df, selected_customer)
        st.plotly_chart(monthly_fig, use_container_width=True)
        
        # Season legend
        st.markdown("""
        **Season Classification:**
        - 🔴 **High Season**: November, December, January (Holiday period)
        - 🟢 **Moderate Season**: February, March, April, May, September, October
        - 🔵 **Low Season**: June, July, August (Summer period)
        """)
        
        # Monthly summary table
        st.subheader("Monthly Summary")
        monthly_summary = monthly_data.copy()
        monthly_summary['Sales Amount'] = monthly_summary['Abs_Sales'].apply(lambda x: f"${x:,.2f}")
        monthly_summary['Quantity'] = monthly_summary['Invoiced Quantity'].apply(lambda x: f"{abs(x):,.0f}")
        st.dataframe(monthly_summary[['Month', 'Season', 'Sales Amount', 'Quantity']], use_container_width=True)
    
    with tab3:
        st.subheader("Yearly Trend by Month (Fiscal Year: July-June)")
        yearly_fig, yearly_data = create_yearly_trend(df, selected_customer)
        st.plotly_chart(yearly_fig, use_container_width=True)
        
        # Yearly summary table
        st.subheader("Yearly Summary by Month")
        yearly_summary = yearly_data.pivot_table(
            index=['Month', 'Month_Num', 'Season'], 
            columns='Fiscal_Year', 
            values='Abs_Sales', 
            fill_value=0
        ).reset_index()
        
        # Format the data
        yearly_summary = yearly_summary.sort_values('Month_Num')
        for col in yearly_summary.columns:
            if col not in ['Month', 'Month_Num', 'Season']:
                yearly_summary[col] = yearly_summary[col].apply(lambda x: f"${x:,.2f}" if x > 0 else "-")
        
        st.dataframe(yearly_summary.drop('Month_Num', axis=1), use_container_width=True)
    
    with tab4:
        st.subheader("Raw Data")
        display_df = df.copy()
        display_df['Sales Amount'] = display_df['Abs_Sales'].apply(lambda x: f"${x:,.2f}")
        display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
        
        columns_to_show = ['Date', 'Item No', 'Description', 'Name', 'Invoiced Quantity', 'Sales Amount', 'Fiscal_Week']
        st.dataframe(display_df[columns_to_show], use_container_width=True)
        
        # Download button
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name='sales_data.csv',
            mime='text/csv',
        )

if __name__ == "__main__":
    main()
