# Reverse-Engineering HTTP Video Streaming

## Introduction

This project investigates how different video streaming services (YouTube, Vimeo, Dropbox, and Google Drive) deliver video content over HTTP. By capturing and analyzing network traffic traces, we reverse-engineer the streaming strategies used by these services. Specifically, our analysis focuses on:

- **Connection Persistence:**  
  Determining whether a video server uses a persistent (single TCP connection) or non-persistent (multiple TCP connections) strategy during a video streaming session.

- **Bit-Rate Analysis:**  
  Analyzing if the video server uses constant bit-rate streaming or variable bit-rate streaming that adapts to network conditions. We evaluate this by plotting the amount of data received per unit time (e.g., every 200 ms).

## Project Overview

This project uses the following tools and libraries:
- **Wireshark:** For capturing network traffic and saving the capture as a pcap file.
- **PyShark:** A Python wrapper for Wireshark that allows parsing of pcap files.
- **Matplotlib:** For plotting the throughput over time to visually inspect the streaming behavior.

The analysis script (`analyze_video_stream.py`) processes the pcap file to:
1. Group TCP packets by their stream identifier to assess the persistence of TCP connections.
2. Compute and plot throughput over fixed time windows to determine whether the video streaming is constant or variable bit-rate.

## Prerequisites

- **Python 3.x**
- **Wireshark** (or any similar packet capture tool)
- **Python Packages:**
  - [PyShark](https://pypi.org/project/pyshark/)
  - [Matplotlib](https://pypi.org/project/matplotlib/)

### Installation

Install the required Python packages using pip:

```bash
pip install pyshark matplotlib
```

### Project Structure
```bash .
├── analyze_video_stream.py  # Main analysis script 
├── README.md                # This README file 
└── video_stream.pcap
```
### Usage

```bash
python analyze_video_stream.py video_stream.pcap --time_window 0.2
```

The `--time_window` is optional. It is to adjust the time window for throughput calculation (default is 0.2 seconds)

### 3. Interpret the Results

#### Connection Persistence
The script analyzes the number of TCP streams used during a video session.

- **Single TCP Stream:** Indicates a persistent connection.
- **Multiple TCP Streams:** Suggests non-persistent connections or multiple connection reuse.

#### Bit-Rate Analysis
The script generates throughput plots (bits per second) over time to identify the streaming behavior.

- **Constant Throughput:** Suggests constant bit-rate streaming.
- **Fluctuating Throughput:** Suggests adaptive streaming that adjusts to network conditions.

## Analysis Details

### Connection Persistence Analysis

- **Methodology:**  
  The script uses Wireshark’s `tcp.stream` field to group packets into streams. By counting the number of unique streams, we determine whether the session is using a single persistent connection or multiple connections.

- **Interpretation:**  
  - **1 TCP Stream:** Persistent connection.
  - **>1 TCP Stream:** Non-persistent connections or connection reuse.

### Bit-Rate Analysis

- **Methodology:**  
  The script bins packet data over fixed time intervals (default: 200 ms) and calculates the throughput in bits per second.  
  - **Plotting:** A line plot of throughput vs. time is generated for each TCP stream.

- **Interpretation:**  
  - **Constant Throughput:** Likely constant bit-rate streaming.
  - **Variable Throughput:** Likely adaptive streaming that changes bit-rate based on network conditions.

## Figures & Plots

Below are placeholders for figures and plots that will be added as the analysis progresses. Replace these placeholders with your actual figures:

- **Figure 1:** Overview of TCP Streams  
  *Description: A diagram or screenshot showing the number of TCP streams identified during the analysis.*

  ![Figure 1](path/to/figure1.png)

- **Figure 2:** Throughput Plot for YouTube  
  *Description: A throughput vs. time plot for a video streaming session on YouTube.*

  ![Figure 2](path/to/figure2.png)

- **Figure 3:** Throughput Plot for Vimeo  
  *Description: A throughput vs. time plot for a video streaming session on Vimeo.*

  ![Figure 3](path/to/figure3.png)

- **Figure 4:** Throughput Plot for Dropbox  
  *Description: A throughput vs. time plot for a video streaming session on Dropbox.*

  ![Figure 4](path/to/figure4.png)

- **Figure 5:** Throughput Plot for Google Drive  
  *Description: A throughput vs. time plot for a video streaming session on Google Drive.*

  ![Figure 5](path/to/figure5.png)

## Experimentation

For a fair and thorough comparison:
- Ensure similar video content and duration across all services.
- Use the same WiFi network and similar link conditions for each capture.
- Experiment by varying link quality (e.g., moving the device farther from the access point or placing it behind a wall) to observe how each service adapts its streaming bit-rate.

## Conclusion

This project provides insights into the streaming strategies used by popular video services by analyzing connection persistence and bit-rate adaptation. The results help in understanding how streaming services optimize content delivery based on network conditions.

## License

This project is provided for educational purposes. You are free to modify and use it as needed.
