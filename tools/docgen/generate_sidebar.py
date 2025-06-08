# This script updates your documentation generator to also build a sidebar/table of contents (TOC)
# for the HTML docs. It generates a `sidebar.php` file that can be included in `index.php`.

from pathlib import Path
import os
import re

output_dir = Path("docs/api")
toc_file = output_dir / "sidebar.php"


def generate_sidebar():
    def extract_ids(filepath):
        ids = []
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                match = re.search(r'id=[\'"]([\w\d_]+)[\'"]', line)
                if match:
                    ids.append(match.group(1))
        return ids

    sidebar = ["<div id='sidebar'>", "<h2>Contents</h2>", "<ul>"]
    groups = {}

    for file in output_dir.glob("*.php"):
        parts = file.stem.split(".")
        if len(parts) < 2:
            continue
        group = parts[0]
        kind = parts[1]
        groups.setdefault(group, []).append((file, kind))

    for group, items in sorted(groups.items()):
        sidebar.append(f"<li><strong>{group}</strong><ul>")
        for filepath, kind in sorted(items, key=lambda x: x[1]):
            ids = extract_ids(filepath)
            for id in ids:
                display = id.replace(f"{group}_", "")  # Optional cleaner label
                sidebar.append(f"  <li><a href='#{id}'>{display}</a></li>")
        sidebar.append("</ul></li><br>")

    sidebar.append("</ul>")
    sidebar.append("</div>")
    toc_file.write_text("\n".join(sidebar), encoding="utf-8")


if __name__ == "__main__":
    generate_sidebar()
    print("✅ Sidebar generated in docs/api/sidebar.php")
