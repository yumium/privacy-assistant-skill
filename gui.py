from xml.dom.expatbuilder import parseString
from pywebio.output import *

class SimpleGUI:
    HOME_URL = 'https://storage.googleapis.com/mocha-instructions/screen.png'

    def __init__(self):
        self.states = ['stand_by','recording','thinking','speaking']
        self.current_state = 'stand_by'
        self._update_text('Stand by')
        self.reset_image()

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

    # Displays the graph generated from pyecharts
    @use_scope(name='graph', clear=True)
    def put_graph(self, c):
        put_html(c.render_notebook())
        pass

    @use_scope(name='graph', clear=True)
    def put_image(self, url):
        put_image(url)

    def reset_image(self):
        self.put_image(self.HOME_URL)

    def _set_state(self, new_state):
        assert new_state in self.states
        self.current_state = new_state

    @use_scope(name='main', clear=True)
    def _update_text(self, txt):
        #put_text(txt).style('color: red')
        put_html(
            f'''
                <div style="
                    height: 40px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background-image: linear-gradient(180deg, #fff, #ddd 40%, #ccc)
                ">
                    <p>{txt}</p>
                </div>
            '''
        )
