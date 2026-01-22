#!/usr/bin/env python3
"""
Configurable Event Counter Logger for Rigol DHO924
Logs the number of events per time interval to CSV
"""

import socket
import time
import csv
from datetime import datetime
import argparse

class ScopeConnection:
    def __init__(self, ip, port=5555, timeout=3):
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.sock = None

    def connect(self):
        """Establish TCP connection to oscilloscope"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(self.timeout)
            self.sock.connect((self.ip, self.port))
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def send_command(self, command):
        """Send SCPI command"""
        try:
            if not command.endswith('\n'):
                command += '\n'
            self.sock.sendall(command.encode('utf-8'))
        except Exception as e:
            print(f"Send error: {e}")

    def query(self, command):
        """Send SCPI query and read response"""
        try:
            self.send_command(command)
            response = self.sock.recv(4096).decode('utf-8').strip()
            return response
        except socket.timeout:
            return None
        except Exception as e:
            print(f"Query error: {e}")
            return None

    def close(self):
        """Close connection"""
        if self.sock:
            self.sock.close()

def read_counter_value(scope):
    """Read current counter value"""
    result = scope.query(':MEASure:COUNTer:VALue?')
    if result and result != '' and 'ERROR' not in result.upper():
        try:
            return float(result.split(',')[0])
        except:
            return None
    return None

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Log oscilloscope counter events at regular intervals')
    parser.add_argument('-i', '--interval', type=int, default=60,
                        help='Time interval in seconds (default: 60 for 1 minute)')
    parser.add_argument('-o', '--output', type=str, default='events_log.csv',
                        help='Output CSV filename (default: events_log.csv)')
    parser.add_argument('-s', '--sample', type=float, default=1.0,
                        help='Sample rate in seconds (default: 1.0)')
    parser.add_argument('--ip', type=str, default='172.29.9.197',
                        help='Oscilloscope IP address (default: 172.29.9.197)')

    args = parser.parse_args()

    OSCILLOSCOPE_IP = args.ip
    SCPI_PORT = 5555
    SAMPLE_RATE = args.sample
    INTERVAL_SECONDS = args.interval
    OUTPUT_FILE = args.output

    print("=" * 70)
    print("RIGOL DHO924 EVENT LOGGER - Configurable Intervals")
    print("=" * 70)
    print(f"Oscilloscope: {OSCILLOSCOPE_IP}:{SCPI_PORT}")
    print(f"Logging interval: {INTERVAL_SECONDS} seconds ({INTERVAL_SECONDS/60:.1f} minutes)")
    print(f"Sample rate: {SAMPLE_RATE} seconds")
    print(f"Output file: {OUTPUT_FILE}")
    print("=" * 70)

    scope = ScopeConnection(OSCILLOSCOPE_IP, SCPI_PORT)

    if not scope.connect():
        print("\nFailed to connect to oscilloscope.")
        return

    idn = scope.query('*IDN?')
    if idn:
        print(f"Connected to: {idn}")

    # Read initial counter value
    initial_counter = read_counter_value(scope)
    if initial_counter is None:
        print("Error: Could not read initial counter value.")
        scope.close()
        return

    print(f"Initial counter value: {initial_counter}")
    print("\nStarting event logging (Press Ctrl+C to stop)...")
    print("-" * 70)

    with open(OUTPUT_FILE, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Interval', 'Start Time', 'End Time', 'Events', 'Rate (events/s)', 'Cumulative Events'])

        last_counter = initial_counter
        interval_start_counter = initial_counter
        cumulative_events = 0
        interval_count = 0

        interval_start_time = time.time()
        interval_start_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            while True:
                # Read current counter value
                counter = read_counter_value(scope)

                if counter is not None:
                    # Calculate events since last reading
                    events_delta = counter - last_counter
                    if events_delta < 0:
                        print(f"\nWarning: Counter reset (was {last_counter}, now {counter})")
                        events_delta = counter

                    cumulative_events += events_delta
                    last_counter = counter

                    # Check if interval has elapsed
                    elapsed = time.time() - interval_start_time

                    if elapsed >= INTERVAL_SECONDS:
                        # Calculate events in this interval
                        interval_events = counter - interval_start_counter
                        if interval_events < 0:
                            interval_events = counter

                        interval_count += 1
                        interval_end_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        # Calculate rate
                        rate = interval_events / elapsed if elapsed > 0 else 0

                        # Write to CSV
                        csv_writer.writerow([
                            interval_count,
                            interval_start_timestamp,
                            interval_end_timestamp,
                            int(interval_events),
                            f"{rate:.3f}",
                            int(cumulative_events)
                        ])
                        csvfile.flush()

                        # Display progress
                        print(f"Interval {interval_count:3d} | {interval_start_timestamp} → {interval_end_timestamp} | Events: {int(interval_events):6d} | Rate: {rate:6.2f}/s | Total: {int(cumulative_events):8d}")

                        # Reset for new interval
                        interval_start_time = time.time()
                        interval_start_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        interval_start_counter = counter

                    # Display current status
                    current_interval_events = counter - interval_start_counter
                    time_in_interval = time.time() - interval_start_time
                    print(f"Current interval: {time_in_interval:.0f}/{INTERVAL_SECONDS}s | Events: {int(current_interval_events):6d} | Total: {int(cumulative_events):8d}", end='\r', flush=True)

                else:
                    print("\nWarning: Failed to read counter", end='\r', flush=True)

                time.sleep(SAMPLE_RATE)

        except KeyboardInterrupt:
            print("\n" + "=" * 70)
            print("Logging stopped by user.")

            # Save final interval data
            final_counter = read_counter_value(scope)
            if final_counter is not None:
                final_events = final_counter - interval_start_counter
                if final_events > 0:
                    interval_count += 1
                    elapsed = time.time() - interval_start_time
                    rate = final_events / elapsed if elapsed > 0 else 0
                    csv_writer.writerow([
                        interval_count,
                        interval_start_timestamp,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        int(final_events),
                        f"{rate:.3f}",
                        int(cumulative_events)
                    ])
                    csvfile.flush()
                    print(f"\nSaved final partial interval: {int(final_events)} events")

            print(f"\n✓ Data saved to '{OUTPUT_FILE}'")
            print(f"  Total intervals logged: {interval_count}")
            print(f"  Total events recorded: {int(cumulative_events)}")
            if interval_count > 0:
                print(f"  Average events/interval: {cumulative_events/interval_count:.2f}")

    scope.close()
    print("Connection closed.")

if __name__ == "__main__":
    main()
