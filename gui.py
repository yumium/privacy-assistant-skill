from pywebio.output import *

class SimpleGUI:
    def __init__(self):
        self.states = ['stand_by','recording','thinking','speaking']
        self.current_state = 'stand_by'
        self._update_text('Stand by')

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
        put_text(txt)