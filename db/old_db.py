# The old ad-hoc python structure for types

DATABASE = {
    'Withings Smart Scale': [],
    'Philips Hue Bulbs': [],
    'Philips Hue Bridge': [],
    'WeMo Switch and Motion': []
}

DEVICES = {
    'Withings Smart Scale',
    'Philips Hue Bridge',
    'Philips Hue Bulb',
    'WeMo Switch',
    'WeMo Motion'
}

NODES = {
    'Phone',
    'Mocha',
    'Router',
    'Internet'
} | DEVICES

class ProtocolInfo():
    def __init__(self, protocol, purpose, edges, example=None, connects_to_internet=True):
        self.protocol = protocol
        self.purpose = purpose
        self.edges = edges
        self.example = example
        self.connects_to_internet = connects_to_internet
    
class Edge():
    def __init__(self, source, target, protocol):
        self.source = source
        self.target = target
        self.protocol = protocol

    # This is necessary for the edge comparison in generate_graph. Note edges are undirected
    def __eq__(self,other):
        return self.source == other.source and self.target == other.target or self.source == other.target and self.target == other.source
    
    def __str__(self):
        return f"Edge from {self.source} to {self.target}"

DATABASE['Withings Smart Scale'].append(ProtocolInfo(
    protocol='WiFi',
    purpose=['connect to the internet and download upgrades','synchronise health data on your phone'],
    edges=[
        Edge('Withings Smart Scale','Mocha','WiFi'),
        Edge('Mocha','Phone','WiFi')
    ],
    example='each time you step on the scale and record a new weight, the data is uploaded to the server via WiFi, which can then be viewed from your phone'
))

DATABASE['Philips Hue Bulbs'].append(ProtocolInfo(
    protocol='ZigBee',
    purpose=['receive automation commands from the Philips Hue Bridge'],
    edges=[
        Edge('Philips Hue Bulb','Philips Hue Bridge','ZigBee'),
        Edge('Philips Hue Bridge','Mocha','WiFi'),
        Edge('Mocha','Phone','WiFi')
    ],
    example='when you switch the bulbs off from your phone, the Philips Hue Bridge sends the command via ZigBee to the bulbs to turn them off'
))

DATABASE['Philips Hue Bridge'].append(ProtocolInfo(
    protocol='WiFi',
    purpose=['receive automations and commands from the phone'],
    edges=[
        Edge('Philips Hue Bridge','Mocha','WiFi'),
        Edge('Mocha','Phone','WiFi')
    ],
    example='when you switch the bulbs off from your phone, your phone sends the command via WiFi to the Philips Hue Bridge, which will then turn off the bulbs'
))

DATABASE['WeMo Switch and Motion'].append(ProtocolInfo(
    protocol='WiFi',
    purpose=['connect to Belkin servers to receive automations and commands from the phone'],
    edges=[
        Edge('WeMo Switch','Mocha','WiFi'),
        Edge('WeMo Motion','Mocha','WiFi'),
        Edge('Phone','Mocha','WiFi')
    ]
))

DATABASE['WeMo Switch and Motion'].append(ProtocolInfo(
    protocol='LAN',
    purpose=['receive automations and commands from the phone'],
    edges=[
        Edge('WeMo Switch','Mocha','LAN'),
        Edge('WeMo Motion','Mocha','LAN'),
        Edge('Phone','Mocha','LAN')
    ],
    connects_to_internet=False
))



## ----DATABASES FOR DATA COLLECTION---- ##
class DataSourceInfo():
    def __init__(self,example,purpose,urgent_controls):
        self.example = example
        self.purpose = purpose
        self.urgent_controls = urgent_controls

class UrgentControlInfo():
    def __init__(self,description,control):
        self.description = description
        # Control of an empty string means no control is available
        self.control = control

