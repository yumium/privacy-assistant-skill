from mycroft import MycroftSkill, intent_file_handler, intent_handler
from adapt.intent import IntentBuilder
from time import sleep
from mycroft.util.parse import match_one

'''
To do:
- [ ] Display with graph
- [ ] Refining dialog sequence
'''


DATABASE = {
    'Withings Smart Scale': [],
    'Philips Hue Bulbs': [],
    'Philips Hue Bridge': [],
    'WeMo Switch and Motion': []
}

class ProtocolInfo():
    def __init__(self, protocol, purpose, example=None):
        self.protocol = protocol
        self.purpose = purpose
        self.example = example

DATABASE['Withings Smart Scale'].append(ProtocolInfo(
    protocol='WiFi',
    purpose=['connect to the internet and download upgrades','synchronise health data on your phone'],
    example='each time you step on the scale and record a new weight, the data is uploaded to the server via WiFi, which can then be viewed from your phone'
))

DATABASE['Philips Hue Bulbs'].append(ProtocolInfo(
    protocol='ZigBee',
    purpose=['receive automation commands from the Philips Hue Bridge'],
    example='when you switch the bulbs off from your phone, the Philips Hue Bridge sends the command via ZigBee to the bulbs to turn them off'
))

DATABASE['Philips Hue Bridge'].append(ProtocolInfo(
    protocol='WiFi',
    purpose=['receive automations and commands from the phone'],
    example='when you switch the bulbs off from your phone, your phone sends the command via WiFi to the Philips Hue Bridge, which will then turn off the bulbs'
))

DATABASE['WeMo Switch and Motion'].append(ProtocolInfo(
    protocol='WiFi',
    purpose=['connect to Belkin servers to receive automations and commands from the phone']
))

DATABASE['WeMo Switch and Motion'].append(ProtocolInfo(
    protocol='LAN',
    purpose=['receive automations and commands from the phone']
))

class PrivacyAssistant(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
       #self.add_event('recognizer_loop:wakeword', self.handle_recognizer_wakeword)

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

    @intent_handler(IntentBuilder('Start Demo').require('unique'))
    def handle_www_intro(self, message):
        self.speak_dialog('www.intro.1',wait=True)
        sleep(1)
        self.speak_dialog('www.intro.2',wait=True)
        sleep(1)
        self.speak_dialog('www.intro.3',wait=True)
        sleep(1)

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
        self.remove_context('WWWReadingDoneContext')  # remove context to stop subsequent triggering for this handler with keywords in `done.voc`
        self.speak("Let's learn about how data flows on each device!")
        skipped = False
        while not skipped:
            response = self._ask_device_selection(list(DATABASE.keys()), 'Which device would you like to learn next? Remember, you can say skip to skip this section')
            while response is None:
                self.speak_dialog('confused')
                response = self._ask_device_selection(list(DATABASE.keys()), 'Which device would you like to learn next? Remember, you can say skip to skip this section')

            if response == 'skip':
                skipped = True
            else:
                for info in DATABASE[response]:  # Go through each protocol of the device
                    self.speak(f"The {response} {self._decorate_protocol(info.protocol)} to {self._combine_list(info.purpose)}." + (f" For example, {info.example}" if info.example else ""),wait=True)
                    sleep(3)

    def handle_recognizer_wakeword(self):
        self.log.error('Wake word detected!')

    # @intent_handler(IntentBuilder('Start Demo').require('unique'))
    def _test(self, message):
        self.log.error(message.data['utterances'][0])


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

