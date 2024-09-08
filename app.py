# Import necessary packages
from dash import Dash, html, dcc, Output, Input
import pandas as pd
import plotly.express as px
import requests
import io

# Download and read data
URL = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/historical_automobile_sales.csv"
response = requests.get(URL)
response.raise_for_status()
text = io.StringIO(response.text)
df = pd.read_csv(text)
print('Data downloaded and read into a dataframe!')

# Initialize the Dash app
app = Dash(__name__)

# Define year list for dropdown
year_list = [str(year) for year in range(1980, 2024)]  

# App layout
app.layout = html.Div([
    html.H1(children='Automobile Sales Statistics Dashboard', style={'textAlign': 'center', 'color': '#503D36', 'fontSize': 25}),
    
    dcc.Dropdown(
        id='dropdown-statistics', 
        options=[
            {'label': 'Yearly Statistics', 'value': 'Yearly'},
            {'label': 'Recession Period Statistics', 'value': 'Recession'}
        ],
        placeholder='Select a report type',
        style={'width': '100%', 'padding': '3px', 'fontSize': 20, 'textAlignLast': 'center'}
    ),
    
    html.Div(id='select-year-container', children=[
        dcc.Dropdown(
            id='select-year', 
            options=[{'label': year, 'value': year} for year in year_list],
            placeholder='Select year',
            style={'width': '100%', 'padding': '3px', 'fontSize': 20, 'textAlignLast': 'center'}
        )
    ]),
    
    html.Div(id='output-container', className='chart-grid', style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'center'}),
])

# Callback to show/hide year dropdown based on report type selection
@app.callback(
    Output('select-year-container', 'style'),
    [Input('dropdown-statistics', 'value')]
)
def update_year_dropdown_visibility(value):
    if value == 'Yearly':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

# Callback to update yearly statistics based on selected year
@app.callback(
    Output('output-container', 'children'),
    [Input('dropdown-statistics', 'value'),
     Input('select-year', 'value')]
)
def update_output_container(statistics_type, input_year):
    if statistics_type == 'Yearly' and input_year:
        yearly_data = df[df['Year'] == int(input_year)]

        
        yas_mean = yearly_data['Automobile_Sales'].mean()
        mas_sum = yearly_data['Automobile_Sales'].sum()
        avr_vdata = yearly_data.groupby('Vehicle_Type')['Automobile_Sales'].mean()
        exp_data = yearly_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum()

        
        Y_chart1 = dcc.Graph(
            figure=px.line(yearly_data, x='Year', y='Automobile_Sales', title='Yearly Automobile Sales')
        )

        Y_chart2 = dcc.Graph(
            figure=px.line(yearly_data, x='Month', y='Automobile_Sales', title='Total Monthly Automobile Sales')
        )

        Y_chart3 = dcc.Graph(
            figure=px.bar(yearly_data, x='Vehicle_Type', y='Automobile_Sales', 
                          title='Average Vehicles Sold by Vehicle Type in {}'.format(input_year))
        )

        Y_chart4 = dcc.Graph(
            figure=px.pie(yearly_data, values='Advertising_Expenditure', names='Vehicle_Type',
                          title='Total Advertisement Expenditure for Each Vehicle')
        )

        return [
            html.Div(className='chart-item', children=[Y_chart1, Y_chart2], style={'flex': '50%'}),
            html.Div(className='chart-item', children=[Y_chart3, Y_chart4], style={'flex': '50%'})
        ]

    elif statistics_type == 'Recession':
        recession_data = df[df['Recession'] == 1]

        yearly_rec = recession_data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        average_sales = recession_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        exp_rec = recession_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        unemp_data = recession_data.groupby(['Vehicle_Type', 'unemployment_rate'])['Automobile_Sales'].mean().reset_index()
         
         
        
        R_chart1 = dcc.Graph(
            figure=px.line(yearly_rec, x='Year', y='Automobile_Sales', title='Automobile Sales During Recession Period')
        )
        R_chart2 = dcc.Graph(
            figure=px.bar(average_sales, x='Vehicle_Type', y='Automobile_Sales', 
                          title='Average Vehicles Sold by Vehicle Type During Recession')
        )
        R_chart3 = dcc.Graph(
            figure=px.pie(exp_rec, values='Advertising_Expenditure', names='Vehicle_Type',
                          title='Total Advertising Expenditure Share by Vehicle Type During Recession')
        )
        R_chart4 = dcc.Graph(
            figure=px.bar(unemp_data, x='Vehicle_Type', y='Automobile_Sales', color='unemployment_rate',
                          labels={'unemployment_rate': 'Unemployment Rate', 'Automobile_Sales': 'Average Automobile Sales'},
                          title='Effect of Unemployment Rate on Vehicle Type and Sales During Recession')
        )

        return [
            html.Div(className='chart-item', children=[R_chart1, R_chart2], style={'flex': '50%'}),
            html.Div(className='chart-item', children=[R_chart3, R_chart4], style={'flex': '50%'})
        ]

    return [] 

if __name__ == '__main__':
    app.run_server(debug=True)
