from mycroft import MycroftSkill, intent_file_handler


class PrivacyAssistant(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('assistant.privacy.intent')
    def handle_assistant_privacy(self, message):
        self.speak_dialog('assistant.privacy')


def create_skill():
    return PrivacyAssistant()

