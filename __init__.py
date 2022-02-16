from mycroft import MycroftSkill, intent_file_handler, intent_handler
from adapt.intent import IntentBuilder
from time import sleep
from mycroft.util.parse import match_one
from pywebio.output import *
from pyecharts import options as opts
from pyecharts.charts import Graph

class SimpleGUI:
    def __init__(self):
        self.states = ['stand_by','recording','thinking','speaking']
        self.current_state = 'stand_by'
        self._update_text('Stand by')

    # @use_scope('main', clear=True)
    def display(self, event):
        clear()

        if event == 'recognizer_loop:wakeword':
            put_text('Wake word recognized!')
        elif event == 'recognizer_loop:record_begin':
            put_text('Recording starts')
        elif event == 'recognizer_loop:record_end':
            put_text('Recording ends')
        elif event == 'recognizer_loop:audio_output_start':
            put_text('Speaking starts')
        elif event == 'recognizer_loop:audio_output_end':
            put_text('Speaking ends')
        elif event == 'recognizer_loop:sleep':
            put_text('Sleeping zzz')
        elif event == 'recognizer_loop:wake_up':
            put_text('Woke up!')

    def advance(self, event):
        if event == 'recognizer_loop:wakeword':
            return

        if self.current_state == 'stand_by' and event == 'recognizer_loop:record_begin':
            self._set_state('recording')
            self._update_text('Recording')
        elif self.current_state == 'stand_by' and event == 'recognizer_loop:audio_output_start':
            self._set_state('speaking')
            self._update_text('Speaking')
        elif self.current_state == 'recording' and event == 'recognizer_loop:record_end':
            self._set_state('thinking')
            self._update_text('Thinking')
        elif self.current_state == 'thinking' and event == 'recognizer_loop:audio_output_start':
            self._set_state('speaking')
            self._update_text('Speaking')
        elif self.current_state == 'speaking' and event == 'recognizer_loop:audio_output_end':
            self._set_state('stand_by')
            self._update_text('Stand by')
        else:
            print(f"Unknown pattern: handling event {event} at state {self.current_state}")

    def _set_state(self, new_state):
        assert new_state in self.states
        self.current_state = new_state

    @use_scope(name='main',clear=True)
    def _update_text(self, txt):
        #clear()
        put_text(txt)

'''
To do:
- [ ] Display with graph
- [ ] Refining dialog sequence
'''

GUI = SimpleGUI()

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

    @intent_handler(IntentBuilder('Start Demo').require('unique'))
    def handle_www_intro(self, message):
        '''
        self.speak_dialog('www.intro.1',wait=True)
        sleep(1)
        self.speak_dialog('www.intro.2',wait=True)
        sleep(1)
        self.speak_dialog('www.intro.3',wait=True)
        sleep(1)
        '''

        understand = self.ask_yesno('Does this makes sense?')
        num_tries = 1
        MAX_TRIES = 5
        while understand != 'yes' and understand != 'no' and num_tries < MAX_TRIES:
            self.speak_dialog('confused')
            understand = self.ask_yesno('Does what I said make sense to you?')
            num_tries += 1

        if understand == 'yes':
            self.handle_www_tutoring(None)

        elif understand == 'no':
            # Display more information
            self.speak_dialog('www.intro.more.info')
            self.set_context('WWWReadingDoneContext', '')

    @intent_handler(IntentBuilder('Start WWW Tutoring').require('done').require('WWWReadingDoneContext'))
    def handle_www_tutoring(self, message):
        '''
            DATABASE = {
                'Withings Smart Scale': [],
                'Philips Hue Bulbs': [],
                'Philips Hue Bridge': [],
                'WeMo Switch and Motion': []
            }
        '''
        self.remove_context('WWWReadingDoneContext')  # remove context to stop subsequent triggering for this handler with keywords in `done.voc`
        self.speak("Let's learn about how data flows on each device!")
        skipped = False
        while not skipped:
            with use_scope(name='image', clear=True):
                try:
                    put_html(generate_full_graph().render_notebook())
                except:
                    put_text('Picture here')

            response = self._ask_device_selection(list(DATABASE.keys()), 'Which device would you like to learn next? Remember, you can say skip to skip this section')
            while response is None:
                self.speak_dialog('confused')
                response = self._ask_device_selection(list(DATABASE.keys()), 'Which device would you like to learn next? Remember, you can say skip to skip this section')

            if response == 'skip':
                skipped = True
                self.speak('Skipped')
            else:
                for info in DATABASE[response]:  # Go through each protocol of the device
                    with use_scope(name='image',clear=True):
                        try:
                            self.log.error(f'Called graph API with ({response},{info.protocol})')
                            c, links = generate_graph(response, info.protocol)
                            put_html(c.render_notebook())
                        except:
                            put_text('Picture here')
                    self.speak(f"The {response} {self._decorate_protocol(info.protocol)} to {self._combine_list(info.purpose)}." + (f" For example, {info.example}" if info.example else ""),wait=True) 
                    sleep(5)

    def handle_event_constructor(self, event):
        return lambda msg: self.handle_event(msg,event)

    def handle_event(self, message, event):
        try:
            GUI.advance(event)
        except Exception as e:
            self.log.error(e.args)
            self.log.error('An error occured!')


    #@intent_handler(IntentBuilder('Start Demo').require('unique'))
    def _test(self, message):
        with use_scope(name='image',clear=True):
            try:
                c, links = generate_graph('Philips Hue Bridge', 'WiFi')
                self.log.error(links)
                put_html(c.render_notebook())
            except:
                put_text('Picture here')
        self.speak('')

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

def create_skill():
    return PrivacyAssistant()

