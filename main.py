import growattServer
import datetime
import getpass
from rich.console import Console
from rich.table import Table
from datetime import datetime
import matplotlib.pyplot as plt

def plot_bar_graph(chart_data, param):
    """
    Generate a bar graph for the provided chart data.

    :param chart_data: List of data points.
    :param param: Parameter name (for the graph title).
    """
    if not chart_data:
        print("No data available for plotting.")
        return

    plt.figure(figsize=(10, 5))
    plt.bar(range(len(chart_data)), chart_data, color='blue')
    plt.title(f"Daily Trend for {param}")
    plt.xlabel("Time Slots")
    plt.ylabel("Value")
    plt.grid(axis='y')
    plt.show()

current_date = datetime.now().strftime('%Y-%m-%d')

def main():
    username = "hadyk"
    user_pass = "hccj1918"

    api = growattServer.GrowattApi()

    # Login
    login_response = api.login(username, user_pass)
    if not login_response or login_response.get('result') != 1:
        print("Login failed. Please check your credentials.")
        return

    # Fetch plant list
    plant_list = api.get_plant_list()
    if plant_list:
        print("Plant List:")
        print(plant_list)
        print("")

        # Assuming there's at least one plant
        plant_tz = plant_list[0]['timezone']
        plant_id = plant_list[0]['id']  
        plant_name = plant_list[0]['plantName'] 
        print(f"Plant timezone: {plant_tz}")
        print(f"Plant ID: {plant_id}")
        print(f"Plant Name: {plant_name}")

        # Fetch weather information
        weather_data = api.get_weather_by_plant(plant_id)
        # Extract weather data
        weather_info = weather_data.get('obj', {}).get('data', {}).get('HeWeather6', [])[0]
        if weather_info:
            current = weather_info.get('now', {})
            basic = weather_info.get('basic', {})
            update = weather_info.get('update', {})

            # Print weather data
            print("\nWeather Data:")
            print(f"City: {basic.get('location', 'Unknown')}")
            print(f"Temperature: {current.get('tmp', 'N/A')}°C")
            print(f"Feels Like: {current.get('fl', 'N/A')}°C")
            print(f"Humidity: {current.get('hum', 'N/A')}%")
            print(f"Condition: {current.get('cond_txt', 'N/A')}")
            print(f"Wind Speed: {current.get('wind_spd', 'N/A')} km/h")
            print(f"Wind Direction: {current.get('wind_dir', 'N/A')}")
            print(f"Sunrise: {basic.get('sr', 'N/A')}")
            print(f"Sunset: {basic.get('ss', 'N/A')}")
            print(f"Local Update Time: {update.get('loc', 'N/A')}")
        else:
            print("\nWeather data is incomplete.")

        # Fetch devices data
        devices_data = api.get_devices_by_plant(plant_id)
        if not devices_data or devices_data.get('result') != 1:
            print("\nFailed to fetch devices data.")
            return

        # Extract devices information
        devices = devices_data.get('obj', {}).get('storage', [])
        if devices:
            print("\nDevices Data:")
            for device in devices:
                device_serial = device[0]  # Device serial number
                device_name = device[1]   # Device name
                device_type = device[2]   # Device type
                print(f"Device Serial: {device_serial}")
                print(f"Device Name: {device_name}")
                print(f"Device Type: {device_type}\n")
        else:
            print("\nNo devices found.")

        # Fetch panel data
        plant_details = api.get_panel_data(plant_id)
        #plant_details = api.get_plant_details(plant_id)
        if not plant_details or plant_details.get('result') != 1:
            print("\nFailed to fetch plant details.")
            return

        # Extract and display plant information
        plant_info = plant_details.get('obj', {})
        if plant_info:
            print("\nPlant Details:")
            
            # Core information
            plant_name = plant_info.get('plantName', 'N/A')
            plant_id = plant_info.get('id', 'N/A')
            country = plant_info.get('country', 'N/A')
            city = plant_info.get('city', 'N/A')
            timezone = plant_info.get('timezone', 'N/A')
            latitude = plant_info.get('lat', 'N/A')
            longitude = plant_info.get('lng', 'N/A')
            
            # Environmental and energy details
            co2_reduction = plant_info.get('co2', 'N/A')
            tree_equivalent = plant_info.get('tree', 'N/A')
            coal_saved = plant_info.get('coal', 'N/A')
            total_energy = plant_info.get('eTotal', 'N/A')
            nominal_power = plant_info.get('nominalPower', 'N/A')
            
            # Financial details
            currency_unit = plant_info.get('moneyUnitText', 'N/A')
            fixed_power_price = plant_info.get('fixedPowerPrice', 'N/A')
            peak_period_price = plant_info.get('peakPeriodPrice', 'N/A')
            valley_period_price = plant_info.get('valleyPeriodPrice', 'N/A')
            flat_period_price = plant_info.get('flatPeriodPrice', 'N/A')

            # Miscellaneous
            creation_date = plant_info.get('creatDate', 'N/A')
            plant_type = plant_info.get('plantType', 'N/A')
            account_name = plant_info.get('accountName', 'N/A')
            plant_image = plant_info.get('plantImg', 'N/A')

            # Display the extracted details
            print(f"Plant Name: {plant_name}")
            print(f"Plant ID: {plant_id}")
            print(f"Country: {country}")
            print(f"City: {city}")
            print(f"Timezone: {timezone}")
            print(f"Latitude: {latitude}")
            print(f"Longitude: {longitude}")
            print(f"CO2 Reduction (kg): {co2_reduction}")
            print(f"Tree Equivalent: {tree_equivalent}")
            print(f"Coal Saved (kg): {coal_saved}")
            print(f"Total Energy Generated (kWh): {total_energy}")
            print(f"Nominal Power (W): {nominal_power}")
            print(f"Currency Unit: {currency_unit}")
            print(f"Fixed Power Price: {fixed_power_price}")
            print(f"Peak Period Price: {peak_period_price}")
            print(f"Valley Period Price: {valley_period_price}")
            print(f"Flat Period Price: {flat_period_price}")
            print(f"Creation Date: {creation_date}")
            print(f"Plant Type: {plant_type}")
            print(f"Account Name: {account_name}")
            print(f"Plant Image File: {plant_image}")
        else:
            print("\nNo plant details found.")



        # Fetch storage total data
        storage_total_data = api.get_storage_total_data(plant_id)
        print("\nStorage Total Data:")
        print(storage_total_data)

        # Fetch storage status data
        storage_status_data = api.get_storage_status_data(plant_id)
        print("\nStorage Status Data:")
        print(storage_status_data)

        panel_page_data = api.get_panel_page_by_type(1730679568634)
        print("\nPanel Page Data:")
        print(panel_page_data)

        storage_bat_chart = api.get_storage_bat_chart(plant_id, device_serial)
        # Extract relevant data
        date = storage_bat_chart['obj']['date']
        cds_titles = storage_bat_chart['obj']['cdsTitle']
        cd_charge = storage_bat_chart['obj']['cdsData']['cd_charge']
        cd_discharge = storage_bat_chart['obj']['cdsData']['cd_disCharge']

        # Initialize Rich Console and Table
        console = Console()
        table = Table(title=f"Storage Battery Data for {date}")

        # Define columns
        table.add_column("Date", justify="center")
        table.add_column("Charge (kWh)", justify="right")
        table.add_column("Discharge (kWh)", justify="right")

        # Add rows to the table
        for i in range(len(cds_titles)):
            table.add_row(
                cds_titles[i],
                f"{cd_charge[i]:.2f}",
                f"{cd_discharge[i]:.2f}"
            )

        # Print the table
        console.print(table)

        storage_energy_day_chart = api.get_storage_energy_day_chart(plant_id, device_serial, current_date)
        console = Console()
        obj = storage_energy_day_chart.get("obj", {})

        # Summary Metrics
        e_charge_total = obj.get("eChargeTotal", "N/A")
        e_discharge_total = obj.get("eDisChargeTotal", "N/A")
        e_charge = obj.get("eCharge", "N/A")
        e_discharge = obj.get("eDisCharge", "N/A")

        # Charts
        charts = obj.get("charts", {})
        sys_out = charts.get("sysOut", [])
        user_load = charts.get("userLoad", [])
        pac_to_grid = charts.get("pacToGrid", [])

        # Render Summary Metrics
        summary_table = Table(title="Storage Energy Day Summary")
        summary_table.add_column("Metric", style="cyan", justify="left")
        summary_table.add_column("Value", style="green", justify="right")
        summary_table.add_row("Total Charge Energy", f"{e_charge_total} kWh")
        summary_table.add_row("Total Discharge Energy", f"{e_discharge_total} kWh")
        summary_table.add_row("Charge Energy (Day)", f"{e_charge} kWh")
        summary_table.add_row("Discharge Energy (Day)", f"{e_discharge} kWh")
        console.print(summary_table)

        # Helper for Slot Tables
        def render_slots_table(title, data, unit="kW"):
            table = Table(title=title)
            table.add_column("Slot", style="magenta", justify="center")
            table.add_column("Value", style="yellow", justify="center")
            for idx, value in enumerate(data):
                display_value = f"{value:.2f} {unit}" if value is not None else "N/A"
                table.add_row(f"Slot {idx + 1}", display_value)
            return table

        # Render System Output
        console.print(render_slots_table("System Output (sysOut)", sys_out))

        # Render User Load
        console.print(render_slots_table("User Load", user_load))

        # Render PAC to Grid
        console.print(render_slots_table("PAC to Grid", pac_to_grid))

        # Highlight the current consumption
        current_consumption = next((v for v in user_load if v is not None), "N/A")
        console.print(f"[bold green]Current Consumption Power: {current_consumption} kW[/bold green]")

        parameters = ["outPutPower", "capacity", "pBat", "vBat", "iAcCharge", "outPutVolt", "vGrid", "pGrid"]

        params = "pBat,pAcInPut,outPutPower"
        # Extract date components

        date_day = current_date  # Full date in 'YYYY-MM-DD' format
        date_month = current_date[:7]  # Extract 'YYYY-MM'
        date_year = current_date[:4]  # Extract 'YYYY'

        
        # Plot for various scales
        api.plot_parameters(plant_id, date_day, device_serial, params, scale="Day")
        api.plot_parameters(plant_id, date_month, device_serial, params, scale="Month")
        api.plot_parameters(plant_id, date_year, device_serial, params, scale="Year")
        api.plot_parameters(plant_id, date_year, device_serial, params, scale="Total")




    else:
        print("Failed to fetch plant list.")


if __name__ == "__main__":
    main()

'''
    https://server.growatt.com/index/getPlantListTitle
    https://server.growatt.com/index/getWeatherByPlantId?plantId=1602774
    https://server.growatt.com/panel/getDevicesByPlant?plantId=1602774
    https://server.growatt.com/panel/getPanelPageByType?ttt=1730679568634
    https://server.growatt.com/panel/getPlantData?plantId=1602774
    https://server.growatt.com/panel/storage/getStorageTotalData?plantId=1602774
    https://server.growatt.com/panel/storage/getStorageBatChart
    https://server.growatt.com/panel/storage/getStorageEnergyDayChart
    https://server.growatt.com/panel/storage/getStorageStatusData?plantId=1602774
'''