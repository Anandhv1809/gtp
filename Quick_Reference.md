# GTP PCAP Quick Reference Card

A one-page quick reference for common GTP PCAP analysis tasks.

## Wireshark Display Filters

### Basic Filters
```
gtp                           # All GTP traffic (v1)
gtpv2                         # All GTPv2 traffic
gtp || gtpv2                  # All GTP versions
```

### Message Type Filters (GTPv1)
```
gtp.message == 0x12           # Update PDP Context Request
gtp.message == 0x13           # Update PDP Context Response
gtp.message == 0x14           # Delete PDP Context Request
gtp.message == 0x15           # Delete PDP Context Response
```

### Message Type Filters (GTPv2)
```
gtpv2.message_type == 34      # Modify Bearer Request
gtpv2.message_type == 35      # Modify Bearer Response
gtpv2.message_type == 36      # Delete Session Request
gtpv2.message_type == 37      # Delete Session Response
gtpv2.message_type == 99      # Delete Bearer Request
gtpv2.message_type == 100     # Delete Bearer Response
```

### Field-Specific Filters
```
gtpv2.teid == 0x12345678      # Filter by TEID
gtpv2.seq == 0x123456         # Filter by sequence number
gtpv2.eps_bearer_id == 5      # Filter by bearer ID
gtpv2.cause == 16             # Only successful operations
gtpv2.cause != 16             # Only failed operations
```

### Network Element Filters
```
ip.addr == 10.0.1.100 && gtpv2           # Specific element
ip.addr == 10.0.1.100 && ip.addr == 10.0.2.100 && gtpv2  # Conversation
```

### Combined Filters
```
# All modify operations
(gtp.message == 0x12) || (gtpv2.message_type == 34)

# All delete operations
(gtp.message == 0x14) || (gtpv2.message_type == 99) || (gtpv2.message_type == 36)

# Failed modify operations
(gtpv2.message_type == 35) && (gtpv2.cause != 16)
```

## Capture Filters (BPF)

```bash
udp port 2123                 # GTP-C (Control Plane)
udp port 2152                 # GTP-U (User Plane)
udp port 2123 or udp port 2152  # Both planes

# Specific hosts
host 10.0.1.100 and udp port 2123
(host 10.0.1.100 or host 10.0.2.100) and udp port 2123
```

## Command-Line Tools

### tshark
```bash
# Capture GTP traffic
tshark -i eth0 -f "udp port 2123" -w gtp.pcap

# Read and filter
tshark -r gtp.pcap -Y "gtpv2.message_type == 34"

# Display specific fields
tshark -r gtp.pcap -T fields -e gtpv2.message_type -e gtpv2.seq -e gtpv2.teid

# Statistics
tshark -r gtp.pcap -q -z io,stat,1,"gtpv2"
```

### tcpdump
```bash
# Capture
tcpdump -i any -s0 -w gtp.pcap 'udp port 2123'

# Read
tcpdump -r gtp.pcap -n

# Filter by host
tcpdump -r gtp.pcap 'host 10.0.1.100' -n
```

## Message Types

### GTPv1
| Hex  | Dec | Message                      |
|------|-----|------------------------------|
| 0x12 | 18  | Update PDP Context Request   |
| 0x13 | 19  | Update PDP Context Response  |
| 0x14 | 20  | Delete PDP Context Request   |
| 0x15 | 21  | Delete PDP Context Response  |

### GTPv2
| Hex  | Dec | Message                      |
|------|-----|------------------------------|
| 0x22 | 34  | Modify Bearer Request        |
| 0x23 | 35  | Modify Bearer Response       |
| 0x24 | 36  | Delete Session Request       |
| 0x25 | 37  | Delete Session Response      |
| 0x63 | 99  | Delete Bearer Request        |
| 0x64 | 100 | Delete Bearer Response       |

## Cause Codes

