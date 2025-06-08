import ast
import os
import html
import json
import fnmatch
import re
from pathlib import Path
from typing import List

from tools.debugtool import debug as d
d.set_debug_level(5)  ## TRACE
d.set_max_log_file_size(1024) ## 1 GB
d.set_max_log_files(5) ## Default: 5

# === Config ===
home_dir        = Path(os.getcwd()) # This should be the home folder of the app
d.trace(home_dir)
tools_dir       = Path(os.path.join(home_dir, "tools"))
d.trace(tools_dir)
logs_dir        = Path(os.path.join(home_dir, "logs"))
d.trace(logs_dir)
docgen_dir      = Path(os.path.join(tools_dir, "docgen"))
d.trace(docgen_dir)
debug_dir       = Path(os.path.join(tools_dir, "debug"))
d.trace(debug_dir)
config_path     = Path(os.path.join(docgen_dir, "config.json"))
d.trace(config_path)
app_dir         = Path(os.path.join(home_dir, "app"))
d.trace(app_dir)
docs_dir        = Path(os.path.join(home_dir, "docs"))
d.trace(docs_dir)
api_dir         = Path(os.path.join(docs_dir, "api"))
d.trace(api_dir)
scripts_dir     = Path(os.path.join(home_dir, "scripts"))
d.trace(scripts_dir)
static_dir      = Path(os.path.join(home_dir, "static"))
d.trace(static_dir)
templates_dir   = Path(os.path.join(home_dir, "templates"))
d.trace(templates_dir)
tests_dir       = Path(os.path.join(home_dir, "tests"))
d.trace(tests_dir)
venv_dir        = Path(os.path.join(home_dir, "venv"))
d.trace(venv_dir)

# print(config_path)
ignore_patterns = []
scan_dir = app_dir    # Default: scan your app logic
d.trace(scan_dir)
output_dir = api_dir  # Default: docs output folder
d.trace(output_dir)
# exit()
if config_path.exists():
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
        ignore_patterns = config.get("ignore", [])
        d.trace(ignore_patterns)
        scan_dir = (home_dir / config.get("scan_dir", scan_dir.relative_to(home_dir))).resolve()
        d.trace(scan_dir)
        output_dir = (home_dir / config.get("output_dir", output_dir.relative_to(home_dir))).resolve()
        d.trace(output_dir)


d.trace(config)
d.trace(ignore_patterns)
d.trace(scan_dir)
d.trace(output_dir)
d.trace(os.listdir(output_dir))

def is_ignored(filepath: Path) -> bool:
    """
    Checks whether a given file path matches any patterns defined in `config.json` (such as ignored folders or files) and determines if it should be skipped during documentation generation.
    """
    file_str = str(filepath).replace("\\", "/")
    for pattern in ignore_patterns:
        pattern = pattern.replace("\\", "/")
        if fnmatch.fnmatch(file_str, pattern) or file_str.startswith(
            pattern.rstrip("/") + "/"
        ):
            d.skipped(file_str)
            return True
    return False


output_dir = Path("docs/api")
output_dir.mkdir(parents=True, exist_ok=True)


def get_docstring(node) -> str:
    try:
        doc = ast.get_docstring(node)
        if not doc:
            return ""
        return doc
    except Exception:
        return ""


def wrap_anchor(name: str, anchor_id: str) -> str:
    return (
        f"<span class='anchor-link-wrapper'>"
        f"<a id='{anchor_id}'></a><span class='anchor-label'>{name}</span>"
        f"<span class='anchor-copy' onclick=\"copyAnchor('{anchor_id}')\">¶</span>"
        f"</span>"
    )


def safe_html_escape(text: str, allow_tags: List[str] = ["em"]) -> str:
    """
    Escapes HTML in the text except for allowed tags like em.
    """
    tag_pattern = re.compile(rf"</?({'|'.join(allow_tags)})[^>]*>", re.IGNORECASE)
    placeholders = []

    # Temporarily replace allowed tags with placeholders
    def replace_tag(match):
        placeholders.append(match.group(0))
        return f"__HTML_TAG_{len(placeholders)-1}__"

    temp_text = tag_pattern.sub(replace_tag, text)
    escaped = html.escape(temp_text)

    # Restore allowed tags
    for i, tag in enumerate(placeholders):
        escaped = escaped.replace(f"__HTML_TAG_{i}__", tag)

    return escaped