'''
    A database for different types of data collected by devices

    Schema:
    Device | Data Source | Example | Purpose | URGENT CONTROLS (data source . description . control)
'''
DATABASE_DEVICE = {
    'Withings Smart Scale': {
        'Account data': DataSourceInfo(
            example="email address, birth date, name, phone number, and delivery address",
            purpose=['Providing a service'],
            urgent_controls=[]
        ),

        'Usage data': DataSourceInfo(
            example="",
            purpose=['Product feedback and improvement'],
            urgent_controls=[]
        ),

        'Body data': DataSourceInfo(
            example="weight, height, muscle, fat, and water percentage",
            purpose=['Product feedback and improvement', 'Marketing'],
            urgent_controls=[]
        ),

        'Third-party integration': DataSourceInfo(
            example="MyFitnessPal, Google Fit, and Strava",
            purpose=['Providing a service'],
            urgent_controls=[]
        ),

        'Third-party service': DataSourceInfo(
            example="",
            purpose=['Providing a service'],
            urgent_controls=[
                UrgentControlInfo(
                    description="Your shares your health data to their Research Hub to help medical research and improve everyone's health and wellness.",
                    control="You can disable this, and it will not affect the functionality of the app."
                )
            ]
        )
    },

    'Philips Hue Bulbs': {
        'Account data': DataSourceInfo(
            example="full name, email, password, country, and language",
            purpose=['Providing a service'],
            urgent_controls=[]
        ),

        'Usage data': DataSourceInfo(
            example="device log",
            purpose=['Providing a service', 'Product feedback and improvement', 'Personalisation', 'Marketing'],
            urgent_controls=[
                UrgentControlInfo(
                    description="Your Philips Hue Bulbs collect your location data. They claim it is only used when strictly necessary and for functionalities, such as turning lights on and off based on time which needs location to know your time zone, or when you leave or come back from home. They claim your location data will stay in the Bridge.",
                    control="You can switch off location but will lose functionality to the aforementioned features."
                )
            ]
        ),

        'Third-party integration': DataSourceInfo(
            example="Alexa, Siri, and Google Home",
            purpose=['Providing a service'],
            urgent_controls=[]
        )
    },

    'WeMo Switch and Motion': {
        'Account data': DataSourceInfo(
            example="username, email, and password",
            purpose=['Providing a service'],
            urgent_controls=[]
        ),

        'Usage data': DataSourceInfo(
            example="IP, app setting, and login times",
            purpose=['Product feedback and improvement'],
            urgent_controls=[
                UrgentControlInfo(
                    description="Your WeMo Switch and Motion runs data inference on your device usage data to infer about your behaviour. They then use this data in advertising.",
                    control=""
                )
            ]
        ),

        'Third-party service': DataSourceInfo(
            example="user analytics service",
            purpose=['Product feedback and improvement', 'Ad revenue'],
            urgent_controls=[]
        ),

        'Third-party integration': DataSourceInfo(
            example="Alexa, Google Home",
            purpose=['Providing a service'],
            urgent_controls=[]
        )
    }
}
 
'''
    A database for controls available on devices

    Schema:
    Device | Purpose | Control

    Semantics:
    I have decided so that missing entries for purpose means either device isn't collecting data for tha purpose or it is but no controls are available
'''
DATABASE_CONTROL = {
    'Withings Smart Scale': {
        'Personalisation': "Disable customisation in app",
        'Marketing': "Disable marketing from Hue or Friends of Hue in app",
        'Third-party integration': "Disable third-party connection in app"
    },

    'Philips Hue Bulbs': {
        'Marketing': "Disable in app on news and promotional offer",
        'Product feedback and improvement': "Disable in app on sending data for product feedback",
        'Third-party integration': "Disable in app for MyFitnessPal and other integrations",
        'Third-party service': "Disable in app for Research Lab"
    },

    'WeMo Switch and Motion': {
        'Marketing': "Unsubscribe from email",
        'Third-party integration': "Disconnect from third parties in app"
    }
}

'''
    A database for data source information

    Schema:
    DATA SOURCE NAME | DATA SOURCE INFORMATION
'''
DATA_SOURCE = {
    'Account data': "Your account data is the data you provide when registering for an account to use a particular product.",

    'Usage data': "Usage data is data collected by logging how you interact with the device. Usage data is used for a variety number of purposes.",

    'Body data': "Body data includes potentially sensitive data about your biometrics.",

    'Third-party integration': "Third-party integration is about the data flow that happens between many smart home devices. For example, a smart TV can be integrated with Alexa so you can turn the TV on with your voice. Some data from the smart TV must be shared to Alexa to allow correct functionality, such as the available channels. But how Alexa (the third-party) uses that data is largely unknown, which can pose a privacy risk.",

    'Third-party service': "A company may use services from a third-party to reduce the work they need to do themselves. For example, a company that manufactures smart doorbells might use a third-party service to manage their users' accounts. That way, they don't have to build the account management system themselves. The company would need to share necessary data (like users' names) for the third-party to function correctly. But how Alexa the third-party uses that data is largely unknown, which can pose a privacy risk."
}

'''
    A database for collection purpose information

    Schema:
    PURPOSE NAME | PURPOSE INFORMATION
'''
PURPOSE = {
    'Providing a service': "Data is needed to provide you the relevant service. For example, a bank cannot provide financial services for you if they don't have your bank details.",

    'Personalisation': "Data is used to filter information that are the most relevant to you. For example, a meal planning app might use information about your dietary requirements and meal preferences to suggest personalised meal plans for you",

    'Marketing': "Data is used to provide the most relevant marketing information about the company to you. For example, a bank may market mortgage plans to you if it knew you are in your late 20s --- the time most people consider buying a house",

    'Product feedback and improvement': "Data is used to learn how you use the company's products and how you behave. This information is then used to improve the product and service.",

    'Ad revenue': "Data is shared with third-party analytics providers to show personalised ads to you, and the company earns revenue based on that"
}

