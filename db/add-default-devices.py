import databaseBursts

def copy_purpose(DB_MANAGER, client_name=None):
	if client_name is None:
		client_name = databaseBursts.CLIENT_NAME

	DB_MANAGER.execute(
		f'''
			INSERT INTO {client_name}.purposes
			SELECT DISTINCT name
			FROM purposes
		'''
	,None)

	DB_MANAGER.execute(f"INSERT INTO {client_name}.progress VALUES ('the internet')", None)
	DB_MANAGER.execute(f"INSERT INTO {client_name}.progress VALUES ('data storage and inference')", None)

# Pre: devices have been added
def initialise_progress(DB_MANAGER, client_name=None):
	if client_name is None:
		client_name = databaseBursts.CLIENT_NAME
	
	DB_MANAGER.execute(
		f'''
			INSERT INTO {client_name}.progress
			SELECT DISTINCT data_source
			FROM {client_name}.devices D, device_data_collection C
			WHERE D.id = C.device_id
		'''
	,None)


def register_device(DB_MANAGER, device_name, device_manufacturer, client_name=None): # client_name is the schema for the client
	
	if client_name is None:
		client_name = databaseBursts.CLIENT_NAME

	device_id = DB_MANAGER.execute(
		f"SELECT id FROM devices WHERE name = '{device_name}' AND manufacturer = '{device_manufacturer}'",
		None,
		all=False
	)

	if device_id is None:
		print(f"Registration failed. Device {device_name} not found in database.")
		return

	device_id = device_id[0] # The returned result from the query is a tuple of answers from each statement executed

	DB_MANAGER.execute(
		f"INSERT INTO {client_name}.devices(id) VALUES ('{device_id}')"
	,None)

	DB_MANAGER.execute(
		f'''
			INSERT INTO {client_name}.device_data_collection_controls
			SELECT DISTINCT P.device_id, P.purpose, C.control
			FROM device_data_collection_purpose P NATURAL LEFT OUTER JOIN device_data_collection_controls C
			WHERE device_id = '{device_id}'
		'''
	,None) # natural join selects rows where controls are present and (device_id,purpose) in ..._purpose. It also adds (device_id,purpose) pairs in ..._purpose but not found in ..._controls and set control to be null, which is exactly what we want. We need DISTINCT as the same (device_id,purpose) pair can exist across many data_sources.

	DB_MANAGER.execute(
		f'''
			INSERT INTO {client_name}.device_data_collection_urgent_controls
			SELECT id
			FROM device_data_collection_urgent_controls
			WHERE device_id = '{device_id}'
		'''
	,None)

def main():
	owned_devices = [
		('Withings Body Cardio', 'Withings'),
		('Philips Hue Bulb', 'Philips'),
		('WeMo Switch and Motion', 'Belkin')
	]

	DB_MANAGER = databaseBursts.dbManager()

	copy_purpose(DB_MANAGER)

	for d in owned_devices:
		register_device(DB_MANAGER, d[0], d[1])

	initialise_progress(DB_MANAGER)

if __name__ == '__main__':
	main()
	print("User devices registered")
