import dearpygui.dearpygui as dpg
import threading
from ameba_party import AmebaParty
import logging

logging.basicConfig(level=logging.DEBUG)
amebaparty = AmebaParty()

dpg.create_context()

server_thread = threading.Thread(name="server", target=amebaparty.listen_blocking)
server_thread.start()


# dpg.set_primary_window("Primary Window", True)


with dpg.window(label="Update"):
    dpg.add_text("Hello, world")

dpg.set_primary_window("Update", True)

dpg.setup_dearpygui()
dpg.create_viewport()
dpg.show_viewport()
dpg.start_dearpygui()

dpg.destroy_context()
