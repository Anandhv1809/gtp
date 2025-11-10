#!/usr/bin/env python3
"""
GTPv2 Modify Bearer PCAP Generator

This script generates a sample PCAP file containing GTPv2 Modify Bearer
Request and Response messages for testing and analysis purposes.

Requirements:
    pip install scapy

Usage:
    python generate_gtpv2_modify_bearer.py
"""

from scapy.all import *
from scapy.contrib.gtp import *
import time

def create_modify_bearer_request():
    """Create a GTPv2 Modify Bearer Request packet."""
    # Network layer
    ip = IP(src="10.0.1.100", dst="10.0.2.100")  # MME -> SGW
    udp = UDP(sport=2123, dport=2123)
    
    # GTP layer
    gtp_header = GTPHeader(
        version=2,
        T=1,  # TEID flag
        teid=0x22222222,  # SGW Control TEID
        seq=0x123456
    )
    
    # Information Elements
    ie_list = [
        # FTEID for eNodeB
        IE_FTEID(
            instance=0,
            ipv4_present=1,
            ipv4="10.5.1.10",
            GRE_Key=0x21000001  # eNodeB TEID
        ),
        # EPS Bearer ID
        IE_EBI(instance=0, EBI=5),
        # Indication flags (optional)
        IE_Indication(instance=0, DAF=0, DTF=0, OI=0)
    ]
    
    # Modify Bearer Request message
    modify_req = GTPModifyBearerRequest(IE_list=ie_list)
    
    # Complete packet
    packet = ip / udp / gtp_header / modify_req
    
    return packet

def create_modify_bearer_response():
    """Create a GTPv2 Modify Bearer Response packet."""
    # Network layer (reversed direction)
    ip = IP(src="10.0.2.100", dst="10.0.1.100")  # SGW -> MME
    udp = UDP(sport=2123, dport=2123)
    
    # GTP layer
    gtp_header = GTPHeader(
        version=2,
        T=1,  # TEID flag
        teid=0x11111111,  # MME Control TEID
        seq=0x123456  # Same sequence as request
    )
    
    # Information Elements
    ie_list = [
        # Cause (Request accepted)
        IE_Cause(instance=0, Cause=16),  # 16 = Request accepted
        # Bearer Context with cause
        IE_BearerContext(
            instance=0,
            IE_list=[
                IE_EBI(instance=0, EBI=5),
                IE_Cause(instance=0, Cause=16)  # Bearer-specific cause
            ]
        )
    ]
    
    # Modify Bearer Response message
    modify_resp = GTPModifyBearerResponse(IE_list=ie_list)
    
    # Complete packet
    packet = ip / udp / gtp_header / modify_resp
    
    return packet

def main():
    """Generate PCAP file with Modify Bearer flow."""
    print("Generating GTPv2 Modify Bearer PCAP...")
    
    # Create packets
    request = create_modify_bearer_request()
    response = create_modify_bearer_response()
    
    # Add small time delay between packets (simulating network delay)
    request.time = time.time()
    response.time = time.time() + 0.015  # 15ms delay
    
    # Write to PCAP file
    pcap_filename = "gtpv2_modify_bearer_example.pcap"
    wrpcap(pcap_filename, [request, response])
    
    print(f"✓ PCAP file created: {pcap_filename}")
    print("\nPacket Summary:")
    print(f"  Packet 1: Modify Bearer Request")
    print(f"    MME (10.0.1.100) -> SGW (10.0.2.100)")
    print(f"    TEID: 0x22222222, Seq: 0x123456")
    print(f"    Bearer ID: 5")
    print()
    print(f"  Packet 2: Modify Bearer Response")
    print(f"    SGW (10.0.2.100) -> MME (10.0.1.100)")
    print(f"    TEID: 0x11111111, Seq: 0x123456")
    print(f"    Cause: 16 (Request accepted)")
    print()
    print("To analyze with Wireshark:")
    print(f"  wireshark {pcap_filename}")
    print()
    print("To analyze with tshark:")
    print(f"  tshark -r {pcap_filename} -V")
    print()
    print("Wireshark display filter:")
    print("  gtpv2.message_type == 34 || gtpv2.message_type == 35")

if __name__ == "__main__":
    main()
