-- IoT devices of the smart home

INSERT INTO devices (id, name, manufacturer)
	VALUES (
		'WIT-BODYCA-98299053',
		'Withings Body Cardio',
		'Withings'
	);

INSERT INTO devices (id, name, manufacturer)
	VALUES (
		'PHI-HUEBUL-296608048',
		'Philips Hue Bulb',
		'Philips'
	);

INSERT INTO devices (id, name, manufacturer)
	VALUES (
		'PHI-HUEBUL-258280268',
		'Philips Hue Bridge',
		'Philips'
	);

INSERT INTO devices (id, name, manufacturer)
	VALUES (
		'BEL-WEMOSW-7571896',
		'WeMo Switch and Motion',
		'Belkin'
	);




-- Entities are all the devices in the home vicinity. Each device corresponds to one or more entities

INSERT INTO entities (name) VALUES ('Withings Body Cardio');
INSERT INTO entities (name) VALUES ('Philips Hue Bridge');
INSERT INTO entities (name) VALUES ('Philips Hue Bulb');
INSERT INTO entities (name) VALUES ('WeMo Switch');
INSERT INTO entities (name) VALUES ('WeMo Motion');
INSERT INTO entities (name) VALUES ('Phone');
INSERT INTO entities (name) VALUES ('Mocha');
INSERT INTO entities (name) VALUES ('Router');
INSERT INTO entities (name) VALUES ('Internet');





-- Source of data collection (Account data, Usage data, Body data ...)

INSERT INTO data_source (name, information)
	VALUES (
		'account data',
		'Account data is the data you provide when registering for an account to use a particular product.'
	);

INSERT INTO data_source (name, information)
	VALUES (
		'usage data',
		'Usage data is data collected by logging how you interact with the device.'
	);

INSERT INTO data_source (name, information)
	VALUES (
		'body data',
		'Body data includes potentially sensitive data about your biometrics.'
	);

INSERT INTO data_source (name, information)
	VALUES (
		'third-party integration',
		'Third-party integration is about the data flow that happens between many smart home devices. For example, a smart TV can be integrated with Alexa so you can turn the TV on with your voice. Some data from the smart TV must be shared to Alexa to allow correct functionality, such as the available channels. But how Alexa uses that data is largely unknown, which can pose a privacy risk.'
	);

INSERT INTO data_source (name, information)
	VALUES (
		'third-party service',
		'A company may use services from a third-party to reduce the work they need to do themselves. For example, a company that manufactures smart doorbells might use a third-party service to manage their users accounts. That way, they do not have to build the account management system themselves. The company would need to share necessary data (like users names) for the third-party to function correctly. But how the third-party uses that data is largely unknown, which can pose a privacy risk.'
	);




-- Connection protocol (WiFi, LAN, ZigBee ...)

INSERT INTO protocols (name) VALUES ('WiFi');
INSERT INTO protocols (name) VALUES ('LAN');
INSERT INTO protocols (name) VALUES ('ZigBee');
INSERT INTO protocols (name) VALUES ('Bluetooth');  -- Not yet used in our data set



-- Data collection purposes (Ad revenue, Product development and improvment, Providing a servioce ...)

INSERT INTO purposes (name, information)
	VALUES (
		'providing a service',
		'Data is needed to provide you the relevant service. For example, a bank cannot provide financial services for you if they do not have your bank details.'
	);

INSERT INTO purposes (name, information)
	VALUES (
		'personalisation',
		'Data is used to filter information that are the most relevant to you. For example, a meal planning app might use information about your dietary requirements and meal preferences to suggest personalised meal plans for you.'
	);

INSERT INTO purposes (name, information)
	VALUES (
		'marketing',
		'Data is used to provide the most relevant marketing information about the company to you. For example, a bank may market mortgage plans to you if it knew you are in your late 20s, as it is the time most people consider buying a house.'
	);

INSERT INTO purposes (name, information)
	VALUES (
		'product feedback and improvement',
		'Data is used to learn how you use the company''s products and how you behave. This information is then used to improve the product and service.'
	);

INSERT INTO purposes (name, information)
	VALUES (
		'ad revenue',
		'Data is shared with third-party analytics providers to show personalised ads to you, and the company earns revenue based on that.'
	);

INSERT INTO purposes (name, information)
	VALUES (
		'third-party integration',
		'Data is shared with third-party devices to provide a service.'
	);






