from scapy.all import ARP, Ether, srp


def scan_network(ip_range):
    try:
        arp = ARP(pdst=ip_range)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether / arp

        result = srp(packet, timeout=3, verbose=False)[0]

        devices = []
        for sent, received in result:
            devices.append({
                'IP': received.psrc,
                'MAC': received.hwsrc
            })

        return devices
    except Exception as e:
        print(f'Error: {e}')

network_ip_range = 'YOUR_NETWORK'
devices_found = scan_network(network_ip_range)

print('Devices found on the network: ')

for device in devices_found:
    print(f'IP: {device["IP"]}, MAC: {device["MAC"]}')