import databaseBursts

owned_devices = [
	('Withings Body Cardio', 'Withings'),
	('Philips Hue Bulb', 'Philips'),
	('Philips Hue Bridge', 'Philips'),
	('WeMo Switch and Motion', 'Belkin')
]

DB_MANAGER = databaseBursts.dbManager()
for d in owned_devices:
	DB_MANAGER.register_device(d[0], d[1])

print("User devices registered")