def highlight(text: str) -> str:
    """
    Processes docstring text and applies syntax highlighting to:
        - Quoted strings ("...")
        - Code snippets (`...`)
        - Brackets: (parentheses), [square brackets], {curly brackets}, <angle brackets>
        - Parameters (:param name:)
        - Common Windows API types (HWND, etc.)
    Returns: HTML-formatted string with <span>/<code> tags for styling.
    """
    text = safe_html_escape(text, allow_tags=["em"])

    # Highlight quoted strings: "..."
    text = re.sub(
        r"&quot;([^&]+)&quot;", r'<span class="highlight-string">"\1"</span>', text
    )

    # Highlight backtick code blocks
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)

    # Highlight :param, :return:, :raises:
    text = re.sub(
        r":(param|return|raises?)\b(?: ([^:<]+))?:",
        lambda m: f'<span class="highlight-param">:{m.group(1)}{f" {m.group(2)}" if m.group(2) else ""}:</span>',
        text,
    )

    # Highlight API types
    win_types = [
        'HWND', 'UINT', 'LPARAM', 'WPARAM', 'DWORD', 'LRESULT', 'LPCWSTR', 'HANDLE',
        'BOOL', 'BYTE', 'CHAR', 'WCHAR', 'WORD', 'LONG', 'ULONG', 'WNDCLASS',
        'HINSTANCE', 'CSIDL', 'MRU', 'URL', 'AST', 'API', 'WNDCLASSEX', 'TOC',
        'WS', 'BORDER', 'CAPTION', 'CHILD', 'CHILDWINDOW', 'CLIPCHILDREN',
        'CLIPSIBLINGS', 'DISABLED', 'DLGFRAME', 'GROUP', 'HSCROLL', 'ICONIC', 'ICONERROR'
        'MAXIMIZE', 'MAXIMIZEBOX', 'MINIMIZE', 'MINIMIZEBOX', 'OVERLAPPED', 'POPUP',
        'SIZEBOX', 'SYSMENU', 'TABSTOP', 'THICKFRAME', 'TILED', 'TILEDWINDOW',
        'POPUPWINDOW', 'OVERLAPPEDWINDOW', 'VISIBLE', 'VSCROLL', 'WS_EX',
        'ACCEPTFILES', 'WINDOWEDGE', 'APPWINDOW', 'CLIENTEDGE', 'COMPOSITED',
        'CONTEXTHELP', 'CONTROLPARENT', 'DLGMODALFRAME', 'LAYERED', 'LAYOUTRTL',
        'LEFT', 'LEFTSCROLLBAR', 'LTRREADING', 'MDICHILD', 'NOACTIVATE',
        'NOINHERITLAYOUT', 'NOPARENTNOTIFY', 'NOREDIRECTIONBITMAP', 'TRANSPARENT',
        'TOOLWINDOW', 'TOPMOST', 'PALETTEWINDOW', 'RIGHT', 'RIGHTSCROLLBAR',
        'RTLREADING', 'STATICEDGE', 'SW', 'HIDE', 'RESTORE', 'SHOW', 'SHOWDEFAULT',
        'SHOWMAXIMIZED', 'SHOWMINIMIZED', 'SHOWMINNOACTIVE', 'SHOWNA',
        'SHOWNOACTIVATE', 'SHOWNORMAL', 'ERROR', 'ZERO', 'FILE_NOT_FOUND',
        'PATH_NOT_FOUND', 'BAD_FORMAT', 'ACCESS_DENIED', 'ASSOC_INCOMPLETE',
        'DDE_BUSY', 'DDE_FAIL', 'DDE_TIMEOUT', 'DLL_NOT_FOUND', 'NO_ASSOC',
        'OOM', 'SHARE', 'MB', 'OK', 'OK_CANCEL', 'ABORT_RETRY_IGNORE',
        'YES_NO_CANCEL', 'YES_NO', 'RETRY_CANCEL', 'CANCEL_RETRY_CONTINUE',
        'REDX', 'QMRK', 'WARN', 'INFO', 'USERICON', 'MASKICON', 'DEFAULT_MASK',
        'TYPEMASK', 'DEFAULT_BUTTON_1', 'DEFAULT_BUTTON_2', 'DEFAULT_BUTTON_3',
        'DEFAULT_BUTTON_4', 'SYSTEMMODAL', 'TASKMODAL', 'MASK_MODE', 'HELP',
        'NOFOCUS', 'MISC_MASK', 'SET_AS_FOREGROUND_WINDOW', 'DEFAULT_DESKTOP_ONLY',
        'RIGHT_JUSTIFIED_TEXT', 'WS_EX_TOPMOST', 'RIGHT_TO_LEFT_READING',
        'SERVICE_NOTIFICATION', 'BEEP', 'ID', 'NULL', 'CANCEL', 'ABORT', 'RETRY',
        'IGNORE', 'YES', 'NO', '_8', '_9', 'TRY_AGAIN', 'CONTINUE', 'DT', 'CENTER',
        'TOP', 'VCENTER', 'BOTTOM', 'SINGLELINE', 'NOCLIP', 'WORDBREAK', 'CALCRECT',
        'EDITCONTROL', 'NOPREFIX', 'END_ELLIPSIS', 'PATH_ELLIPSIS', 'WORD_ELLIPSIS',
        'NOFULLWIDTHCHARBREAK', 'HIDEPREFIX', 'PREFIXONLY', 'WM', 'CREATE',
        'DESTROY', 'MOVE', 'SIZE', 'ACTIVATE', 'SETFOCUS', 'KILLFOCUS', 'ENABLE',
        'SETREDRAW', 'SETTEXT', 'GETTEXT', 'GETTEXTLENGTH', 'PAINT', 'CLOSE',
        'QUERYENDSESSION', 'QUIT', 'QUERYOPEN', 'ERASEBKGND', 'SYSCOLORCHANGE',
        'ENDSESSION', 'SHOWWINDOW', 'SETCURSOR', 'MOUSEACTIVATE',
        'WINDOWPOSCHANGING', 'WINDOWPOSCHANGED', 'CONTEXTMENU', 'CS', 'VREDRAW',
        'HREDRAW', 'DBLCLKS', 'OWNDC', 'CLASSDC', 'PARENTDC', 'NOCLOSE', 'SAVEBITS',
        'BYTEALIGNCLIENT', 'BYTEALIGNWINDOW', 'GLOBALCLASS', 'SM', 'CXSCREEN',
        'CYSCREEN', 'CXVSCROLL', 'CYHSCROLL', 'CXCAPTION', 'CYCAPTION', 'CXBORDER',
        'CYBORDER', 'CXDLGFRAME', 'CYDLGFRAME', 'CYVTHUMB', 'CXHTHUMB', 'CXICON',
        'CYICON', 'CXCURSOR', 'CYCURSOR', 'MOUSEPRESENT', 'CYMENU', 'CMONITORS',
        'REMOTESESSION', 'IDC', 'APPSTARTING', 'ARROW', 'CROSS', 'HAND', 'IBEAM',
        'SIZEALL', 'SIZENESW', 'SIZENS', 'SIZENWSE', 'SIZEWE', 'UPARROW', 'WAIT',
        'MF', 'INSERT', 'CHANGE', 'APPEND', 'DELETE', 'REMOVE', 'BYCOMMAND',
        'BYPOSITION', 'SEPARATOR', 'ENABLED', 'GRAYED', 'UNCHECKED', 'CHECKED',
        'USECHECKBITMAPS', 'STRING', 'BITMAP', 'OWNERDRAW', 'MENUBARBREAK',
        'MENUBREAK', 'HILITE', 'DEFAULT', 'RIGHTJUSTIFY', 'DEBUG_LEVEL', 'ICONERROR',
        'IP', 'PHP', "HTML", "XHTM", "XHTML"]
    type_regex = r"\b(" + "|".join(win_types) + r")\b"
    text = re.sub(type_regex, r'<span class="highlight-type">\1</span>', text)

    # Highlight bracket types
    text = re.sub(r"\(([^\(\)]+)\)", r'<span class="highlight-paren">(\1)</span>', text)
    text = re.sub(
        r"\[([^\[\]]+)\]", r'<span class="highlight-bracket">[\1]</span>', text
    )
    text = re.sub(r"\{([^\{\}]+)\}", r'<span class="highlight-brace">{\1}</span>', text)
    text = re.sub(
        r"&lt;([^&<>]+)&gt;", r'<span class="highlight-angle">&lt;\1&gt;</span>', text
    )

    # Indentation and newlines
    text = text.replace("  ", "&nbsp;&nbsp;")
    text = text.replace("    ", "&nbsp;&nbsp;&nbsp;&nbsp;")
    text = text.replace("\t", "&nbsp;&nbsp;&nbsp;&nbsp;")
    text = text.replace("\n", "<br>")

    return text


