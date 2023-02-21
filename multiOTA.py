import dearpygui.dearpygui as dpg
import threading
from ameba_party import AmebaParty
import logging

logging.basicConfig(level=logging.DEBUG)

dpg.create_context()



def update_callback(number_of_robots):
    dpg.set_value("robots", f"Number of robots: {number_of_robots}")
    logging.debug("callback called")

amebaparty = AmebaParty(callback=update_callback)
server_thread = threading.Thread(name="server", target=amebaparty.listen_blocking)
server_thread.start()

with dpg.window(tag="Update"):
    dpg.add_text("Hello, world", tag="robots")

dpg.set_primary_window("Update", True)

dpg.setup_dearpygui()
dpg.create_viewport()
dpg.show_viewport()
dpg.start_dearpygui()

dpg.destroy_context()
