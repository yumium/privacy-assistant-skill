from xml.dom.pulldom import parseString
from mycroft import MycroftSkill, intent_handler
from adapt.intent import IntentBuilder
from time import sleep
from mycroft.util.parse import match_one
from . import (gui, graph)
from .db import (databaseBursts)
from os.path import join as osjoin
import string

DB_MANAGER = databaseBursts.dbManager()
CLIENT_NAME = databaseBursts.CLIENT_NAME
GUI = gui.SimpleGUI()
MASTER_CURRICULUM = [  # Order of curriculum for all data source. Actual user curriculum will be a subsequence of this.
    'the internet',
    'usage data',
    'account data',
    'body data',
    'financial data',  # hypothetical data source
    'third-party service',
    'third-party integration',
    'data storage and inference'
]
CURRICULUM_DIR = 'curriculum'

class PrivacyAssistant(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        self._locvars = {} # A dictionary of local variables for context storage during user confirmation
        self.curriculum = [] # Personalised curriculum based on users' devices

    def _set_locvar(self, key,value):
        assert isinstance(key, str)
        self._locvars[key] = value

    def _get_locvar(self, key):
        assert key in self._locvars
        return self._locvars[key]

    def _remove_locvars(self, *args):
        for arg in args:
            if arg in self._locvars:
                del self._locvars[arg]

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

        self.add_devices()

    # Displays dashboard
    def show_home(self):
        num_finished = DB_MANAGER.execute(f"SELECT COUNT(*) FROM {CLIENT_NAME}.progress WHERE status = TRUE", None)[0][0]
        num_total = len(self.curriculum)
        GUI.put_home(round(num_finished / num_total, 2))

    # Displays progress in curriculum
    def show_curriculum(self):
        curriculum = DB_MANAGER.execute(f"SELECT * FROM {CLIENT_NAME}.progress",None)  # The list of pairs of curriculum items with a boolean representing if the user has finished it or not
        curriculum.sort(key=lambda x: self.curriculum.index(x[0]))  # Sort based on order in self.curriculum
        GUI.put_curriculum(curriculum)

    # Displays current control in device
    def show_device(self, device):
        controls = DB_MANAGER.execute(f'''
            SELECT purpose, taken
            FROM {CLIENT_NAME}.device_data_collection_controls C, devices D
            WHERE D.name = '{device}' AND D.id = C.device_id
        ''',None)
        GUI.put_device(device, [c[0] for c in controls if c[1]], [c[0] for c in controls if not c[1]])

    # !!! Slight issue with this. We just lack a good framework for handling flows ...
    def handle_module(self, module):
        assert module in self.curriculum

        callback = None  # The continuation for the curriculum
        if module == 'the internet':
            callback = self.handle_assistant_privacy
        elif module == 'data storage and inference':
            callback = self.handle_storage_and_data
        else:
            callback = lambda: self.handle_data_tutoring_data_source_intro(module)
        
        callback()
        # Log completion of module
        DB_MANAGER.execute(f"UPDATE {CLIENT_NAME}.progress SET status = TRUE WHERE title = '{module}'", None)

    @intent_handler(IntentBuilder('Start Demo').require('start').require('demo'))
    def handle_assistant_privacy(self, message):
        self.speak('Starting demo',wait=True); sleep(1)
        self.speak_dialog('startup.intro',wait=True)

        GUI.put_disclosure()
        self.speak_dialog('disclosure1',wait=True)
        sleep(1)
        self.speak_dialog('disclosure2',wait=True)
        sleep(1)
        self.speak_dialog('disclosure3',wait=True)
        sleep(1)
        self.speak_dialog('disclosure4',wait=True)

        agree = self._ask_yesno_safe('accept.policy')
        if agree is None:
            self.speak_dialog('error')
            return
        elif agree == 'no':
            self.speak_dialog('decline.policy')
        elif agree == 'yes':
            GUI.put_open_data()
            self.speak_dialog('opendata1',wait=True)
            sleep(1)
            self.speak_dialog('opendata2',wait=True)
            sleep(1)
            self.speak_dialog('opendata3',wait=True)

            OPT_IN = True
            query_dialog = 'opt.out.from.in' if OPT_IN else 'opt.in.from.out'
            agree = self._ask_yesno_safe(query_dialog)

            if agree is None:
                self.speak_dialog('error')
                return
            elif agree == 'yes':
                self.speak_dialog('acknowledge')
                self.speak_dialog('onscreen.instructions')
                self._put_md('open-data-project.md')
                self.set_context('DemoPartOneDone')
            elif agree == 'no':
                self.speak_dialog('acknowledge')
                self.set_context('DemoPartOneDone')

    # A fictitious process that simulate the client adding devices
    def add_devices(self):
        data_sources = [d[0] for d in DB_MANAGER.execute(f'SELECT title FROM {CLIENT_NAME}.progress', None)]
        self.curriculum = self._sort_merge(MASTER_CURRICULUM, data_sources + ['the internet', 'data storage and inference'])

    def _sort_merge(self, big, small):
        '''
            Pre: `small` is a subset of `big` AND all elements in `big` and `small` are unique
            Post: A subsequence of `big` that contains only the elements in `small`
            (the algorithm is naive, assuming small `big` and `small` sizes)
        '''
        return [x for x in big if x in small]

    @intent_handler(IntentBuilder('Internet Intro').require('start').require('part').require('two'))
    def handle_internet_intro(self, message):
        self.remove_context('DemoPartOneDone')

        GUI.put_module(1, 'The Internet')
        self.speak_dialog('internet.intro.0',wait=True)
        GUI.put_graph(graph.generate_full_graph())
        sleep(1)
        self.speak_dialog('internet.intro.1',wait=True)
        sleep(1)
        self.speak_dialog('internet.intro.2',wait=True)
        sleep(1)
        self.speak_dialog('internet.intro.3',wait=True)
        sleep(1)

        understand = self._ask_yesno_safe('query.make.sense')
        if understand is None:
            self.speak_dialog('error')
            return
        elif understand == 'yes':
            self.handle_internet_tutoring(None)
        elif understand == 'no':
            self._put_md('the-internet.md')
            self.speak_dialog('more.info')
            self.set_context('InternetReadingDoneContext')

    @intent_handler(IntentBuilder('Start Internet Tutoring').require('done').require('InternetReadingDoneContext'))
    def handle_internet_tutoring(self, message):
        self.remove_context('InternetReadingDoneContext')  # remove context to stop subsequent triggering for this handler with keywords in `done.voc`
        self.speak_dialog('internet.intro.intro')
        entities = [d[0] for d in DB_MANAGER.execute('SELECT name FROM entities',None)]  # output is a list of tuples, each tuple representing one row
        assert len(entities) > 0  # retrieval is successful
        
        skipped = False
        while not skipped:
            GUI.put_graph(graph.generate_full_graph())

            response = self._ask_device_selection_safe(entities, 'query.internet.device')
            if response == 'skip':
                skipped = True
                self.set_context('DemoPartTwoDone')
                self.speak("Got it, moving on to the next section.")
            else:
                if (response,) in DB_MANAGER.execute("SELECT name FROM entities WHERE device_id IS NULL", None):  # The entity does not belong to any device
                    info = DB_MANAGER.execute(f"SELECT info FROM entities WHERE name = '{response}'", None)[0][0]
                    self.speak(info)
                else:
                    # Pre: each device in the devices table has a protocol entry associated with it
                    protocols = DB_MANAGER.execute(
                        f'''
                            SELECT D.name, X.protocol, X.purpose, X.example
                            FROM entities E, devices D, device_data_flow_example X
                            WHERE E.name = '{response}' AND E.device_id = X.device_id AND E.device_id = D.id
                        '''
                    ,None)
                    for p in protocols:  # Go through each protocol of the device
                        device, protocol, purpose, example = p
                        GUI.put_graph(graph.generate_graph(device, protocol))
                        self.speak(f"The {device} {self._decorate_protocol(protocol)} to {purpose}." + (f" For example, {example}" if example else ""),wait=True) 
                        sleep(3)

    @intent_handler(IntentBuilder('Start Data Source Tutoring').require('start').require('part').require('three'))
    def demo_start_part_3(self, message):
        self.remove_context('DemoPartTwoDone')
        self.handle_data_tutoring_data_source_intro('usage data')

    def handle_data_tutoring_data_source_intro(self, data_source):
        assert data_source in self.curriculum

        self.speak(f"Let's learn in more detail about how data is collected and used in your smart home devices. First, let's talk about {data_source}.")
        GUI.put_module(self.curriculum.index(data_source) + 1, string.capwords(data_source))

        understand = self._ask_yesno_safe('query.familiar')
        if understand is None:
            self.speak_dialog('error')
            return
        elif understand == 'no':
            self.speak(DB_MANAGER.execute(f"SELECT information FROM data_source WHERE name = '{data_source}'",None)[0][0], wait=True)
            sleep(1)
            more_info = self._ask_yesno_safe('query.more.info')
            if more_info is None:
                self.speak_dialog('error')
                return
            elif more_info == 'yes':
                self._put_md(osjoin('data-sources', data_source.replace(' ', '-') + '.md'))
                self.speak_dialog('more.info')
                self.set_context('PurposeIntroContext')
                self._set_locvar('DataSourceContext',data_source)
            else:
                self.handle_data_tutoring_purpose_intro2(data_source)
        else:
            self.handle_data_tutoring_purpose_intro2(data_source)
    
    @intent_handler(IntentBuilder('Continue purpose intro').require('done').require('PurposeIntroContext'))
    def handle_data_tutoring_purpose_intro(self, message):
        self.remove_context('PurposeIntroContext')
        data_source = self._get_locvar('DataSourceContext')
        self._remove_locvars('DataSourceContext')
        self.handle_data_tutoring_purpose_intro2(data_source)

    def handle_data_tutoring_purpose_intro2(self, data_source):
        # A dictionary that reverse maps each purpose to a list of devices that collects the `data_source` for that purpose
        purposes = dict(DB_MANAGER.execute(
        f'''
            SELECT purpose, array_agg(name)
            FROM device_data_collection_purpose P, devices D
            WHERE P.data_source = '{data_source}' AND D.id = P.device_id
            GROUP BY purpose;
        '''
        ,None))
        self._set_locvar('Purposes', purposes)  # The `purposes` dictionary
        self._set_locvar('PurposeList', sorted(list(purposes.keys()), key=self._get_purpose_percentage))  # The remaining list of purposes to go through, sorted from low to high priority so highest priority is popped first

        urgents = DB_MANAGER.execute(
        f'''
            SELECT C.id, D.name, C.data_source, C.description, C.control
            FROM device_data_collection_urgent_controls C, devices D
            WHERE C.device_id = D.id AND C.data_source = '{data_source}'
        '''
        ,None)

        self._set_locvar('Urgents',urgents)
        self.handle_next_urgent_control(data_source)


    def _get_purpose_percentage(self, purpose):
        '''
            Returns a float that is the percentage of times a user disabled data collection for `purpose`
        '''
        a = DB_MANAGER.execute(f"SELECT COUNT(*) FROM {CLIENT_NAME}.device_data_collection_controls WHERE purpose = '{purpose}' AND taken = TRUE", None)[0][0]
        b = DB_MANAGER.execute(f"SELECT COUNT(*) FROM {CLIENT_NAME}.device_data_collection_controls WHERE purpose = '{purpose}'", None)[0][0]
        try:
            assert b > 0
        except:
            self.log.error(f"a = {a}, b = {b}, purpose = {purpose}")
            return 0
        return a / b

    def handle_next_urgent_control(self, data_source):
        self.remove_context('NextUrgentControlContext')

        urgents = self._get_locvar('Urgents')
        if len(urgents) == 0:  # All urgent controls have been taken care of
            self._remove_locvars('Urgents')
            p = self._get_locvar('PurposeList').pop()  # Begin non-urgent controls
            self.handle_data_purpose_intro(data_source, p, self._get_locvar('Purposes')[p])
        else:
            self.handle_urgent_control(*urgents.pop())

    @intent_handler(IntentBuilder('Continue urgent control').require('done').require('NextUrgentControlContext'))
    def handle_next_urgent_control_continue(self, message):
        self.remove_context('NextUrgentControlContext')
        data_source = self._get_locvar('data_source')
        self._remove_locvars('data_source')

        self.handle_next_urgent_control(data_source)

    def handle_urgent_control(self, urgent_id, device_name, data_source, description, control):
        self.speak_dialog('urgent.worried')
        GUI.put_urgent(description)
        self.speak(description, wait=True); sleep(1)

        response = None
        if control is None:
            self.speak_dialog('no.control', wait=True); sleep(1)
            response = self._ask_yesno_safe('query.firm.for.control')
        else:
            self.speak(control, wait=True); sleep(1)
            response = self._ask_yesno_safe('query.disable')
        
        if response is None:
            self.speak_dialog('error',wait=True)
        elif response == 'yes':
            # Log the control being taken
            DB_MANAGER.execute(f"UPDATE {CLIENT_NAME}.device_data_collection_urgent_controls SET taken = TRUE WHERE id = {urgent_id}",None)

            if control is None:
                self.speak_dialog('done',wait=True)
            else:
                self._put_md(osjoin('urgent-control', str(urgent_id) + '.md'))
                self.speak_dialog('onscreen.instructions')
                self._set_locvar('data_source', data_source)
                self.set_context('NextUrgentControlContext')
                return
        else:
            self.speak_dialog('acknowledge',wait=True)
        sleep(2)
        self.handle_next_urgent_control(data_source)

    def handle_data_purpose_intro(self, data_source, purpose, relevant_devices):
        purpose_introduced = DB_MANAGER.execute(f"SELECT introduced FROM {CLIENT_NAME}.purposes WHERE name = '{purpose}'", None)[0][0]
        GUI.put_dp(data_source, purpose)
        self.speak_dialog('data.purpose.intro', {'data_source': data_source, 'purpose': purpose})
        if purpose_introduced:
            remember = self._ask_yesno_safe('query.purpose.remember', {'purpose': purpose})
            if remember is None:
                self.speak_dialog('error')
                return
            elif remember == 'no':
                self.speak(DB_MANAGER.execute(f"SELECT information FROM purposes WHERE name = '{purpose}'",None)[0][0])

            self.handle_data_purpose2(data_source, purpose, relevant_devices)
        else:
            DB_MANAGER.execute(f"UPDATE {CLIENT_NAME}.purposes SET introduced = TRUE WHERE name = '{purpose}'", None)  # Set purpose to be introduced
            familiar = self._ask_yesno_safe('query.purpose.familiar', {'purpose': purpose})
            if familiar is None:
                self.speak_dialog('error')
                return
            elif familiar == 'no':
                self.speak(DB_MANAGER.execute(f"SELECT information FROM purposes WHERE name = '{purpose}'",None)[0][0])
                sleep(1)
                more_info = self._ask_yesno_safe('query.more.info')
                if more_info is None:
                    self.speak_dialog('error')
                    return
                elif more_info == 'yes':
                    self._put_md(osjoin('collection-purposes', purpose.replace(' ','-') + '.md'))
                    self.speak_dialog('more.info')
                    self.set_context('PurposeContinueContext')
                    self._set_locvar('DataSourceContext',data_source)
                    self._set_locvar('PurposeContext',purpose)
                    self._set_locvar('RelevantDevicesContext',relevant_devices)
                else:
                    self.handle_data_purpose2(data_source, purpose, relevant_devices)
            else:
                self.handle_data_purpose2(data_source, purpose, relevant_devices)

    @intent_handler(IntentBuilder('Continue purpose').require('done').require('PurposeContinueContext'))
    def handle_data_purpose(self,messge):
        self.remove_context('PurposeContinueContext')

        data_source = self._get_locvar('DataSourceContext')
        purpose = self._get_locvar('PurposeContext')
        relevant_devices = self._get_locvar('RelevantDevicesContext')

        self._remove_locvars('DataSourceContext', 'PurposeContext', 'RelevantDevicesContext')
        self.handle_data_purpose2(data_source, purpose, relevant_devices)


    def handle_data_purpose2(self, data_source, purpose, relevant_devices):
        for d in relevant_devices:
            # No need to repeat in full if purpose was not explained
            GUI.put_ddp(d, data_source, purpose)
            concerned = self._ask_yesno_safe('query.concern',{'device': d, 'data_source': data_source, 'purpose': purpose})
            if concerned is None:
                self.speak_dialog('error')
                return
            elif concerned == 'yes':
                self.speak_dialog('acknowledge')

                disable = self._ask_yesno_safe('query.disable.no.consequence')
                if disable is None:
                    self.speak_dialog('error')
                    return
                elif disable == 'yes':
                    control = DB_MANAGER.execute(  # Whether control is available
                        f'''
                            SELECT C.control, C.device_id
                            FROM device_data_collection_controls C, devices D
                            WHERE C.device_id = D.id AND D.name = '{d}' AND C.purpose = '{purpose}'
                        ''' # piggybacks device id as it will be useful. As (device_id, purpose) forms a key, the query has at most 1 rows
                    ,None)

                    if len(control) > 0:
                        DB_MANAGER.execute(  # Set `taken` for this action to be TRUE
                            f'''
                                UPDATE {CLIENT_NAME}.device_data_collection_controls SET taken = TRUE WHERE purpose = '{purpose}' AND device_id IN 
                                    (SELECT D.id FROM devices D WHERE D.name = '{d}')
                            '''
                        ,None)

                        self.speak_dialog('manual.control', {'control_info': control[0][0]})
                        self._put_md(osjoin('controls', control[0][1] + '-' + purpose.replace(' ','-') + '.md'))
                        self._set_locvar('DataSourceContext', data_source)
                        self._set_locvar('PurposeContext', purpose)
                        self._set_locvar('RelevantDevicesContext', relevant_devices[relevant_devices.index(d):])  # remove previous devices
                        self.set_context('SettingsContext')
                        return
                    else:
                        self.speak_dialog('no.control')
                        contact = self._ask_yesno_safe('query.contact.firm')
                        if contact is None:
                            self.speak_dialog('error')
                            return
                        elif contact == 'yes':
                            self.speak_dialog('done')
                            self.speak_dialog('congradulate')
                        else:
                            self.speak_dialog('acknowledge')
                else:
                    self.speak_dialog('acknowledge')
            else:
                self.speak_dialog('acknowledge')

        # The (data_source, purpose) pair is finished
        purpose_list = self._get_locvar('PurposeList')
        if len(purpose_list) > 0:
            p = purpose_list.pop()
            self.handle_data_purpose_intro(data_source, p, self._get_locvar('Purposes')[p])
        else:
            self._remove_locvars('Purposes', 'PurposeList')
            GUI.congradulate(self.curriculum.index(data_source) + 1, string.capwords(data_source))
            self.speak("Great work! That is it for today, come back tomorrow to learn about the next data source.",wait=True)
            sleep(2)
            
            # Show dashboard
            self.show_dashboard()

            self.set_context('DemoPartThreeDone')

    def show_dashboard(self):
        #self.show_home()
        GUI.put_home(0.29)
        self.speak("Congradulations, you have now unlocked the home screen")
        self.speak("Here you can find your progress on your personalised curriculum, and the devices you own",wait=True); sleep(1)

        self.show_curriculum()
        self.speak("Here you can find more information about your personalised curriculum",wait=True); sleep(2)

        self.speak("Lastly, you can view the current controls you have taken for each device")
        for d in ['Withings Body Cardio', 'Philips Hue Bulb', 'WeMo Switch and Motion']:
            self.show_device(d)
            sleep(4)

        #self.show_home()
        GUI.put_home(0.29)


    @intent_handler(IntentBuilder('Continue settings').require('done').require('SettingsContext'))
    def handle_settings_done(self, message):
        self.speak_dialog('congradulate')

        data_source = self._get_locvar('DataSourceContext')
        purpose = self._get_locvar('PurposeContext')
        relevant_devices = self._get_locvar('RelevantDevicesContext')

        self._remove_locvars('DataSourceContext','PurposeContext','RelevantDevicesContext')
        self.handle_data_purpose2(data_source, purpose, relevant_devices[1:])

    # @intent_handler(IntentBuilder('Start data storage and inference').require('continue').require('demo').require('DemoPartThreeDone'))
    # @intent_handler(IntentBuilder('Start data storage and inference').require('continue').require('demo'))
    # def handle_storage_and_data(self, message):
    #     self.remove_context('DemoPartThreeDone')

    #     GUI.put_module(8, 'data storage and inference')
    #     self.speak_dialog('storage.and.data.intro')

    #     self.speak_dialog('statement.1.statement')
    #     ans = self._ask_yesno_safe('query.correct')
    #     if ans is None:
    #         self.speak_dialog('error')
    #         return
    #     self.speak_dialog('correct' if ans == 'no' else 'incorrect')
    #     self.speak_dialog('statement.1.answer')

    #     self.speak_dialog('statement.2.statement')
    #     ans = self._ask_yesno_safe('query.correct')
    #     if ans is None:
    #         self.speak_dialog('error')
    #         return
    #     self.speak_dialog('correct' if ans == 'no' else 'incorrect')
    #     self.speak_dialog('statement.2.answer')

    #     self.speak_dialog('statement.3.statement')
    #     ans = self._ask_yesno_safe('query.correct')
    #     if ans is None:
    #         self.speak_dialog('error')
    #         return
    #     self.speak_dialog('correct' if ans == 'no' else 'incorrect')
    #     self.speak_dialog('statement.3.answer')

    #     self.speak('''
    #         Let's look at your devices in more detail. 
    #         For storage, your Philips Hue Bulbs and WeMo Switch keep your data as long as it needs to provide functionality, then they are deleted or anonymised.
    #         Your Nokia Smart Scale keeps your data permanently.
    #     ''',wait=True)
    #     sleep(1)
    #     self.speak('''
    #         On data inference, your WeMo Switch stated that your data will be inferred and used for advertising.
    #         There is no information on this for your Philips Hue Bulbs and Nokia Body Scale.
    #     ''')

    #     self.set_context('DemoPartFourDone')

    @intent_handler(IntentBuilder('Start data storage and inference').require('turn').require('on').require('light'))
    def start_context_trigger(self, message):
        self.remove_context('DemoPartThreeDone')
        self.speak('Turning lights on',wait=True)
        sleep(1)

        # Privacy information on lights ...
        self.speak('Did you know that your Philips Hue Bulb record your device log, which includes when you turn on the bulb?')
        self.speak('Philips then uses this data for personalisation and marketing',wait=True)
        purposes = ['personalisation', 'marketing']
        for p in purposes:
            taken = DB_MANAGER.execute(f"SELECT taken FROM {CLIENT_NAME}.device_data_collection_controls WHERE device_id = 'PHI-HUEBUL-296608048' AND purpose = '{p}'", None)[0][0]
            GUI.put_ddp('Philips Hue Bulbs', 'usage data', p)
            if taken:
                self.speak(f'Currently, you have disabled data collection for {p}.')
            else:
                self.speak(f'Currently, data collection for {p} is enabled.')

            remember = self._ask_yesno_safe('query.purpose.remember', {'purpose': p})
            if remember is None:
                self.speak_dialog('error')
                return
            elif remember == 'no':
                self.speak(DB_MANAGER.execute(f"SELECT information FROM purposes WHERE name = '{p}'",None)[0][0])
            else:
                self.speak_dialog('acknowledge')

            if taken:
                self.speak(f'You have disabled data collection for {p}.')
                reenable = self._ask_yesno_safe('Would you like to reenable it?')
                if reenable is None:
                    self.speak_dialog('error')
                    return
                elif reenable == 'yes':
                    control = DB_MANAGER.execute(  # Whether control is available
                        f'''
                            SELECT C.control, C.device_id
                            FROM device_data_collection_controls C, devices D
                            WHERE C.device_id = D.id AND D.name = 'Philips Hue Bulb' AND C.purpose = '{p}'
                        ''' # piggybacks device id as it will be useful. As (device_id, purpose) forms a key, the query has at most 1 rows
                    ,None)

                    assert len(control) > 0  # Control must be available, as otherwise it cannot be disabled in the first place
                    self._put_md(osjoin('controls', control[0][1] + '-' + p.replace(' ','-') + '.md'))
                    self.speak_dialog('manual.control', {'control_info': control[0][0]},wait=True)
                    sleep(5)
                    # No need to let user do this in the demo
                else:
                    self.speak_dialog('acknowledge',wait=True)
                    sleep(1)
            else:
                concerned = self._ask_yesno_safe('query.concern',{'device': 'Philips Hue Bulbs', 'data_source': 'usage data', 'purpose': p})
                if concerned is None:
                    self.speak_dialog('error')
                    return
                elif concerned == 'yes':
                    self.speak_dialog('acknowledge')

                    disable = self._ask_yesno_safe('query.disable.no.consequence')
                    if disable is None:
                        self.speak_dialog('error')
                        return
                    elif disable == 'yes':
                        control = DB_MANAGER.execute(  # Whether control is available
                            f'''
                                SELECT C.control, C.device_id
                                FROM device_data_collection_controls C, devices D
                                WHERE C.device_id = D.id AND D.name = 'Philips Hue Bulb' AND C.purpose = '{p}'
                            ''' # piggybacks device id as it will be useful. As (device_id, purpose) forms a key, the query has at most 1 rows
                        ,None)

                        if len(control) > 0:
                            self._put_md(osjoin('controls', control[0][1] + '-' + p.replace(' ','-') + '.md'))
                            self.speak_dialog('manual.control', {'control_info': control[0][0]},wait=True)
                            sleep(5)
                        else:
                            self.speak_dialog('no.control')
                            contact = self._ask_yesno_safe('query.contact.firm')
                            if contact is None:
                                self.speak_dialog('error')
                                return
                            elif contact == 'yes':
                                self.speak_dialog('done')
                                self.speak_dialog('congradulate')
                            else:
                                self.speak_dialog('acknowledge')
                    else:
                        self.speak_dialog('acknowledge')
                else:
                    self.speak_dialog('acknowledge')


    def handle_event_constructor(self, event):
        return lambda msg: self.handle_event(msg,event)

    def handle_event(self, message, event):
        try:
            GUI.advance(event)
        except Exception as e:
            self.log.error(e.args)
            self.log.error('An error occured!')

    # @intent_handler(IntentBuilder('Start Demo').require('unique'))
    def _test(self, message):
        #data_source = 'body data'
        #self.handle_module('body data')
        # self.speak_dialog('acknowledge')
        self.speak("Starting demo")

    def _put_md(self, fname):
        '''
            Displays content of file `fname` on the main screen
            `fname` is the string containing the relative directory of the file under CURRICULUM_DIR 
        '''
        try:
            self.file_system.exists(osjoin(CURRICULUM_DIR, fname))
            with self.file_system.open(osjoin(CURRICULUM_DIR, fname), 'r') as my_file:
                GUI.put_md(my_file.read())
        except:
            self.speak_dialog('error.file.not.available')

    def _ask_device_selection(self, options, dialog='Which one would you like?',
                      data=None, min_conf=0.65):
        '''
        A modification of the `ask_selection` function in the mycroft package.
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
            Queries devices but asks repeatedly until a valid response is registerd or `MAX_TRIES` reached

            Args:
              devices (list): list of devices to choose
              query (str): a dialog ID or string to read

            Returns:
              string: list element selected or None if fails to register a response within `MAX_TRIES` # of tries
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

    def _ask_yesno_safe(self, query, data=None, MAX_TRIES=5):
        '''     
            Queries yes/no but asks repeatedly until a yes/no response is successfully interpreted or `MAX_TRIES` reached

            Args:
                query (string): a dialog id or string to read
            Returns 
                'yes'/'no' or None if fails to register a response within `MAX_TRIES` # of tries
        '''
        response = self.ask_yesno(query, data)
        num_tries = 1
        MAX_TRIES = 5
        while response != 'yes' and response != 'no' and num_tries < MAX_TRIES:
            self.speak_dialog('confused')
            response = self.ask_yesno(query, data)
            num_tries += 1
        
        return response if response == 'yes' or response == 'no' else None



def create_skill():
    return PrivacyAssistant()

