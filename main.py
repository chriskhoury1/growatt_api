import growattServer

def get_plant_data(api, plant_id):
    try:
        # Fetch the data overview for a plant (GET request as per documentation)
        data = api.plant_overview(plant_id)
        print("Plant Data Overview:", data)
    except Exception as e:
        print(f"Error fetching plant data: {e}")

def main():
    api = growattServer.GrowattApi()
    username = 'hadyk'
    password = 'hccj1918'

    # Log in
    login_response = api.login(username, password)
    if 'user' in login_response:
        print("Login successful.")
        user_id = login_response['user']['id']
        # Replace with your actual plant ID
        plant_id = 'your_actual_plant_id'  # Change to the correct plant ID
        get_plant_data(api, plant_id)
    else:
        print("Login failed. Response:", login_response)

if __name__ == "__main__":
    main()
