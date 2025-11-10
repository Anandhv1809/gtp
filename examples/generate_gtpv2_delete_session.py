#!/usr/bin/env python3
"""
GTPv2 Delete Session PCAP Generator

This script generates a sample PCAP file containing GTPv2 Delete Session
Request and Response messages for testing and analysis purposes.

Requirements:
    pip install scapy

Usage:
    python generate_gtpv2_delete_session.py
"""

from scapy.all import *
from scapy.contrib.gtp import *
import time

def create_delete_session_request():
    """Create a GTPv2 Delete Session Request packet."""
    # Network layer
    ip = IP(src="10.0.1.100", dst="10.0.2.100")  # MME -> SGW
    udp = UDP(sport=2123, dport=2123)
    
    # GTP layer
    gtp_header = GTPHeader(
        version=2,
        T=1,  # TEID flag
        teid=0x22222222,  # SGW Control TEID
        seq=0xDEF012
    )
    
    # Information Elements
    ie_list = [
        # Linked EPS Bearer ID (default bearer)
        IE_EBI(instance=0, EBI=5),
        # Indication flags (UE detach)
        IE_Indication(instance=0, OI=1, DAF=0, DTF=0),
    ]
    
    # Delete Session Request message
    delete_req = GTPDeleteSessionRequest(IE_list=ie_list)
    
    # Complete packet
    packet = ip / udp / gtp_header / delete_req
    
    return packet

def create_delete_session_response():
    """Create a GTPv2 Delete Session Response packet."""
    # Network layer (reversed direction)
    ip = IP(src="10.0.2.100", dst="10.0.1.100")  # SGW -> MME
    udp = UDP(sport=2123, dport=2123)
    
    # GTP layer
    gtp_header = GTPHeader(
        version=2,
        T=1,  # TEID flag
        teid=0x11111111,  # MME Control TEID
        seq=0xDEF012  # Same sequence as request
    )
    
    # Information Elements
    ie_list = [
        # Cause (Request accepted)
        IE_Cause(instance=0, Cause=16),  # 16 = Request accepted
    ]
    
    # Delete Session Response message
    delete_resp = GTPDeleteSessionResponse(IE_list=ie_list)
    
    # Complete packet
    packet = ip / udp / gtp_header / delete_resp
    
    return packet

def create_delete_bearer_request():
    """Create a subsequent Delete Bearer Request (SGW -> PGW)."""
    # Network layer
    ip = IP(src="10.0.2.100", dst="10.0.3.100")  # SGW -> PGW
    udp = UDP(sport=2123, dport=2123)
    
    # GTP layer
    gtp_header = GTPHeader(
        version=2,
        T=1,  # TEID flag
        teid=0x44444444,  # PGW Control TEID
        seq=0xABC123
    )
    
    # Information Elements
    ie_list = [
        # Linked EPS Bearer ID
        IE_EBI(instance=0, EBI=5),
        # Bearer Context (default bearer)
        IE_BearerContext(
            instance=0,
            IE_list=[
                IE_EBI(instance=0, EBI=5),
                IE_Cause(instance=0, Cause=54)  # 54 = Bearer deactivation
            ]
        ),
        # Bearer Context (dedicated bearer if exists)
        IE_BearerContext(
            instance=1,
            IE_list=[
                IE_EBI(instance=0, EBI=6),
                IE_Cause(instance=0, Cause=54)
            ]
        )
    ]
    
    # Delete Bearer Request message
    delete_bearer_req = GTPDeleteBearerRequest(IE_list=ie_list)
    
    # Complete packet
    packet = ip / udp / gtp_header / delete_bearer_req
    
    return packet

def create_delete_bearer_response():
    """Create a Delete Bearer Response packet."""
    # Network layer (reversed direction)
    ip = IP(src="10.0.3.100", dst="10.0.2.100")  # PGW -> SGW
    udp = UDP(sport=2123, dport=2123)
    
    # GTP layer
    gtp_header = GTPHeader(
        version=2,
        T=1,  # TEID flag
        teid=0x33333333,  # SGW Control TEID (for PGW->SGW)
        seq=0xABC123  # Same sequence as request
    )
    
    # Information Elements
    ie_list = [
        # Cause (Request accepted)
        IE_Cause(instance=0, Cause=16),
        # Bearer Contexts
        IE_BearerContext(
            instance=0,
            IE_list=[
                IE_EBI(instance=0, EBI=5),
                IE_Cause(instance=0, Cause=16)
            ]
        ),
        IE_BearerContext(
            instance=1,
            IE_list=[
                IE_EBI(instance=0, EBI=6),
                IE_Cause(instance=0, Cause=16)
            ]
        )
    ]
    
    # Delete Bearer Response message
    delete_bearer_resp = GTPDeleteBearerResponse(IE_list=ie_list)
    
    # Complete packet
    packet = ip / udp / gtp_header / delete_bearer_resp
    
    return packet

def main():
    """Generate PCAP file with complete Delete Session flow."""
    print("Generating GTPv2 Delete Session PCAP...")
    
    # Create packets
    packets = []
    base_time = time.time()
    
    # Delete Session Request/Response (MME <-> SGW)
    delete_sess_req = create_delete_session_request()
    delete_sess_req.time = base_time
    packets.append(delete_sess_req)
    
    delete_sess_resp = create_delete_session_response()
    delete_sess_resp.time = base_time + 0.015  # 15ms delay
    packets.append(delete_sess_resp)
    
    # Delete Bearer Request/Response (SGW <-> PGW)
    delete_bearer_req = create_delete_bearer_request()
    delete_bearer_req.time = base_time + 0.020  # 20ms from start
    packets.append(delete_bearer_req)
    
    delete_bearer_resp = create_delete_bearer_response()
    delete_bearer_resp.time = base_time + 0.035  # 35ms from start
    packets.append(delete_bearer_resp)
    
    # Write to PCAP file
    pcap_filename = "gtpv2_delete_session_example.pcap"
    wrpcap(pcap_filename, packets)
    
    print(f"✓ PCAP file created: {pcap_filename}")
    print("\nPacket Summary:")
    print(f"  Packet 1: Delete Session Request")
    print(f"    MME (10.0.1.100) -> SGW (10.0.2.100)")
    print(f"    TEID: 0x22222222, Seq: 0xDEF012")
    print(f"    Linked Bearer ID: 5")
    print()
    print(f"  Packet 2: Delete Session Response")
    print(f"    SGW (10.0.2.100) -> MME (10.0.1.100)")
    print(f"    TEID: 0x11111111, Seq: 0xDEF012")
    print(f"    Cause: 16 (Request accepted)")
    print()
    print(f"  Packet 3: Delete Bearer Request")
    print(f"    SGW (10.0.2.100) -> PGW (10.0.3.100)")
    print(f"    TEID: 0x44444444, Seq: 0xABC123")
    print(f"    Bearer IDs: 5, 6")
    print()
    print(f"  Packet 4: Delete Bearer Response")
    print(f"    PGW (10.0.3.100) -> SGW (10.0.2.100)")
    print(f"    TEID: 0x33333333, Seq: 0xABC123")
    print(f"    Cause: 16 (Request accepted)")
    print()
    print("To analyze with Wireshark:")
    print(f"  wireshark {pcap_filename}")
    print()
    print("To analyze with tshark:")
    print(f"  tshark -r {pcap_filename} -V")
    print()
    print("Wireshark display filter:")
    print("  gtpv2.message_type == 36 || gtpv2.message_type == 37 || gtpv2.message_type == 99 || gtpv2.message_type == 100")

if __name__ == "__main__":
    main()
