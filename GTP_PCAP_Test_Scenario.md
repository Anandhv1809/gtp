# GTP Modify/Delete PCAP Test Scenario Guide

This document provides comprehensive guidelines for capturing and analyzing GTP (GPRS Tunneling Protocol) Modify and Delete operations using Wireshark PCAP files.

## Table of Contents
1. [Overview](#overview)
2. [GTPv1 Test Scenarios](#gtpv1-test-scenarios)
3. [GTPv2 Test Scenarios](#gtpv2-test-scenarios)
4. [Wireshark Capture Guidelines](#wireshark-capture-guidelines)
5. [Test Data Examples](#test-data-examples)
6. [PCAP Field Annotations](#pcap-field-annotations)
7. [Open Source Tools and Resources](#open-source-tools-and-resources)

---

## Overview

GTP (GPRS Tunneling Protocol) is used in mobile networks to carry user data between network elements. This guide focuses on:
- **GTPv1**: Modify PDP Context and Delete PDP Context flows
- **GTPv2**: Modify Bearer, Delete Bearer, and Delete Session flows

### Protocol Basics
- **GTP-C (Control Plane)**: Port 2123 (UDP)
- **GTP-U (User Plane)**: Port 2152 (UDP)
- **TEID**: Tunnel Endpoint Identifier - unique identifier for each tunnel

---

## GTPv1 Test Scenarios

### 1. Modify PDP Context Request/Response

#### Flow Description
```
UE/MS → SGSN → GGSN
```

#### Message Flow
1. **Update PDP Context Request** (SGSN → GGSN)
   - Message Type: `0x12` (18)
   - Purpose: Modify QoS, charging characteristics, or other PDP context parameters
   
2. **Update PDP Context Response** (GGSN → SGSN)
   - Message Type: `0x13` (19)
   - Indicates success or failure of the modification

#### Key Fields to Capture
- **TEID**: Tunnel Endpoint Identifier in GTP header
- **Sequence Number**: For request/response correlation
- **QoS Profile**: Quality of Service parameters being modified
- **Charging Characteristics**: Billing-related modifications
- **Cause Code**: 
  - `0x80`: Request accepted
  - `0xC0`: Non-existent
  - `0xC1`: Invalid message format
  - `0xC5`: Missing or unknown APN

#### Example Scenario
```
Modify PDP Context Request:
- Source IP: 192.168.10.1 (SGSN)
- Destination IP: 192.168.20.1 (GGSN)
- TEID: 0x00001234
- Sequence Number: 0x5678
- QoS: Updated from Best Effort to Interactive class
```

### 2. Delete PDP Context Request/Response

#### Flow Description
```
UE/MS → SGSN → GGSN (Network-initiated)
GGSN → SGSN → UE/MS (GGSN-initiated)
```

#### Message Flow
1. **Delete PDP Context Request**
   - Message Type: `0x14` (20)
   - Purpose: Tear down the PDP context and release resources
   
2. **Delete PDP Context Response**
   - Message Type: `0x15` (21)
   - Confirms deletion

#### Key Fields to Capture
- **TEID**: Identifies which tunnel to delete
- **Sequence Number**: For request/response correlation
- **Teardown Indicator**: Indicates if all PDP contexts should be deleted
- **Cause Code**:
  - `0x80`: Request accepted
  - `0xC4`: Context not found

#### Example Scenario
```
Delete PDP Context Request:
- Source IP: 192.168.10.1 (SGSN)
- Destination IP: 192.168.20.1 (GGSN)
- TEID: 0x00001234
- Sequence Number: 0x5679
- Teardown Indicator: false (delete single context)
```

---

## GTPv2 Test Scenarios

### 1. Modify Bearer Request/Response

#### Flow Description
```
UE → MME → SGW → PGW
```

#### Message Flow
1. **Modify Bearer Request** (MME → SGW, or SGW → PGW)
   - Message Type: `0x22` (34)
   - Purpose: Modify bearer QoS, charging, or other parameters
   
2. **Modify Bearer Response**
   - Message Type: `0x23` (35)
   - Confirms modification

#### Key Fields to Capture
- **TEID**: Tunnel Endpoint Identifier (C-plane TEID)
- **Sequence Number**: 3-byte sequence for correlation
- **Bearer Context**: Contains EPS Bearer ID
- **EPS Bearer ID**: Identifies the bearer being modified
- **Delay Value**: Delay tolerance being modified
- **Bearer QoS**: QCI, ARP, GBR, MBR values
- **Cause Code**:
  - `16`: Request accepted
  - `64`: Context not found
  - `65`: Invalid message format
  - `66`: Version not supported

#### Example Scenario
```
Modify Bearer Request:
- Source IP: 10.0.1.100 (MME)
- Destination IP: 10.0.2.100 (SGW)
- TEID (C-plane): 0x0000ABCD
- Sequence Number: 0x123456
- Bearer Context:
  - EPS Bearer ID: 5
  - QCI: 7 (was 9, upgraded to lower latency)
  - ARP: Priority Level 10
```

### 2. Delete Bearer Request/Response

#### Flow Description
```
PGW → SGW → MME → eNodeB → UE (Network-initiated)
UE → eNodeB → MME → SGW → PGW (UE-initiated)
```

#### Message Flow
1. **Delete Bearer Request**
   - Message Type: `0x63` (99)
   - Purpose: Delete dedicated bearer(s)
   
2. **Delete Bearer Response**
   - Message Type: `0x64` (100)
   - Confirms bearer deletion

#### Key Fields to Capture
- **TEID**: C-plane TEID
- **Sequence Number**: For request/response matching
- **Linked EPS Bearer ID**: Default bearer associated with bearers being deleted
- **EPS Bearer IDs**: List of bearers to delete
- **Bearer Context**: Details of each bearer being removed
- **Cause Code**:
  - `16`: Request accepted
  - `54`: Bearer not found
  - `64`: Context not found

#### Example Scenario
```
Delete Bearer Request:
- Source IP: 10.0.3.100 (PGW)
- Destination IP: 10.0.2.100 (SGW)
- TEID (C-plane): 0x0000EFGH
- Sequence Number: 0x789ABC
- Linked EPS Bearer ID: 5 (default bearer)
- EPS Bearer ID to delete: 6 (dedicated bearer)
- Cause: QoS policy change
```

### 3. Delete Session Request/Response

#### Flow Description
```
MME → SGW → PGW (UE detach/handover)
PGW → SGW → MME (Network-initiated)
```

#### Message Flow
1. **Delete Session Request**
   - Message Type: `0x24` (36)
   - Purpose: Delete all bearers and tear down PDN connection
   
2. **Delete Session Response**
   - Message Type: `0x25` (37)
   - Confirms session deletion

#### Key Fields to Capture
- **TEID**: C-plane TEID
- **Sequence Number**: For correlation
- **Linked EPS Bearer ID**: Default bearer ID
- **Indication Flags**: Operation indication
- **ULI**: User Location Information (optional)
- **Cause Code**:
  - `16`: Request accepted
  - `64`: Context not found

#### Example Scenario
```
Delete Session Request:
- Source IP: 10.0.1.100 (MME)
- Destination IP: 10.0.2.100 (SGW)
- TEID (C-plane): 0x0000ABCD
- Sequence Number: 0xDEF012
- Linked EPS Bearer ID: 5
- Indication: UE detach
```

---

## Wireshark Capture Guidelines

### Pre-Capture Setup

1. **Identify Network Elements**
   - SGSN IP addresses (GTPv1)
   - GGSN IP addresses (GTPv1)
   - MME IP addresses (GTPv2)
   - SGW IP addresses (GTPv2)
   - PGW IP addresses (GTPv2)

2. **Capture Interface Selection**
   - Capture on interface connecting network elements
   - For lab environments: often on virtual/tun interfaces
   - For production: use TAP/SPAN ports

### Wireshark Display Filters

#### Basic GTP Filters
```
# All GTP traffic
gtp

# GTP Control Plane only
gtp.message_type

# GTP User Plane only
udp.port == 2152

# GTPv1 only
gtp.version == 1

# GTPv2 only
gtp.version == 2
```

#### GTPv1 Specific Filters
```
# Update/Modify PDP Context messages
gtp.message == 0x12 || gtp.message == 0x13

# Delete PDP Context messages
gtp.message == 0x14 || gtp.message == 0x15

# Filter by TEID
gtp.teid == 0x1234

# Filter by specific SGSN/GGSN
ip.addr == 192.168.10.1
```

#### GTPv2 Specific Filters
```
# Modify Bearer messages
gtpv2.message_type == 34 || gtpv2.message_type == 35

# Delete Bearer messages
gtpv2.message_type == 99 || gtpv2.message_type == 100

# Delete Session messages
gtpv2.message_type == 36 || gtpv2.message_type == 37

# Filter by TEID
gtpv2.teid == 0xABCD

# Filter by sequence number
gtpv2.seq == 0x123456

# Filter by specific network element
ip.addr == 10.0.1.100

# Filter by bearer ID
gtpv2.eps_bearer_id == 5
```

#### Combined Filters
```
# All modify operations (v1 and v2)
(gtp.message == 0x12) || (gtpv2.message_type == 34)

# All delete operations
(gtp.message == 0x14) || (gtpv2.message_type == 99) || (gtpv2.message_type == 36)

# Specific conversation between two nodes
ip.addr == 192.168.10.1 && ip.addr == 192.168.20.1 && gtp

# Only successful responses (GTPv2)
gtpv2.cause == 16

# Failed operations
gtpv2.cause != 16 && gtpv2.message_type in {23, 35, 37, 64, 100}
```

### Capture Filters (BPF Syntax)

Use these at capture time to reduce file size:

```bash
# GTP control plane only
udp port 2123

# Both control and user plane
udp port 2123 or udp port 2152

# Specific host pair
host 192.168.10.1 and host 192.168.20.1 and udp port 2123

# Multiple network elements
(host 10.0.1.100 or host 10.0.2.100 or host 10.0.3.100) and udp port 2123
```

### Capture Best Practices

1. **Start capture before initiating test**
   - Begin capturing 5-10 seconds before test sequence
   
2. **Use appropriate buffer size**
   - Set buffer to at least 256 MB for busy networks
   - Use: `dumpcap -i <interface> -b filesize:100000 -w output.pcap`

3. **Timestamp accuracy**
   - Enable high-resolution timestamps in Wireshark preferences
   
4. **Capture duration**
   - For modify operations: 10-30 seconds sufficient
   - For delete operations: 5-15 seconds sufficient
   
5. **Save filter settings**
   - Save commonly used filters as buttons for quick access

---

## Test Data Examples

### GTPv1 Test Environment

#### Network Element Configuration
```
SGSN:
- IP Address: 192.168.10.1
- IMSI Range: 001010000000001 - 001010000000100

GGSN:
- IP Address: 192.168.20.1
- APN: internet.test.com
- IP Pool: 10.100.0.0/16

UE/MS:
- IMSI: 001010000000042
- MSISDN: +1234567890
- UE IP: 10.100.1.42
- TEID (Uplink): 0x00001234
- TEID (Downlink): 0x00005678
```

#### Test Scenario Values (Modify PDP Context)
```
Request:
- TEID: 0x00001234
- Sequence: 0xA1B2
- IMSI: 001010000000042
- NSAPI: 5
- QoS (New):
  - Traffic Class: Interactive (0x03)
  - Delivery Order: Yes
  - Reliability: Acknowledged
  - Peak Throughput: 256000 kbps
  - Mean Throughput: 100000 kbps

Response:
- TEID: 0x00005678
- Sequence: 0xA1B2 (same as request)
- Cause: 128 (Request accepted)
- QoS (Negotiated): Same as requested
```

#### Test Scenario Values (Delete PDP Context)
```
Request:
- TEID: 0x00001234
- Sequence: 0xB3C4
- NSAPI: 5
- Teardown Indicator: false

Response:
- TEID: 0x00005678
- Sequence: 0xB3C4
- Cause: 128 (Request accepted)
```

### GTPv2 Test Environment

#### Network Element Configuration
```
MME:
- IP Address: 10.0.1.100
- GUMMEI: MCC=001, MNC=01, MME Group ID=1, MME Code=1

SGW:
- IP Address: 10.0.2.100
- Control Plane TEID Pool: 0x10000000 - 0x1FFFFFFF
- User Plane TEID Pool: 0x20000000 - 0x2FFFFFFF

PGW:
- IP Address: 10.0.3.100
- APN: ims.mnc001.mcc001.gprs
- IP Pool: 172.16.0.0/12

UE:
- IMSI: 001010000000099
- MSISDN: +1987654321
- UE IP: 172.16.5.99
- Default Bearer ID: 5
- Dedicated Bearer ID: 6
```

#### Control Plane TEIDs
```
MME → SGW:
- MME Control TEID: 0x11111111
- SGW Control TEID: 0x22222222

SGW → PGW:
- SGW Control TEID: 0x33333333
- PGW Control TEID: 0x44444444
```

#### User Plane TEIDs
```
eNodeB → SGW (Uplink):
- eNodeB User TEID: 0x21000001
- SGW User TEID: 0x22000001

SGW → PGW (Uplink):
- SGW User TEID: 0x23000001
- PGW User TEID: 0x24000001

Downlink uses different TEIDs in reverse direction
```

#### Test Scenario Values (Modify Bearer)
```
Request (MME → SGW):
- TEID: 0x22222222 (SGW Control TEID)
- Sequence: 0x123456
- Bearer Context:
  - EPS Bearer ID: 5
  - eNodeB FTEID: 10.5.1.10, TEID 0x21000001
  
Response (SGW → MME):
- TEID: 0x11111111 (MME Control TEID)
- Sequence: 0x123456
- Cause: 16 (Request accepted)
- Bearer Context:
  - EPS Bearer ID: 5
  - Cause: 16
```

#### Test Scenario Values (Delete Bearer)
```
Request (PGW → SGW):
- TEID: 0x33333333 (SGW Control TEID)
- Sequence: 0x789ABC
- Linked EPS Bearer ID: 5
- Bearer Context:
  - EPS Bearer ID: 6
  - Cause: 54 (Bearer deactivation)

Response (SGW → PGW):
- TEID: 0x44444444 (PGW Control TEID)
- Sequence: 0x789ABC
- Cause: 16 (Request accepted)
- Bearer Context:
  - EPS Bearer ID: 6
  - Cause: 16
```

#### Test Scenario Values (Delete Session)
```
Request (MME → SGW):
- TEID: 0x22222222 (SGW Control TEID)
- Sequence: 0xDEF012
- Linked EPS Bearer ID: 5
- Indication: 0x01 (UE detach)

Response (SGW → MME):
- TEID: 0x11111111 (MME Control TEID)
- Sequence: 0xDEF012
- Cause: 16 (Request accepted)
```

---

## PCAP Field Annotations

### GTPv1 Header Structure

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|Ver|PT|*|E|S|PN|  Message Type |          Length               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                   TEID (Tunnel Endpoint ID)                   |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|         Sequence Number       | N-PDU Number  |Next Ext Hdr   |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

#### Field Details:
- **Version (Ver)**: 3 bits, value = 1 for GTPv1
- **Protocol Type (PT)**: 1 bit, 1 = GTP, 0 = GTP'
- **Extension Header (E)**: 1 bit, indicates extension headers present
- **Sequence Number (S)**: 1 bit, indicates sequence number present
- **N-PDU Number (PN)**: 1 bit, indicates N-PDU number present
- **Message Type**: 8 bits
  - `0x12`: Update PDP Context Request
  - `0x13`: Update PDP Context Response
  - `0x14`: Delete PDP Context Request
  - `0x15`: Delete PDP Context Response
- **Length**: 16 bits, length of payload (excluding GTP header)
- **TEID**: 32 bits, identifies the tunnel
- **Sequence Number**: 16 bits, for request/response correlation

### GTPv2 Header Structure

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|Ver|P|T|  Spare  | Message Type|          Length               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                   TEID (if T=1)                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                Sequence Number                |    Spare      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

#### Field Details:
- **Version (Ver)**: 3 bits, value = 2 for GTPv2
- **Piggyback (P)**: 1 bit, piggybacked message present
- **TEID Flag (T)**: 1 bit, 1 = TEID present (control messages)
- **Message Type**: 8 bits
  - `34` (0x22): Modify Bearer Request
  - `35` (0x23): Modify Bearer Response
  - `36` (0x24): Delete Session Request
  - `37` (0x25): Delete Session Response
  - `99` (0x63): Delete Bearer Request
  - `100` (0x64): Delete Bearer Response
- **Length**: 16 bits, length of payload (excluding first 4 octets)
- **TEID**: 32 bits (optional, present when T=1)
- **Sequence Number**: 24 bits, for request/response correlation

### Important Information Elements (IEs)

#### GTPv1 IEs for Modify/Delete

```
IE Type | IE Name                    | Modify | Delete
--------|----------------------------|--------|--------
0x02    | IMSI                       | M      | C
0x03    | Routing Area Identity      | C      | C
0x0E    | Recovery                   | O      | O
0x0F    | Selection Mode             | C      | -
0x10    | TEID Data I                | M      | -
0x11    | TEID Control Plane         | C      | -
0x14    | Charging Characteristics   | M      | -
0x1A    | Teardown Indicator         | -      | C
0x80    | End User Address           | M      | -
0x83    | Protocol Config Options    | C      | -
0x84    | GSN Address                | M      | C
0x85    | GSN Address                | M      | C
0x87    | QoS Profile                | M      | -
0xFF    | Private Extension          | O      | O

M = Mandatory, C = Conditional, O = Optional
```

#### GTPv2 IEs for Modify/Delete

```
IE Type | IE Name                    | Modify Bearer | Delete Bearer | Delete Session
--------|----------------------------|---------------|---------------|---------------
0x01    | IMSI                       | C             | C             | C
0x02    | Cause                      | M (Resp)      | M             | M (Resp)
0x03    | Recovery                   | O             | C             | O
0x4D    | Bearer Context             | M             | M             | C
0x49    | Bearer QoS                 | C             | -             | -
0x50    | PDN Type                   | -             | -             | C
0x53    | EPS Bearer ID              | M             | M             | M
0x56    | User Location Info         | C             | C             | C
0x57    | FTEID                      | M             | C             | C
0x5C    | Delay Value                | C             | -             | -
0x7F    | Indication                 | O             | C             | C
0x86    | User CSG Information       | O             | O             | O

M = Mandatory, C = Conditional, O = Optional
```

### Cause Code Reference

#### GTPv1 Cause Codes
```
Value | Meaning
------|--------------------------------------------------
0x80  | Request accepted
0x81  | Request accepted with modification
0xC0  | Non-existent
0xC1  | Invalid message format
0xC2  | IMSI not known
0xC3  | MS is GPRS detached
0xC4  | MS is not GPRS responding
0xC5  | MS refuses
0xC6  | Version not supported
0xC7  | No resources available
0xC8  | Service not supported
0xC9  | Mandatory IE incorrect
0xCA  | Mandatory IE missing
0xCB  | Optional IE incorrect
0xCC  | System failure
0xCD  | Roaming restriction
```

#### GTPv2 Cause Codes
```
Value | Meaning
------|--------------------------------------------------
16    | Request accepted
17    | Request accepted partially
64    | Context not found
65    | Invalid message format
66    | Version not supported
67    | Invalid length
68    | Service not supported
69    | Mandatory IE incorrect
70    | Mandatory IE missing
71    | System failure
72    | No resources available
73    | Semantic error in TFT operation
74    | Syntactic error in TFT operation
75    | Semantic errors in packet filter(s)
76    | Syntactic errors in packet filter(s)
77    | Missing or unknown APN
```

### Analyzing PCAPs in Wireshark

#### Step 1: Open PCAP and Apply Display Filter
```
1. File → Open → Select PCAP file
2. Apply filter: gtp or gtpv2
3. View → Time Display Format → Seconds Since Previous Displayed Packet
```

#### Step 2: Identify Message Pairs
```
1. Find request message (e.g., Modify Bearer Request)
2. Note the Sequence Number in packet details
3. Find corresponding response with same Sequence Number
4. Verify TEID relationship (request uses peer's TEID)
```

#### Step 3: Examine Key Fields
```
For each message, expand:
- GTPv2 Header → Check Version, Message Type, TEID, Sequence
- Information Elements → Expand each IE
  - Bearer Context → Check Bearer ID, Cause
  - Cause → Verify success/failure code
  - FTEID → Check IP addresses and TEIDs
```

#### Step 4: Follow Complete Flow
```
1. Right-click on packet → Follow → UDP Stream
2. Or use: (ip.addr == <src> && ip.addr == <dst>) && gtp
3. Analyze timing between request and response
4. Check for retransmissions (duplicate sequence numbers)
```

#### Step 5: Export Specific Packets
```
1. Select packets of interest
2. File → Export Specified Packets
3. Save subset for focused analysis
```

---

## Open Source Tools and Resources

### Capture and Analysis Tools

#### 1. Wireshark
- **Website**: https://www.wireshark.org/
- **Description**: Industry-standard packet analyzer with excellent GTP support
- **GTP Features**:
  - Full GTPv1 and GTPv2 dissection
  - TEID tracking across messages
  - Statistics → GTP message types distribution
  - Expert info for protocol violations
- **Usage**:
  ```bash
  # Command-line capture
  tshark -i eth0 -f "udp port 2123" -w gtp_capture.pcap
  
  # Read and filter
  tshark -r gtp_capture.pcap -Y "gtpv2.message_type == 34"
  ```

#### 2. tcpdump
- **Website**: https://www.tcpdump.org/
- **Description**: Command-line packet capture utility
- **Usage**:
  ```bash
  # Capture GTP control plane
  tcpdump -i any -s0 -w gtp.pcap 'udp port 2123'
  
  # Capture specific host pair
  tcpdump -i any -s0 -w gtp.pcap 'host 10.0.1.100 and host 10.0.2.100 and udp port 2123'
  ```

#### 3. Termshark
- **Website**: https://termshark.io/
- **Description**: Terminal UI for tshark, like Wireshark in your terminal
- **Installation**:
  ```bash
  # Linux
  wget https://github.com/gcla/termshark/releases/latest/download/termshark_*_linux_x64.tar.gz
  tar -xvf termshark_*_linux_x64.tar.gz
  ```

### GTP Simulation and Testing Tools

#### 1. Open5GS
- **Website**: https://open5gs.org/
- **Description**: Open source implementation of 5G Core and EPC
- **Features**:
  - Complete MME, SGW, PGW implementation
  - GTPv2 support for LTE/EPC
  - Can generate realistic GTP traffic for testing
- **Installation**:
  ```bash
  sudo add-apt-repository ppa:open5gs/latest
  sudo apt update
  sudo apt install open5gs
  ```
- **Use Case**: Set up test network and capture real GTP modify/delete flows

#### 2. free5GC
- **Website**: https://free5gc.org/
- **Description**: Open source 5G core network implementation
- **Features**:
  - Full 5GC implementation
  - GTPv2 and PFCP support
  - Good for GTPv2 testing
- **GitHub**: https://github.com/free5gc/free5gc

#### 3. srsRAN
- **Website**: https://www.srslte.com/
- **Description**: Open source 4G/5G RAN (Radio Access Network)
- **Features**:
  - UE simulator
  - eNodeB implementation
  - Can be used with Open5GS/free5GC
- **GitHub**: https://github.com/srsran/srsRAN

#### 4. UERANSIM
- **Website**: https://github.com/aligungr/UERANSIM
- **Description**: Open source 5G UE and RAN simulator
- **Features**:
  - Simulates UE and gNodeB
  - Works with 5G core networks
  - Good for generating test traffic
- **Installation**:
  ```bash
  git clone https://github.com/aligungr/UERANSIM
  cd UERANSIM
  make
  ```

#### 5. PacketDrill
- **Website**: https://github.com/google/packetdrill
- **Description**: Script-based network stack testing tool
- **Use Case**: Create scripted GTP packet sequences for testing

### PCAP Sample Repositories

#### 1. Wireshark Sample Captures
- **Website**: https://wiki.wireshark.org/SampleCaptures
- **GTP Samples**: Look for files with "gprs", "umts", "lte" in names
- **Direct Links** (if available):
  - Search for: gtp, gprs, umts captures

#### 2. Malware-Traffic-Analysis.net
- **Website**: https://www.malware-traffic-analysis.net/
- **Note**: Primarily malware traffic, but has comprehensive samples

#### 3. PacketLife.net
- **Website**: http://packetlife.net/captures/
- **Description**: Curated collection of packet captures
- **Search for**: GTP, GPRS, mobile network captures

#### 4. CloudShark Public Captures
- **Website**: https://www.cloudshark.org/captures
- **Description**: Cloud-based packet analysis with public captures

### GTP Testing and Traffic Generation

#### 1. TRex Realistic Traffic Generator
- **Website**: https://trex-tgn.cisco.com/
- **Description**: Cisco's open source traffic generator
- **Features**:
  - Can generate GTP traffic
  - Stateful traffic generation
- **GitHub**: https://github.com/cisco-system-traffic-generator/trex-core

#### 2. Scapy
- **Website**: https://scapy.net/
- **Description**: Python packet manipulation library
- **GTP Example**:
  ```python
  from scapy.all import *
  from scapy.contrib.gtp import *
  
  # Create GTPv2 Modify Bearer Request
  ip = IP(src="10.0.1.100", dst="10.0.2.100")
  udp = UDP(sport=2123, dport=2123)
  gtp_header = GTPHeader(version=2, T=1, teid=0x22222222, seq=0x123456)
  modify_bearer = GTPModifyBearerRequest()
  
  packet = ip/udp/gtp_header/modify_bearer
  send(packet)
  ```
- **Installation**:
  ```bash
  pip install scapy
  ```

#### 3. GTP-U Kernel Module (Linux)
- **Description**: Linux kernel module for GTP-U encapsulation
- **Documentation**: https://www.kernel.org/doc/Documentation/networking/gtp.txt
- **Use Case**: Create GTP tunnels for testing

### Reference Materials

#### 1. 3GPP Specifications
- **TS 29.060**: GTPv1 protocol specification
  - URL: https://www.3gpp.org/DynaReport/29060.htm
  - Sections 7.5 (Modify) and 7.3 (Delete)
  
- **TS 29.274**: GTPv2 protocol specification
  - URL: https://www.3gpp.org/DynaReport/29274.htm
  - Sections 7.2.7 (Modify Bearer), 7.2.8 (Delete Session), 7.2.17 (Delete Bearer)

#### 2. IANA Protocol Numbers
- **GTP Protocol Numbers**: https://www.iana.org/assignments/gtp-parameters/gtp-parameters.xhtml
- **Message types, IEs, cause codes**

#### 3. Wireshark Display Filter Reference
- **GTP Filters**: https://www.wireshark.org/docs/dfref/g/gtp.html
- **GTPv2 Filters**: https://www.wireshark.org/docs/dfref/g/gtpv2.html

### Sample Test Lab Setup

#### Minimal Test Environment
```
┌──────┐      ┌──────┐      ┌──────┐
│  MME │◄────►│  SGW │◄────►│  PGW │
└──────┘      └──────┘      └──────┘
   │
   │ GTPv2-C (2123/UDP)
   │
┌──────────┐
│ Wireshark│
│  Capture │
└──────────┘

Setup using Open5GS:
1. Install Open5GS on Ubuntu 20.04+
2. Configure MME, SGW, PGW on same host (different interfaces)
3. Use UE simulator (srsRAN or UERANSIM)
4. Capture on loopback or virtual interfaces
```

#### Docker-Based Lab
```bash
# Using free5GC compose
git clone https://github.com/free5gc/free5gc-compose.git
cd free5gc-compose
docker-compose up -d

# Start capture on docker network
docker network ls
docker run --rm --net=container:<container_id> \
  nicolaka/netshoot tcpdump -i any -w /tmp/gtp.pcap udp port 2123
```

### Creating Your Own Test PCAPs

#### Method 1: Using Scapy Script
```python
#!/usr/bin/env python3
from scapy.all import *
from scapy.contrib.gtp import *

# Create Modify Bearer Request
ip_req = IP(src="10.0.1.100", dst="10.0.2.100")
udp_req = UDP(sport=2123, dport=2123)
gtp_hdr_req = GTPHeader(version=2, T=1, teid=0x22222222, seq=0x123456)
modify_req = GTPModifyBearerRequest(IE_list=[
    IE_FTEID(v4=1, ipv4="10.5.1.10", TEID=0x21000001),
    IE_EBI(EBI=5)
])
pkt_req = ip_req/udp_req/gtp_hdr_req/modify_req

# Create Modify Bearer Response
ip_resp = IP(src="10.0.2.100", dst="10.0.1.100")
udp_resp = UDP(sport=2123, dport=2123)
gtp_hdr_resp = GTPHeader(version=2, T=1, teid=0x11111111, seq=0x123456)
modify_resp = GTPModifyBearerResponse(IE_list=[
    IE_Cause(Cause=16),  # Request accepted
    IE_EBI(EBI=5)
])
pkt_resp = ip_resp/udp_resp/gtp_hdr_resp/modify_resp

# Write to PCAP
wrpcap("modify_bearer_test.pcap", [pkt_req, pkt_resp])
print("PCAP file created: modify_bearer_test.pcap")
```

#### Method 2: Using Text2pcap
```bash
# Create hex dump file
cat > gtp_modify.txt << 'EOF'
0000  00 00 00 00 00 00 00 00 00 00 00 00 08 00 45 00
0010  00 54 00 00 40 00 40 11 00 00 0a 00 01 64 0a 00
0020  02 64 08 4b 08 4b 00 40 00 00 48 22 00 28 22 22
0030  22 22 12 34 56 00 57 00 09 00 86 0a 05 01 0a 21
0040  00 00 01 49 00 01 00 05
EOF

# Convert to PCAP
text2pcap -u 2123,2123 gtp_modify.txt gtp_modify.pcap

# Verify
tshark -r gtp_modify.pcap -V
```

---

## Practical Analysis Examples

### Example 1: Successful Modify Bearer Flow

```
Frame 1: Modify Bearer Request (MME → SGW)
├─ IP: 10.0.1.100 → 10.0.2.100
├─ UDP: 2123 → 2123
├─ GTPv2
│  ├─ Version: 2
│  ├─ Message Type: 34 (Modify Bearer Request)
│  ├─ TEID: 0x22222222
│  ├─ Sequence: 0x123456
│  └─ Information Elements:
│     ├─ FTEID (eNodeB): 10.5.1.10, TEID 0x21000001
│     └─ EPS Bearer ID: 5

Frame 2: Modify Bearer Response (SGW → MME)
├─ IP: 10.0.2.100 → 10.0.1.100
├─ UDP: 2123 → 2123
├─ GTPv2
│  ├─ Version: 2
│  ├─ Message Type: 35 (Modify Bearer Response)
│  ├─ TEID: 0x11111111
│  ├─ Sequence: 0x123456 (matches request)
│  └─ Information Elements:
│     ├─ Cause: 16 (Request accepted) ✓
│     └─ Bearer Context:
│        ├─ EPS Bearer ID: 5
│        └─ Cause: 16 (Request accepted) ✓

Analysis:
✓ Sequence numbers match (0x123456)
✓ Response uses MME's TEID (0x11111111)
✓ Cause code 16 indicates success
✓ Round-trip time: 15 ms (normal)
```

### Example 2: Failed Delete Bearer (Context Not Found)

```
Frame 1: Delete Bearer Request (PGW → SGW)
├─ IP: 10.0.3.100 → 10.0.2.100
├─ UDP: 2123 → 2123
├─ GTPv2
│  ├─ Message Type: 99 (Delete Bearer Request)
│  ├─ TEID: 0x33333333
│  ├─ Sequence: 0x789ABC
│  └─ Information Elements:
│     ├─ Linked EPS Bearer ID: 5
│     └─ EPS Bearer ID: 6 (to be deleted)

Frame 2: Delete Bearer Response (SGW → PGW)
├─ IP: 10.0.2.100 → 10.0.3.100
├─ UDP: 2123 → 2123
├─ GTPv2
│  ├─ Message Type: 100 (Delete Bearer Response)
│  ├─ TEID: 0x44444444
│  ├─ Sequence: 0x789ABC
│  └─ Information Elements:
│     ├─ Cause: 64 (Context not found) ✗
│     └─ Bearer Context:
│        ├─ EPS Bearer ID: 6
│        └─ Cause: 64 (Context not found) ✗

Analysis:
✓ Sequence numbers match (0x789ABC)
✗ Cause code 64 indicates failure
✗ Bearer context was not found at SGW
→ Possible causes:
  - Bearer already deleted
  - Wrong TEID or Bearer ID
  - SGW context mismatch
→ Recommendation: Check bearer setup logs
```

### Example 3: Delete Session with Multiple Bearers

```
Frame 1: Delete Session Request (MME → SGW)
├─ IP: 10.0.1.100 → 10.0.2.100
├─ GTPv2
│  ├─ Message Type: 36 (Delete Session Request)
│  ├─ TEID: 0x22222222
│  ├─ Sequence: 0xDEF012
│  └─ Information Elements:
│     ├─ Linked EPS Bearer ID: 5 (default)
│     └─ Indication: UE detach

Frame 2: Delete Session Response (SGW → MME)
├─ IP: 10.0.2.100 → 10.0.1.100
├─ GTPv2
│  ├─ Message Type: 37 (Delete Session Response)
│  ├─ TEID: 0x11111111
│  ├─ Sequence: 0xDEF012
│  └─ Information Elements:
│     └─ Cause: 16 (Request accepted) ✓

Frame 3: Delete Bearer Request (SGW → PGW)
├─ IP: 10.0.2.100 → 10.0.3.100
├─ GTPv2
│  ├─ Message Type: 99 (Delete Bearer Request)
│  ├─ TEID: 0x44444444
│  └─ Information Elements:
│     ├─ Linked EPS Bearer ID: 5
│     ├─ EPS Bearer ID: 5 (default)
│     └─ EPS Bearer ID: 6 (dedicated)

Frame 4: Delete Bearer Response (PGW → SGW)
├─ IP: 10.0.3.100 → 10.0.2.100
├─ GTPv2
│  ├─ Message Type: 100 (Delete Bearer Response)
│  └─ Information Elements:
│     ├─ Cause: 16 (Request accepted) ✓
│     └─ Bearer Contexts (both deleted)

Analysis:
✓ Complete session teardown
✓ Default bearer (5) and dedicated bearer (6) both deleted
✓ Proper signaling chain: MME → SGW → PGW
✓ All cause codes indicate success (16)
→ Total teardown time: 45 ms
```

---

## Troubleshooting Common Issues

### Issue 1: Missing GTP Dissection in Wireshark

**Symptoms**: Packets show as UDP but not dissected as GTP

**Solutions**:
```
1. Verify UDP port is 2123 (GTP-C) or 2152 (GTP-U)
2. Enable GTP protocol: Analyze → Enabled Protocols → Check GTP
3. Decode as GTP: Right-click packet → Decode As → UDP port → GTP
4. Check Wireshark version (ensure > 2.6 for GTPv2 support)
```

### Issue 2: TEID Mismatch Errors

**Symptoms**: Responses appear but don't correlate with requests

**Analysis**:
```
1. Check TEID in request vs response
   - Request uses peer's TEID
   - Response uses sender's TEID
2. Verify in Wireshark: GTPv2 → TEID field
3. Use filter: gtpv2.teid == 0xXXXXXXXX
```

### Issue 3: Sequence Number Tracking

**Symptoms**: Cannot match requests with responses

**Solution**:
```
1. Extract sequence number: GTPv2 → Sequence Number
2. Filter request/response pair:
   gtpv2.seq == 0x123456
3. Use Wireshark conversation tracking:
   Right-click → Follow → UDP Stream
```

### Issue 4: Capture Shows No GTP Traffic

**Check**:
```
1. Verify capture interface (use correct network interface)
2. Check capture filter syntax: udp port 2123
3. Ensure traffic is flowing (check with: tcpdump -i any -n udp)
4. Verify no firewall blocking
5. Check if traffic is encrypted/tunneled
```

---

## Quick Reference Cheat Sheet

### Essential Wireshark Filters

```bash
# Quick filter combinations
gtp || gtpv2                    # All GTP traffic
gtpv2.message_type == 34        # Modify Bearer Request
gtpv2.message_type == 36        # Delete Session Request
gtpv2.cause == 16               # Successful operations
gtpv2.cause != 16               # Failed operations
gtpv2.teid == 0x12345678        # Specific TEID
gtpv2.seq == 0x123456           # Specific sequence
ip.addr == 10.0.1.100 && gtp    # Specific network element
```

### Message Type Quick Reference

```
GTPv1:
0x12 = Update PDP Context Request
0x13 = Update PDP Context Response
0x14 = Delete PDP Context Request
0x15 = Delete PDP Context Response

GTPv2:
34 = Modify Bearer Request
35 = Modify Bearer Response
36 = Delete Session Request
37 = Delete Session Response
99 = Delete Bearer Request
100 = Delete Bearer Response
```

### Success/Failure Cause Codes

```
GTPv1: 0x80 = Success
GTPv2: 16 = Success

Common Failure Codes (GTPv2):
64 = Context not found
65 = Invalid message format
69 = Mandatory IE incorrect
70 = Mandatory IE missing
```

### Port Numbers

```
2123/UDP = GTP-C (Control Plane)
2152/UDP = GTP-U (User Plane)
```

---

## Conclusion

This guide provides comprehensive information for capturing and analyzing GTP Modify and Delete operations. Key takeaways:

1. **Use appropriate Wireshark filters** to isolate specific message types
2. **Track TEID and sequence numbers** for request/response correlation
3. **Analyze cause codes** to determine success or failure
4. **Leverage open source tools** (Open5GS, free5GC, srsRAN) for test traffic generation
5. **Follow message flows** across network elements (MME → SGW → PGW)

For further assistance:
- 3GPP specifications (TS 29.060 for GTPv1, TS 29.274 for GTPv2)
- Wireshark documentation and sample captures
- Open5GS and free5GC communities for practical implementations

---

**Document Version**: 1.0  
**Last Updated**: 2025  
**Author**: GTP PCAP Analysis Guide  
**License**: Open Documentation - Free to use and distribute
