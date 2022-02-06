from mycroft import MycroftSkill, intent_file_handler, intent_handler
from adapt.intent import IntentBuilder
from time import sleep

class PrivacyAssistant(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    # @intent_file_handler('assistant.privacy.intent')
    @intent_handler(IntentBuilder('Start Demo').require('unique'))
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
        while agree != 'yes' and agree != 'no' and num_tries < MAX_TRIES:  # Boolean is a subclass of int
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
            while agree != 'yes' and agree != 'no' and num_tries < MAX_TRIES:  # Boolean is a subclass of int
                self.speak_dialog('confused')
                agree = self.ask_yesno(query_dialog)
                num_tries += 1

            if agree == 'yes':
                self.log.error('Yes!')
            elif agree == 'no':
                self.log.error('No!')



def create_skill():
    return PrivacyAssistant()

