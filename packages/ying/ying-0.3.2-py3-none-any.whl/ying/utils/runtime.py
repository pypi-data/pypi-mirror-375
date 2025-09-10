import requests
import socket
import getpass
import pwd
import os


def get_hostname():
    return socket.gethostname()


def get_current_user():
    return (
        getpass.getuser()
        or os.getlogin()
        or pwd.getpwuid(os.getuid()).pw_name
        or os.environ.get("USERNAME")
        or os.environ.get("USER")
    )


def get_internal_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(("10.255.255.255", 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP


def get_external_ip():
    """
    http://ip-api.com/json?fields=status,message,continent,continentCode,country,countryCode,region,regionName,city,district,zip,lat,lon,timezone,isp,org,as,asname,query
    """
    response = requests.get("https://api.ipify.org")
    if response.status_code == 200:
        return response.text
    else:
        return "Unable to get IP"


def get_working_directory():
    return os.getcwd()


def format_host_banner():
    user = get_current_user()
    hostname = get_hostname()
    internal_ip = get_internal_ip()
    external_ip = get_external_ip()
    return f"{user}@{hostname}[{internal_ip}][{external_ip}]:{get_working_directory()}"
