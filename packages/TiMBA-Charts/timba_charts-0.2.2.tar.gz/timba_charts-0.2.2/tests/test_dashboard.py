import pytest
import pandas as pd
from unittest.mock import patch
import plotly.graph_objects as go
from Toolbox.classes.dashboard import DashboardPlotter

@pytest.fixture
def mock_data():
    data = pd.DataFrame({
        'ISO3': ['USA', 'CAN', 'DEU', 'USA', 'CAN', 'DEU'],
        'Continent': ['North America', 'North America', 'Europe', 'North America', 'North America', 'Europe'],
        'domain': ['Consumption', 'Production', 'Consumption', 'Production', 'Consumption', 'Production'],
        'Commodity': ['Sawnwood C', 'Sawnwood NC', 'Newsprint', 'Sawnwood C', 'Sawnwood NC', 'Newsprint'],
        'Commodity_Group': ['Sawnwood', 'Sawnwood', 'Paper', 'Sawnwood', 'Sawnwood', 'Paper'],
        'Scenario': ['Scenario1', 'Scenario1', 'Scenario2', 'Scenario2', 'Scenario1', 'Scenario2'],
        'year': [2020, 2020, 2021, 2021, 2020, 2021],
        'quantity': [100, 200, 150, 250, 120, 180],
        'price': [2.5, 3.0, 2.8, 3.2, 2.6, 3.1],
        'ForStock': [50, 60, 55, 65, 52, 58]
    })
    return data

@pytest.fixture
def dashboard(mock_data):
    return DashboardPlotter(mock_data)

def test_dashboard_initialization(dashboard):
    assert dashboard.data is not None
    assert dashboard.start == 2020
    assert dashboard.end == 2021
    assert dashboard.app is not None

def test_filter_data(dashboard, mock_data):
    filtered_data = dashboard.filter_data(region=['USA'], continent=None, domain=None, commodity=None, commodity_group=None, scenario=None)
    assert len(filtered_data) == 2
    assert all(filtered_data['ISO3'] == 'USA')

    filtered_data = dashboard.filter_data(region=['DEU'], continent=['Europe'], domain=['Consumption'], 
                                          commodity=['Newsprint'], commodity_group=["Paper"], scenario=['Scenario1', 'Scenario2'])
    assert len(filtered_data) == 1
    assert filtered_data['ISO3'].iloc[0] == 'DEU'
    assert filtered_data['Commodity'].iloc[0] == 'Newsprint'

    filtered_data = dashboard.filter_data(region=None, continent=None, domain=None, commodity=None, commodity_group=None, scenario=None)
    assert len(filtered_data) == len(mock_data)

@pytest.mark.skip(reason="Fehler im test")
def test_update_plot_data(dashboard):
    fig_quantity, fig_price, fig_stock = dashboard.update_plot_data(region=None, continent=None, domain=None, commodity=None, commodity_group=None, scenario=None)
    assert isinstance(fig_quantity, go.Figure)
    assert isinstance(fig_price, go.Figure)
    assert isinstance(fig_stock, go.Figure)
    assert len(fig_quantity.data) > 0
    assert len(fig_price.data) > 0
    assert len(fig_stock.data) > 0

@pytest.mark.skip(reason="Fehler im test")
def test_generate_title(dashboard):
    title = dashboard.generate_title(region=['USA'], continent=['North America'], domain=['Consumption'], commodity=['Sawnwood C'], commodity_group=['Sawnwood'])
    assert title == "['USA'], ['North America'], ['Consumption'], ['Sawnwood C'], ['Sawnwood']"
    title = dashboard.generate_title(region=None, continent=None, domain=None, commodity=None, commodity_group=None)
    assert title == "all data"

def test_create_layout(dashboard):
    dashboard.create_layout()
    assert dashboard.app.layout is not None

def test_create_callbacks(dashboard):
    dashboard.create_callbacks()
    assert True