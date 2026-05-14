#!/usr/bin/env python3
# H3C S5120V3 Port Traffic Monitor
# Supports SSH login and parses "display interface" output
import datetime
import re
import time
import os
from netmiko import ConnectHandler
from tabulate import tabulate
from colorama import init, Fore, Style

init(autoreset=True)  # 支持彩色输出

# === 配置区（请按实际情况修改）===
SWITCH_IP = "192.168.1.254"
USERNAME = "admin"
PASSWORD = "Admin@12345"
DEVICE_TYPE = "hp_comware_telnet"  # H3C 使用 hp_comware 驱动
REFRESH_INTERVAL = 3  # 刷新间隔（秒）

# ===============================

def parse_interface_output(output):
    """从 display interface 输出中提取速率和带宽"""
    result = {
        "input_bps": 0,
        "output_bps": 0,
        "speed_mbps": 1000,  # 默认千兆
        "status": "unknown"
    }

    # 提取 input/output rate
    in_rate_match = re.search(r"input rate:\s*(\d+)\s*bps", output)
    out_rate_match = re.search(r"output rate:\s*(\d+)\s*bps", output)
    if in_rate_match:
        result["input_bps"] = int(in_rate_match.group(1))
    if out_rate_match:
        result["output_bps"] = int(out_rate_match.group(1))

    # 提取 Speed
    speed_match = re.search(r"Speed:\s*(\d+)\s*Mbps", output)
    if speed_match:
        result["speed_mbps"] = int(speed_match.group(1))

    # 提取状态
    if "Current state: UP" in output and "Line protocol state: UP" in output:
        result["status"] = "UP"
    else:
        result["status"] = "DOWN"

    return result

def print_port_info(conn):
    """
    display interface GigabitEthernet 1/0/15

    Last 300 seconds input: 220 packets/sec 157868 bytes/sec 0%
    过去 300 秒（5 分钟）内，该端口 接收方向（入口） 的平均流量统计,
    平均每秒收到 220 个数据包,
    平均每秒收到 157,868 字节（约 1.26 Mbps）,
    带宽利用率百分比（即：当前流量占端口总带宽的比例）

    """
    # port_list = ["1",'2','3','4','5','6','15']
    port_list = ['19']
    for port in port_list:
        cmd_line = f"display interface GigabitEthernet 1/0/{port}"
        print(cmd_line)
        output = conn.send_command(cmd_line)
        for line in output.splitlines():
            if "Last 300 seconds" in line:
                print(line)
    return

def get_up_interfaces(conn):
    """获取所有 UP 的接口名称"""
    output = conn.send_command("display interface brief")
    up_interfaces = []
    for line in output.splitlines():
        if "UP" in line and "ADM" not in line and (line.startswith("GE") or line.startswith("XGE")):
            parts = line.split()
            if parts:
                iface = parts[0]
                # 标准化接口名（H3C 显示为 GE1/0/1，但命令需 GigabitEthernet）
                if iface.startswith("GE"):
                    full_name = "GigabitEthernet" + iface[2:]
                elif iface.startswith("XGE"):
                    full_name = "Ten-GigabitEthernet" + iface[3:]
                else:
                    full_name = iface
                up_interfaces.append(full_name)
    return up_interfaces

def format_bps(bps):
    """将 bps 转换为易读格式"""
    if bps < 1000:
        return f"{bps} bps"
    elif bps < 1_000_000:
        return f"{bps/1000:.1f} Kbps"
    else:
        return f"{bps/1_000_000:.2f} Mbps"

def main():
    device = {
        "device_type": DEVICE_TYPE,
        "host": SWITCH_IP,
        "username": USERNAME,
        "password": PASSWORD,
        "timeout": 10,
        "session_log": None
    }

    print(f"{Fore.CYAN}Connecting to H3C switch at {SWITCH_IP}...{Style.RESET_ALL}")
    try:
        conn = ConnectHandler(**device)
        print(f"{Fore.GREEN}Connected successfully!{Style.RESET_ALL}\n")
    except Exception as e:
        print(f"{Fore.RED}Failed to connect: {e}{Style.RESET_ALL}")
        return

    try:
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"{Fore.YELLOW}=== H3C Port Traffic Monitor ({time.strftime('%Y-%m-%d %H:%M:%S')}) ==={Style.RESET_ALL}")
            print(f"Refresh every {REFRESH_INTERVAL} seconds. Press Ctrl+C to exit.\n")
            print_port_info(conn)

            # up_ifaces = get_up_interfaces(conn)
            # table_data = []
            #
            # for iface in up_ifaces:
            #     try:
            #         output = conn.send_command(f"display interface {iface}", use_textfsm=False)
            #         stats = parse_interface_output(output)
            #
            #         if stats["status"] != "UP":
            #             continue
            #
            #         in_util = (stats["input_bps"] / (stats["speed_mbps"] * 1_000_000)) * 100
            #         out_util = (stats["output_bps"] / (stats["speed_mbps"] * 1_000_000)) * 100
            #
            #         # 高亮高占用（>70%）
            #         in_color = Fore.RED if in_util > 70 else ""
            #         out_color = Fore.RED if out_util > 70 else ""
            #
            #         table_data.append([
            #             iface,
            #             f"{stats['speed_mbps']}M",
            #             in_color + format_bps(stats["input_bps"]) + Style.RESET_ALL,
            #             f"{in_util:.1f}%",
            #             out_color + format_bps(stats["output_bps"]) + Style.RESET_ALL,
            #             f"{out_util:.1f}%"
            #         ])
            #     except Exception as e:
            #         table_data.append([iface, "Err", str(e), "", "", ""])
            #
            # headers = ["Interface", "Speed", "Input", "In %", "Output", "Out %"]
            # print(tabulate(table_data, headers=headers, tablefmt="grid"))
            time.sleep(REFRESH_INTERVAL)

    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Exiting...{Style.RESET_ALL}")
    finally:
        conn.disconnect()

if __name__ == "__main__":
    main()