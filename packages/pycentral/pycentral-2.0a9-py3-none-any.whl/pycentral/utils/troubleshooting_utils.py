# (C) Copyright 2025 Hewlett Packard Enterprise Development LP.
# MIT License

SUPPORTED_DEVICE_TYPES = ["aos-s", "cx", "aps", "gateways"]

TROUBLESHOOTING_METHOD_DEVICE_MAPPING = {
    "retrieve_arp_table_test": ["aos-s", "aps", "gateways"],
    "locate_test": ["cx", "aps", "gateways"],
    "http_test": ["cx", "aps", "gateways"],
    "poe_bounce_test": ["cx", "aos-s", "gateways"],
    "port_bounce_test": ["cx", "aos-s", "gateways"],
    "speedtest_test": ["aps"],
    "aaa_test": ["cx", "aps"],
    "tcp_test": ["aps"],
    "iperf_test": ["gateways"],
    "cable_test": ["cx", "aos-s"],
    "nslookup_test": ["aps"],
    "disconnect_user_mac_addr": ["aps"],
    "disconnect_all_users": ["aps"],
    "disconnect_all_users_ssid": ["aps"],
    "disconnect_all_clients": ["gateways"],
    "disconnect_client_mac_addr": ["gateways"],
}
