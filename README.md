# BarcodeScanningUtility

This scanner utility utilizes pyserial and pynput to automate an inventory data entry process via barcode scanning. The utility iterates over open COM Ports to match to a specific scanner description, then assigns that port using pyserial. Pynput uses keyboard shortcuts to navigate a database and enters barcode data. Several QR code 'modes' can be scanned at any point of a data entry process to back out/change modes.