-- Intersection table relating (device, protocol) pair with their collection purpose and example connection

INSERT INTO device_data_flow_example (device_id, protocol, example, purpose)
	VALUES (
		'WIT-BODYCA-98299053',
		'WiFi',
		'each time you step on the scale and record a new weight, the data is uploaded to the server via WiFi, which can then be viewed from your phone',
		'connect to the internet and download upgrades and synchronise health data on your phone'
	);

INSERT INTO device_data_flow_example (device_id, protocol, example, purpose)
	VALUES (
		'PHI-HUEBUL-296608048',
		'ZigBee',
		'when you switch the bulbs off from your phone, the Philips Hue Bridge sends the command via ZigBee to the bulbs to turn them off',
		'receive automation commands from the Philips Hue Bridge'
	);

INSERT INTO device_data_flow_example (device_id, protocol, example, purpose)
	VALUES (
		'PHI-HUEBUL-258280268',
		'WiFi',
		'when you switch the bulbs off from your phone, your phone sends the command via WiFi to the Philips Hue Bridge, which will then turn off the bulbs',
		'receive automations and commands from the phone'
	);

INSERT INTO device_data_flow_example (device_id, protocol, purpose)
	VALUES (
		'BEL-WEMOSW-7571896',
		'WiFi',
		'connect to Belkin servers to receive automations and commands from the phone'
	);

INSERT INTO device_data_flow_example (device_id, protocol, purpose)
	VALUES (
		'BEL-WEMOSW-7571896',
		'LAN',
		'receive automations and commands from the phone'
	);





-- Intersection table relating (device, protocol) pair with edges representing the connection

INSERT INTO device_data_flow_edges (device_id, protocol, source, target, edge_protocol)
	VALUES (
		'WIT-BODYCA-98299053',
		'WiFi',
		'Withings Body Cardio',
		'Mocha',
		'WiFi'
	);

INSERT INTO device_data_flow_edges (device_id, protocol, source, target, edge_protocol)
	VALUES (
		'WIT-BODYCA-98299053',
		'WiFi',
		'Phone',
		'Mocha',
		'WiFi'
	);	


INSERT INTO device_data_flow_edges (device_id, protocol, source, target, edge_protocol)
	VALUES (
		'PHI-HUEBUL-296608048',
		'ZigBee',
		'Philips Hue Bulb',
		'Philips Hue Bridge',
		'ZigBee'
	);	

INSERT INTO device_data_flow_edges (device_id, protocol, source, target, edge_protocol)
	VALUES (
		'PHI-HUEBUL-296608048',
		'ZigBee',
		'Philips Hue Bridge',
		'Mocha',
		'WiFi'
	);	

INSERT INTO device_data_flow_edges (device_id, protocol, source, target, edge_protocol)
	VALUES (
		'PHI-HUEBUL-296608048',
		'ZigBee',
		'Phone',
		'Mocha',
		'WiFi'
	);	


INSERT INTO device_data_flow_edges (device_id, protocol, source, target, edge_protocol)
	VALUES (
		'PHI-HUEBUL-258280268',
		'WiFi',
		'Philips Hue Bridge',
		'Mocha',
		'WiFi'
	);	

INSERT INTO device_data_flow_edges (device_id, protocol, source, target, edge_protocol)
	VALUES (
		'PHI-HUEBUL-258280268',
		'WiFi',
		'Phone',
		'Mocha',
		'WiFi'
	);	


INSERT INTO device_data_flow_edges (device_id, protocol, source, target, edge_protocol)
	VALUES (
		'BEL-WEMOSW-7571896',
		'WiFi',
		'WeMo Switch',
		'Mocha',
		'WiFi'
	);	

INSERT INTO device_data_flow_edges (device_id, protocol, source, target, edge_protocol)
	VALUES (
		'BEL-WEMOSW-7571896',
		'WiFi',
		'WeMo Motion',
		'Mocha',
		'WiFi'
	);	

INSERT INTO device_data_flow_edges (device_id, protocol, source, target, edge_protocol)
	VALUES (
		'BEL-WEMOSW-7571896',
		'WiFi',
		'Phone',
		'Mocha',
		'WiFi'
	);	


INSERT INTO device_data_flow_edges (device_id, protocol, source, target, edge_protocol)
	VALUES (
		'BEL-WEMOSW-7571896',
		'LAN',
		'WeMo Switch',
		'Mocha',
		'LAN'
	);	

