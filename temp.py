from graph import generate_full_graph, generate_graph
from pywebio.output import *
from gui import SimpleGUI
from time import sleep
from db import databaseBursts

def main():
	GUI = SimpleGUI()
	# GUI.put_home(0.29)
        
	GUI.put_curriculum([
		('the internet', True),
		('usage data', True),
		('account data', False),
		('body data', False),
		('third-party service', False),
		('third-party integration', False),
		('data storage and inference', False)
	])

	# DB_MANAGER = databaseBursts.dbManager()
	# device = 'Withings Body Cardio'
	# controls = DB_MANAGER.execute(f'''
  #           SELECT purpose, taken
  #           FROM client.device_data_collection_controls C, devices D
  #           WHERE D.name = '{device}' AND D.id = C.device_id
  #       ''',None)
	# GUI.put_device(device, [c[0] for c in controls if c[1]], [c[0] for c in controls if not c[1]])

	sleep(10)

if __name__ == '__main__':
	main()
