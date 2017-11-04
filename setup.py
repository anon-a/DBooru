from cx_Freeze import setup, Executable
import requests

buildOptions = {"packages": ["os", 'requests', 'queue', 'idna', 'netifaces', 'gc'],
                'includes': ['requests', 'dermod', 'queue', 'idna', 'netifaces', 'gc'],
                "excludes": ["tkinter"],
                'include_files': ["extra/", (requests.certs.where(), 'cacert.pem')]
                }

setup(
    name="DBooru",
    version="1.0.0",
    requires=['requests', 'idna', 'netifaces', 'gc'],
    options={"build_exe": buildOptions},
    executables=[Executable("main.py"), Executable('webv3.py')]
)
