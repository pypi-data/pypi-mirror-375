import streamlit as st
import pandas as pd
from dateutil.relativedelta import relativedelta
from datetime import date
import time
import plotly.express as px

palette = ['#EB8957', '#F2C865', '#9ABC77', '#60A78C', '#5D8F8D', '#5D758E', '#3E7B9D', '#E7514B', '#E4793F','#EB993D', ]
main_color = '#549084'

def header(header):
     st.markdown(f'<p style="background-color:{main_color};color:#f9f9f9;font-size:24px;text-align:center;border-radius:10px">{header}</p>', unsafe_allow_html=True)

def get_data_labels():
     return st.sidebar.toggle('Data Labels', value=True)

def convert_from_snake_case(string):
    if(len(string)<=3):
        return string.upper()
    else:
        converted_string = string.replace('_', ' ')
        converted_string = converted_string.title()
        return converted_string
    
def get_view_size_selection(view_size):
    return st.selectbox('**View Size**', view_size, format_func=convert_from_snake_case)

def get_time_size_selection(start_size=0):
    time_size = ['Day', 'Week', 'Month','Quarter', 'Year']
    time_size = time_size[start_size:]
    return st.selectbox('**Time Size**', time_size)

def add_multiselect(col_name, df):
    unique_values = pd.unique(df[col_name])
    unique_values_all = ["(ALL)"] + list(unique_values)
    with st.expander(convert_from_snake_case(col_name)): 
        selection = st.multiselect(
            '..',
            unique_values_all,
            default="(ALL)",
            label_visibility="hidden",
            key=col_name
        )
    if "(ALL)" in selection:
        selection = unique_values
    return selection

def time_range_filter(s_date, relative_date=None):
    if relative_date is None:
        relative_date = date.today() + relativedelta(months=-1)
    date_range = st.date_input('**Date Range**', (relative_date, date.today()))
    st.caption(f"*Date range from {min(s_date)} to {max(s_date)}")
    return date_range

def cols_filter(df, filter_cols):
    return {col: add_multiselect(col, df) for col in filter_cols}

def get_mask(df, date_col, date_range, selections):
    mask = (df[date_col] >= date_range[0]) & (df[date_col] <= date_range[1])
    for col, selection in selections.items():
        mask &= df[col].isin(selection)
    return mask

def get_week_string(date):
    date = pd.to_datetime(date)
    previous_monday = date - pd.Timedelta(days=date.weekday())
    return previous_monday.strftime('%YW%W')

def get_quarter_string(date):
    year = date.year
    if date.month in [1, 2, 3]:
        return f"{year}Q1"
    elif date.month in [4, 5, 6]:
        return f"{year}Q2"
    elif date.month in [7, 8, 9]:
        return f"{year}Q3"
    else:
        return f"{year}Q4"

def init_date_col(df, date_col):
    if isinstance(df[date_col].iloc[0], str):
        df[date_col] = pd.to_datetime(df[date_col]).dt.date

def add_time_cols(df, date_col):
    df['Day'] = pd.to_datetime(df[date_col])
    df['Year'] = df['Day'].dt.strftime('%Y').astype(str)
    df['Month'] = df['Day'].dt.strftime('%Y-%m').astype(str)
    df['Week'] = df['Day'].apply(get_week_string)
    df['Quarter'] = df['Day'].apply(get_quarter_string)

def metric(label, value, delta=None, delta_color="normal", help=None, label_visibility="visible"):
    list_ani_val = [int(value/10), int(value/4), int(value/3*2)]
    with st.empty():
        for val in list_ani_val:
            st.metric(':rainbow['+label+']', f'{val:,}')
            time.sleep(0.08)
        st.metric(label, f'{value:,}')

def side_control(df, date_col, view_size_cols, relative_date=None, start_time_size=0, multi_pages=None):
    if relative_date is None:
        relative_date = date.today() + relativedelta(months=-1)
    with st.sidebar:
        data_labels = get_data_labels()
        page_selection = None
        if multi_pages:
            page_selection = st.radio(
                "**Page**",
                multi_pages
            )
        view_size_selection = get_view_size_selection(view_size_cols)
        time_size_selection = get_time_size_selection(start_time_size)
        st.divider()
        date_range = time_range_filter(df[date_col], relative_date)
        selections = cols_filter(df, view_size_cols)
        st.divider()
    mask = get_mask(df, date_col, date_range, selections)
    df = df[mask]
    add_time_cols(df, date_col)
    if multi_pages:
        return df, data_labels, view_size_selection, time_size_selection, page_selection
    else:
        return df, data_labels, view_size_selection, time_size_selection

def stacked_bar(df, x_col, y_col, color, data_labels=True, title=False):
    x_title = f'{x_col}'
    y_title = y_col
    if not title:
        title = f'By {x_col} {convert_from_snake_case(y_title)}'
    if x_col == color:
        df_plot = df.groupby([x_col])[y_col].sum().reset_index()
    else:
        df_plot = df.groupby([color, x_col])[y_col].sum().reset_index()
    x_order = list(pd.unique(df_plot[x_col]))
    x_order.sort()

    bar_chart = px.bar(
        df_plot,
        x=x_col,
        y=y_col,
        color=color,
        barmode='stack',
        color_discrete_sequence=palette
    )
    bar_chart.update_layout(title=title, xaxis_title=x_title, yaxis_title=y_title)
    bar_chart.update_xaxes(categoryorder='array', categoryarray=x_order)
    
    df_label = df_plot.groupby(x_col, as_index=False).sum()
    margin_label = df_label[y_col].max() * 0.04
    if data_labels:
        bar_chart.update_layout(annotations=[
            {"x": x, "y": total+margin_label, "text": f'{round(total):,}', "showarrow": False}
            for x, total in df_plot.groupby(x_col, as_index=False).agg({y_col: "sum"}).values
        ])
    # Stacked plot
    st.plotly_chart(bar_chart, config= {'displaylogo': False})
    return df_plot

def line_chart(df, x_col, y_col, color):
            x_title = f'{x_col}'
            y_title = y_col
            title = f'By {x_col} {convert_from_snake_case(y_title)}'
            if x_col == color:
                df_plot = df.groupby([x_col])[y_col].sum().reset_index()
            else:
                df_plot = df.groupby([color, x_col])[y_col].sum().reset_index()
            x_order = list(pd.unique(df_plot[x_col]))
            x_order.sort()

            line_chart = px.line(
                df_plot,
                x=x_col,
                y=y_col,
                color=color,
                color_discrete_sequence=palette
            )
            line_chart.update_layout(title=title, xaxis_title=x_title, yaxis_title=y_title)
            line_chart.update_xaxes(categoryorder='array', categoryarray=x_order)


            # Display line chart
            st.plotly_chart(line_chart, config= {'displaylogo': False})
            return df_plot