import dearpygui.dearpygui as dpg
import threading
from ameba_party import AmebaParty
import logging

logging.basicConfig(level=logging.DEBUG)
amebaparty = AmebaParty()


dpg.create_context()
dpg.create_viewport()
dpg.setup_dearpygui()

with dpg.window(tag="Primary Window"):
    dpg.add_text("Hello, world")



server_thread = threading.Thread(name="server", target=amebaparty.listen_blocking)
server_thread.start()


dpg.create_viewport(title='Custom Title', width=600, height=200)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Primary Window", True)
dpg.start_dearpygui()
dpg.destroy_context()
