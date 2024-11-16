name = "growattServer"

import datetime
from enum import IntEnum
import hashlib
import json
import requests
import warnings
from random import randint
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from datetime import datetime, timedelta



def hash_password(password):
    """
    Normal MD5, except add c if a byte of the digest is less than 10.
    """
    password_md5 = hashlib.md5(password.encode('utf-8')).hexdigest()
    for i in range(0, len(password_md5), 2):
        if password_md5[i] == '0':
            password_md5 = password_md5[0:i] + 'c' + password_md5[i + 1:]
    return password_md5

class Timespan(IntEnum):
    hour = 0
    day = 1
    month = 2

class GrowattApi:
    server_url = 'http://server.growatt.com/'
    agent_identifier = "Dalvik/2.1.0 (Linux; U; Android 12; https://github.com/indykoning/PyPi_GrowattServer)"

    def __init__(self, add_random_user_id=False, agent_identifier=None):
        if (agent_identifier != None):
          self.agent_identifier = agent_identifier

        #If a random user id is required, generate a 5 digit number and add it to the user agent
        if (add_random_user_id):
          random_number = ''.join(["{}".format(randint(0,9)) for num in range(0,5)])
          self.agent_identifier += " - " + random_number

        self.session = requests.Session()
        self.session.verify = False  # Disable SSL verification
        self.session.hooks = {
            'response': lambda response, *args, **kwargs: response.raise_for_status()
        }
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        })

    def __get_date_string(self, timespan=None, date=None):
        if timespan is not None:
         assert timespan in Timespan

        if date is None:
          date = datetime.datetime.now()

        date_str=""
        if timespan == Timespan.month:
            date_str = date.strftime('%Y-%m')
        else:
            date_str = date.strftime('%Y-%m-%d')

        return date_str

    def get_url(self, page):
        """
        Simple helper function to get the page url/
        """
        return self.server_url + page



    def login(self, username, password):
        """
        Log the user in using the Growatt API.
        """
        # Hash the password using MD5
        md5_hasher = hashlib.md5()
        md5_hasher.update(password.encode('utf-8'))
        hashed_password = md5_hasher.hexdigest()

        # Prepare the payload
        payload = {
            'account': username,
            'password': '',
            'validateCode': '',
            'isReadPact': 0,
            'passwordCrc': hashed_password
        }

        try:
            # Send the POST request to the login URL
            response = self.session.post(
                url='http://server.growatt.com/login',
                data=payload
            )

            # Check if the request was successful
            if response.status_code == 200:
                data = response.json()
                if data.get('result') == 1:
                    print("Login successful.")
                    print("Cookies after login:", self.session.cookies)
                    return data
                else:
                    print("Login failed. Response:", data)
                    return None
            else:
                print(f"Login failed with status code: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"An error occurred during login: {e}")
            return None


    def get_plant_list(self):
        """
        Fetch the plant list using the Growatt API session.
        [{"timezone":"2","id":"1602774","plantName":"Hady"}]
        """
        try:
            # Use the same session to send the GET request
            response = self.session.get(self.server_url + 'index/getPlantListTitle')
            response.raise_for_status()  # Raise an error for HTTP response codes >= 400

            # Parse and return the JSON response
            plant_list = response.json()
            print("Plant List:", plant_list)
            return plant_list

        except requests.exceptions.RequestException as e:
            print(f"An error occurred while fetching the plant list: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON response: {e}")
            return None


    def get_weather_by_plant(self, plant_id):
        """
        Fetches weather information for a specific plant.
        """
        try:
            response = self.session.get(self.server_url + (f'index/getWeatherByPlantId?plantId={plant_id}'))
            response.raise_for_status()
            data = response.json()
            return data
        except requests.RequestException as e:
            print(f"An error occurred while fetching weather data: {e}")
            return None

    def get_devices_by_plant(self, plant_id):
        """
        Fetches a list of devices associated with a specific plant.
        """
        try:
            response = self.session.post(self.server_url + (f'panel/getDevicesByPlant?plantId={plant_id}'))
            response.raise_for_status()
            data = response.json()
            return data
        except requests.RequestException as e:
            print(f"An error occurred while fetching device list: {e}")
            return None

    def get_panel_data(self, plant_id):
        """
        Fetches panel data for a specific plant.
        """
        try:
            response = self.session.post(self.server_url + (f'panel/getPlantData?plantId={plant_id}'))
            response.raise_for_status()
            data = response.json()
            return data
        except requests.RequestException as e:
            print(f"An error occurred while fetching panel data: {e}")
            return None

    def get_storage_total_data(self, plant_id):
        """
        Fetches total storage data for a specific plant.
        """
        try:
            response = self.session.post(self.server_url + (f'panel/storage/getStorageTotalData?plantId={plant_id}'))
            response.raise_for_status()
            data = response.json()
            return data
        except requests.RequestException as e:
            print(f"An error occurred while fetching storage total data: {e}")
            return None

    def get_storage_status_data(self, plant_id):
        """
        Fetches storage status data for a specific plant.
        """
        try:
            response = self.session.post(self.server_url + (f'panel/storage/getStorageStatusData?plantId={plant_id}'))
            response.raise_for_status()
            data = response.json()
            return data
        except requests.RequestException as e:
            print(f"An error occurred while fetching storage status data: {e}")
            return None
    def get_panel_page_by_type(self, ttt):
        """
        Fetches panel page data by type.
        """
        try:
            response = self.session.post(self.server_url + f'panel/getPanelPageByType?ttt={ttt}')
            response.raise_for_status()
            data = response.json()
            return data
        except requests.RequestException as e:
            print(f"An error occurred while fetching panel page data: {e}")
            return None

    def get_storage_bat_chart(self, plant_id, device_sn):
        """
        Fetches storage battery chart data.
        """
        payload = {
            "plantId": plant_id,
            "storageSn": device_sn
        }
        try:
            response = self.session.post(self.server_url + 'panel/storage/getStorageBatChart', payload)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.RequestException as e:
            print(f"An error occurred while fetching storage battery chart data: {e}")
            return None

    def get_storage_energy_day_chart(self, plant_id, device_sn, currentdate):
        """
        Fetches daily energy chart data for storage.
        """
        payload = {
            "plantId": plant_id,
            "storageSn": device_sn,
            "date": currentdate
        }
        try:
            response = self.session.post(self.server_url + 'panel/storage/getStorageEnergyDayChart', payload)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.RequestException as e:
            print(f"An error occurred while fetching storage energy day chart data: {e}")
            return None
        
    def get_device_day_chart(self, plant_id, date, device_sn, param):
        """
        Fetch data for a specific parameter and generate a bar graph.

        :param plant_id: ID of the plant.
        :param date: Date in 'YYYY-MM-DD' format.
        :param device_sn: Serial number of the device.
        :param param: Parameter to query (e.g., "outPutPower").
        """
        url = self.server_url + "energy/compare/getDevicesDayChart"
        payload = {
            "plantId": plant_id,
            "date": date,
            "jsonData": json.dumps([{"type": "storage", "sn": device_sn, "params": param}])
        }

        try:
            response = self.session.post(url, data=payload)
            response.raise_for_status()

            data = response.json()
            if data.get("result") == 1:
                chart_data = data.get("obj", {}).get("chart", [])
                current_value = chart_data[-1] if chart_data else None
                self.plot_bar_graph(chart_data, param)
                print(f"Current Value for {param}: {current_value}")
                return chart_data, current_value
            else:
                print(f"Error fetching data: {data.get('msg', 'Unknown error')}")
                return None, None

        except requests.RequestException as e:
            print(f"An error occurred while fetching device data: {e}")
            return None, None
        
    def get_chart(self, plant_id, date, device_sn, params, scale):
        """
        Fetches chart data for specific parameters and scale.

        :param plant_id: The plant ID.
        :param date: The date or time period for the query.
        :param device_sn: The device serial number.
        :param params: Comma-separated string of parameters (e.g., "pBat,pAcInPut,outPutPower").
        :param scale: The time scale ("Day", "Month", "Year", "Total").
        :return: A dictionary containing parameter data.
        """
        scale_to_url = {
            "Day": "energy/compare/getDevicesDayChart",
            "Month": "energy/compare/getDevicesMonthChart",
            "Year": "energy/compare/getDevicesYearChart",
            "Total": "energy/compare/getDevicesTotalChart",
        }

        url = self.server_url + scale_to_url[scale]

        # Prepare the payload
        payload = {
            "plantId": plant_id,
            "jsonData": json.dumps([{"type": "storage", "sn": device_sn, "params": params}])
        }

        # Add "date" or "year" depending on the scale
        if scale in ["Day", "Month"]:
            payload["date"] = date  # Use "date" key for day or month scales
        elif scale in ["Year", "Total"]:
            payload["year"] = date  # Use "year" key for year or total scales

        try:
            response = self.session.post(url, data=payload)
            response.raise_for_status()
            data = response.json()
            if data.get("result") == 1 and data.get("obj"):
                return data["obj"][0]["datas"]
            else:
                print(f"Failed to fetch data for {params} ({scale}): {data.get('msg', 'Unknown error')}")
                return {}
        except requests.RequestException as e:
            print(f"An error occurred while fetching data for {params} ({scale}): {e}")
            return {}

    def generate_time_labels(self, scale, date):
        """
        Generate accurate time labels based on the scale and date.

        :param scale: The time scale ("Day", "Month", "Year", "Total").
        :param date: The date or time period for the query.
        :return: A list of time labels.
        """
        if scale == "Day":
            start_time = datetime.strptime(date, "%Y-%m-%d")
            labels = [(start_time + timedelta(minutes=5 * i)).strftime("%H:%M") for i in range(288)]  # 288 slots (5-min intervals)
        elif scale == "Month":
            start_time = datetime.strptime(date, "%Y-%m")
            num_days = (start_time.replace(month=start_time.month % 12 + 1, day=1) - timedelta(days=1)).day
            labels = [f"{start_time.year}-{start_time.month:02d}-{day:02d}" for day in range(1, num_days + 1)]
        elif scale == "Year":
            labels = [f"{month:02d}" for month in range(1, 13)]  # 12 months
        elif scale == "Total":
            current_year = datetime.now().year
            labels = [str(year) for year in range(current_year - len(labels) + 1, current_year + 1)]
        else:
            labels = []
        return labels
    
    def truncate_to_current_time(self, labels, values, scale):
        """
        Truncate labels and values to ensure they don't exceed the current datetime.

        :param labels: List of time labels.
        :param values: List of values corresponding to the labels.
        :param scale: The time scale ("Day", "Month", "Year", "Total").
        :return: Truncated labels and values.
        """
        current_datetime = datetime.now()
        truncated_labels = []
        truncated_values = []

        if scale == "Day":
            for label, value in zip(labels, values):
                if datetime.strptime(label, "%H:%M") <= current_datetime:
                    truncated_labels.append(label)
                    truncated_values.append(value)
        elif scale == "Month":
            for label, value in zip(labels, values):
                if datetime.strptime(label, "%Y-%m-%d").date() <= current_datetime.date():
                    truncated_labels.append(label)
                    truncated_values.append(value)
        elif scale == "Year":
            for label, value in zip(labels, values):
                if int(label) <= current_datetime.year:
                    truncated_labels.append(label)
                    truncated_values.append(value)
        elif scale == "Total":
            truncated_labels = labels  # Total is historical data and doesn't depend on the current date.
            truncated_values = values

        return truncated_labels, truncated_values

    def plot_parameters(self, plant_id, date, device_sn, params, scale="Day"):
        """
        Plots the chart for multiple parameters over a given scale.

        :param plant_id: The plant ID.
        :param date: The date or time period for the query.
        :param device_sn: The device serial number.
        :param params: Comma-separated string of parameters (e.g., "pBat,pAcInPut,outPutPower").
        :param scale: The time scale ("Day", "Month", "Year", "Total").
        """
        data = self.get_chart(plant_id, date, device_sn, params, scale)
        if not data:
            print(f"No data available for {params} ({scale})")
            return

        time_labels = self.generate_time_labels(scale, date)

        # Plot each parameter
        plt.figure(figsize=(14, 8))
        for param, values in data.items():
            # Truncate data and labels to the current time
            truncated_labels, truncated_values = self.truncate_to_current_time(time_labels, values, scale)

            # Filter out None values
            filtered_data = [(i, val) for i, val in enumerate(truncated_values) if val is not None]
            if not filtered_data:
                print(f"No valid data points for {param} ({scale})")
                continue

            indices, values = zip(*filtered_data)
            plt.plot(indices, values, marker='o', label=f"{param} ({scale})")

        # Formatting the plot
        plt.title(f"Parameters Over {scale} on {date}")
        plt.xlabel("Time Slots")
        plt.ylabel("Value")
        plt.xticks(
            range(len(truncated_labels)), truncated_labels, rotation=45, ha="right", fontsize=8
        )
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def plant_detail(self, plant_id, timespan, date=None):
        """
        Get plant details for specified timespan.
        """
        date_str = self.__get_date_string(timespan, date)

        response = self.session.get(self.get_url('PlantDetailAPI.do'), params={
            'plantId': plant_id,
            'type': timespan.value,
            'date': date_str
        })
        data = json.loads(response.content.decode('utf-8'))
        return data['back']

    def inverter_data(self, inverter_id, date=None):
        """
        Get inverter data for specified date or today.
        """
        date_str = self.__get_date_string(date=date)
        response = self.session.get(self.get_url('newInverterAPI.do'), params={
            'op': 'getInverterData',
            'id': inverter_id,
            'type': 1,
            'date': date_str
        })
        data = json.loads(response.content.decode('utf-8'))
        return data

    def inverter_detail(self, inverter_id):
        """
        Get "All parameters" from PV inverter.
        """
        response = self.session.get(self.get_url('newInverterAPI.do'), params={
            'op': 'getInverterDetailData',
            'inverterId': inverter_id
        })

        data = json.loads(response.content.decode('utf-8'))
        return data

    def inverter_detail_two(self, inverter_id):
        """
        Get "All parameters" from PV inverter.
        """
        response = self.session.get(self.get_url('newInverterAPI.do'), params={
            'op': 'getInverterDetailData_two',
            'inverterId': inverter_id
        })

        data = json.loads(response.content.decode('utf-8'))
        return data

    def tlx_data(self, tlx_id, date=None):
        """
        Get inverter data for specified date or today.
        """
        date_str = self.__get_date_string(date=date)
        response = self.session.get(self.get_url('newTlxApi.do'), params={
            'op': 'getTlxData',
            'id': tlx_id,
            'type': 1,
            'date': date_str
        })
        data = json.loads(response.content.decode('utf-8'))
        return data

    def tlx_detail(self, tlx_id):
        """
        Get "All parameters" from PV inverter.
        """
        response = self.session.get(self.get_url('newTlxApi.do'), params={
            'op': 'getTlxDetailData',
            'id': tlx_id
        })

        data = json.loads(response.content.decode('utf-8'))
        return data

    def mix_info(self, mix_id, plant_id = None):
        """
        Returns high level values from Mix device

        Keyword arguments:
        mix_id -- The serial number (device_sn) of the inverter
        plant_id -- The ID of the plant (the mobile app uses this but it does not appear to be necessary) (default None)

        Returns:
        'acChargeEnergyToday' -- ??? 2.7
        'acChargeEnergyTotal' -- ??? 25.3
        'acChargePower' -- ??? 0
        'capacity': '45' -- The current remaining capacity of the batteries (same as soc but without the % sign)
        'eBatChargeToday' -- Battery charged today in kWh
        'eBatChargeTotal' -- Battery charged total (all time) in kWh
        'eBatDisChargeToday' -- Battery discharged today in kWh
        'eBatDisChargeTotal' -- Battery discharged total (all time) in kWh
        'epvToday' -- Energy generated from PVs today in kWh
        'epvTotal' -- Energy generated from PVs total (all time) in kWh
        'isCharge'-- ??? 0 - Possible a 0/1 based on whether or not the battery is charging
        'pCharge1' -- ??? 0
        'pDischarge1' -- Battery discharging rate in W
        'soc' -- Statement of charge including % symbol
        'upsPac1' -- ??? 0
        'upsPac2' -- ??? 0
        'upsPac3' -- ??? 0
        'vbat' -- Battery Voltage
        'vbatdsp' -- ??? 51.8
        'vpv1' -- Voltage PV1
        'vpv2' -- Voltage PV2
        """
        request_params={
            'op': 'getMixInfo',
            'mixId': mix_id
        }

        if (plant_id):
          request_params['plantId'] = plant_id

        response = self.session.get(self.get_url('newMixApi.do'), params=request_params)

        data = json.loads(response.content.decode('utf-8'))
        return data['obj']

    def mix_totals(self, mix_id, plant_id):
        """
        Returns "Totals" values from Mix device

        Keyword arguments:
        mix_id -- The serial number (device_sn) of the inverter
        plant_id -- The ID of the plant

        Returns:
        'echargetoday' -- Battery charged today in kWh (same as eBatChargeToday from mix_info)
        'echargetotal' -- Battery charged total (all time) in kWh (same as eBatChargeTotal from mix_info)
        'edischarge1Today' -- Battery discharged today in kWh (same as eBatDisChargeToday from mix_info)
        'edischarge1Total' -- Battery discharged total (all time) in kWh (same as eBatDisChargeTotal from mix_info)
        'elocalLoadToday' -- Load consumption today in kWh
        'elocalLoadTotal' -- Load consumption total (all time) in kWh
        'epvToday' -- Energy generated from PVs today in kWh (same as epvToday from mix_info)
        'epvTotal' -- Energy generated from PVs total (all time) in kWh (same as epvTotal from mix_info)
        'etoGridToday' -- Energy exported to the grid today in kWh
        'etogridTotal' -- Energy exported to the grid total (all time) in kWh
        'photovoltaicRevenueToday' -- Revenue earned from PV today in 'unit' currency
        'photovoltaicRevenueTotal' -- Revenue earned from PV total (all time) in 'unit' currency
        'unit' -- Unit of currency for 'Revenue'
        """
        response = self.session.post(self.get_url('newMixApi.do'), params={
            'op': 'getEnergyOverview',
            'mixId': mix_id,
            'plantId': plant_id
        }, verify=False)

        data = json.loads(response.content.decode('utf-8'))
        return data['obj']

    def mix_system_status(self, mix_id, plant_id):
        """
        Returns current "Status" from Mix device

        Keyword arguments:
        mix_id -- The serial number (device_sn) of the inverter
        plant_id -- The ID of the plant

        Returns:
        'SOC' -- Statement of charge (remaining battery %)
        'chargePower' -- Battery charging rate in kw
        'fAc' -- Frequency (Hz)
        'lost' -- System status e.g. 'mix.status.normal'
        'pLocalLoad' -- Load conumption in kW
        'pPv1' -- PV1 Wattage in W
        'pPv2' -- PV2 Wattage in W
        'pactogrid' -- Export to grid rate in kW
        'pactouser' -- Import from grid rate in kW
        'pdisCharge1' -- Discharging batteries rate in kW
        'pmax' -- ??? 6 ??? PV Maximum kW ??
        'ppv' -- PV combined Wattage in kW
        'priorityChoose' -- Priority setting - 0=Local load
        'status' -- System statue - ENUM - Unknown values
        'unit' -- Unit of measurement e.g. 'kW'
        'upsFac' -- ??? 0
        'upsVac1' -- ??? 0
        'uwSysWorkMode' -- ??? 6
        'vAc1' -- Grid voltage in V
        'vBat' -- Battery voltage in V
        'vPv1' -- PV1 voltage in V
        'vPv2' -- PV2 voltage in V
        'vac1' -- Grid voltage in V (same as vAc1)
        'wBatteryType' -- ??? 1
        """
        response = self.session.post(self.get_url('newMixApi.do'), params={
            'op': 'getSystemStatus_KW',
            'mixId': mix_id,
            'plantId': plant_id
        }, verify=False)

        data = json.loads(response.content.decode('utf-8'))
        return data['obj']

    def mix_detail(self, mix_id, plant_id, timespan=Timespan.hour, date=None):
        """
        Get Mix details for specified timespan

        Keyword arguments:
        mix_id -- The serial number (device_sn) of the inverter
        plant_id -- The ID of the plant
        timespan -- The ENUM value conforming to the time window you want e.g. hours from today, days, or months (Default Timespan.hour)
        date -- The date you are interested in (Default datetime.datetime.now())

        Returns:
        A chartData object where each entry is for a specific 5 minute window e.g. 00:05 and 00:10 respectively (below)
        'chartData': {   '00:05': {   'pacToGrid' -- Export rate to grid in kW
                                      'pacToUser' -- Import rate from grid in kW
                                      'pdischarge' -- Battery discharge in kW
                                      'ppv' -- Solar generation in kW
                                      'sysOut' -- Load consumption in kW
                                  },
                         '00:10': {   'pacToGrid': '0',
                                      'pacToUser': '0.93',
                                      'pdischarge': '0',
                                      'ppv': '0',
                                      'sysOut': '0.93'},
                          ......
                     }
        'eAcCharge' -- Exported to grid in kWh
        'eCharge' -- System production in kWh = Self-consumption + Exported to Grid
        'eChargeToday' -- Load consumption from solar in kWh
        'eChargeToday1' -- Self-consumption in kWh
        'eChargeToday2' -- Self-consumption in kWh (eChargeToday + echarge1)
        'echarge1' -- Load consumption from battery in kWh
        'echargeToat' -- Total battery discharged (all time) in kWh
        'elocalLoad' -- Load consumption in kW (battery + solar + imported)
        'etouser' -- Load consumption imported from grid in kWh
        'photovoltaic' -- Load consumption from solar in kWh (same as eChargeToday)
        'ratio1' -- % of system production that is self-consumed
        'ratio2' -- % of system production that is exported
        'ratio3' -- % of Load consumption that is "self consumption"
        'ratio4' -- % of Load consumption that is "imported from grid"
        'ratio5' -- % of Self consumption that is directly from Solar
        'ratio6' -- % of Self consumption that is from batteries
        'unit' -- Unit of measurement e.g kWh
        'unit2' -- Unit of measurement e.g kW


        NOTE - It is possible to calculate the PV generation that went into charging the batteries by performing the following calculation:
        Solar to Battery = Solar Generation - Export to Grid - Load consumption from solar
                           epvToday (from mix_info) - eAcCharge - eChargeToday
        """
        date_str = self.__get_date_string(timespan, date)

        response = self.session.post(self.get_url('newMixApi.do'), params={
            'op': 'getEnergyProdAndCons_KW',
            'plantId': plant_id,
            'mixId': mix_id,
            'type': timespan.value,
            'date': date_str
        }, verify=False)
        data = json.loads(response.content.decode('utf-8'))

        return data['obj']

    def dashboard_data(self, plant_id, timespan=Timespan.hour, date=None):
        """
        Get 'dashboard' data for specified timespan
        NOTE - All numerical values returned by this api call include units e.g. kWh or %
             - Many of the 'total' values that are returned for a Mix system are inaccurate on the system this was tested against.
               However, the statistics that are correct are not available on any other interface, plus these values may be accurate for
               non-mix types of system. Where the values have been proven to be inaccurate they are commented below.

        Keyword arguments:
        plant_id -- The ID of the plant
        timespan -- The ENUM value conforming to the time window you want e.g. hours from today, days, or months (Default Timespan.hour)
        date -- The date you are interested in (Default datetime.datetime.now())

        Returns:
        A chartData object where each entry is for a specific 5 minute window e.g. 00:05 and 00:10 respectively (below)
        NOTE: The keys are interpreted differently, the examples below describe what they are used for in a 'Mix' system
        'chartData': {   '00:05': {   'pacToUser' -- Power from battery in kW
                                      'ppv' -- Solar generation in kW
                                      'sysOut' -- Load consumption in kW
                                      'userLoad' -- Export in kW
                                  },
                         '00:10': {   'pacToUser': '0',
                                      'ppv': '0',
                                      'sysOut': '0.7',
                                      'userLoad': '0'},
                          ......
                     }
        'chartDataUnit' -- Unit of measurement e.g. 'kW',
        'eAcCharge' -- Energy exported to the grid in kWh e.g. '20.5kWh' (not accurate for Mix systems)
        'eCharge' -- System production in kWh = Self-consumption + Exported to Grid e.g '23.1kWh' (not accurate for Mix systems - actually showing the total 'load consumption'
        'eChargeToday1' -- Self-consumption of PPV (possibly including excess diverted to batteries) in kWh e.g. '2.6kWh' (not accurate for Mix systems)
        'eChargeToday2' -- Total self-consumption (PPV consumption(eChargeToday2Echarge1) + Battery Consumption(echarge1)) e.g. '10.1kWh' (not accurate for Mix systems)
        'eChargeToday2Echarge1' -- Self-consumption of PPV only e.g. '0.8kWh' (not accurate for Mix systems)
        'echarge1' -- Self-consumption from Battery only e.g. '9.3kWh'
        'echargeToat' -- Not used on Dashboard view, likely to be total battery discharged e.g. '152.1kWh'
        'elocalLoad' -- Total load consumption (etouser + eChargeToday2) e.g. '20.3kWh', (not accurate for Mix systems)
        'etouser'-- Energy imported from grid today (includes both directly used by load and AC battery charging e.g. '10.2kWh'
        'keyNames' -- Keys to be used for the graph data e.g. ['Solar', 'Load Consumption', 'Export To Grid', 'From Battery']
        'photovoltaic' -- Same as eChargeToday2Echarge1 e.g. '0.8kWh'
        'ratio1' -- % of 'Solar production' that is self-consumed e.g. '11.3%' (not accurate for Mix systems)
        'ratio2' -- % of 'Solar production' that is exported e.g. '88.7%' (not accurate for Mix systems)
        'ratio3' -- % of 'Load consumption' that is self consumption e.g. '49.8%' (not accurate for Mix systems)
        'ratio4' -- % of 'Load consumption' that is imported from the grid e.g '50.2%' (not accurate for Mix systems)
        'ratio5' -- % of Self consumption that is from batteries e.g. '92.1%' (not accurate for Mix systems)
        'ratio6' -- % of Self consumption that is directly from Solar e.g. '7.9%' (not accurate for Mix systems)
        """
        date_str = self.__get_date_string(timespan, date)

        response = self.session.post(self.get_url('newPlantAPI.do'), params={
            'action': "getEnergyStorageData",
            'date': date_str,
            'type': timespan.value,
            'plantId': plant_id
        }, verify=False)

        data = json.loads(response.content.decode('utf-8'))
        return data

    def storage_detail(self, storage_id):
        """
        Get "All parameters" from battery storage.
        """
        response = self.session.get(self.get_url('newStorageAPI.do'), params={
            'op': 'getStorageInfo_sacolar',
            'storageId': storage_id
        })

        data = json.loads(response.content.decode('utf-8'))
        return data

    def storage_params(self, storage_id):
        """
        Get much more detail from battery storage.
        """
        response = self.session.get(self.get_url('newStorageAPI.do'), params={
            'op': 'getStorageParams_sacolar',
            'storageId': storage_id
        })

        data = json.loads(response.content.decode('utf-8'))
        return data

    def storage_energy_overview(self, plant_id, storage_id):
        """
        Get some energy/generation overview data.
        """
        response = self.session.post(self.get_url('newStorageAPI.do?op=getEnergyOverviewData_sacolar'), params={
            'plantId': plant_id,
            'storageSn': storage_id
        }, verify=False)

        data = json.loads(response.content.decode('utf-8'))
        return data['obj']

    def inverter_list(self, plant_id):
        """
        Use device_list, it's more descriptive since the list contains more than inverters.
        """
        warnings.warn("This function may be deprecated in the future because naming is not correct, use device_list instead", DeprecationWarning)
        return self.device_list(plant_id)

    def device_list(self, plant_id):
        """
        Get a list of all devices connected to plant.
        """
        return self.plant_info(plant_id)['deviceList']

    def plant_info(self, plant_id):
        """
        Get basic plant information with device list.
        """
        response = self.session.get(self.get_url('newTwoPlantAPI.do'), params={
            'op': 'getAllDeviceListTwo',
            'plantId': plant_id,
            'pageNum': 1,
            'pageSize': 1
        })

        data = json.loads(response.content.decode('utf-8'))
        return data

    def get_plant_settings(self, plant_id):
        """
        Returns a dictionary containing the settings for the specified plant

        Keyword arguments:
        plant_id -- The id of the plant you want the settings of

        Returns:
        A python dictionary containing the settings for the specified plant
        """
        response = self.session.get(self.get_url('newPlantAPI.do'), params={
            'op': 'getPlant',
            'plantId': plant_id
        })
        data = json.loads(response.content.decode('utf-8'))
        return data
    
    def is_plant_noah_system(self, plant_id):
        """
        Returns a dictionary containing if noah devices are configured for the specified plant

        Keyword arguments:
        plant_id -- The id of the plant you want the noah devices of (str)

        Returns
        'msg'
        'result'    -- True or False
        'obj'   -- An Object containing if noah devices are configured
            'isPlantNoahSystem' -- Is the specified plant a noah system (True or False)
            'plantId'   -- The ID of the plant
            'isPlantHaveNoah'   -- Are noah devices configured in the specified plant (True or False)
            'deviceSn'  -- Serial number of the configured noah device
            'plantName' -- Friendly name of the plant
        """
        response = self.session.post(self.get_url('noahDeviceApi/noah/isPlantNoahSystem'), data={
            'plantId': plant_id
        }, verify=False)
        data = json.loads(response.content.decode('utf-8'))
        return data
    
    def noah_system_status(self, serial_number):
        """
        Returns a dictionary containing the status for the specified Noah Device

        Keyword arguments:
        serial_number -- The Serial number of the noah device you want the status of (str)

        Returns
        'msg'
        'result'    -- True or False
        'obj' -- An Object containing the noah device status
            'chargePower'   -- Battery charging rate in watt e.g. '200Watt'
            'workMode'  -- Workingmode of the battery (0 = Load First, 1 = Battery First)
            'soc'   -- Statement of charge (remaining battery %)
            'associatedInvSn'   -- ???
            'batteryNum'    -- Numbers of batterys
            'profitToday'   -- Today generated profit through noah device
            'plantId'   -- The ID of the plant
            'disChargePower'    -- Battery discharging rate in watt e.g. '200Watt'
            'eacTotal'  -- Total energy exported to the grid in kWh e.g. '20.5kWh'
            'eacToday'  -- Today energy exported to the grid in kWh e.g. '20.5kWh'
            'pac'   -- Export to grid rate in watt e.g. '200Watt'
            'ppv'   -- Solar generation in watt e.g. '200Watt'
            'alias' -- Friendly name of the noah device
            'profitTotal'   -- Total generated profit through noah device
            'moneyUnit' -- Unit of currency e.g. '€'
            'status'    -- Is the noah device online (True or False)
        """
        response = self.session.post(self.get_url('noahDeviceApi/noah/getSystemStatus'), data={
            'deviceSn': serial_number
        }, verify=False)
        data = json.loads(response.content.decode('utf-8'))
        return data
    
    def noah_info(self, serial_number):
        """
        Returns a dictionary containing the informations for the specified Noah Device

        Keyword arguments:
        serial_number -- The Serial number of the noah device you want the informations of (str)

        Returns
        'msg'
        'result'    -- True or False
        'obj' -- An Object containing the noah device informations
            'neoList'   -- A List containing Objects
            'unitList'  -- A Object containing currency units e.g. "Euro": "euro", "DOLLAR": "dollar"
            'noah'  -- A Object containing the folowing
                'time_segment'  -- A List containing Objects with configured "Operation Mode"
                    NOTE: The keys are generated numerical, the values are generated with folowing syntax "[workingmode (0 = Load First, 1 = Battery First)]_[starttime]_[endtime]_[output power]"
                    'time_segment': {
                        'time_segment1': "0_0:0_8:0_150", ([Load First]_[00:00]_[08:00]_[150 watt])
                        'time_segment2': "1_8:0_18:0_0", ([Battery First]_[08:00]_[18:00]_[0 watt])
                        ....
                     }
                'batSns'    -- A List containing all battery Serial Numbers 
                'associatedInvSn'   -- ???
                'plantId'   -- The ID of the plant
                'chargingSocHighLimit'  -- Configured "Battery Management" charging upper limit
                'chargingSocLowLimit'   -- Configured "Battery Management" charging lower limit
                'defaultPower'  -- Configured "System Default Output Power"
                'version'   -- The Firmware Version of the noah device
                'deviceSn'  -- The Serial number of the noah device
                'formulaMoney'  -- Configured "Select Currency" energy cost per kWh e.g. '0.22'
                'alias' -- Friendly name of the noah device
                'model' -- Model Name of the noah device
                'plantName' -- Friendly name of the plant
                'tempType'  -- ???
                'moneyUnitText' -- Configured "Select Currency" (Value from the unitList) e.G. "euro"
            'plantList' -- A List containing Objects containing the folowing
                'plantId'   -- The ID of the plant
                'plantImgName'  -- Friendly name of the plant Image
                'plantName' -- Friendly name of the plant
        """        
        response = self.session.post(self.get_url('noahDeviceApi/noah/getNoahInfoBySn'), data={
            'deviceSn': serial_number
        }, verify=False)
        data = json.loads(response.content.decode('utf-8'))
        return data

    def update_plant_settings(self, plant_id, changed_settings, current_settings = None):
        """
        Applies settings to the plant e.g. ID, Location, Timezone
        See README for all possible settings options

        Keyword arguments:
        plant_id -- The id of the plant you wish to update the settings for
        changed_settings -- A python dictionary containing the settings to be changed and their value
        current_settings -- A python dictionary containing the current settings of the plant (use the response from get_plant_settings), if None - fetched for you

        Returns:
        A response from the server stating whether the configuration was successful or not
        """
        #If no existing settings have been provided then get them from the growatt server
        if current_settings == None:
            current_settings = self.get_plant_settings(plant_id)

        #These are the parameters that the form requires, without these an error is thrown. Pre-populate their values with the current values
        form_settings = {
            'plantCoal': (None, str(current_settings['formulaCoal'])),
            'plantSo2': (None, str(current_settings['formulaSo2'])),
            'accountName': (None, str(current_settings['userAccount'])),
            'plantID': (None, str(current_settings['id'])),
            'plantFirm': (None, '0'), #Hardcoded to 0 as I can't work out what value it should have
            'plantCountry': (None, str(current_settings['country'])),
            'plantType': (None, str(current_settings['plantType'])),
            'plantIncome': (None, str(current_settings['formulaMoneyStr'])),
            'plantAddress': (None, str(current_settings['plantAddress'])),
            'plantTimezone': (None, str(current_settings['timezone'])),
            'plantLng': (None, str(current_settings['plant_lng'])),
            'plantCity': (None, str(current_settings['city'])),
            'plantCo2': (None, str(current_settings['formulaCo2'])),
            'plantMoney': (None, str(current_settings['formulaMoneyUnitId'])),
            'plantPower': (None, str(current_settings['nominalPower'])),
            'plantLat': (None, str(current_settings['plant_lat'])),
            'plantDate': (None, str(current_settings['createDateText'])),
            'plantName': (None, str(current_settings['plantName'])),
        }

        #Overwrite the current value of the setting with the new value
        for setting, value in changed_settings.items():
            form_settings[setting] = (None, str(value))

        response = self.session.post(self.get_url('newTwoPlantAPI.do?op=updatePlant'), files = form_settings)
        data = json.loads(response.content.decode('utf-8'))
        return data

    def update_inverter_setting(self, serial_number, setting_type, 
                                default_parameters, parameters):
        """
        Applies settings for specified system based on serial number
        See README for known working settings

        Arguments:
        serial_number -- Serial number (device_sn) of the inverter (str)
        setting_type -- Setting to be configured (str)
        default_params -- Default set of parameters for the setting call (dict)
        parameters -- Parameters to be sent to the system (dict or list of str)
                (array which will be converted to a dictionary)

        Returns:
        JSON response from the server whether the configuration was successful
        """
        settings_parameters = parameters
        
        #If we've been passed an array then convert it into a dictionary
        if isinstance(parameters, list):
            settings_parameters = {}
            for index, param in enumerate(parameters, start=1):
                settings_parameters['param' + str(index)] = param
        
        settings_parameters = {**default_parameters, **settings_parameters}

        response = self.session.post(self.get_url('newTcpsetAPI.do'), 
                                     params=settings_parameters)
        data = json.loads(response.content.decode('utf-8'))
        return data

    def update_mix_inverter_setting(self, serial_number, setting_type, parameters):
        """
        Alias for setting inverter parameters on a mix inverter
        See README for known working settings

        Arguments:
        serial_number -- Serial number (device_sn) of the inverter (str)
        setting_type -- Setting to be configured (str)
        parameters -- Parameters to be sent to the system (dict or list of str)
                (array which will be converted to a dictionary)

        Returns:
        JSON response from the server whether the configuration was successful
        """
        default_parameters = {
            'op': 'mixSetApiNew',
            'serialNum': serial_number,
            'type': setting_type
        }
        return self.update_inverter_setting(serial_number, setting_type, 
                                            default_parameters, parameters)

    def update_ac_inverter_setting(self, serial_number, setting_type, parameters):
        """
        Alias for setting inverter parameters on an AC-coupled inverter
        See README for known working settings

        Arguments:
        serial_number -- Serial number (device_sn) of the inverter (str)
        setting_type -- Setting to be configured (str)
        parameters -- Parameters to be sent to the system (dict or list of str)
                (array which will be converted to a dictionary)

        Returns:
        JSON response from the server whether the configuration was successful
        """
        default_parameters = {
            'op': 'spaSetApi',
            'serialNum': serial_number,
            'type': setting_type
        }
        return self.update_inverter_setting(serial_number, setting_type, 
                                            default_parameters, parameters)

    def update_noah_settings(self, serial_number, setting_type, parameters):
        """
        Applies settings for specified noah device based on serial number
        See README for known working settings

        Arguments:
        serial_number -- Serial number (device_sn) of the noah (str)
        setting_type -- Setting to be configured (str)
        parameters -- Parameters to be sent to the system (dict or list of str)
                (array which will be converted to a dictionary)

        Returns:
        JSON response from the server whether the configuration was successful
        """
        default_parameters = {
            'serialNum': serial_number,
            'type': setting_type
        }
        settings_parameters = parameters
        
        #If we've been passed an array then convert it into a dictionary
        if isinstance(parameters, list):
            settings_parameters = {}
            for index, param in enumerate(parameters, start=1):
                settings_parameters['param' + str(index)] = param
        
        settings_parameters = {**default_parameters, **settings_parameters}

        response = self.session.post(self.get_url('noahDeviceApi/noah/set'), 
                                     data=settings_parameters)
        data = json.loads(response.content.decode('utf-8'))
        return data