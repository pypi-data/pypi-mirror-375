import pytest
from root.system_info import get_distro, get_ascii_art, get_system_info

def test_get_distro():
    distro = get_distro()
    assert isinstance(distro, str)
    assert distro in ["linux", "windows", "darwin", "termux"] or distro in [
        "arch", "ubuntu", "debian", "fedora", "centos", "manjaro", "kali",
        "gentoo", "alpine", "void", "linuxmint", "opensuse", "nixos", "slackware"
    ]

def test_get_ascii_art():
    art = get_ascii_art("arch")
    assert isinstance(art, str)
    assert len(art.splitlines()) > 0
    art = get_ascii_art("unknown")
    assert art == get_ascii_art("linux")

def test_get_system_info():
    info = get_system_info()
    assert isinstance(info, dict)
    assert all(key in info for key in [
        "user_host", "os", "host", "kernel", "uptime", "shell", "terminal",
        "cpu", "memory", "disk", "local_ip", "packages", "platform"
    ])
    assert isinstance(info["os"], str)
    assert isinstance(info["memory"], str)
    assert isinstance(info["disk"], str)
