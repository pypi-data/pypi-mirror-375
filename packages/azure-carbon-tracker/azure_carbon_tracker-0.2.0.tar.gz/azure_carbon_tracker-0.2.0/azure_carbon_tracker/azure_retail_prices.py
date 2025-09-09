import csv
import requests
import time
import os

def query_price(meter_name, location):
    """
    Queries the Azure Retail Prices API for a given meter name and location.
    Returns (unitPrice, currencyCode) or (None, None) if not found.
    """
    url = (
        f"https://prices.azure.com/api/retail/prices?"
        f"$filter=meterName eq '{meter_name}' and location eq '{location}'"
    )
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        items = data.get('Items', [])
        if items:
            first_item = items[0]
            unitPrice = first_item.get('unitPrice', None)
            currencyCode = first_item.get('currencyCode', None)
            return unitPrice, currencyCode
    except Exception as e:
        print(f"Error fetching price for {meter_name} in {location}: {e}")
    return None, None

def create_pricing_table(input_file, output_file, sleep_seconds=1):
    """
    Reads input CSV with 'meter_name' and 'location', queries prices,
    writes results to output CSV with columns: ['meter_name', 'location', 'unitPrice', 'currencyCode'],
    but only writes rows where unitPrice is not None.
    """
    import csv
    import time

    fieldnames = ['meter_name', 'location', 'unitPrice', 'currencyCode']
    with open(input_file, newline='', encoding='utf-8-sig') as csvfile_in, \
         open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile_out:
        reader = csv.DictReader(csvfile_in, delimiter=';')
        writer = csv.DictWriter(csvfile_out, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        for row in reader:
            meter_name = row['meter_name']
            location = row['location']
            unitPrice, currencyCode = query_price(meter_name, location)
            if unitPrice is not None:
                writer.writerow({
                    'meter_name': meter_name,
                    'location': location,
                    'unitPrice': unitPrice,
                    'currencyCode': currencyCode if currencyCode is not None else ''
                })
            time.sleep(sleep_seconds)
    print(f"Finished. Output written to {output_file}")


def update_pricing_table(missing_pairs, pricing_table_file, sleep_seconds=1):
    """
    For each (meter_name, location) in missing_pairs, query the Azure Retail Prices API.
    If not already present in the pricing_table_file, append the price as a new row.
    """
    fieldnames = ['meter_name', 'location', 'unitPrice', 'currencyCode']

    # Read existing entries to avoid duplicates
    existing_keys = set()
    if os.path.exists(pricing_table_file):
        with open(pricing_table_file, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                key = (row['meter_name'], row['location'])
                existing_keys.add(key)

    # Open for appending
    with open(pricing_table_file, 'a', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
        # Write header if file is empty
        if os.stat(pricing_table_file).st_size == 0:
            writer.writeheader()

        for meter_name, location in missing_pairs:
            key = (meter_name, location)
            if key in existing_keys:
                print(f"Skipping existing pair: {meter_name}, {location}")
                continue

            unitPrice, currencyCode = query_price(meter_name, location)
            if unitPrice is not None and currencyCode is not None:
                print(f"Appending price for {meter_name} in {location}: {unitPrice} {currencyCode}")
                writer.writerow({
                    'meter_name': meter_name,
                    'location': location,
                    'unitPrice': unitPrice,
                    'currencyCode': currencyCode
                })
            else:
                print(f"Price not found for {meter_name} in {location}")
            time.sleep(sleep_seconds)

    print(f"Appended new prices to {pricing_table_file}")
