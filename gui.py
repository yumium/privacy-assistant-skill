from . import (graph)
from pywebio.output import *
import datetime as dt

class SimpleGUI:
    HOME_URL = 'https://storage.googleapis.com/mocha-instructions/screen.png'

    STATES = ['stand_by','recording','thinking','speaking']

    # What color each term takes. Colors are keywords in CSS color value
    COLOR_MAP = {
        'account data': 'red',
        'usage data': 'purple',
        'body data': 'lime',
        'third-party integration': 'teal',
        'third-party service': 'blueviolet',
        'providing a service': 'lightseagreen',
        'personalisation': 'lightsalmon',
        'marketing': 'limegreen',
        'product feedback and improvement': 'lightslategray',
        'ad revenue': 'mediumvioletred',
        'third-party integration': 'mediumaquamarine'
    }

    def __init__(self):
        clear()
        self._init_layout()
        self._set_state('stand_by')
        put_text(f"Saturday                                                                                                                                                                ☀️ 10°C", scope='header')
        self.put_start_screen()
        put_text("Try say 'Hey Mocha, tell me about my privacy'", scope='footer')

    def _init_layout(self):
        put_scope('status_bar')
        put_scope('header')
        put_scrollable(put_scope('main'), height=400, keep_bottom=True, border=False)
        put_scope('footer')

    @use_scope('main', clear=True)
    def put_md(self, md):
        put_markdown(md)

    @use_scope('main', clear=True)
    def put_dp(self, data_source, purpose):
        put_html(
            f'''
                <div style="
                    height: 400px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                ">
                    <p style="font-size: 24px">Your device uses <strong style="color:{self.COLOR_MAP[data_source]}">{data_source}</strong></p>
                    <p style="font-size: 24px">for <strong style="color:{self.COLOR_MAP[purpose]}">{purpose}</strong></p>
                </div>
            '''
        )

    @use_scope('main', clear=True)
    def put_ddp(self, device, data_source, purpose):
        put_html(
            f'''
                <div style="
                    height: 400px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                ">
                    <p style="font-size: 24px">Your <strong>{device}</strong></p>
                    <p style="font-size: 24px">collects <strong style="color:{self.COLOR_MAP[data_source]}">{data_source}</strong></p>
                    <p style="font-size: 24px">for <strong style="color:{self.COLOR_MAP[purpose]}">{purpose}</strong></p>
                </div>
            '''
        )

    @use_scope('main', clear=True)
    def congradulate(self, module_num, module):
        put_html(
            f'''
                <div style="
                    height: 400px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                ">
                    <h3 style="color: grey">Congradulations on completing</h3>
                    <h3 style="color: grey; font-size: 50px">Module {module_num} - {module}</h3>
                </div>
            '''
        )

    @use_scope('main', clear=True)
    def put_start_screen(self):
        put_html(
            f'''
                <div style="
                    height: 400px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    background-image: url('https://storage.googleapis.com/mocha-instructions/northern_lights.jpg');
                    background-size: cover;
                    background-repeat: no-repeat;
                    background-position: center;
                ">
                    <p style="color: white; font-weight: bold; font-size: 80px">19/03</p>
                    <p style="color: white; font-weight: bold; font-size: 50px">Hello, Lance!</p>
                </div>
            '''
        )

    # Screen for privacy disclosure
    @use_scope('main', clear=True)
    def put_disclosure(self):
        put_html(
            f'''
                <div style="
                    height: 400px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                ">
                    <h3 style="color: grey">Privacy disclosure</h3>
                    <ul style="color: purple; font-weight: bold; font-size: 20px">
                        <li>No data is recorded unless wakeword is heard</li>
                        <li>Location data only used for timezone</li>
                        <li>No data used for advertising</li>
                        <li>Go to mycroft.ai for information on offline use</li>
                    </ul>
                </div>
            '''
        )

    # Screen for Open Data Project information
    @use_scope('main', clear=True)
    def put_open_data(self):
        put_html(
            f'''
                <div style="
                    height: 400px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                ">
                    <h3 style="color: grey">Voluntary Open Data Project</h3>
                    <ul style="color: purple; font-weight: bold; font-size: 20px">
                        <li>Recording is stored to help improve voice technology</li>
                        <li>Store voice commands and 10 seconds before wakeword</li>
                        <li>Data anonymised and made open periodically</li>
                    </ul>
                </div>
            '''
        )

    @use_scope('main', clear=True)
    def put_urgent(self, description):
        put_html(
            f'''
            <html>
                <head>
                    <link href="https://fonts.googleapis.com/icon?family=Material+Icons"
                        rel="stylesheet">
                </head>
                <body>
                    <div style="
                    height: 400px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    ">
                        <span class="material-icons" style="font-size:24px; color:red">warning</span>
                        <h3>{description}</h3>
                    </div>
                </body>
            </html>
            '''
        )

    @use_scope('main', clear=True)
    def put_module(self,module_number,module_name):
        put_html(
            f'''
                <div style="
                    height: 400px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                ">
                    <h3 style="color: grey; font-size: 50px">Module {module_number} - {module_name}</h3>
                </div>
            '''
        )

    def advance(self, event):
        if event == 'recognizer_loop:wakeword':
            return

        if self.current_state == 'stand_by' and event == 'recognizer_loop:record_begin':
            self._set_state('recording')
        elif self.current_state == 'stand_by' and event == 'recognizer_loop:audio_output_start':
            self._set_state('speaking')
        elif self.current_state == 'recording' and event == 'recognizer_loop:record_end':
            self._set_state('thinking')
        elif self.current_state == 'thinking' and event == 'recognizer_loop:audio_output_start':
            self._set_state('speaking')
        elif self.current_state == 'speaking' and event == 'recognizer_loop:audio_output_end':
            self._set_state('stand_by')
        else:
            print(f"Unknown pattern: handling event {event} at state {self.current_state}")

    # Displays the graph generated from pyecharts
    @use_scope(name='main', clear=True)
    def put_graph(self, c):
        put_html(c.render_notebook())

    @use_scope(name='main', clear=True)
    def put_image(self, url):
        put_image(url)

    @use_scope(name='main', clear=True)
    def put_home(self, perc):
        g = graph.generate_home(perc)
        put_html(g.render_notebook())

    @use_scope(name='main', clear=True)
    def put_curriculum(self, curriculum):
        '''
            Curriculum is a list of pairs of curriculum name with a boolean that indicates its completion.
            Pre: The list is sorted in the order which the materials are to be presented
        '''
        g = graph.generate_curriculum_view(curriculum)
        put_html(g.render_notebook())

    @use_scope(name='main', clear=True)
    def put_device(self, device_name, control_taken, control_offered_but_not_taken):
        '''
            Displays the controls taken and not taken with the device
        '''
        # put_markdown(f'''
        # ## {device_name}

        # ### Controls taken
        # ✔️ Marketing
        
        # ### Controls not taken
        # 🔲 Personalisation
        # ''')

        out = f"## {device_name} \n ### Controls taken \n"
        for c in control_taken:
            out += f"✔️ {c} \n"
        out += "### Controls not taken \n"
        for c in control_offered_but_not_taken:
            out += f"🔲 {c} \n"

        put_markdown(out)

    def reset_image(self):
        self.put_image(self.HOME_URL)

    def _set_state(self, new_state):
        assert new_state in self.STATES
        self.current_state = new_state
        self._update_text(new_state)

    @use_scope(name='status_bar', clear=True)
    def _update_text(self, txt):
        if txt == 'stand_by':
            txt = '―――'
        elif txt == 'speaking':
            #txt = '( \' o \' )'
            txt = '(( - ))'
        elif txt == 'recording':
            txt = '?'
        elif txt == 'thinking':
            txt = '...'

        put_html(
            f'''
                <div style="
                    height: 40px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                ">
                    <p style="color: purple; font-weight: bold; font-size: large">{txt}</p>
                </div>
            '''
        )

        #background-image: linear-gradient(180deg, #fff, #ddd 40%, #ccc)
