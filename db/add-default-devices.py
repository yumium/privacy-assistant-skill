import databaseBursts, configparser, os

IOTR_BASE = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
CONFIG_PATH = IOTR_BASE + "/config/config.cfg"

def register_device(DB_MANAGER, device_name, device_manufacturer, client_name=None): # client_name is the schema for the client
	CONFIG = configparser.ConfigParser()
	CONFIG.read(CONFIG_PATH)
	
	if client_name is None:
		client_name = CONFIG['postgresql']['client_schema']

	device_id = DB_MANAGER.execute(
		f"SELECT id FROM devices WHERE name = '{device_name}' AND manufacturer = '{device_manufacturer}'",
		None,
		all=False
	)

	if device_id is None:
		print("Registration failed. Device not found in database.")
		return

	device_id = device_id[0] # The returned result from the query is a tuple of answers from each statement executed

	DB_MANAGER.execute(
		f"INSERT INTO {client_name}.devices(id) VALUES ('{device_id}')",None
	)

	DB_MANAGER.execute(
		f'''
			INSERT INTO {client_name}.device_data_collection_controls
			SELECT DISTINCT P.device_id, P.purpose, C.control
			FROM device_data_collection_purpose P NATURAL LEFT OUTER JOIN device_data_collection_controls C
			WHERE device_id = '{device_id}'
		''',None
	) # natural join selects rows where controls are present and (device_id,purpose) in ..._purpose. It also adds (device_id,purpose) pairs in ..._purpose but not found in ..._controls and set control to be null, which is exactly what we want. We need DISTINCT as the same (device_id,purpose) pair can exist across many data_sources.

	DB_MANAGER.execute(
		f'''
			INSERT INTO {client_name}.device_data_collection_urgent_controls
			SELECT id
			FROM device_data_collection_urgent_controls
			WHERE device_id = '{device_id}'
		''',None
	)

def main():
	owned_devices = [
		('Withings Body Cardio', 'Withings'),
		('Philips Hue Bulb', 'Philips'),
		('Philips Hue Bridge', 'Philips'),
		('WeMo Switch and Motion', 'Belkin')
	]

	DB_MANAGER = databaseBursts.dbManager()

	for d in owned_devices:
		register_device(DB_MANAGER, d[0], d[1])

if __name__ == '__main__':
	main()
	print("User devices registered")
