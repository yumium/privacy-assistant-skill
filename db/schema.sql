-- IoT devices of the smart home
DROP TABLE IF EXISTS devices CASCADE;
CREATE TABLE devices (
	id VARCHAR(20) NOT NULL,  -- Created with 3 first letters of manufacturer - 6 first letters of device name - numbers of python hash(f"{device_name} {manufacturer}") % 1e9 zero padded in front
	name VARCHAR(50) NOT NULL,
	manufacturer VARCHAR(30) NOT NULL,
	information TEXT,
	external_link TEXT,  -- ! Can be made rigorous with a regex
	
	PRIMARY KEY (id),
	UNIQUE (name)
);


-- Entities are all the devices in the home vicinity. Each device corresponds to one or more entities
DROP TABLE IF EXISTS entities CASCADE;
CREATE TABLE entities (
	name VARCHAR(50) PRIMARY KEY,
	device_id VARCHAR(20) REFERENCES devices(id),  -- The device this entity belongs to, if exists
	info TEXT,  -- Info string if this entity doesn’t belong to any device

	Constraint reference_chk Check(  -- Either an entity references a device or it has an info string
		(device_id IS NULL) != (info IS NULL)
	)
);


-- Source of data collection (Account data, Usage data, Body data ...)
DROP TABLE IF EXISTS data_source CASCADE;
CREATE TABLE data_source (
	name VARCHAR(50) NOT NULL,
	information TEXT NOT NULL,
	external_link TEXT,

	PRIMARY KEY (name)
);


-- Connection protocol (WiFi, LAN, ZigBee ...)
DROP TABLE IF EXISTS protocols CASCADE;
CREATE TABLE protocols (
	name VARCHAR(50) PRIMARY KEY
);


-- Data collection purposes (Ad revenue, Product development and improvment, Providing a servioce ...)
DROP TABLE IF EXISTS purposes CASCADE;
CREATE TABLE purposes (
	name VARCHAR(50) NOT NULL,
	information TEXT,

	PRIMARY KEY (name)
);


-- Intersection table relating (device, protocol) pair with their collection purpose and example connection
DROP TABLE IF EXISTS device_data_flow_example CASCADE;
CREATE TABLE device_data_flow_example (
	device_id VARCHAR(20) NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
	protocol VARCHAR(50) NOT NULL REFERENCES protocols(name) ON DELETE CASCADE,
	example TEXT,
	purpose TEXT NOT NULL,
	connects_to_internet BOOLEAN NOT NULL DEFAULT TRUE,

	PRIMARY KEY (device_id, protocol)
);


-- Intersection table relating (device, protocol) pair with edges representing the connection
DROP TABLE IF EXISTS device_data_flow_edges CASCADE;
CREATE TABLE device_data_flow_edges (
	device_id VARCHAR(20) NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
	protocol VARCHAR(50) NOT NULL REFERENCES protocols(name) ON DELETE CASCADE,
	source VARCHAR(50) NOT NULL REFERENCES entities(name) ON DELETE CASCADE,
	target VARCHAR(50) NOT NULL REFERENCES entities(name) ON DELETE CASCADE,
	edge_protocol VARCHAR(50) NOT NULL REFERENCES protocols(name) ON DELETE CASCADE,  -- We might include relevant edges that run a different protocol, but forms part of a system that uses the protocol

	PRIMARY KEY (device_id, protocol, source, target),  -- No duplicated edges given a (device_id, protocol) pair
	Constraint edge_chk Check(  -- We make canonical that edges have the smaller node (lexicographically) as source, as edges are undirected
		source <= target
	)
);


-- Data collection information for a device
DROP TABLE IF EXISTS device_data_collection CASCADE;
CREATE TABLE device_data_collection (
	device_id VARCHAR(20) NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
	data_source VARCHAR(50) NOT NULL REFERENCES data_source(name) ON DELETE CASCADE,
	example TEXT,  -- Examples of data collected on this device from this data source

	PRIMARY KEY (device_id, data_source)
);


