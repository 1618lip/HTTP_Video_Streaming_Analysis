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

def plot_throughput_for_stream(packets, stream_id, time_window=0.2, previous_end_time =0, cumu_thru = None):
    """
    Plots the throughput (in bits per second) over time for a given TCP stream.
    It bins the data by the specified time window (e.g., every 200ms).
    """
    
    # Sort packets by timestamp
    packets = sorted(packets, key=lambda x: x[0])
    start_time = packets[0][0]
    end_time = packets[-1][0]
    
    # Create time bins for the duration of the stream
    num_bins = max(int((end_time - start_time) / time_window),1)+1 #prevents division issues in small windows
    throughput = [0] * num_bins  # initialize bins to hold byte sums
    bins = np.linspace(0, end_time-start_time, num_bins+1) #normalize to start at 0 to video played
    
    # Sum up packet lengths in each time window
    for (timestamp, length) in packets:
        bin_index = int((timestamp - start_time) / time_window)
        if bin_index < len(throughput):
            throughput[bin_index] += length
            
    # Convert from bytes per window to bits per second
    # Ensure non-zero throughput only
    throughput_bps = [(val * 8) / time_window if val > 0 else 0 for val in throughput]

    bins = bins + previous_end_time #append to previous end to 
    plt.figure(stream_id, figsize=(10, 6)) #each fig has unique id
    
    plt.plot(bins[:-1], throughput_bps, marker='o', linestyle='-', color ='b')
    plt.xlabel("Time (x 0.1 s)")
    plt.ylabel("Throughput (bps)")
    stream_index = int(stream_id)+1
    plt.title("Throughput Over Time for TCP Stream {}".format(stream_index))
    plt.grid(True)
    plt.show()

    if cumu_thru is not None:
        cumu_thru = np.concatenate([cumu_thru, np.array(throughput_bps)])
    else:
     cumu_thru = np.array(throughput_bps)
    
    return bins[-1], cumu_thru #to continue from end of pervious stream simulating a continuous stream...
 
    

def analyze_bit_rate(streams, time_window=0.2,max_plots = 31):
    """
    For each TCP stream, analyze the throughput pattern.
    Constant bit-rate streaming will result in a relatively steady throughput,
    whereas variable bit-rate streaming will show fluctuations over time.
    """
    # Limit the number of plotted streams
    print("\n----- Bit-Rate Analysis -----")
    previous_end_time = 0
    cumu_thru = np.array([])
    
    for i, (stream_id, packets) in enumerate(streams.items()):
        if i >= max_plots:
            break  # Stop after plotting `max_plots` streams
        
        packets = sorted(packets, key=lambda x: x[0])
        duration = packets[-1][0] - packets[0][0]
        print(f"Stream {stream_id}: {len(packets)} packets over {duration:.2f} miliseconds")
        print(f"Plotting throughput for stream {stream_id} (using a {time_window}s window)...")
        
        previous_end_time, cumu_thru = plot_throughput_for_stream(packets, stream_id, time_window, previous_end_time, cumu_thru)
        
        print("Examine the plots: steady throughput suggests constant bit-rate streaming, while fluctuating throughput suggests variable bit-rate streaming that may be adapting to changes in link quality.")
        # Cumulative Throughput Plot

    if cumu_thru is not None:
        plt.figure(figsize=(12, 6))
        plt.plot(np.linspace(0, previous_end_time, len(cumu_thru)), cumu_thru, marker='o', linestyle='-', color='g', alpha=0.7)
        plt.xlabel("Time (ms)")
        plt.ylabel("Cumulative Throughput (bps)")
        plt.title("Cumulative Throughput Across All TCP Streams")
        plt.grid(True)
        plt.show()
    
def main():
    args = parse_args()
    streams = process_pcap(args.pcap_file)
    analyze_connection_persistence(streams)
    analyze_bit_rate(streams, time_window=args.time_window)

if __name__ == "__main__":
    main()
