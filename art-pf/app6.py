import pandas as pd
import requests
import dash
from dash import html, dcc
from dash.dependencies import Output, Input
import plotly.express as px

# Function to download COVID-19 data for US states from GitHub
def download_covid_data():
    url = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv'
    response = requests.get(url)
    if response.status_code == 200:
        covid_data = pd.read_csv(url)
        # Convert the 'date' column to a proper date type
        covid_data['date'] = pd.to_datetime(covid_data['date'])
        return covid_data
    else:
        print("Failed to download data")
        return None

# Load COVID-19 data
covid_data = download_covid_data()

# Create a color mapping for each state using the 'tab20' color scale
color_mapping = px.colors.qualitative.Plotly

# Create an instance of the Dash app
app = dash.Dash(__name__)
server = app.server

# Layout of the app (with two graphs and dropdowns)
app.layout = html.Div(children=[

    html.Link(href="https://fonts.googleapis.com/css2?family=Teko:wght@600&display=swap" , rel="stylesheet"),

    html.H1("COVID-19 : U.S Cases and Deaths", style={'textAlign': 'center', 'font-family' : 'Teko, sans-serif' , 'font-size' :'58px' ,  'border': '3px solid #2d12ed', 'padding': '10px', 'margin-left':'10px' ,'margin-right':'10px'}),

    # Dropdown to select state
    html.Div(children=[
        html.Label("State", style={'fontWeight': 'bold' , 'color':'#2d12ed' ,'font-size':'28px','font-family':'Teko, sans-serif','margin-left':'10px' ,'margin-right':'10px'}),
        dcc.Dropdown(
            id='state-dropdown',
            options=[
                {'label': 'All states', 'value': 'All states'}
            ] + [{'label': state, 'value': state} for state in covid_data['state'].unique()],
            value='All states', 
            style={'margin-bottom': '10px' ,'font-family':'Arial, sans-serif' }  # Set the default value to "All states"
        )
    ], className='dropdown-item'),

    # Dropdown to select month
    html.Div(children=[
        html.Label("Month", style={'fontWeight': 'bold', 'color':'#2d12ed' ,'font-size':'28px','font-family':'Teko, sans-serif', 'margin-left':'10px' ,'margin-right':'10px'}),
        dcc.Dropdown(
            id='month-dropdown',
            options=[
                {'label': month, 'value': month} for month in covid_data['date'].dt.month_name().unique()
            ],
            value='January', 
            style={'margin-bottom': '10px','font-family':'Arial, sans-serif'  }  # Set the default value to January
        )
    ], className='dropdown-item'),

    # Dropdown to select year
    html.Div(children=[
        html.Label("Year", style={'fontWeight': 'bold', 'color':'#2d12ed'  ,'font-size':'28px' ,'font-family':'Teko, sans-serif', 'margin-left':'10px' ,'margin-right':'10px'}),
        dcc.Dropdown(
            id='year-dropdown',
            options=[
                {'label': str(year), 'value': year} for year in covid_data['date'].dt.year.unique()
            ],
            value=2021, 
            style={'margin-bottom': '10px' ,'font-family':'Arial , sans-serif'  }  # Set the default value to 2021
        )
    ], className='dropdown-item'),

    # Line chart for cases
    dcc.Graph(id='line_chart_cases'),

    # Line chart for deaths
    dcc.Graph(id='line_chart_deaths'),

])

# Callback function to update the line charts based on the selected state, month, and year
@app.callback(
    [Output('line_chart_cases', 'figure'),
     Output('line_chart_deaths', 'figure')],
    [Input('state-dropdown', 'value'),
     Input('month-dropdown', 'value'),
     Input('year-dropdown', 'value')]
)
def update_figures(selected_state, selected_month, selected_year):
    # Filter data based on the selected state, month, and year
    start_date = pd.to_datetime(f'{selected_year}-{selected_month}-01')
    end_date = start_date + pd.offsets.MonthEnd(0)
    
    if selected_state == 'All states':
        covid_data_filtered_cases = covid_data[
            (covid_data['date'] >= start_date) & (covid_data['date'] <= end_date)
        ]
        covid_data_filtered_deaths = covid_data_filtered_cases.copy()
        title_cases = f'COVID-19 Cases in {selected_month} {selected_year} - All States'
        title_deaths = f'COVID-19 Deaths in {selected_month} {selected_year} - All States'
    else:
        covid_data_filtered_cases = covid_data[
            (covid_data['state'] == selected_state) & (covid_data['date'] >= start_date) & (covid_data['date'] <= end_date)
        ]
        covid_data_filtered_deaths = covid_data[
            (covid_data['state'] == selected_state) & (covid_data['date'] >= start_date) & (covid_data['date'] <= end_date)
        ]
        title_cases = f'COVID-19 Cases in {selected_month} {selected_year} - {selected_state}'
        title_deaths = f'COVID-19 Deaths in {selected_month} {selected_year} - {selected_state}'
    
    # Prepare data for the first graph (cases)
    fig_cases = px.line(covid_data_filtered_cases, x='date', y='cases', color='state',
                        labels={'date': 'Date', 'cases': 'Cases'},
                        title=title_cases)
    fig_cases.update_yaxes(range=[0, covid_data_filtered_cases['cases'].max() + 5])

      # Prepare data for the second graph (deaths)
    fig_deaths = px.line(covid_data_filtered_deaths, x='date', y='deaths', color='state',
                         labels={'date': 'Date', 'deaths': 'Deaths'},
                         title=title_deaths)
    fig_deaths.update_yaxes(range=[0, covid_data_filtered_deaths['deaths'].max() + 5])



    # If 'All states' is selected, maintain the same colors as the all states graph
    if selected_state == 'All states':
        for state, color in zip(covid_data['state'].unique(), color_mapping):
            fig_cases.for_each_trace(lambda trace: trace.update(line=dict(color=color)) if trace.name == state else ())
            fig_deaths.for_each_trace(lambda trace: trace.update(line=dict(color=color)) if trace.name == state else ())

    return fig_cases, fig_deaths

if __name__ == '__main__':
    app.run_server(port=8081)