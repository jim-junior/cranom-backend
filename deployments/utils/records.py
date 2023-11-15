# Querying DNS Servers with Python - Checking NS Records

import requests
import dns.resolver


def get_dns_servers(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text.splitlines()
    else:
        return []


def is_ipv4(address):
    try:
        ip_parts = address.split(".")
        if len(ip_parts) != 4:
            return False
        for part in ip_parts:
            if not (0 <= int(part) <= 255):
                return False
        return True
    except ValueError:
        return False


def check_ns_records(ip_addresses, domain):
    for ip in ip_addresses:
        if is_ipv4(ip):
            print(f"Checking NS records for {domain} on IPv4: {ip}")
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [ip]

            try:
                ns_records = resolver.query(domain, "NS")
                if len(ns_records) == 0:
                    print(f"No NS records found for {domain} on IPv4: {ip}")
                else:
                    for record in ns_records:
                        print(f"NS Record: {record}")
            except dns.resolver.NXDOMAIN:
                print(f"No NS records found for {domain} on IPv4: {ip}")
            except dns.exception.Timeout:
                print(f"DNS query for {domain} on IPv4 {ip} timed out")
            except dns.resolver.NoNameservers:
                print(
                    f"DNS server {ip} refused to respond to the query for {domain}")
            except dns.resolver.NoAnswer:
                print(f"No NS records found for {domain} on IPv4: {ip}")


# read dns server list from url
if __name__ == "__main__":
    url = "https://public-dns.info/nameservers.txt"
    domain = "your_domain_.com"  # Domain to check NS records

    ip_addresses = get_dns_servers(url)
    if ip_addresses:
        check_ns_records(ip_addresses, domain)
    else:
        print("No DNS servers found from the provided URL.")