def parse_python_file(filepath: Path):
    """
    Parses a Python .py file using ast and returns a structured dictionary ready for documentation output.
    """
    with open(filepath, "r", encoding="utf-8-sig") as file:
        source = file.read()
    tree = ast.parse(source)
    module_doc = ast.get_docstring(tree) or ""
    results = {"classes": [], "enums": [], "functions": [], "module_doc": module_doc}

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            class_info = {
                "name": node.name,
                "doc": get_docstring(node),
                "methods": [],
                "is_enum": False,
            }
            for base in node.bases:
                if isinstance(base, ast.Name) and "Enum" in base.id:
                    class_info["is_enum"] = True
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    args = [arg.arg for arg in item.args.args]
                    class_info["methods"].append(
                        {"name": item.name, "args": args, "doc": get_docstring(item)}
                    )
            if class_info["is_enum"]:
                results["enums"].append(class_info)
            else:
                results["classes"].append(class_info)

        elif isinstance(node, ast.FunctionDef):
            args = [arg.arg for arg in node.args.args]
            results["functions"].append(
                {"name": node.name, "args": args, "doc": get_docstring(node)}
            )
    d.info(f"Parsed File: {filepath}")
    return results


def generate_docs(name: str, kind: str, entries: List[dict]):
    """
    Generates .md, .php, .json, and .js documentation files for a module:
        name: name of the file/module
        kind: "Class", "Enum", or "Function"
        entries: extracted elements (from parse_python_file)
    Also adds anchor IDs for use in TOC, and applies highlighting with fallbacks for missing docs.
    """
    d.info(f"Generating Docs for {name}:{kind}")
    md = [f"# {kind}: {name}", ""]
    php = [f"<a id='{name}'></a><h2>{kind}: {name}</h2>", "<ul class='enum-list'>"]
    json_out = []

    for entry in entries:
        d.info(f"Parsing the entry: {entry['name']}")
        entry_doc = highlight(
            entry["doc"]
            or f"<em class='no-doc'>No documentation provided for `{entry['name']}`.</em>"
        )

        if kind == "Enum":
            php.append(
                f"<li id='{name}_{entry['name']}'><strong>{entry['name']}</strong><br>{entry_doc}</li>"
            )

        elif kind == "Class":
            php.append(
                f"<li><strong class='toc-class'>{entry['name']}</strong><br>{entry_doc}"
            )
            for method in entry["methods"]:
                method_id = f"{name}_{entry['name']}_{method['name']}"
                mdoc = highlight(
                    method["doc"]
                    or f"<em class='no-doc'>No documentation provided for `{method['name']}`.</em>"
                )
                php.append(
                    f"<br><a id='{method_id}'></a><code>{method['name']}({', '.join(method['args'])})</code>: {mdoc}"
                )
            php.append("</li>")

        elif kind == "Function":
            func_id = f"{name}_{entry['name']}"
            php.append(
                f"<li id='{func_id}'><code>{entry['name']}({', '.join(entry['args'])})</code><br>{entry_doc}</li>"
            )

        json_out.append(entry)

    # Output
    (output_dir / f"{name}.{kind.lower()}.md").write_text(
        "\n".join(md), encoding="utf-8"
    )
    (output_dir / f"{name}.{kind.lower()}.php").write_text(
        "\n".join(php) + "</ul>", encoding="utf-8"
    )
    (output_dir / f"{name}.{kind.lower()}.json").write_text(
        json.dumps(json_out, indent=2), encoding="utf-8"
    )
    (output_dir / f"{name}.{kind.lower()}.js").write_text(
        f"export const {name}_{kind} = " + json.dumps(json_out, indent=2) + ";",
        encoding="utf-8",
    )


