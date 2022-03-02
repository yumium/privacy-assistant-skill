from mycroft import MycroftSkill, intent_file_handler, intent_handler
from adapt.intent import IntentBuilder
from time import sleep
from mycroft.util.parse import match_one
from . import (gui)
from .db import (databaseBursts)

'''
To do:
- [x] Display with graph
- [ ] Diversify dialog sequence + make it less robotic
- [ ] Modularize this
- [ ] Edge case correction (when Mocha gives up..)
'''

DB_MANAGER = databaseBursts.dbManager()
CLIENT_NAME = databaseBursts.CLIENT_NAME

class PrivacyAssistant(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        self._locvars = {} # A dictionary of local variables for context storage during user confirmation

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
            self.speak_dialog('more.info')
            self.set_context('WWWReadingDoneContext')

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


    def handle_data_tutoring_data_source_intro(self, data_source):
        self.speak(f"Welcome back! Today we will talk about {data_source}.")

        understand = self._ask_yesno_safe('Are you familiar with this concept?')
        if understand is None:
            self.speak("Sorry, I don't understand. Please try again later.")
            return
        elif understand == 'no':
            self.speak(DB_MANAGER.execute(f"SELECT information FROM data_source WHERE name = '{data_source}'",None)[0][0], wait=True)
            sleep(1)
            more_info = self._ask_yesno_safe('Do you need more information?')
            if more_info is None:
                self.speak("Sorry, I don't understand. Please try again later.")
                return
            elif more_info == 'yes':
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
        return a / b

    @intent_handler(IntentBuilder('Continue urgent control').require('done').require('NextUrgentControlContext'))
    def handle_next_urgent_control(self, data_source):
        self.remove_context('NextUrgentControlContext')
        urgents = self._get_locvar('Urgents')
        if len(urgents) == 0:  # All urgent controls have been taken care of
            self._remove_locvars('Urgents')
            p = self._get_locvar('PurposeList').pop()  # Begin non-urgent controls
            self.handle_data_purpose_intro(data_source, p, self._get_locvar('Purposes')[p])
        else:
            self.handle_urgent_control(*urgents.pop())

    def handle_urgent_control(self, urgent_id, device_name, data_source, description, control):
        self.speak("Here's something I'm a little worried about.")
        self.speak(description)

        response = None
        if control is None:
            self.speak("Unfortunately, there is no way to disable this. Under UK legislations, you have the right to limit how companies use your data.")
            response = self._ask_yesno_safe("Would you like me to contact the firm about this?")
        else:
            self.speak(control)
            response = self._ask_yesno_safe("Would you like to disable this?")
        
        if response is None:
            self.speak("Sorry, I don't understand. Please try at a later time.",wait=True)
        elif response == 'yes':
            if control is None:
                self.speak("Done",wait=True)
            else:
                self.speak("Please follow the onscreen instructions. When you are done, say 'Hey Mocha, done'",wait=True)
                self.set_context('NextUrgentControlContext','')
                return
        else:
            self.speak("Okay",wait=True)
        sleep(2)
        self.handle_next_urgent_control(data_source)

    def handle_data_purpose_intro(self, data_source, purpose, relevant_devices):
        purpose_introduced = DB_MANAGER.execute(f"SELECT introduced FROM {CLIENT_NAME}.purposes WHERE name = '{purpose}'", None)[0][0]
        self.speak(f"Your device uses {data_source} for {purpose}.")  
        if purpose_introduced:
            remember = self._ask_yesno_safe(f'Do you remember what {purpose} means?')
            if remember is None:
                self.speak("Sorry, I don't understand. Please try again later")
                return
            elif remember == 'no':
                self.speak(DB_MANAGER.execute(f"SELECT information FROM purposes WHERE name = '{purpose}'",None)[0][0])

            self.handle_data_purpose2(data_source, purpose, relevant_devices)
        else:
            DB_MANAGER.execute(f"UPDATE {CLIENT_NAME}.purposes SET introduced = TRUE WHERE name = '{purpose}'", None)  # Set purpose to be introduced
            familiar = self._ask_yesno_safe(f'Are you familiar with what {purpose} means?')
            if familiar is None:
                self.speak("Sorry, I don't understand. Please try again later")
                return
            elif familiar == 'no':
                self.speak(DB_MANAGER.execute(f"SELECT information FROM purposes WHERE name = '{purpose}'",None)[0][0])
                sleep(1)
                more_info = self._ask_yesno_safe('Do you need more information?')
                if more_info is None:
                    self.speak("Sorry, I don't understand. Please try again later.")
                    return
                elif more_info == 'yes':
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

        data_source = self._get_locvar('DataSourceContext'); self.log.error(data_source)
        purpose = self._get_locvar('PurposeContext'); self.log.error(purpose)
        relevant_devices = self._get_locvar('RelevantDevicesContext'); self.log.error(relevant_devices)

        self._remove_locvars('DataSourceContext', 'PurposeContext', 'RelevantDevicesContext')
        self.handle_data_purpose2(data_source, purpose, relevant_devices)


    def handle_data_purpose2(self, data_source, purpose, relevant_devices):
        for d in relevant_devices:
            # No need to repeat in full if purpose was not explained
            concerned = self._ask_yesno_safe(f"Are you concerned about {d} collecting {data_source} for {purpose}?")
            if concerned is None:
                self.speak("Sorry, I don't understand. Please try again later.")
                return
            elif concerned == 'yes':
                self.speak("Okay.")

                disable = self._ask_yesno_safe("Would you like me to disable that? This will not change the functionality.")
                if disable is None:
                    self.speak("Sorry, I don't understand. Please try again later.")
                    return
                elif disable == 'yes':
                    DB_MANAGER.execute(  # Set `taken` for this action to be TRUE
                        f'''
                            UPDATE {CLIENT_NAME}.device_data_collection_controls SET taken = TRUE WHERE purpose = '{purpose}' AND device_id IN 
                                (SELECT D.id FROM devices D WHERE D.name = '{d}')
                        '''
                    ,None)

                    control = DB_MANAGER.execute(  # Whether control is available
                        f'''
                            SELECT C.control
                            FROM device_data_collection_controls C, devices D
                            WHERE C.device_id = D.id AND D.name = '{d}' AND C.purpose = '{purpose}'
                        '''    
                    ,None)

                    if len(control) > 0:
                        self.speak(f"I cannot do this automatically, but you can follow the instructions on screen to {control[0][0]}. Let me know when you are done.")
                        self._set_locvar('DataSourceContext', data_source)
                        self._set_locvar('PurposeContext', purpose)
                        self._set_locvar('RelevantDevicesContext', relevant_devices[relevant_devices.index(d):])
                        self.set_context('SettingsContext')
                        return
                    else:
                        self.speak("Okay. Unfortunately, there is no way to disable this. Under UK legislations, you have the right to limit how companies use your data.")
                        contact = self._ask_yesno_safe('Would you like me to contact the firm for this feature?')
                        if contact is None:
                            self.speak("Sorry, I don't understand. Please try again later.")
                            return
                        elif contact == 'yes':
                            self.speak("Okay, that's done.")
                            self.speak_dialog('congradulate')
                        else:
                            self.speak("Okay.")
                else:
                    self.speak("Okay.")
            else:
                self.speak("Okay.")

        # The (data_source, purpose) pair is finished
        purpose_list = self._get_locvar('PurposeList')
        if len(purpose_list) > 0:
            p = purpose_list.pop()
            self.handle_data_purpose_intro(data_source, p, self._get_locvar('Purposes')[p])
        else:
            self._remove_locvars('Purposes', 'PurposeList')
            self.speak("Great work! That is it for today, come back tomorrow to learn about the next data source. You can also say “continue” to start tomorrow's material right now")

    @intent_handler(IntentBuilder('Continue settings').require('done').require('SettingsContext'))
    def handle_settings_done(self, message):
        self.speak_dialog('congradulate')

        data_source = self._get_locvar('DataSourceContext')
        purpose = self._get_locvar('PurposeContext')
        relevant_devices = self._get_locvar('RelevantDevicesContext')

        self._remove_locvars('DataSourceContext','PurposeContext','RelevantDevicesContext')
        self.handle_data_purpose2(data_source, purpose, relevant_devices[1:])

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

    @intent_handler(IntentBuilder('Start Demo').require('unique'))
    def _test(self, message):
        # self.handle_data_tutoring_data_source_intro('Account data')
        # self.handle_data_purpose_intro('Account data', 'Marketing', ['Withings Smart Scale', 'Philips Hue Bulbs', 'WeMo Switch and Motion'])
        data_source = 'usage data'
        self.handle_data_tutoring_purpose_intro2(data_source)

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

