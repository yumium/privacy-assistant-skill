from mycroft import MycroftSkill, intent_file_handler, intent_handler
from adapt.intent import IntentBuilder
from time import sleep
from mycroft.util.parse import match_one
from pyecharts import options as opts
from pyecharts.charts import Graph
from . import (gui)
from .db import (databaseBursts)

'''
To do:
- [x] Display with graph
- [ ] Refining dialog sequence
- [ ] Modularize this file --- currently all code is on one file 
- [ ] Increase variety on dialog
'''

DB_MANAGER = databaseBursts.dbManager()

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

def _find(lis,f):
    '''
    Returns the first element in the list that returns True when the element is passed to the function `f`
    Otherwise, return None
    If `lis` is empty, return None
    
    Pre: `f` is pure
    '''
    for elem in lis:
        if f(elem):
            return elem
    return None

def generate_full_graph():
    '''
        Generate the overview graph of the smart home
    '''
    nodes = []
    for n in NODES:
        if n == 'Mocha':
            nodes.append(opts.GraphNode(name='Mocha', x=100, y=300, is_fixed=True))
        elif n == 'Router':
            nodes.append(opts.GraphNode(name='Router', x=100, y=320, is_fixed=True))
        elif n == 'Internet':
            nodes.append(opts.GraphNode(name='Internet', x=100, y=340, is_fixed=True))
        else:
            nodes.append(opts.GraphNode(name=n, x=100, y=100))
    
    # Create an intermediate data structure to collate all links that share the same (source,target) pair, so their protocols can be concatenated
    collected_edges = {}
    for e in [e for d in DATABASE.keys() for p in DATABASE[d] for e in p.edges]:
        # We make canonical that the smaller name (lexicographically) is source
        source = target = None
        if e.source <= e.target:
            source = e.source; target = e.target
        else:
            source = e.target; target = e.source
            
        if (source,target) in collected_edges:
            collected_edges[(source,target)].add(e.protocol)
        else:
            collected_edges[(source,target)] = {e.protocol}
    
    links = []
    for st, ps in collected_edges.items():
        source, target = st
        links.append(opts.GraphLink(source=source, target=target, 
            label_opts=opts.LabelOpts(formatter='/'.join(sorted(ps)), position='middle')))
        
    # Links for Mocha - Router - Internet
    links.append(opts.GraphLink(source='Mocha', target='Router', linestyle_opts=opts.LineStyleOpts(color='rgb(255,0,0)')))
    links.append(opts.GraphLink(source='Router', target='Internet', linestyle_opts=opts.LineStyleOpts(color='rgb(255,0,0)')))
        
    c = (
        Graph()
        .add(
            "",
            nodes,
            links,
            is_focusnode=False,
            linestyle_opts=opts.LineStyleOpts(color='rgb(255,0,0)'),
            edge_length=50,
            repulsion=150,
            symbol_size=20
        )
    )
    
    return c
    
