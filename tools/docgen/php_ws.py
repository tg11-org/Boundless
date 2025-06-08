# Copyright 2025 TG11
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import subprocess


def start_php_server(ip='localhost', port=8000, directory="../../docs"):
    """
    Starts a local PHP server.
    :param ip: The IP address assignment to run the server on (default "localhost")
    :param port: Port to run the server on (default "8000")
    :param directory: Folder to serve (default "docs")
    """
    try:
        subprocess.run(["php", "-S", f"{ip}:{port}", "-t", directory], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to start PHP server: {e}")


if __name__ == "__main__":
    start_php_server()
