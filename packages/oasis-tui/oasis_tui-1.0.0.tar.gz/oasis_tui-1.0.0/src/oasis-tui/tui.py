import questionary
import serial.tools.list_ports
from oasis.api import OasisBoard
import sys
import os

def list_serial_ports():
    return [port.device for port in serial.tools.list_ports.comports()]

def main():
    print("OASIS Board TUI (8-channel, 18-bit)\n--------------------")

    # ---- 0. Choose mode ----
    mode = questionary.select(
        "How would you like to work?",
        choices=[
            "Serial (live acquisition)",
            "TCP (live acquisition over network)",
            "SD Card File Only (postprocess, no device required)"
        ]).ask()

    board = None
    if mode.startswith("Serial"):
        ports = list_serial_ports()
        if not ports:
            print("No serial ports found. Exiting.")
            sys.exit(1)
        port = questionary.select("Select serial port:", choices=ports).ask()
        baud = int(questionary.select("Baudrate:", choices=["115200", "921600"]).ask())
        board = OasisBoard(mode="serial", port=port, baudrate=baud)
        try:
            board.connect()
            print(f"Connected to {port} at {baud} baud.")
        except Exception as e:
            print(f"Error connecting: {e}")
            sys.exit(1)
    elif mode.startswith("TCP"):
        ip = questionary.text("Enter OASIS Board IP address:", default="192.168.4.1").ask()
        port_tcp = int(questionary.text("TCP Port:", default="5025").ask())
        board = OasisBoard(mode="tcp", ip=ip, tcp_port=port_tcp)
        try:
            board.connect()
            print(f"Connected to OASIS at {ip}:{port_tcp}.")
        except Exception as e:
            print(f"Error connecting: {e}")
            sys.exit(1)
    else:
        board = OasisBoard(mode="offline")  # Dummy for postprocessing only

    # --------- 2. Main menu loop ----------
    while True:
        if mode.startswith("Serial") or mode.startswith("TCP"):
            action = questionary.select(
                "Choose action:",
                choices=[
                    "Acquire Data",
                    "Write Acquisition Parameters",
                    "Board Settings",
                    "Plot Last Data",
                    "Save Last Data (.h5)",
                    "Save Last Data (.mat)",
                    "Exit"
                ]).ask()

        else:
            action = questionary.select(
                "Choose action:",
                choices=[
                    "Load SD Card File",
                    "Plot Last Data",
                    "Save Last Data (.h5)",
                    "Save Last Data (.mat)",
                    "Exit"
                ]).ask()

        if action == "Acquire Data":
            use_defaults = questionary.confirm(
                "Sample with stored parameters (on device)?",
                default=True
            ).ask()
            if use_defaults:
                board.acquire_default()
            else:
                t_sample = float(questionary.text("Acquisition time (s):", default="1.0").ask())
                f_sample = int(questionary.text("Sampling rate (Hz):", default="1000").ask())
                vchoices = [str(v) for v in OasisBoard.VOLTAGE_RANGE_ID.keys()]
                voltage_range = []
                print("\nSpecify voltage range (V) for each channel:")
                for ch in range(8):
                    vr = float(questionary.select(
                        f"Channel {ch+1} voltage range:",
                        choices=vchoices,
                        default="5"
                    ).ask())
                    voltage_range.append(vr)
                triggered = questionary.confirm("Triggered acquisition?", default=False).ask()
                v_trigg = 0
                if triggered:
                    v_trigg = float(questionary.text("Trigger voltage (V):", default="2.5").ask())
                oversampling = int(questionary.select(
                    "Oversampling (integer, 0=none):", choices=[str(x) for x in range(0, 5)], default="0"
                ).ask())
                sync_mode = questionary.select(
                    "Sync mode:", choices=["Off", "Mode 1", "Mode 2"], default="Off"
                ).ask()
                sync_map = {"Off": 0, "Mode 1": 1, "Mode 2": 2}

                board.set_parameters(
                    t_sample, f_sample, voltage_range,
                    trigger=triggered, v_trigg=v_trigg,
                    oversampling=oversampling, sync_mode=sync_map[sync_mode]
                )
                print("\nStarting acquisition...")

                def log(msg): print(msg)
                def progress_cb(val):
                    bar_length = 40
                    filled = int(val / 100 * bar_length)
                    bar = "[" + "#" * filled + "-" * (bar_length - filled) + "]"
                    print(f"\r{bar} {val:3d}%", end='', flush=True)
                    if val == 100:
                        print()  # Newline at end

                try:
                    board.acquire(print_log=log, progress=progress_cb)
                    print("Acquisition finished.\n")
                except Exception as e:
                    print(f"Error: {e}\n")
                    continue

        elif action == "Write Acquisition Parameters":
            t_sample = float(questionary.text("Acquisition time (s):", default="1.0").ask())
            f_sample = int(questionary.text("Sampling rate (Hz):", default="1000").ask())
            vchoices = [str(v) for v in OasisBoard.VOLTAGE_RANGE_ID.keys()]
            voltage_range = []
            print("\nSpecify voltage range (V) for each channel:")
            for ch in range(8):
                vr = float(questionary.select(
                    f"Channel {ch+1} voltage range:",
                    choices=vchoices,
                    default="5"
                ).ask())
                voltage_range.append(vr)
            triggered = questionary.confirm("Triggered acquisition?", default=False).ask()
            v_trigg = 0
            if triggered:
                v_trigg = float(questionary.text("Trigger voltage (V):", default="2.5").ask())
            oversampling = int(questionary.select(
                "Oversampling (integer, 0=none):", choices=[str(x) for x in range(0, 5)], default="0"
            ).ask())
            sync_mode = questionary.select(
                "Sync mode:", choices=["Off", "Mode 1", "Mode 2"], default="Off"
            ).ask()
            sync_map = {"Off": 0, "Mode 1": 1, "Mode 2": 2}

            board.set_parameters(
                t_sample, f_sample, voltage_range,
                trigger=triggered, v_trigg=v_trigg,
                oversampling=oversampling, sync_mode=sync_map[sync_mode]
            )
            try:
                board.write_parameters_to_device()
            except Exception as e:
                print(f"Error: {e}")
            continue

        elif action == "Board Settings":
            setting = questionary.select(
                "Board setting to access/change:",
                choices=[
                    "Mute buzzer",
                    "Unmute buzzer",
                    "Enable WiFi",
                    "Disable WiFi",
                    "Show Device Info",
                    "Show Raw Device Info",
                    "Set Device Info (advanced)",
                    "Back"
                ]).ask()

            if setting == "Mute buzzer":
                board.mute_buzzer()
            elif setting == "Unmute buzzer":
                board.unmute_buzzer()
            elif setting == "Enable WiFi":
                board.enable_wifi()
            elif setting == "Disable WiFi":
                board.disable_wifi()
            elif setting == "Show Device Info":
                info = board.device_info()
                print(info)
            elif setting == "Show Raw Device Info":
                info = board.device_raw_info()
                print(info)
            elif setting == "Set Device Info (advanced)":
                print("\n--- Entering board menu ---")
                resp = board.set_device_info()
                print(resp)
            elif setting == "Back":
                pass
            continue

        elif action == "Load SD Card File":
            meta_path = questionary.path(
                "Path to .OASISmeta file:",
                default=".",
                validate=lambda path: (
                    path.endswith(".OASISmeta") and os.path.isfile(path)
                    or "Please select a valid .OASISmeta file"
                )
            ).ask()
            if meta_path is None:
                print("Cancelled.")
                continue
            try:
                board.load_from_files(meta_path)
                print("Raw SD card data loaded and decoded. You can now plot or save as usual.")
            except Exception as e:
                print(f"Error loading SD card files: {e}")
            continue

        elif action == "Plot Last Data":
            try:
                board.plot_data()
            except Exception as e:
                print(f"Nothing to plot or error: {e}")

        elif action == "Save Last Data (.h5)":
            fname = questionary.text(
                "Save filename:", default="OASISData.h5"
            ).ask()
            try:
                board.save_data_h5(fname)
                print(f"Data saved to {fname}")
            except Exception as e:
                print(f"Error saving: {e}")

        elif action == "Save Last Data (.mat)":
            fname = questionary.text(
                "Save filename:", default="OASISData.mat"
            ).ask()
            try:
                board.save_data_mat(fname)
                print(f"Data saved to {fname}")
            except Exception as e:
                print(f"Error saving: {e}")

        elif action == "Exit":
            if hasattr(board, "close"):
                try:
                    board.close()
                except Exception:
                    pass
            print("Bye!")
            break

if __name__ == "__main__":
    main()