def generate_graph(device, protocol):
    '''
        Generate the graph for selected (`device`, `protocol`)
    '''
    selected_protocol = _find(DATABASE[device], lambda x: x.protocol == protocol)
    selected_edges = selected_protocol.edges
    selected_nodes = set()
    for e in selected_edges:
        selected_nodes.add(e.source)
        selected_nodes.add(e.target)
        
    nodes = []
    for n in NODES:
        if n == 'Mocha':
            nodes.append(opts.GraphNode(name='Mocha', x=100, y=300, is_fixed=True))
        elif n == 'Router':
            nodes.append(opts.GraphNode(name='Router', x=100, y=320, is_fixed=True))
        elif n == 'Internet':
            nodes.append(opts.GraphNode(name='Internet', x=100, y=340, is_fixed=True))
        else:
            if n in selected_nodes:
                nodes.append(opts.GraphNode(name=n, x=100, y=100))
            else:
                nodes.append(opts.GraphNode(name=n, x=100, y=100, category=0))

    links = []
    selected_links = [] #!!
    for d, ps in DATABASE.items():
        for p in ps:
            for e in p.edges:
                # When displaying for a specific pair of (device,protocol), we will only register one link for the selected link to make sure the label is correct
                if e in selected_edges and d == device and p.protocol == protocol:
                    links.append(opts.GraphLink(source=e.source, target=e.target, 
                        linestyle_opts=opts.LineStyleOpts(color='rgb(255,0,0)'),
                        label_opts=opts.LabelOpts(formatter=e.protocol, position='middle')))
                elif e not in selected_edges:
                    links.append(opts.GraphLink(source=e.source, target=e.target, 
                        linestyle_opts=opts.LineStyleOpts(color='rgb(178,190,181)')))
                    selected_links.append((e.source,e.target)) #!!
                    
    links.append(opts.GraphLink(source='Mocha', target='Router', 
        linestyle_opts=opts.LineStyleOpts(color='rgb(255,0,0)' if selected_protocol.connects_to_internet else 'rgb(178,190,181)')))
    links.append(opts.GraphLink(source='Router', target='Internet', 
        linestyle_opts=opts.LineStyleOpts(color='rgb(255,0,0)' if selected_protocol.connects_to_internet else 'rgb(178,190,181)')))
    
    categories = [
        opts.GraphCategory(
            symbol='roundRect',
            symbol_size=5,
            label_opts=opts.LabelOpts(color='rgb(178,190,181)')
        )
    ]
    
    c = (
        Graph()
        .add(
            "",
            nodes,
            links,
            categories,
            is_focusnode=False,
            edge_length=50,
            repulsion=150,
            symbol_size=20
        )
    )
    
    return (c,selected_links) #!!


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



