import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from functools import lru_cache

# Configure page
st.set_page_config(page_title="Sales Trend Analysis", layout="wide")

st.title("📈 Sales Trend Analysis Dashboard")
st.markdown("*Fiscal Year: July to June | Week: Friday to Thursday*")

# Sample data - cached more aggressively
@st.cache_data(ttl=3600, show_spinner=False)
def load_sample_data():
    # [Previous sample data remains exactly the same]
    data = [
        # ... (your existing sample data)
    ]
    
    df = pd.DataFrame(data, columns=[
        'Posting Date', 'Item No', 'Description', 'Source No', 'Name', 'Invoiced Quantity', 'Sales Amount'
    ])
    return df

# Optimized data preparation with memoization
@st.cache_data(ttl=3600, show_spinner=False)
def prepare_data(df):
    df = df.copy()
    
    # Convert date with error handling
    try:
        df['Date'] = pd.to_datetime(df['Posting Date'], dayfirst=True, errors='coerce')
        df = df.dropna(subset=['Date'])  # Remove rows with invalid dates
    except Exception as e:
        st.error(f"Date conversion error: {str(e)}")
        return pd.DataFrame()

    # Basic calculations
    df['Abs_Sales'] = abs(df['Sales Amount'])
    
    # Vectorized fiscal year calculation (faster than apply)
    df['Fiscal_Year'] = df['Date'].dt.year.where(df['Date'].dt.month >= 7, df['Date'].dt.year - 1)
    
    # Pre-calculate weekday for performance
    df['Weekday'] = df['Date'].dt.weekday
    
    # Vectorized fiscal week start calculation
    days_since_friday = (df['Weekday'] + 3) % 7
    df['Fiscal_Week_Start'] = df['Date'] - pd.to_timedelta(days_since_friday, unit='d')
    df['Fiscal_Week_Str'] = df['Fiscal_Week_Start'].dt.strftime('%Y-%m-%d')
    
    # Optimized week number calculation
    def calculate_week_numbers(dates, fiscal_years):
        week_numbers = []
        for date, fiscal_year in zip(dates, fiscal_years):
            fiscal_start = datetime(fiscal_year, 7, 1)
            days_to_friday = (4 - fiscal_start.weekday()) % 7
            first_friday = fiscal_start + timedelta(days=days_to_friday)
            
            if fiscal_start.weekday() > 4:
                first_friday = fiscal_start - timedelta(days=(fiscal_start.weekday() - 4))
            
            week_start = date - timedelta(days=(date.weekday() + 3) % 7)
            
            if week_start >= first_friday:
                week_number = ((week_start - first_friday).days // 7) + 1
            else:
                week_number = 1
                
            week_numbers.append(min(week_number, 53))
        
        return week_numbers
    
    df['Week_Number'] = calculate_week_numbers(df['Date'], df['Fiscal_Year'])
    
    # Add other date components
    df['Month'] = df['Date'].dt.strftime('%B')
    df['Month_Num'] = df['Date'].dt.month
    df['Year'] = df['Date'].dt.year
    
    return df

def classify_season(month_num):
    # Simple lookup is faster than multiple ifs
    season_map = {
        11: "High Season", 12: "High Season", 1: "High Season",
        6: "Low Season", 7: "Low Season", 8: "Low Season"
    }
    return season_map.get(month_num, "Moderate Season")

# Optimized filtering function
def get_filtered_data(df, customer_filter=None, year_filter=None, month_filter=None, fiscal_year_filter=None):
    """Apply all filters to the dataframe efficiently using vectorized operations"""
    mask = pd.Series(True, index=df.index)
    
    if customer_filter and customer_filter != "All":
        mask &= (df['Name'] == customer_filter)
    
    if year_filter and year_filter != "All":
        mask &= (df['Year'] == int(year_filter))
    
    if month_filter and month_filter != "All":
        mask &= (df['Month'] == month_filter)
        
    if fiscal_year_filter and fiscal_year_filter != "All":
        mask &= (df['Fiscal_Year'] == int(fiscal_year_filter))
    
    return df[mask].copy()  # Return a copy to avoid SettingWithCopyWarning

# Optimized chart creation functions
def create_weekly_trend(df, customer_filter=None, year_filter=None, month_filter=None, fiscal_year_filter=None):
    filtered_df = get_filtered_data(df, customer_filter, year_filter, month_filter, fiscal_year_filter)
    
    if filtered_df.empty:
        fig = px.line(title="No data available for selected filters")
        fig.update_layout(height=400)
        return fig, pd.DataFrame()

    # Optimized groupby with named aggregation
    weekly_data = filtered_df.groupby(['Fiscal_Week_Str', 'Week_Number', 'Fiscal_Week_Start'], as_index=False).agg(
        Abs_Sales=('Abs_Sales', 'sum'),
        Quantity=('Invoiced Quantity', 'sum')
    ).sort_values('Fiscal_Week_Start')
    
    weekly_data['Week_Label'] = weekly_data.apply(
        lambda row: f"Week {row['Week_Number']}<br>{row['Fiscal_Week_Start'].strftime('%b %d')}", 
        axis=1
    )

    # Build title
    title_parts = ['Weekly Sales Trend (Friday to Thursday)']
    if customer_filter != "All":
        title_parts.append(f'Customer: {customer_filter}')
    if fiscal_year_filter != "All":
        title_parts.append(f'FY: {fiscal_year_filter}')
    if year_filter != "All":
        title_parts.append(f'Year: {year_filter}')
    if month_filter != "All":
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

    monthly_data = filtered_df.groupby(['Month', 'Month_Num'], as_index=False).agg(
        Abs_Sales=('Abs_Sales', 'sum'),
        Quantity=('Invoiced Quantity', 'sum')
    ).sort_values('Month_Num')
    
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

    try:
        yearly_data = filtered_df.groupby(['Fiscal_Year', 'Month', 'Month_Num'], as_index=False).agg(
            Abs_Sales=('Abs_Sales', 'sum'),
            Quantity=('Invoiced Quantity', 'sum')
        ).sort_values(['Fiscal_Year', 'Month_Num'])
    except KeyError as e:
        st.error(f"Data error: {str(e)}")
        return px.line(), pd.DataFrame()

    yearly_data['Season'] = yearly_data['Month_Num'].apply(classify_season)

    fig = px.line(yearly_data, x='Month', y='Abs_Sales', color='Fiscal_Year',
                 title='Yearly Trend by Month (Fiscal Year: July-June)',
                 labels={'Abs_Sales': 'Sales Amount'},
                 hover_data=['Season', 'Quantity'])
    
    # Add reference line for average
    avg_sales = yearly_data['Abs_Sales'].mean()
    fig.add_hline(y=avg_sales, line_dash="dot",
                 annotation_text=f"Average: {avg_sales:,.2f}",
                 annotation_position="bottom right")

    fig.update_layout(height=400)
    return fig, yearly_data

def validate_data_structure(df):
    required_columns = ['Posting Date', 'Item No', 'Description', 
                       'Source No', 'Name', 'Invoiced Quantity', 'Sales Amount']
    return all(col in df.columns for col in required_columns)

# Main app logic with performance optimizations
def main():
    # Load and prepare data
    with st.spinner("Loading data..."):
        df = load_sample_data()
        df = prepare_data(df)

    # File upload section
    st.sidebar.header("📁 Data Upload")
    uploaded_file = st.sidebar.file_uploader("Upload Excel file", type=['xlsx', 'xls'])

    if uploaded_file:
        try:
            with st.spinner("Processing uploaded file..."):
                uploaded_df = pd.read_excel(uploaded_file)
                if validate_data_structure(uploaded_df):
                    df = prepare_data(uploaded_df)  # Re-prepare with new data
                    st.sidebar.success("✅ File uploaded successfully!")
                else:
                    st.sidebar.error("❌ Missing required columns.")
                    st.sidebar.info("Required: Posting Date, Item No, Description, Source No, Name, Invoiced Quantity, Sales Amount")
                    return
        except Exception as e:
            st.sidebar.error(f"❌ Error: {str(e)}")
            return

    # Extract filter options
    with st.spinner("Preparing filters..."):
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
    st.markdown(f"### 📊 Analysis for: **{selected_customer if selected_customer != 'All' else 'All Customers'}**")
    
    # Create tabs for different trend views
    tab1, tab2, tab3 = st.tabs(["📅 Weekly Trend", "📊 Monthly Trend", "📈 Yearly Trend"])
    
    with tab1:
        st.markdown("### Weekly Sales Trend")
        
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
        
        with st.spinner("Generating weekly trend..."):
            fig_weekly, weekly_data = create_weekly_trend(
                df, selected_customer, selected_year, selected_month, selected_fiscal_year
            )
            st.plotly_chart(fig_weekly, use_container_width=True)
        
        if not weekly_data.empty:
            with st.expander("📋 Weekly Summary Table", expanded=False):
                summary_df = weekly_data[['Week_Number', 'Fiscal_Week_Str', 'Abs_Sales', 'Quantity']].copy()
                summary_df.columns = ['Week #', 'Week Start', 'Sales Amount', 'Quantity']
                summary_df['Sales Amount'] = summary_df['Sales Amount'].round(2)
                st.dataframe(summary_df, use_container_width=True)
    
    with tab2:
        st.markdown("### Monthly Sales Trend")
        if selected_customer != "All":
            st.info(f"🔍 Active filter: Customer: {selected_customer}")
        
        with st.spinner("Generating monthly trend..."):
            fig_monthly, monthly_data = create_monthly_trend(df, selected_customer)
            st.plotly_chart(fig_monthly, use_container_width=True)
        
        if not monthly_data.empty:
            with st.expander("📋 Monthly Summary Table", expanded=False):
                summary_df = monthly_data[['Month', 'Season', 'Abs_Sales', 'Quantity']].copy()
                summary_df.columns = ['Month', 'Season', 'Sales Amount', 'Quantity']
                summary_df['Sales Amount'] = summary_df['Sales Amount'].round(2)
                st.dataframe(summary_df, use_container_width=True)
    
    with tab3:
        st.markdown("### Yearly Sales Trend")
        if selected_customer != "All":
            st.info(f"🔍 Active filter: Customer: {selected_customer}")
        
        with st.spinner("Generating yearly trend..."):
            fig_yearly, yearly_data = create_yearly_trend(df, selected_customer)
            st.plotly_chart(fig_yearly, use_container_width=True)
        
        if not yearly_data.empty:
            with st.expander("📋 Yearly Summary Table", expanded=False):
                summary_df = yearly_data[['Fiscal_Year', 'Month', 'Season', 'Abs_Sales', 'Quantity']].copy()
                summary_df.columns = ['Fiscal Year', 'Month', 'Season', 'Sales Amount', 'Quantity']
                summary_df['Sales Amount'] = summary_df['Sales Amount'].round(2)
                st.dataframe(summary_df, use_container_width=True)

if __name__ == "__main__":
    main()
