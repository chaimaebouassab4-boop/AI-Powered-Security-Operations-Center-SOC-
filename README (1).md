# SIEM-Log-Monitoring-Threat-Detection-Lab
A hands-on SIEM and Detection Engineering project using Elasticsearch, Logstash, and Kibana. Includes log ingestion for Windows/Linux and custom detection rules for common attack vectors like PowerShell abuse and brute force.

# 🛡️ SIEM Lab: Log Monitoring & Threat Detection

A hands-on security lab simulating real-world SOC operations. Detect, investigate, and respond to security threats using industry-standard SIEM platforms.

## 🎯 What You'll Build

- **Log Ingestion Pipeline**: Aggregate Sysmon, Windows Event Logs, and Linux auth logs
- **Custom Detection Rules**: Identify brute force attacks, suspicious PowerShell execution, and lateral movement
- **Alert Triage Workflow**: Investigate real-world attack simulations and correlation events
- **Response Playbooks**: Document findings and remediation steps

## 🛠️ Tech Stack

| Component | Tool |
|-----------|------|
| SIEM | **Splunk Free** or **ELK Stack** |
| Log Sources | Sysmon, Windows Event Logs, Linux auditd |
| Simulation | Custom Python/Bash attack scripts |
| Infrastructure | Windows & Linux VMs |

## 🚀 Quick Start

### Prerequisites
- 2+ VMs (Windows 10/Server, Ubuntu 20.04+)
- 8GB+ RAM available
- Basic Linux/Windows command line knowledge

### Installation

**Option 1: Splunk**
```bash
# Download Splunk Free from splunk.com
# Install on dedicated VM
./splunk_installer
# Enable Sysmon on Windows hosts
# Forward logs to Splunk
```

**Option 2: ELK Stack**
```bash
docker-compose up -d elasticsearch kibana logstash
# Configure Beats (Auditbeat, Winlogbeat) on hosts
# Ingest logs via Logstash pipeline
```

## 📋 Lab Objectives

- ✅ Ingest and parse multi-source logs
- ✅ Create detection rules for brute force attacks
- ✅ Identify suspicious PowerShell execution patterns
- ✅ Correlate events across multiple data sources
- ✅ Document alert investigations & response

## 🎓 Key Skills Learned

- **SIEM Fundamentals**: Log aggregation, parsing, and analysis
- **Detection Engineering**: Building correlation rules and alert logic
- **Incident Response**: Alert triage and investigation workflows
- **Log Analysis**: Identifying attack indicators and TTPs

## 📁 Project Structure

```
siem-lab/
├── configs/
│   ├── splunk_inputs.conf
│   ├── logstash_pipelines/
│   └── sysmon_config.xml
├── detection_rules/
│   ├── brute_force.yml
│   ├── powershell_abuse.yml
│   └── lateral_movement.yml
├── attack_simulations/
│   ├── brute_force.sh
│   ├── powershell_misuse.ps1
│   └── README.md
├── dashboards/
│   └── threat_overview.json
└── README.md
```

## 💡 Detection Use Cases

| Attack | Detection Logic | Data Source |
|--------|-----------------|-------------|
| **Brute Force** | >10 failed logins in 5min | Windows Event 4625 |
| **PowerShell Abuse** | Encoded commands + obfuscation | Sysmon Event 1 |
| **Lateral Movement** | RDP + credential access combo | Sysmon + Event Logs |

## 🎬 Typical Lab Flow

1. **Set up infrastructure** → Deploy VMs & SIEM platform
2. **Configure log forwarding** → Enable agents on hosts
3. **Create detection rules** → Build searches & alerts
4. **Simulate attacks** → Run attack scripts
5. **Investigate alerts** → Triage and document findings
6. **Improve detections** → Refine rules based on results

## ⏱️ Time Estimate

- **Setup**: 4-6 hours
- **Rule Development**: 8-10 hours
- **Attack Simulation & Investigation**: 6-8 hours
- **Documentation**: 2-4 hours

**Total**: ~20-30 hours

## 📊 Resume Impact

This lab demonstrates:
- Real SOC Tier 1-2 alert triage experience
- Hands-on detection engineering skills
- Ability to work with enterprise security tools
- Log analysis and threat hunting capabilities

## 🔗 Resources

- [Splunk Documentation](https://docs.splunk.com/)
- [ELK Stack Guide](https://www.elastic.co/guide/index.html)
- [Sysmon Event Reference](https://docs.microsoft.com/en-us/sysinternals/downloads/sysmon)
- [MITRE ATT&CK Framework](https://attack.mitre.org/)

## 📝 Next Steps

- [ ] Build lab infrastructure
- [ ] Deploy SIEM platform
- [ ] Configure data sources
- [ ] Create detection rules
- [ ] Simulate attacks & investigate
- [ ] Document findings

---

**Status**: Active Development | **Last Updated**: 2026 | **License**: MIT
