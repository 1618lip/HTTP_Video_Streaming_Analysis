#!/usr/bin/env python3
"""
Analyze HTTP video streaming traffic from a pcap file.
- Determines whether the video server uses a persistent or non-persistent TCP connection by counting TCP streams.
- Plots throughput over time (per 200ms by default) to reveal if streaming is constant bit-rate or variable bit-rate.
"""

import pyshark
import matplotlib.pyplot as plt
import numpy as np
import argparse
from collections import defaultdict

def parse_args():
    parser = argparse.ArgumentParser(description="Analyze video streaming pcap file for TCP connection and bit-rate behavior.")
    parser.add_argument("pcap_file", help="Path to the pcap file captured with Wireshark")
    parser.add_argument("--time_window", type=float, default=0.2, help="Time window (in seconds) for throughput calculation (default: 0.2s)")
    return parser.parse_args()

def process_pcap(pcap_file):
    """
    Processes the pcap file and groups TCP packets by their stream id.
    Each entry in the dictionary maps a stream id to a list of (timestamp, packet_length) tuples.
    """
    print(f"Processing pcap file: {pcap_file}")
    capture = pyshark.FileCapture(pcap_file, display_filter="tcp")
    streams = defaultdict(list)
    
    for pkt in capture:
        try:
            # Convert the packet capture timestamp to a float
            timestamp = float(pkt.sniff_timestamp)
            tcp_layer = pkt.tcp
            stream_id = tcp_layer.stream  # Wireshark assigns a stream index to each TCP session
            # Use the total packet length (in bytes)
            length = int(pkt.length)
            streams[stream_id].append((timestamp, length))
        except AttributeError:
            # Skip packets that do not have a TCP layer or required fields
            continue
    capture.close()
    return streams

def analyze_connection_persistence(streams):
    """
    Analyzes whether the session used a single persistent TCP connection or multiple connections.
    """
    num_streams = len(streams)
    print("\n----- Connection Persistence Analysis -----")
    print(f"Total number of TCP streams found: {num_streams}")
    if num_streams == 1:
        print("Conclusion: The video streaming session used a single persistent TCP connection.")
    else:
        print("Conclusion: The video streaming session used multiple TCP connections (implying non-persistent connections or connection reuse).")
    print("Inspect individual stream details for further insights.\n")

def plot_throughput_for_stream(packets, stream_id, time_window=0.2):
    """
    Plots the throughput (in bits per second) over time for a given TCP stream.
    It bins the data by the specified time window (e.g., every 200ms).
    """
    # Sort packets by timestamp
    packets = sorted(packets, key=lambda x: x[0])
    start_time = packets[0][0]
    end_time = packets[-1][0]
    
    # Create time bins for the duration of the stream
    num_bins = int((end_time - start_time) / time_window) + 1
    bins = np.linspace(start_time, end_time, num_bins)
    throughput = [0] * (len(bins) - 1)
    
    # Sum up packet lengths in each time window
    for (timestamp, length) in packets:
        bin_index = int((timestamp - start_time) / time_window)
        if bin_index < len(throughput):
            throughput[bin_index] += length
            
    # Convert from bytes per window to bits per second
    throughput_bps = [ (val * 8) / time_window for val in throughput ]
    
    plt.figure(figsize=(10, 6))
    plt.plot(bins[:-1], throughput_bps, marker='o', linestyle='-')
    plt.xlabel("Time (s)")
    plt.ylabel("Throughput (bps)")
    plt.title(f"Throughput Over Time for TCP Stream {stream_id}")
    plt.grid(True)
    plt.show()

def analyze_bit_rate(streams, time_window=0.2):
    """
    For each TCP stream, analyze the throughput pattern.
    Constant bit-rate streaming will result in a relatively steady throughput,
    whereas variable bit-rate streaming will show fluctuations over time.
    """
    print("\n----- Bit-Rate Analysis -----")
    for stream_id, packets in streams.items():
        packets = sorted(packets, key=lambda x: x[0])
        duration = packets[-1][0] - packets[0][0]
        print(f"Stream {stream_id}: {len(packets)} packets over {duration:.2f} seconds")
        print(f"Plotting throughput for stream {stream_id} (using a {time_window}s window)...")
        plot_throughput_for_stream(packets, stream_id, time_window)
    print("Examine the plots: steady throughput suggests constant bit-rate streaming, while fluctuating throughput suggests variable bit-rate streaming that may be adapting to changes in link quality.")

def main():
    args = parse_args()
    streams = process_pcap(args.pcap_file)
    analyze_connection_persistence(streams)
    analyze_bit_rate(streams, time_window=args.time_window)

if __name__ == "__main__":
    main()
