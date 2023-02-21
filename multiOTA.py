import dearpygui.dearpygui as dpg
import threading
from ameba_party import AmebaParty
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# reduce logging from ameba_party
logging.getLogger("ameba_party").setLevel(logging.ERROR)

dpg.create_context()

filename = None


def update_callback(number_of_robots):
    dpg.set_value("robots", f"Number of robots found: {number_of_robots}")
    # logging.debug("callback called")


amebaparty = AmebaParty(callback=update_callback)
server_thread = threading.Thread(name="server", target=amebaparty.listen_blocking)
server_thread.start()


def callback(sender, app_data):
    global filename
    print("OK was clicked.")
    print("Sender: ", sender)
    print("App Data: ", app_data)
    filename = app_data["file_path_name"]
    print("Filename: ", filename)
    dpg.set_value("file", f"Selected file: {filename}")


def cancel_callback(sender, app_data):
    print("Cancel was clicked.")
    print("Sender: ", sender)
    print("App Data: ", app_data)


def update_all(sender, app_data):
    global filename
    print("Update all was clicked.")
    print("Filename: ", filename)
    amebaparty.perform_ota(filename)


with dpg.window(tag="Update"):
    dpg.add_text("Initializing...", tag="robots")
    dpg.add_text("Please select a binary file to upload", tag="file")
    dpg.add_button(
        label="Open binary file", callback=lambda: dpg.show_item("file_dialog_id")
    )
    dpg.add_button(label="Update all robots", callback=update_all)
    dpg.add_button(label="Exit", callback=lambda: dpg.stop_dearpygui())
    dpg.add_progress_bar(tag="progress", width=500, height=20)

with dpg.file_dialog(
    directory_selector=False,
    show=False,
    callback=callback,
    cancel_callback=cancel_callback,
    id="file_dialog_id",
    width=600,
    height=550,
):
    dpg.add_file_extension(".bin")

dpg.set_primary_window("Update", True)

dpg.setup_dearpygui()
dpg.create_viewport(title="Blockparty OTA updater", width=700, height=700)
dpg.show_viewport()
dpg.start_dearpygui()

dpg.destroy_context()
