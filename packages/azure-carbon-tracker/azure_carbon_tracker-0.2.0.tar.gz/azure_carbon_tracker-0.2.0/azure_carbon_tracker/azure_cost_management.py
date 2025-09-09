import requests
from azure.identity import AzureCliCredential
import csv
from typing import List, Tuple, Dict, Optional
import pandas as pd
import warnings
import importlib.resources

def get_data(
    subscription_id: str,
    resource_group: str,
    start_date: str,
    end_date: str,
    output_csv_path: Optional[str] = None,
    granularity: str = "Monthly",
    metric: str = "ActualCost",
    billing_currency: str = "USD"
) -> Tuple[List[str], List[list], Dict]:
    """
    Fetches Azure cost data for a given resource group and time period.

    Args:
        subscription_id: Azure subscription ID.
        resource_group: Name of the resource group.
        start_date: Start date (YYYY-MM-DD).
        end_date: End date (YYYY-MM-DD).
        output_csv_path: Optional path to write CSV output.
        granularity: Data granularity (default: "Monthly").
        metric: Metric to query (default: "ActualCost").
        billing_currency: Billing currency (default: "USD").

    Returns:
        Tuple of (columns, rows, full response JSON).
    """

    # Acquire token using Azure CLI authentication (make sure 'az login' has been run)
    # https://learn.microsoft.com/en-gb/cli/azure/use-azure-cli-successfully-troubleshooting?view=azure-cli-latest#work-behind-a-proxy
    credential = AzureCliCredential()
    token = credential.get_token("https://management.azure.com/.default").token

    url = (
        f"https://management.azure.com/subscriptions/{subscription_id}/"
        "providers/Microsoft.CostManagement/query?api-version=2023-03-01"
    )

    body = {
        "type": "Usage",
        "metric": metric,
        "billingCurrency": billing_currency,
        "timeframe": "Custom",
        "timePeriod": {
            "from": f"{start_date}T00:00:00Z",
            "to": f"{end_date}T00:00:00Z"
        },
        "dataset": {
            "granularity": granularity,
            "aggregation": {
                "totalCost": {
                    "name": "CostUSD",
                    "function": "Sum"
                }
            },
            "filter": {
                "and": [
                    {
                        "dimensions": {
                            "name": "ServiceName",
                            "operator": "In",
                            "values": ["Cognitive Services"]
                        }
                    },
                    {
                        "dimensions": {
                            "name": "ResourceGroupName",
                            "operator": "In",
                            "values": [resource_group]
                        }
                    }
                ]
            },
            "grouping": [
                {"type": "Dimension", "name": "Meter"},
                {"type": "Dimension", "name": "ResourceLocation"}
            ]
        }
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()
    except requests.RequestException as e:
        error_text = getattr(e.response, 'text', str(e))
        raise RuntimeError(f"Azure API error: {error_text}")

    cost_data = response.json()
    columns = [col['name'] for col in cost_data['properties']['columns']]
    rows = cost_data['properties']['rows']

    if output_csv_path:
        with open(output_csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            writer.writerows(rows)
        print(f"Data written to {output_csv_path}")

    return columns, rows, cost_data

def enrich_with_pricing(df, pricing_path=None):
    if pricing_path is None:
        with importlib.resources.path("azure_carbon_tracker.data", "pricing.csv") as p:
            pricing_path = str(p)
    pricing = pd.read_csv(pricing_path, delimiter=';')
    pricing = pricing.rename(columns={'meter_name': 'Meter', 'location': 'ResourceLocation'})
    merged = pd.merge(
        df,
        pricing,
        how='left',
        left_on=['Meter', 'ResourceLocation'],
        right_on=['Meter', 'ResourceLocation']
    )
    merged = merged.rename(columns={
        'BillingMonth': 'Month',
        'Meter': 'Azure name',
        'ResourceLocation': 'Location',
        'CostUSD': 'TotalCostUSD',
        'unitPrice': 'UnitPriceUSD'
    })
    return merged

def add_token_counts(df):
    mask = (df['UnitPriceUSD'].notnull()) & (df['UnitPriceUSD'] != 0)
    df.loc[mask, 'TokenCount'] = ((df.loc[mask, 'TotalCostUSD'] / df.loc[mask, 'UnitPriceUSD']) * 1000).round().astype(int)
    return df

def enrich_with_model_mapping(df, mapping_path=None):
    if mapping_path is None:
        with importlib.resources.path("azure_carbon_tracker.data", "model_mapping.csv") as p:
            mapping_path = str(p)
    model_mapping = pd.read_csv(mapping_path, delimiter=';')
    return df.merge(model_mapping, left_on='Azure name', right_on='Azure name', how='left')

def enrich_with_carbon_models(df, carbon_path=None):
    if carbon_path is None:
        with importlib.resources.path("azure_carbon_tracker.data", "carbon_models.csv") as p:
            carbon_path = str(p)
    carbon_models = pd.read_csv(carbon_path, delimiter=';', decimal=',')
    return df.merge(carbon_models, on='Name', how='left')

def enrich_with_emission_factors(df, emission_path=None):
    if emission_path is None:
        with importlib.resources.path("azure_carbon_tracker.data", "emission_factors.csv") as p:
            emission_path = str(p)
    emission_factors = pd.read_csv(emission_path, delimiter=';', decimal=',')
    return df.merge(emission_factors, on='Location', how='left')

def calculate_energy_and_co2(df):
    df['TotalEnergykWh'] = (df['TokenCount'] * df['mWhToken']) / 1000000
    df['TotalCO2eKG'] = df['TotalEnergykWh'] * df['kgPerkWh']
    return df

def get_carbon_emissions(
    subscription_id,
    resource_group,
    start_date,
    end_date,
    pricing_path='data/pricing.csv',
    model_mapping_path='data/model_mapping.csv',
    carbon_models_path='data/carbon_models.csv',
    emission_factors_path='data/emission_factors.csv'
):
    """
    Returns a DataFrame with columns:
    month, azure_name, location, total_cost_usd, unit_price_usd, token_count, model_name, milliwatt_hour_per_token, total_energy_kilowatt_hour, kg_co2_per_kilowatt_hour, total_co2e_kg

    Optional CSV paths can be provided to overwrite defaults.
    """
    columns, rows, _ = get_data(
        subscription_id, resource_group, start_date, end_date
    )
    df = pd.DataFrame(rows, columns=columns)
    df = enrich_with_pricing(df, pricing_path)
    df = add_token_counts(df)

    # Warn if any azure_name could not be mapped to a model_name
    df = enrich_with_model_mapping(df, model_mapping_path)
    missing_model = df[df['Name'].isnull()]['Azure name'].unique()
    if len(missing_model) > 0:
        warnings.warn(f"Could not map emission scenario for Azure model(s): {missing_model}")

    df = enrich_with_carbon_models(df, carbon_models_path)

    # Warn if any location could not be mapped to an emission factor
    df = enrich_with_emission_factors(df, emission_factors_path)
    missing_location = df[df['kgPerkWh'].isnull()]['Location'].unique()
    if len(missing_location) > 0:
        warnings.warn(f"Could not map emission factor for location(s): {missing_location}")

    df = calculate_energy_and_co2(df)

    df['Month'] = pd.to_datetime(df['Month']).dt.date
    df['TokenCount'] = df['TokenCount'].fillna(0).astype(int)

    df = df.rename(columns={
        'Month': 'month',
        'Azure name': 'azure_name',
        'Location': 'location',
        'TotalCostUSD': 'total_cost_usd',
        'UnitPriceUSD': 'unit_price_usd',
        'TokenCount': 'token_count',
        'Name': 'model_name',
        'mWhToken': 'milliwatt_hour_per_token',
        'TotalEnergykWh': 'total_energy_kilowatt_hour',
        'kgPerkWh': 'kg_co2_per_kilowatt_hour',
        'TotalCO2eKG': 'total_co2e_kg'
    })

    if 'token_count' in df.columns:
        df['token_count'] = df['token_count'].fillna(0).astype(int)

    final_cols = [
        'month', 'azure_name', 'location', 'total_cost_usd', 'unit_price_usd',
        'token_count', 'model_name', 'milliwatt_hour_per_token',
        'total_energy_kilowatt_hour', 'kg_co2_per_kilowatt_hour', 'total_co2e_kg'
    ]
    return df[final_cols]