INSERT INTO device_data_flow_edges (device_id, protocol, source, target, edge_protocol)
	VALUES (
		'BEL-WEMOSW-7571896',
		'LAN',
		'WeMo Motion',
		'Mocha',
		'LAN'
	);	

INSERT INTO device_data_flow_edges (device_id, protocol, source, target, edge_protocol)
	VALUES (
		'BEL-WEMOSW-7571896',
		'LAN',
		'Phone',
		'Mocha',
		'LAN'
	);	





-- Data collection information for a device

INSERT INTO device_data_collection (device_id, data_source, example)
	VALUES (
		'WIT-BODYCA-98299053',
		'account data',
		'email address, birth date, name, phone number, and delivery address'
	);

INSERT INTO device_data_collection (device_id, data_source)
	VALUES (
		'WIT-BODYCA-98299053',
		'usage data'
	);

INSERT INTO device_data_collection (device_id, data_source, example)
	VALUES (
		'WIT-BODYCA-98299053',
		'body data',
		'weight, height, muscle, fat, and water percentage'
	);

INSERT INTO device_data_collection (device_id, data_source, example)
	VALUES (
		'WIT-BODYCA-98299053',
		'third-party integration',
		'MyFitnessPal, Google Fit, and Strava'
	);

INSERT INTO device_data_collection (device_id, data_source)
	VALUES (
		'WIT-BODYCA-98299053',
		'third-party service'
	);


INSERT INTO device_data_collection (device_id, data_source, example)
	VALUES (
		'PHI-HUEBUL-296608048',
		'account data',
		'full name, email, password, country, and language'
	);

INSERT INTO device_data_collection (device_id, data_source, example)
	VALUES (
		'PHI-HUEBUL-296608048',
		'usage data',
		'device log'
	);

INSERT INTO device_data_collection (device_id, data_source, example)
	VALUES (
		'PHI-HUEBUL-296608048',
		'third-party integration',
		'Alexa, Siri, and Google Home'
	);


INSERT INTO device_data_collection (device_id, data_source, example)
	VALUES (
		'BEL-WEMOSW-7571896',
		'account data',
		'username, email, and password'
	);

INSERT INTO device_data_collection (device_id, data_source, example)
	VALUES (
		'BEL-WEMOSW-7571896',
		'usage data',
		'IP, app setting, and login times'
	);

INSERT INTO device_data_collection (device_id, data_source, example)
	VALUES (
		'BEL-WEMOSW-7571896',
		'third-party service',
		'user analytics service'
	);

INSERT INTO device_data_collection (device_id, data_source, example)
	VALUES (
		'BEL-WEMOSW-7571896',
		'third-party integration',
		'Alexa, Google Home'
	);






-- Purposes for a device collecting data from a particular data source

INSERT INTO device_data_collection_purpose (device_id, data_source, purpose)
	VALUES (
		'WIT-BODYCA-98299053',
		'account data',
		'providing a service'
	);

INSERT INTO device_data_collection_purpose (device_id, data_source, purpose)
	VALUES (
		'WIT-BODYCA-98299053',
		'usage data',
		'product feedback and improvement'
	);

INSERT INTO device_data_collection_purpose (device_id, data_source, purpose)
	VALUES (
		'WIT-BODYCA-98299053',
		'body data',
		'product feedback and improvement'
	);

INSERT INTO device_data_collection_purpose (device_id, data_source, purpose)
	VALUES (
		'WIT-BODYCA-98299053',
		'body data',
		'marketing'
	);

INSERT INTO device_data_collection_purpose (device_id, data_source, purpose)
	VALUES (
		'WIT-BODYCA-98299053',
		'third-party integration',
		'third-party integration'
	);

INSERT INTO device_data_collection_purpose (device_id, data_source, purpose)
	VALUES (
		'WIT-BODYCA-98299053',
		'third-party service',
		'providing a service'
	);


INSERT INTO device_data_collection_purpose (device_id, data_source, purpose)
	VALUES (
		'PHI-HUEBUL-296608048',
		'account data',
		'providing a service'
	);

INSERT INTO device_data_collection_purpose (device_id, data_source, purpose)
	VALUES (
		'PHI-HUEBUL-296608048',
		'usage data',
		'providing a service'
	);

INSERT INTO device_data_collection_purpose (device_id, data_source, purpose)
	VALUES (
		'PHI-HUEBUL-296608048',
		'usage data',
		'product feedback and improvement'
	);