def show_formats():
    """
    This function demonstrates all supported highlighting formats.

    :param hwnd: HWND is a Windows handle (type)
    :param flags: Use MB.OK | MB.ICONERROR as flags
    :return: Returns an LRESULT on success.

    Examples:
        - Quoted string: "Shut Down Windows"
        - Code snippet: `MessageBoxW(hwnd, "Hello", "Title", MB.OK)`
        - Windows API types: HWND, DWORD, LPARAM, BOOL
        - Brackets: (param), [option], {config}, <element>

    Also handles:
        - Escaped tags like <em>italic</em>
        - :raises ValueError: if something goes wrong.
    """
    pass


# === Parse files ===
for pyfile in Path().rglob("*.py"):
    d.info(f"Checking {pyfile}")
    if is_ignored(pyfile):
        d.skipped(f"No docs to be generated for {pyfile}")
        continue
    parsed = parse_python_file(pyfile)
    module_name = pyfile.stem
    if parsed["classes"]:
        generate_docs(module_name, "Class", parsed["classes"])
    if parsed["enums"]:
        generate_docs(module_name, "Enum", parsed["enums"])
    if parsed["functions"]:
        generate_docs(module_name, "Function", parsed["functions"])
    d.success(f"Finished Generating for {pyfile}")

d.success(f"Finished Generating Docs")
d.summary()
