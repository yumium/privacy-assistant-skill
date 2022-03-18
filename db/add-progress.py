# Adds artificial progress in curriculum and controls taken

import databaseBursts

def main():
	DB_MANAGER = databaseBursts.dbManager()
	CLIENT_NAME = databaseBursts.CLIENT_NAME

	# curriculum
	DB_MANAGER.execute(f"UPDATE {CLIENT_NAME}.progress SET status = TRUE WHERE title = 'the internet'", None)
	DB_MANAGER.execute(f"UPDATE {CLIENT_NAME}.progress SET status = TRUE WHERE title = 'usage data'", None)

	# urgent controls
	DB_MANAGER.execute(f"UPDATE {CLIENT_NAME}.device_data_collection_urgent_controls SET taken = TRUE WHERE id = 2", None)  # Location data for Philips Hue Bulb

	# standard controls
	DB_MANAGER.execute(f"UPDATE {CLIENT_NAME}.device_data_collection_controls SET taken = TRUE WHERE device_id = 'PHI-HUEBUL-296608048' AND purpose = 'marketing'", None)
	#DB_MANAGER.execute(f"UPDATE {CLIENT_NAME}.device_data_collection_controls SET taken = TRUE WHERE device_id = 'PHI-HUEBUL-296608048' AND purpose = 'personalisation'", None)
	DB_MANAGER.execute(f"UPDATE {CLIENT_NAME}.device_data_collection_controls SET taken = TRUE WHERE purpose = 'product feedback and improvement'", None)

if __name__ == '__main__':
	main()
	print('Artificial progress logged')