INSERT INTO device_data_collection_purpose (device_id, data_source, purpose)
	VALUES (
		'PHI-HUEBUL-296608048',
		'usage data',
		'personalisation'
	);

INSERT INTO device_data_collection_purpose (device_id, data_source, purpose)
	VALUES (
		'PHI-HUEBUL-296608048',
		'usage data',
		'marketing'
	);

INSERT INTO device_data_collection_purpose (device_id, data_source, purpose)
	VALUES (
		'PHI-HUEBUL-296608048',
		'third-party integration',
		'third-party integration'
	);


INSERT INTO device_data_collection_purpose (device_id, data_source, purpose)
	VALUES (
		'BEL-WEMOSW-7571896',
		'account data',
		'providing a service'
	);

INSERT INTO device_data_collection_purpose (device_id, data_source, purpose)
	VALUES (
		'BEL-WEMOSW-7571896',
		'usage data',
		'product feedback and improvement'
	);

INSERT INTO device_data_collection_purpose (device_id, data_source, purpose)
	VALUES (
		'BEL-WEMOSW-7571896',
		'third-party service',
		'product feedback and improvement'
	);

INSERT INTO device_data_collection_purpose (device_id, data_source, purpose)
	VALUES (
		'BEL-WEMOSW-7571896',
		'third-party service',
		'ad revenue'
	);

INSERT INTO device_data_collection_purpose (device_id, data_source, purpose)
	VALUES (
		'BEL-WEMOSW-7571896',
		'third-party integration',
		'third-party integration'
	);








-- Controls for data collection

INSERT INTO device_data_collection_controls (device_id, purpose, control)
	VALUES (
		'WIT-BODYCA-98299053',
		'personalisation',
		'Disable customisation in app'
	);

INSERT INTO device_data_collection_controls (device_id, purpose, control)
	VALUES (
		'WIT-BODYCA-98299053',
		'marketing',
		'Disable marketing from Hue or Friends of Hue in app'
	);

INSERT INTO device_data_collection_controls (device_id, purpose, control)
	VALUES (
		'WIT-BODYCA-98299053',
		'third-party integration',
		'Disable third-party connection in app'
	);


INSERT INTO device_data_collection_controls (device_id, purpose, control)
	VALUES (
		'PHI-HUEBUL-296608048',
		'marketing',
		'Disable in app on news and promotional offer'
	);

INSERT INTO device_data_collection_controls (device_id, purpose, control)
	VALUES (
		'PHI-HUEBUL-296608048',
		'product feedback and improvement',
		'Disable in app on sending data for product feedback'
	);

INSERT INTO device_data_collection_controls (device_id, purpose, control)
	VALUES (
		'PHI-HUEBUL-296608048',
		'third-party integration',
		'Disable in app for MyFitnessPal and other integrations'
	);


INSERT INTO device_data_collection_controls (device_id, purpose, control)
	VALUES (
		'BEL-WEMOSW-7571896',
		'marketing',
		'Unsubscribe from email'
	);

INSERT INTO device_data_collection_controls (device_id, purpose, control)
	VALUES (
		'BEL-WEMOSW-7571896',
		'third-party integration',
		'Disconnect from third parties in app'
	);










-- Urgent data collection decisions

INSERT INTO device_data_collection_urgent_controls (device_id, data_source, description, control)
	VALUES (
		'WIT-BODYCA-98299053',
		'third-party service',
		'Your Withings Body Cardio shares your health data to their Research Hub to help medical research and improve health and wellness of patients.',
		'You can disable this, and it will not affect the functionality of the app.'
	);

INSERT INTO device_data_collection_urgent_controls (device_id, data_source, description, control)
	VALUES (
		'PHI-HUEBUL-296608048',
		'usage data',
		'Your Philips Hue Bulbs collect your location data. They claim it is only used when strictly necessary and for functionalities, such as turning lights on and off based on time which needs location to know your time zone, or when you leave or come back from home. They claim your location data will stay in the Bridge.',
		'You can switch off location but will lose functionality to the aforementioned features.'
	);

INSERT INTO device_data_collection_urgent_controls (device_id, data_source, description)
	VALUES (
		'BEL-WEMOSW-7571896',
		'usage data',
		'Your WeMo Switch and Motion runs data inference on your device usage data to infer about your behaviour. They then use this data in advertising.'
	);



