import matplotlib.pyplot as plt

# data services
services = ['YouTube', 'Google Drive', 'Vimeo', 'Dropbox']
packets = [45133, 24083, 48523, 48504]
tcp_streams = [42, 65, 63, 80]


fig, ax1 = plt.subplots(figsize=(8, 5))

#bar plot for packets captured
ax1.bar(services, packets, color='b', width=0.4, label='Packets Captured', align='center')
ax1.set_xlabel('Video Streaming Service')
ax1.set_ylabel('Packets Captured', color='b')
ax1.tick_params(axis='y', labelcolor='b')

#second y-axis for tcp streams
ax2 = ax1.twinx()
ax2.plot(services, tcp_streams, color='r', marker='o', label='TCP Streams')
ax2.set_ylabel('TCP Streams', color='r')
ax2.tick_params(axis='y', labelcolor='r')

plt.title('Comparison of Video Streaming Services')
fig.tight_layout()
plt.show()