-- Purposes for a device collecting data from a particular data source
DROP TABLE IF EXISTS device_data_collection_purpose CASCADE;
CREATE TABLE device_data_collection_purpose (
	device_id VARCHAR(20) NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
	data_source VARCHAR(50) NOT NULL REFERENCES data_source(name) ON DELETE CASCADE,
	purpose VARCHAR(50) NOT NULL REFERENCES purposes(name) ON DELETE CASCADE,

	CONSTRAINT fk_pair
		FOREIGN KEY (device_id, data_source)
			REFERENCES device_data_collection(device_id, data_source)
				ON DELETE CASCADE
);


-- Controls for data collection
DROP TABLE IF EXISTS device_data_collection_controls CASCADE;
CREATE TABLE device_data_collection_controls (
	device_id VARCHAR(20) NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
	purpose VARCHAR(50) NOT NULL REFERENCES purposes(name) ON DELETE CASCADE,
	control TEXT NOT NULL,  -- Entries with no control will not be registered

	PRIMARY KEY (device_id, purpose)
	-- Ideally we want to check that (device_id, purpose) pair is present in device_data_collection_purpose
);


-- Urgent data collection decisions
DROP TABLE IF EXISTS device_data_collection_urgent_controls CASCADE;
CREATE TABLE device_data_collection_urgent_controls (
	id SMALLSERIAL, 			-- An auto-incrementing sequence to id the urgent controls
	device_id VARCHAR(20) NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
	data_source VARCHAR(50) NOT NULL REFERENCES data_source(name) ON DELETE CASCADE,
	description TEXT NOT NULL,  -- Description of the urgent control 
	control TEXT,      			-- Control information for the urgent control. Null means no control is available

	PRIMARY KEY (id),
	CONSTRAINT fk_pair
		FOREIGN KEY (device_id, data_source)
			REFERENCES device_data_collection(device_id, data_source)
					ON DELETE CASCADE
);




-- Add user schema

DROP SCHEMA IF EXISTS client CASCADE;
CREATE SCHEMA client;
SET search_path TO public, client;

-- Devices the client owns
CREATE TABLE client.devices (
	id VARCHAR(20) PRIMARY KEY REFERENCES devices(id) ON DELETE CASCADE
);

-- Collection purposes of data collected by client's devices
CREATE TABLE client.purposes (
	name VARCHAR(50) PRIMARY KEY REFERENCES purposes(name) ON DELETE CASCADE,
	introduced BOOLEAN NOT NULL DEFAULT FALSE -- If the purpose has been introduced to the user before
);

-- Controls available for each collection purpose of each device, null if no control available for that collection purpose
CREATE TABLE client.device_data_collection_controls (
	device_id VARCHAR(20) NOT NULL REFERENCES client.devices(id) ON DELETE CASCADE,
	purpose VARCHAR(50) NOT NULL REFERENCES purposes(name) ON DELETE CASCADE,
	control TEXT,							-- If control is null, it means the device is collecting data for this purpose, but no control is available
	taken BOOLEAN NOT NULL DEFAULT FALSE,	-- If action is taken for this (device,purpose) pair

	PRIMARY KEY (device_id, purpose)
);

-- Urgent controls for the client's devices
CREATE TABLE client.device_data_collection_urgent_controls (
	id SMALLINT REFERENCES device_data_collection_urgent_controls(id) ON DELETE CASCADE,
	taken BOOLEAN NOT NULL DEFAULT FALSE, 	-- If action is taken for this urgent control

	PRIMARY KEY (id)
);

-- Client's progress on their curriculum
CREATE TABLE client.progress (
	title VARCHAR(50) NOT NULL,  -- Title of the module
	status BOOLEAN NOT NULL DEFAULT FALSE  -- Whether the user has completed it or not
);