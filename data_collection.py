import csv
import os
import time
import threading

"""
- Add extrussion rate logging and the option for mettler toledo balance logging 
"""

class DataCollector:
    def __init__(self, save_directory, filename="print_data.csv"):
        self.save_directory = save_directory
        self.filename = os.path.join(save_directory, filename)
        self._recording = False
        self._thread = None
        self._start_time = None

    def _record_loop(self, controller, getLoad, interval=0.01):
        self._start_time = time.time()
        file_exists = os.path.isfile(self.filename)
        with open(self.filename, mode='a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            if not file_exists:
                # Adjust header based on whether getLoad is provided
                if getLoad is None:
                    writer.writerow(['time_s', 'X', 'Y', 'Z', 'E'])
                else:
                    writer.writerow(['time_s', 'X', 'Y', 'Z', 'E', 'loadcell_kg'])
                    
            while self._recording:
                t = time.time() - self._start_time
                pos = controller.get_position()  # Should return dict with keys X, Y, Z, E
                if getLoad is None:
                    writer.writerow([
                        f"{t:.3f}",
                        pos.get('X', 0),
                        pos.get('Y', 0),
                        pos.get('Z', 0),
                        pos.get('E', 0)
                    ])
                else:
                    load = getLoad()
                    writer.writerow([
                        f"{t:.3f}",
                        pos.get('X', 0),
                        pos.get('Y', 0),
                        pos.get('Z', 0),
                        pos.get('E', 0),
                        f"{load:.5f}"
                    ])
                csvfile.flush()
                time.sleep(interval)

    def record_print_data(self, controller, getLoad=None, interval=0.01):
        if not self._recording:
            self._recording = True
            self._thread = threading.Thread(target=self._record_loop, args=(controller, getLoad, interval))
            self._thread.start()

    def stop_record_data(self):
        self._recording = False
        if self._thread:
            self._thread.join()
            self._thread = None

# Usage in main.py:
# from data_collection import DataCollector
# data_collector = DataCollector()
# data_collector.record_print_data(controller, getLoad)
# ... do stuff ...
# data_collector.stop_record_data()