### GTPv1
| Hex  | Dec | Meaning                      |
|------|-----|------------------------------|
| 0x80 | 128 | Request accepted             |
| 0x81 | 129 | Request accepted partially   |
| 0xC0 | 192 | Non-existent                 |
| 0xC1 | 193 | Invalid message format       |
| 0xC4 | 196 | Context not found            |
| 0xCC | 204 | System failure               |

### GTPv2
| Dec | Meaning                      |
|-----|------------------------------|
| 16  | Request accepted             |
| 17  | Request accepted partially   |
| 64  | Context not found            |
| 65  | Invalid message format       |
| 66  | Version not supported        |
| 69  | Mandatory IE incorrect       |
| 70  | Mandatory IE missing         |
| 71  | System failure               |
| 72  | No resources available       |

## Common Test Values

### Network Elements (GTPv2 Example)
```
MME:    10.0.1.100    (Control TEID: 0x11111111)
SGW:    10.0.2.100    (Control TEID: 0x22222222, 0x33333333)
PGW:    10.0.3.100    (Control TEID: 0x44444444)
eNodeB: 10.5.1.10     (User TEID: 0x21000001)
```

### Bearer IDs
```
Default Bearer:    5
Dedicated Bearer:  6, 7, 8, ...
```

### UE Information
```
IMSI:        001010000000099
MSISDN:      +1987654321
UE IP:       172.16.5.99
```

## Protocol Ports

```
2123/UDP    GTP-C (Control Plane)
2152/UDP    GTP-U (User Plane)
```

## Typical Message Flow

### Modify Bearer
```
1. MME → SGW: Modify Bearer Request (Type 34)
2. SGW → MME: Modify Bearer Response (Type 35, Cause 16)
```

### Delete Session (with bearers)
```
1. MME → SGW: Delete Session Request (Type 36)
2. SGW → MME: Delete Session Response (Type 37, Cause 16)
3. SGW → PGW: Delete Bearer Request (Type 99)
4. PGW → SGW: Delete Bearer Response (Type 100, Cause 16)
```

## Key Fields to Check

### In Request
- ✓ TEID (uses peer's TEID)
- ✓ Sequence Number
- ✓ Bearer ID(s)
- ✓ Correct Information Elements

### In Response
- ✓ TEID (uses sender's TEID)
- ✓ Sequence Number (matches request)
- ✓ Cause Code (16 = success)
- ✓ Bearer-specific causes

## Analysis Checklist

1. **Verify Message Pair**
   - [ ] Sequence numbers match
   - [ ] TEIDs are correct (swapped)
   - [ ] Reasonable response time (< 100ms typical)

2. **Check Success**
   - [ ] Cause code is 16 (Request accepted)
   - [ ] Bearer-specific causes are 16
   - [ ] All mandatory IEs present

3. **Troubleshoot Failures**
   - [ ] Note cause code value
   - [ ] Check for missing IEs
   - [ ] Verify TEID/Bearer ID exists
   - [ ] Check timing (timeouts?)

## Quick Wireshark Tips

```
# Follow conversation
Right-click packet → Follow → UDP Stream

# Expert Info (errors/warnings)
Analyze → Expert Information

# Statistics
Statistics → GTP → Message Statistics

# Time delta
View → Time Display Format → Seconds Since Previous Packet

# Export packets
File → Export Specified Packets
```

## Scapy Quick Example

```python
from scapy.all import *
from scapy.contrib.gtp import *

# Read PCAP
packets = rdpcap("gtp.pcap")

# Filter GTPv2 Modify Bearer Requests
for pkt in packets:
    if pkt.haslayer(GTPModifyBearerRequest):
        print(f"TEID: {pkt[GTPHeader].teid:08x}")
        print(f"Seq:  {pkt[GTPHeader].seq:06x}")
```

## Resources

- **Full Documentation**: `GTP_PCAP_Test_Scenario.md`
- **Example Scripts**: `examples/`
- **3GPP TS 29.060**: GTPv1 Specification
- **3GPP TS 29.274**: GTPv2 Specification
- **Wireshark**: https://www.wireshark.org/

---
*For complete details, see GTP_PCAP_Test_Scenario.md*
