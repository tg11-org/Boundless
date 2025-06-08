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


def run_generators():
    try:
        print("[*] Generating docs...")
        subprocess.run(["python", "generate_docs.py"], check=True)

        print("[*] Generating sidebar...")
        subprocess.run(["python", "generate_sidebar.py"], check=True)

        print("[+] Done!")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed: {e}")


if __name__ == "__main__":
    run_generators()