class PrivacyAssistant(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    def initialize(self):
        events = [
            'recognizer_loop:wakeword',
            'recognizer_loop:record_begin',
            'recognizer_loop:record_end',
            'recognizer_loop:audio_output_start',
            'recognizer_loop:audio_output_end',
            'recognizer_loop:sleep',
            'recognizer_loop:wake_up'
        ]
        for evt in events:
            self.add_event(evt, self.handle_event_constructor(evt))

    def handle_assistant_privacy(self, message):
        self.speak_dialog('disclosure1',wait=True)
        sleep(1)
        self.speak_dialog('disclosure2',wait=True)
        sleep(1)
        self.speak_dialog('disclosure3',wait=True)
        sleep(1)
        self.speak_dialog('disclosure4',wait=True)

        agree = self.ask_yesno('accept.policy')
        num_tries = 1
        MAX_TRIES = 5
        while agree != 'yes' and agree != 'no' and num_tries < MAX_TRIES:
            self.speak_dialog('confused')
            agree = self.ask_yesno('accept.policy')
            num_tries += 1

        if agree == 'no':
            self.log.error('No!')
            self.speak_dialog('decline.policy')

        elif agree == 'yes':
            self.log.error('Yes!')

            self.speak_dialog('opendata1',wait=True)
            sleep(1)
            self.speak_dialog('opendata2',wait=True)
            sleep(1)
            self.speak_dialog('opendata3',wait=True)

            OPT_IN = True
            query_dialog = 'opt.out.from.in' if OPT_IN else 'opt.in.from.out'
            agree = self.ask_yesno(query_dialog)
            num_tries = 1
            MAX_TRIES = 5
            while agree != 'yes' and agree != 'no' and num_tries < MAX_TRIES:
                self.speak_dialog('confused')
                agree = self.ask_yesno(query_dialog)
                num_tries += 1

            if agree == 'yes':
                self.log.error('Yes!')
            elif agree == 'no':
                self.log.error('No!')

            self.handle_www_intro(None)

    def handle_www_intro(self, message):
        '''
        self.speak_dialog('www.intro.1',wait=True)
        sleep(1)
        self.speak_dialog('www.intro.2',wait=True)
        sleep(1)
        self.speak_dialog('www.intro.3',wait=True)
        sleep(1)
        '''

        understand = self._ask_yesno_safe('Does this makes sense?')
        if understand == 'yes':
            self.handle_www_tutoring(None)
        elif understand == 'no':
            # Display more information
            self.speak_dialog('www.intro.more.info')
            self.set_context('WWWReadingDoneContext', '')

    #@intent_handler(IntentBuilder('Start WWW Tutoring').require('done').require('WWWReadingDoneContext'))
    def handle_www_tutoring(self, message):
        self.remove_context('WWWReadingDoneContext')  # remove context to stop subsequent triggering for this handler with keywords in `done.voc`
        self.speak("Let's learn about how data flows on each device!")
        devices = [d[0] for d in DB_MANAGER.execute('SELECT name FROM devices',None)]  # output is a list of tuples, each tuple representing one row
        assert len(devices) > 0  # retrieval is successful
        
        skipped = False
        while not skipped:
            '''
            with use_scope(name='image', clear=True):
                try:
                    put_html(generate_full_graph().render_notebook())
                except:
                    put_text('Picture here')
            '''

            response = self._ask_device_selection_safe(devices, 'Which device would you like to learn next? Remember, you can say skip to skip this section')
            if response == 'skip':
                skipped = True
                self.speak('Skipped')
            else:
                # Pre: each device in the devices table has a protocol entry associated with it
                protocols = DB_MANAGER.execute(
                    f'''
                        SELECT E.protocol, E.purpose, E.example
                        FROM devices D, device_data_flow_example E
                        WHERE name = '{response}' AND D.id = E.device_id
                    '''
                ,None)
                for p in protocols:  # Go through each protocol of the device
                    '''
                    with use_scope(name='image',clear=True):
                        try:
                            self.log.error(f'Called graph API with ({response},{info.protocol})')
                            c, links = generate_graph(response, info.protocol)
                            put_html(c.render_notebook())
                        except:
                            put_text('Picture here')
                    '''

                    protocol, purpose, example = p
                    self.speak(f"The {response} {self._decorate_protocol(protocol)} to {purpose}." + (f" For example, {example}" if example else ""),wait=True) 
                    sleep(5)

    def handle_data_tutoring(self, data_source):
        self.speak(f"Welcome back! Today we will talk about {data_source}.")

        understand = self._ask_yesno_safe('Are you familiar with this concept?')
        if understand != 'no':
            self.log.error('Unsupported response')
            return
        
        self.speak(DATA_SOURCE[data_source])
        
        understand = self._ask_yesno_safe('Do you need more information?')
        if understand != 'no':
            self.log.error('Unsupported response')
            return

        relevant_devices = [device for device in DATABASE_DEVICE.keys() if data_source in DATABASE_DEVICE[device].keys()]
        # A dictionary that reverse maps each purpose to a list of devices that collects the `data_source` for that purpose
        purposes = {}
        for d in relevant_devices:
            for p in DATABASE_DEVICE[d][data_source].purpose:
                if p not in purposes:
                    purposes[p] = [d]
                else:
                    purposes[p].append(d)
        self.log.error(purposes)

        for p in list(purposes.keys()):
            self.handle_data_purpose(data_source, p, purposes[p])

        self.speak("Great work! That is it for today, come back tomorrow to learn about the next data source. You can also say “continue” to start tomorrow's material right now")


    def handle_data_purpose(self, data_source, purpose, relevant_devices):
        first_device = True
        for d in relevant_devices:
            self.speak(f"Your {d} uses {data_source} for {purpose}.")

            if first_device:
                first_device = False

                understand = self._ask_yesno_safe(f'Are you familiar with what {purpose} means?')
                if understand != 'no':
                    self.log.error('Unsupported response')
                    return

                self.speak(PURPOSE[purpose])

                understand = self._ask_yesno_safe('Do you need more information?')
                if understand != 'no':
                    self.log.error('Unsupported response')
                    return

            # No need to repeat in full if purpose was not explained
            concerned = self._ask_yesno_safe(f"Are you concerned about {d} collecting {data_source} for {purpose}?")
            if concerned == 'yes':
                self.speak("Okay.")

                disable = self._ask_yesno_safe("Would you like me to disable that? This will not change the functionality.")
                if disable != 'yes':
                    self.log.error('Unsupported response')
                    return

                if purpose in DATABASE_CONTROL[d].keys():
                    self.speak(f"I cannot do this automatically, but you can follow the instructions on screen to {DATABASE_CONTROL[d][purpose]}", wait=True)

                else:
                    self.speak("Okay. Unfortunately, there is no way to disable this. Under UK legislations, you have the right to limit how companies use your data. Would you like me to contact the firm for this feature?", wait=True)

                sleep(2)
                self.speak_dialog('congradulate')

    def handle_event_constructor(self, event):
        return lambda msg: self.handle_event(msg,event)

    def handle_event(self, message, event):
        '''
        try:
            GUI.advance(event)
        except Exception as e:
            self.log.error(e.args)
            self.log.error('An error occured!')
        '''

    # @intent_handler(IntentBuilder('Start Demo').require('unique'))
    def _test(self, message):
        response = 'WeMo Switch and Motio'
        query = f'''
                    SELECT E.protocol, E.purpose, E.example
                    FROM devices D, device_data_flow_example E
                    WHERE name = '{response}' AND D.id = E.device_id
                '''
        self.log.error(DB_MANAGER.execute(query, None))

    def _ask_device_selection(self, options, dialog='Which one would you like?',
                      data=None, min_conf=0.65):
        '''
        Read options, ask dialog question and wait for an answer. Adds 'skip' to the list of options (if the list is non-empty)

        This automatically deals with fuzzy matching (the match_one util is imported from mycroft, which is in turn imported from Lingua Franca)

        Args:
              options (list): list of options to present user
              dialog (str): a dialog ID or string to read
              data (dict): Data used to render the dialog
              min_conf (float): minimum confidence for fuzzy match, if not
                                reached return None
        Returns:
              string: list element selected by user, or None if not matched or options empty
        '''
        assert isinstance(options, list)
        assert 'skip' not in [opt.lower() for opt in options]

        if not len(options):
            return None

        resp = self.get_response(dialog=dialog, data=data)

        if resp:
            match, score = match_one(resp, options + ['skip'])
            if score < min_conf:
                resp = None
            else:
                resp = match
        return resp

    def _ask_device_selection_safe(self, devices, query, MAX_TRIES=5):
        '''     
            Queries devices but asks repeatedly until a valid response is registerd
            Returns string of list element selected or None if fails to register a response within `MAX_TRIES` # of tries
        '''
        response = self._ask_device_selection(devices, query)
        num_tries = 1
        MAX_TRIES = 5
        while response is None and num_tries < MAX_TRIES:
            self.speak_dialog('confused')
            response = self._ask_device_selection(devices, query)
            num_tries += 1

        return response

    def _combine_list(self,options):
        '''
        Pre: `options` is a non-empty list of strings
        Post: Return a string that comma seperates the elements and adds an `and` before the last element iff len(`options`) > 1
        '''
        assert len(options) > 0

        if len(options) == 1:
            return options[0]
        else:
            return ', '.join(options[:-1]) + ', and ' + options[-1]

    def _decorate_protocol(self,protocol):
        '''
        Returns the right phrase for the protocol
        Raises ValueError if the protocol is unknown
        '''
        if protocol == 'WiFi':
            return 'uses WiFi'
        elif protocol == 'ZigBee':
            return 'uses ZigBee technology'
        elif protocol == 'LAN':
            return 'connects over LAN'
        else:
            raise ValueError

    def _ask_yesno_safe(self,query,MAX_TRIES=5):
        '''     
            Queries yes/no but asks repeatedly until a yes/no response is successfully interpreted
            Returns 'yes'/'no' or None if fails to register a response within `MAX_TRIES` # of tries
        '''
        response = self.ask_yesno(query)
        num_tries = 1
        MAX_TRIES = 5
        while response != 'yes' and response != 'no' and num_tries < MAX_TRIES:
            self.speak_dialog('confused')
            response = self.ask_yesno(query)
            num_tries += 1
        
        return response if response == 'yes' or response == 'no' else None



def create_skill():
    return PrivacyAssistant()

