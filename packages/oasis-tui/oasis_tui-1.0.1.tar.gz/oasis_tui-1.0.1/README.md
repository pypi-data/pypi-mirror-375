# OASIS Board TUI

A modern, cross-platform Terminal User Interface (TUI) for the **OASIS Board** — an open-source 8-channel, 18-bit data acquisition system for IEPE sensors.

This TUI enables interactive live data acquisition, device configuration, and offline postprocessing directly from your terminal. It works seamlessly over Serial, TCP/IP, and with SD card files.

---

## Features

* **Easy Serial and TCP Connection:**
  Auto-detect serial ports, select baudrate, or connect via network.
* **Interactive Acquisition:**
  Acquire data live, configure all acquisition parameters, enable triggering, oversampling, and sync modes.
* **Board Management:**
  Mute/unmute buzzer, toggle WiFi, show or set device info, all from an intuitive menu.
* **Offline Postprocessing:**
  Load and analyze SD card data without hardware connected.
* **Data Handling:**
  Plot acquired data, and export to HDF5 (`.h5`) or MATLAB (`.mat`) formats.

---

## Quick Start

### 1. **Install**

```bash
pip install oasis-tui
```

### 2. **Run the TUI**

```bash
oasis-tui
```

---

## Usage Overview

1. **Choose Connection Mode:**

   * Serial (local USB)
   * TCP (WiFi/network)
   * SD Card File Only (postprocessing)
2. **Device Connection:**

   * If Serial/TCP, select device and connect.
   * If SD Card, point to your `.OASISmeta` file.
3. **Main Actions:**

   * Acquire new data with full parameter control.
   * Write acquisition settings to device.
   * Adjust board settings (buzzer, WiFi, device info).
   * Load, plot, or export previously acquired data.

---

## Example Session

```
OASIS Board TUI (8-channel, 18-bit)
------------------------------------
? How would you like to work?  (Use arrow keys)
❯ Serial (live acquisition)
  TCP (live acquisition over network)
  SD Card File Only (postprocess, no device required)
```

* After connection, navigate the menu to acquire data, adjust settings, or export data.

---

## Typical Workflows

* **Live Acquisition:**

  1. Connect over serial or TCP.
  2. Set or write acquisition parameters.
  3. Acquire data and monitor progress.
  4. Plot or export results.

* **Offline Analysis:**

  1. Choose SD Card File Only mode.
  2. Load `.OASISmeta` file.
  3. Plot or export data.

---

## Device Compatibility

* **OASIS UROS**