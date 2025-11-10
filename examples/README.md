# GTP PCAP Example Scripts

This directory contains Python scripts for generating sample GTP PCAP files for testing and analysis purposes.

## Prerequisites

Install Scapy with GTP support:

```bash
pip install scapy
```

## Available Scripts

### 1. generate_gtpv2_modify_bearer.py

Generates a PCAP file with GTPv2 Modify Bearer Request/Response message pair.

**Usage:**
```bash
python generate_gtpv2_modify_bearer.py
```

**Output:** `gtpv2_modify_bearer_example.pcap`

**Contains:**
- Modify Bearer Request (MME → SGW)
- Modify Bearer Response (SGW → MME)

### 2. generate_gtpv2_delete_session.py

Generates a PCAP file with a complete Delete Session flow including subsequent Delete Bearer messages.

**Usage:**
```bash
python generate_gtpv2_delete_session.py
```

**Output:** `gtpv2_delete_session_example.pcap`

**Contains:**
- Delete Session Request (MME → SGW)
- Delete Session Response (SGW → MME)
- Delete Bearer Request (SGW → PGW)
- Delete Bearer Response (PGW → SGW)

## Analyzing Generated PCAPs

### Using Wireshark

```bash
wireshark gtpv2_modify_bearer_example.pcap
```

**Useful Display Filters:**
```
gtpv2                                    # All GTPv2 traffic
gtpv2.message_type == 34                 # Modify Bearer Request
gtpv2.message_type == 36                 # Delete Session Request
gtpv2.cause == 16                        # Successful operations
```

### Using tshark

```bash
# View detailed packet information
tshark -r gtpv2_modify_bearer_example.pcap -V

# Filter specific message types
tshark -r gtpv2_modify_bearer_example.pcap -Y "gtpv2.message_type == 34"

# Extract sequence numbers
tshark -r gtpv2_modify_bearer_example.pcap -T fields -e gtpv2.seq
```

### Using tcpdump

```bash
# Basic read
tcpdump -r gtpv2_modify_bearer_example.pcap -n

# Verbose output
tcpdump -r gtpv2_modify_bearer_example.pcap -vv -n
```

## Customizing the Scripts

You can modify the scripts to generate different scenarios by changing:

1. **IP Addresses**: Update source/destination IPs for different network elements
2. **TEIDs**: Change tunnel endpoint identifiers
3. **Sequence Numbers**: Modify for different message correlations
4. **Bearer IDs**: Adjust EPS Bearer IDs
5. **Cause Codes**: Simulate failures by changing cause codes

### Example Modifications

**Change to simulate failure:**
```python
# In create_modify_bearer_response()
IE_Cause(instance=0, Cause=64)  # 64 = Context not found
```

**Add more bearers:**
```python
# In create_delete_bearer_request()
IE_BearerContext(
    instance=2,
    IE_list=[
        IE_EBI(instance=0, EBI=7),
        IE_Cause(instance=0, Cause=54)
    ]
)
```

**Change network element IPs:**
```python
# For different MME
ip = IP(src="10.0.10.50", dst="10.0.2.100")
```

## Testing Scenarios

### Scenario 1: QoS Modification
Use `generate_gtpv2_modify_bearer.py` to simulate QoS changes for an active bearer.

### Scenario 2: UE Detach
Use `generate_gtpv2_delete_session.py` to simulate complete session teardown during UE detach.

### Scenario 3: Failure Analysis
Modify cause codes to 64 (Context not found) or 70 (Mandatory IE missing) to simulate and test error handling.

## Additional Resources

For more detailed information about GTP protocol analysis, refer to:
- Main documentation: `../GTP_PCAP_Test_Scenario.md`
- 3GPP TS 29.274: GTPv2 specification
- Wireshark GTPv2 dissector documentation

## Troubleshooting

### Scapy GTP Import Error

If you encounter import errors:
```bash
pip install --upgrade scapy
# or specifically install GTP contrib module
```

### Permission Denied (Linux/macOS)

Make scripts executable:
```bash
chmod +x generate_gtpv2_modify_bearer.py
chmod +x generate_gtpv2_delete_session.py
```

### Wireshark Doesn't Recognize GTP

1. Ensure Wireshark version is 2.6 or newer
2. Check if GTP dissector is enabled: Analyze → Enabled Protocols
3. Manually decode as GTP: Right-click packet → Decode As → GTP

## Contributing

Feel free to extend these scripts with additional scenarios:
- GTPv1 message generation
- More complex bearer setups
- Error scenarios with different cause codes
- Realistic multi-session traffic patterns
