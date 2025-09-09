import platform
import psutil
import socket
import requests
import subprocess
import re
import os
import time
import getpass
from datetime import timedelta
from .ascii_art import ASCII_ART

def get_distro():
    if platform.system() == "Linux":
        if os.path.exists("/etc/os-release"):
            with open("/etc/os-release") as f:
                data = {line.split("=")[0]: line.split("=")[1].strip().strip('"') 
                        for line in f if "=" in line}
            return data.get("ID", "linux").lower()
        if os.path.exists("/system/build.prop"):
            return "termux"
    return platform.system().lower()

def get_ascii_art(distro):
    return ASCII_ART.get(distro, ASCII_ART["linux"])

def get_uptime():
    try:
        if os.path.exists("/proc/uptime"):
            with open("/proc/uptime", "r") as f:
                uptime_seconds = float(f.read().split()[0])
                return str(timedelta(seconds=int(uptime_seconds)))
        return str(timedelta(seconds=int(time.time() - psutil.boot_time())))
    except (PermissionError, FileNotFoundError, AttributeError):
        return "unknown"

def get_system_info(show_public_ip=False):
    info = {}

    try:
        info["user"] = getpass.getuser()
    except:
        info["user"] = os.environ.get("USER", "unknown")

    info["os"] = platform.system()
    if info["os"] == "Linux":
        if os.path.exists("/etc/os-release"):
            with open("/etc/os-release") as f:
                data = {line.split("=")[0]: line.split("=")[1].strip().strip('"') 
                        for line in f if "=" in line}
                info["os"] = f"{data.get('PRETTY_NAME', 'Linux')}"
        elif os.path.exists("/system/build.prop"):
            try:
                with open("/system/build.prop") as f:
                    props = {line.split("=")[0]: line.split("=")[1].strip() 
                             for line in f if "=" in line and "ro.build.version.release" in line}
                version = props.get("ro.build.version.release", platform.release())
                info["os"] = f"Android {version}"
            except:
                info["os"] = f"Android {platform.release()}"
    elif info["os"] == "Windows":
        info["os"] = f"Windows {platform.release()}"
    elif info["os"] == "Darwin":
        info["os"] = f"macOS {platform.mac_ver()[0]}"

    info["host"] = platform.node()
    info["kernel"] = platform.release()
    info["uptime"] = get_uptime()

    shell = "unknown"
    shell_env = os.environ.get("SHELL")
    if shell_env:
        shell = os.path.basename(shell_env)
        try:
            ver_out = subprocess.check_output([shell_env, "--version"], text=True).splitlines()[0]
            version_match = re.search(r"\d+(\.\d+)+", ver_out)
            if version_match:
                shell = f"{shell} {version_match.group()}"
        except:
            pass
    else:
        try:
            ppid = os.getppid()
            out = subprocess.check_output(["ps", "-p", str(ppid), "-o", "comm="], text=True).strip()
            shell = os.path.basename(out)
        except:
            pass
    info["shell"] = shell

    info["terminal"] = os.environ.get("TERM", "unknown")

    try:
        cpu_count = psutil.cpu_count(logical=True)
        try:
            cpu_freq = psutil.cpu_freq().current / 1000
            info["cpu"] = f"({cpu_count}) @ {cpu_freq:.3f}GHz"
        except:
            info["cpu"] = f"({cpu_count}) @ unknown GHz"
    except:
        info["cpu"] = "unknown"

    try:
        mem = psutil.virtual_memory()
        info["memory"] = f"{int(mem.used/1024/1024)}MiB / {int(mem.total/1024/1024)}MiB ({mem.percent}%)"
    except:
        info["memory"] = "unknown"

    try:
        disk = psutil.disk_usage("/")
        info["disk"] = f"{int(disk.used/1024/1024/1024)}GiB / {int(disk.total/1024/1024/1024)}GiB ({disk.percent}%)"
    except:
        info["disk"] = "unknown"

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        info["local_ip"] = s.getsockname()[0]
        s.close()
    except:
        info["local_ip"] = "unknown"

    if show_public_ip:
        try:
            info["public_ip"] = requests.get("https://api.ipify.org").text
        except:
            info["public_ip"] = "unknown"

    packages = 0
    if platform.system() == "Linux":
        try:
            if os.path.exists("/data/data/com.termux/files/usr/bin/pkg"):
                packages += int(subprocess.check_output("pkg list-installed | wc -l", shell=True, text=True))
            elif os.path.exists("/usr/bin/dpkg"):
                packages += int(subprocess.check_output("dpkg -l | wc -l", shell=True, text=True))
            elif os.path.exists("/usr/bin/rpm"):
                packages += int(subprocess.check_output("rpm -qa | wc -l", shell=True, text=True))
            elif os.path.exists("/usr/bin/pacman"):
                packages += int(subprocess.check_output("pacman -Q | wc -l", shell=True, text=True))
            elif os.path.exists("/usr/bin/apk"):
                packages += int(subprocess.check_output("apk info | wc -l", shell=True, text=True))
        except:
            pass
    info["packages"] = f"{packages} (pkg)" if packages > 0 and os.path.exists("/system/build.prop") else str(packages) if packages > 0 else "unknown"

    info["platform"] = "wsl" if os.path.exists("/proc/sys/fs/binfmt_misc/WSLInterop") else platform.system().lower()
    if os.path.exists("/system/build.prop"):
        info["platform"] = "termux"

    return info