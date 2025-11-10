# GTP (GPRS Tunneling Protocol) PCAP Test Scenarios

This repository provides comprehensive documentation and tools for capturing, analyzing, and generating GTP (GPRS Tunneling Protocol) packet captures for testing and development purposes.

## Overview

GTP is a core protocol used in mobile networks (GPRS, UMTS, LTE, 5G) to carry user data between network elements. This repository focuses on:

- **GTPv1**: Modify PDP Context and Delete PDP Context operations
- **GTPv2**: Modify Bearer, Delete Bearer, and Delete Session operations

## Repository Contents

### 📚 Documentation

**[GTP_PCAP_Test_Scenario.md](GTP_PCAP_Test_Scenario.md)** - Complete guide covering:
- Detailed GTPv1 and GTPv2 test scenarios
- Wireshark capture setup and filter guidelines
- Test data examples (UE/IP/TEID values)
- PCAP field annotations (TEID, message types, sequence numbers, cause codes)
- Protocol header structures and Information Elements
- Open source tools and resources
- Practical analysis examples
- Troubleshooting common issues
- Quick reference cheat sheets

### 🛠️ Example Scripts

**[examples/](examples/)** - Python scripts for generating sample PCAP files:
- `generate_gtpv2_modify_bearer.py` - Creates Modify Bearer Request/Response PCAP
- `generate_gtpv2_delete_session.py` - Creates Delete Session flow PCAP with Delete Bearer messages
- `README.md` - Instructions for using the example scripts

## Quick Start

### 1. View Documentation

Read the comprehensive guide:
```bash
cat GTP_PCAP_Test_Scenario.md
```

### 2. Generate Sample PCAPs

Install requirements:
```bash
pip install scapy
```

Generate example PCAP files:
```bash
cd examples
python generate_gtpv2_modify_bearer.py
python generate_gtpv2_delete_session.py
```

### 3. Analyze with Wireshark

```bash
wireshark gtpv2_modify_bearer_example.pcap
```

Use these display filters:
```
gtpv2                          # All GTPv2 traffic
gtpv2.message_type == 34       # Modify Bearer Request
gtpv2.message_type == 36       # Delete Session Request
gtpv2.cause == 16              # Successful operations
```

## Key Features

### ✅ Comprehensive Coverage
- Complete GTPv1 and GTPv2 protocol documentation
- Modify and Delete operation workflows
- Detailed message structures and fields

### 🔍 Wireshark Guidelines
- Pre-capture setup instructions
- Display and capture filters
- Step-by-step PCAP analysis procedures

### 📊 Test Data Examples
- Realistic network element IP addresses
- Sample TEID values
- Bearer configurations
- Success and failure scenarios

### 🚀 Practical Tools
- Python scripts for PCAP generation
- Ready-to-use Wireshark filters
- Command-line analysis examples

### 📖 Reference Materials
- 3GPP specification links
- Message type quick reference
- Cause code tables
- IE (Information Element) reference

## Use Cases

This repository is useful for:

1. **Network Engineers**: Understanding GTP protocol flows
2. **Test Engineers**: Creating test scenarios and validating implementations
3. **Developers**: Building or debugging GTP-based applications
4. **Security Analysts**: Analyzing mobile network traffic
5. **Students**: Learning about mobile network protocols

## Wireshark Display Filter Examples

```bash
# All GTP modify operations
(gtp.message == 0x12) || (gtpv2.message_type == 34)

# All GTP delete operations  
(gtp.message == 0x14) || (gtpv2.message_type == 99) || (gtpv2.message_type == 36)

# Specific TEID
gtpv2.teid == 0x22222222

# Failed operations
gtpv2.cause != 16 && gtpv2.message_type in {23, 35, 37, 64, 100}

# Specific network element conversation
ip.addr == 10.0.1.100 && ip.addr == 10.0.2.100 && gtpv2
```

## Open Source Tools Referenced

- **[Wireshark](https://www.wireshark.org/)** - Packet analyzer with GTP support
- **[Open5GS](https://open5gs.org/)** - Open source 5G Core and EPC implementation
- **[free5GC](https://free5gc.org/)** - Open source 5G core network
- **[srsRAN](https://www.srslte.com/)** - Open source 4G/5G RAN
- **[UERANSIM](https://github.com/aligungr/UERANSIM)** - 5G UE and RAN simulator
- **[Scapy](https://scapy.net/)** - Python packet manipulation library

## Protocol Reference

### GTPv1 Message Types (Modify/Delete)
```
0x12 (18)  - Update PDP Context Request
0x13 (19)  - Update PDP Context Response
0x14 (20)  - Delete PDP Context Request
0x15 (21)  - Delete PDP Context Response
```

### GTPv2 Message Types (Modify/Delete)
```
34  (0x22) - Modify Bearer Request
35  (0x23) - Modify Bearer Response
36  (0x24) - Delete Session Request
37  (0x25) - Delete Session Response
99  (0x63) - Delete Bearer Request
100 (0x64) - Delete Bearer Response
```

### Common Cause Codes
```
GTPv1:
  0x80 - Request accepted
  0xC0 - Non-existent
  0xC4 - Context not found

GTPv2:
  16 - Request accepted
  64 - Context not found
  65 - Invalid message format
  70 - Mandatory IE missing
```

## Contributing

Contributions are welcome! Areas for contribution:
- Additional test scenarios
- GTPv1 PCAP generation scripts
- More complex multi-bearer scenarios
- Real-world capture examples
- Additional analysis examples

## Resources

### Specifications
- **3GPP TS 29.060**: GTPv1 protocol specification
- **3GPP TS 29.274**: GTPv2 protocol specification

### Documentation
- [Wireshark GTP Display Filter Reference](https://www.wireshark.org/docs/dfref/g/gtp.html)
- [Wireshark GTPv2 Display Filter Reference](https://www.wireshark.org/docs/dfref/g/gtpv2.html)

## License

This documentation and scripts are provided as open resources for educational and testing purposes.

## Support

For questions or issues:
1. Review the main documentation: `GTP_PCAP_Test_Scenario.md`
2. Check the examples README: `examples/README.md`
3. Consult 3GPP specifications for protocol details

---

**Version**: 1.0  
**Last Updated**: 2025  
**Protocol Coverage**: GTPv1, GTPv2
