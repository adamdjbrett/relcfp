import datetime
import hashlib
import html.entities
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

import requests
import xmltodict
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

XML_FILE = Path("feed.xml")
JSON_FILE = Path("_data/feed.json")
OLD_XML_FILE = Path("old_feed.xml")
RUNLOG_FILE = Path("RUNLOG.MD")
FEED_URL = "https://input.relcfp.com/feed.xml"
REQUEST_TIMEOUT = (15, 60)
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; RELCFPFeedBot/1.0; +https://relcfp.com)"
    ),
    "Accept": "application/atom+xml,application/xml,text/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}
XML_SAFE_ENTITIES = {"amp", "lt", "gt", "apos", "quot"}
INVALID_XML_CHARS_RE = re.compile(r"[^\x09\x0A\x0D\x20-\uD7FF\uE000-\uFFFD]")
HTML_ENTITY_RE = re.compile(r"&([A-Za-z][A-Za-z0-9]+);")
UNESCAPED_AMP_RE = re.compile(
    r"&(?!#\d+;|#x[0-9A-Fa-f]+;|(?:amp|lt|gt|apos|quot);)"
)
VOID_ELEMENT_RE = re.compile(
    r"<(?P<tag>area|base|br|col|embed|hr|img|input|link|meta|param|source|track|wbr)"
    r"(?P<attrs>(?:\s[^<>]*?)?)>",
    re.IGNORECASE,
)
XML_DECLARATION_RE = re.compile(
    br"<\?xml[^>]*encoding=[\"'](?P<encoding>[^\"']+)[\"']",
    re.IGNORECASE,
)


class RunLogger:
    def __init__(self, path: Path = RUNLOG_FILE):
        self.path = path
        self.started_at = self.timestamp()
        self.completed_at = ""
        self.status = "started"
        self.content_changed = False
        self.feed_entries: int | None = None
        self.feed_updated: str | None = None
        self.events: list[str] = []
        self.errors: list[str] = []

    @staticmethod
    def timestamp() -> str:
        return datetime.datetime.now(datetime.UTC).replace(microsecond=0).isoformat()

    def log(self, message: str) -> None:
        print(message)
        self.events.append(f"- `{self.timestamp()}` {message}")

    def error(self, message: str) -> None:
        print(message)
        entry = f"- `{self.timestamp()}` {message}"
        self.events.append(entry)
        self.errors.append(entry)

    def write(self) -> None:
        self.completed_at = self.timestamp()
        github_ref = os.environ.get("GITHUB_REF_NAME") or os.environ.get("GITHUB_REF", "local")
        github_event = os.environ.get("GITHUB_EVENT_NAME", "local")
        github_actor = os.environ.get("GITHUB_ACTOR", "local")

        lines = [
            "# RUNLOG",
            "",
            "## Summary",
            f"- Started: `{self.started_at}`",
            f"- Completed: `{self.completed_at}`",
            f"- Status: `{self.status}`",
            f"- Content changed: `{str(self.content_changed).lower()}`",
            f"- Feed URL: `{FEED_URL}`",
            f"- GitHub event: `{github_event}`",
            f"- GitHub actor: `{github_actor}`",
            f"- GitHub ref: `{github_ref}`",
        ]

        if self.feed_updated:
            lines.append(f"- Feed updated timestamp: `{self.feed_updated}`")

        if self.feed_entries is not None:
            lines.append(f"- Feed entry count: `{self.feed_entries}`")

        lines.extend(["", "## Events"])
        lines.extend(self.events or ["- None"])
        lines.extend(["", "## Errors"])
        lines.extend(self.errors or ["- None"])
        lines.append("")

        self.path.write_text("\n".join(lines), encoding="utf-8")


def hash_bytes(content: bytes) -> str:
    return hashlib.md5(content).hexdigest()


def hash_file(file_path: Path) -> str:
    hash_md5 = hashlib.md5()
    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def compare_files_by_hash(file1_path: Path, file2_path: Path) -> bool:
    return hash_file(file1_path) == hash_file(file2_path)


def ensure_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def replace_html_entity(match: re.Match[str]) -> str:
    entity_name = match.group(1)
    if entity_name in XML_SAFE_ENTITIES:
        return match.group(0)

    replacement = html.entities.html5.get(f"{entity_name};")
    if replacement:
        return replacement

    return match.group(0)


def self_close_void_element(match: re.Match[str]) -> str:
    attrs = match.group("attrs") or ""
    if attrs.rstrip().endswith("/"):
        return match.group(0)
    return f"<{match.group('tag')}{attrs}/>"


def normalize_xml_text(xml_text: str) -> str:
    normalized_text = xml_text.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    normalized_text = INVALID_XML_CHARS_RE.sub("", normalized_text)
    normalized_text = HTML_ENTITY_RE.sub(replace_html_entity, normalized_text)
    normalized_text = UNESCAPED_AMP_RE.sub("&amp;", normalized_text)
    normalized_text = VOID_ELEMENT_RE.sub(self_close_void_element, normalized_text)
    return normalized_text


def detect_xml_encoding(raw_bytes: bytes) -> str | None:
    match = XML_DECLARATION_RE.search(raw_bytes[:200])
    if not match:
        return None

    try:
        return match.group("encoding").decode("ascii").strip()
    except UnicodeDecodeError:
        return None


def decode_xml_bytes(raw_bytes: bytes, preferred_encodings: list[str | None] | None = None) -> str:
    encodings: list[str] = []

    for encoding in preferred_encodings or []:
        if encoding:
            encodings.append(encoding)

    declared_encoding = detect_xml_encoding(raw_bytes)
    if declared_encoding:
        encodings.append(declared_encoding)

    encodings.extend(["utf-8", "iso-8859-1"])

    seen: set[str] = set()
    for encoding in encodings:
        normalized_encoding = encoding.lower()
        if normalized_encoding in seen:
            continue
        seen.add(normalized_encoding)
        try:
            return raw_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue

    return raw_bytes.decode("utf-8", errors="replace")


def build_session() -> requests.Session:
    retry = Retry(
        total=3,
        connect=3,
        read=3,
        backoff_factor=2,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )

    session = requests.Session()
    session.headers.update(REQUEST_HEADERS)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def fetch_with_requests(url: str) -> tuple[int, str]:
    with build_session() as session:
        response = session.get(url, timeout=REQUEST_TIMEOUT)

    decoded_content = decode_xml_bytes(
        response.content,
        [response.encoding, getattr(response, "apparent_encoding", None)],
    )
    return response.status_code, decoded_content


def fetch_with_curl(url: str) -> tuple[int, str]:
    status_marker = b"\n__CURL_HTTP_STATUS__:"
    command = [
        "curl",
        "--silent",
        "--show-error",
        "--location",
        "--compressed",
        "--retry",
        "3",
        "--retry-all-errors",
        "--connect-timeout",
        str(REQUEST_TIMEOUT[0]),
        "--max-time",
        str(REQUEST_TIMEOUT[1]),
        "-A",
        REQUEST_HEADERS["User-Agent"],
        "-H",
        f"Accept: {REQUEST_HEADERS['Accept']}",
        "-H",
        f"Accept-Language: {REQUEST_HEADERS['Accept-Language']}",
        "-H",
        f"Cache-Control: {REQUEST_HEADERS['Cache-Control']}",
        "-H",
        f"Pragma: {REQUEST_HEADERS['Pragma']}",
        "--write-out",
        "\n__CURL_HTTP_STATUS__:%{http_code}",
        url,
    ]
    completed = subprocess.run(command, capture_output=True, check=False, text=False)
    stdout = completed.stdout
    body = stdout
    status_code = 0

    if status_marker in stdout:
        body, _, status_bytes = stdout.rpartition(status_marker)
        try:
            status_code = int(status_bytes.strip() or b"0")
        except ValueError:
            status_code = 0

    if completed.returncode != 0 and status_code == 0:
        raise subprocess.CalledProcessError(
            completed.returncode,
            command,
            output=completed.stdout,
            stderr=completed.stderr,
        )

    return status_code, decode_xml_bytes(body)


def fetch_feed_xml(url: str, run_log: RunLogger) -> str:
    errors: list[str] = []

    run_log.log(f"Fetching feed with requests from {url}.")
    try:
        status_code, response_text = fetch_with_requests(url)
        run_log.log(f"requests status: {status_code}")
        if status_code == 200 and response_text.strip():
            run_log.log("Fetched feed with requests.")
            return response_text

        if status_code != 200:
            message = f"requests returned status {status_code}"
        else:
            message = "requests returned empty content"
        run_log.error(message)
        errors.append(message)
    except requests.RequestException as error:
        message = f"requests failed: {error}"
        run_log.error(message)
        errors.append(message)

    run_log.log("Falling back to curl.")
    try:
        status_code, response_text = fetch_with_curl(url)
        run_log.log(f"curl status: {status_code}")
        if status_code == 200 and response_text.strip():
            run_log.log("Fetched feed with curl fallback.")
            return response_text

        if status_code != 200:
            message = f"curl returned status {status_code}"
        else:
            message = "curl returned empty content"
        run_log.error(message)
        errors.append(message)
    except (FileNotFoundError, subprocess.CalledProcessError) as error:
        message = f"curl failed: {error}"
        run_log.error(message)
        errors.append(message)

    raise RuntimeError("; ".join(errors))


def update_null_to_current_date(feed_data: dict[str, Any]) -> dict[str, Any]:
    current_date = datetime.datetime.now(datetime.UTC).isoformat()
    feed = feed_data.setdefault("feed", {})

    if feed.get("updated") is None:
        feed["updated"] = current_date

    entries = ensure_list(feed.get("entry"))
    for entry in entries:
        if isinstance(entry, dict) and entry.get("updated") is None:
            entry["updated"] = current_date

    feed["entry"] = entries
    return feed_data


def convert_xml_to_feed_data(xml_text: str) -> dict[str, Any]:
    normalized_xml = normalize_xml_text(xml_text)
    feed_data = xmltodict.parse(normalized_xml, force_list=("entry",))
    return update_null_to_current_date(feed_data)


def set_content_changed(changed: bool) -> None:
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as output_file:
            output_file.write(f"content_changed={'true' if changed else 'false'}\n")


def write_feed_files(xml_text: str, feed_data: dict[str, Any]) -> None:
    XML_FILE.write_text(xml_text, encoding="utf-8")
    JSON_FILE.write_text(json.dumps(feed_data, indent=4), encoding="utf-8")


def restore_previous_feed(had_existing_feed: bool) -> None:
    if had_existing_feed and OLD_XML_FILE.exists():
        os.replace(OLD_XML_FILE, XML_FILE)
        return

    if XML_FILE.exists():
        XML_FILE.unlink()


def cleanup_old_feed() -> None:
    if OLD_XML_FILE.exists():
        OLD_XML_FILE.unlink()


def main() -> None:
    run_log = RunLogger()
    had_existing_feed = XML_FILE.exists()
    old_feed_bytes = b""
    content_changed = False

    if had_existing_feed:
        old_feed_bytes = XML_FILE.read_bytes()
        os.replace(XML_FILE, OLD_XML_FILE)
        run_log.log("Backed up existing feed.xml to old_feed.xml.")
    else:
        run_log.log("No existing feed.xml found before fetch.")

    try:
        downloaded_xml = fetch_feed_xml(FEED_URL, run_log)
        normalized_xml = normalize_xml_text(downloaded_xml)
        feed_data = convert_xml_to_feed_data(normalized_xml)
        run_log.feed_entries = len(ensure_list(feed_data.get("feed", {}).get("entry")))
        run_log.feed_updated = feed_data.get("feed", {}).get("updated")
        run_log.log(
            f"Parsed feed successfully with {run_log.feed_entries} entries."
        )
        new_feed_bytes = normalized_xml.encode("utf-8")

        if had_existing_feed and hash_bytes(old_feed_bytes) == hash_bytes(new_feed_bytes):
            run_log.log("Files are identical.")
            restore_previous_feed(True)
            run_log.status = "success"
            return

        run_log.log(
            "Files are different." if had_existing_feed else "No previous feed.xml found; writing initial feed."
        )
        write_feed_files(normalized_xml, feed_data)
        cleanup_old_feed()
        content_changed = True
        run_log.status = "success"
        run_log.log("Updated feed.xml and _data/feed.json.")
    except Exception as error:
        run_log.status = "failed"
        run_log.error(f"Feed update failed: {error}")
        restore_previous_feed(had_existing_feed)
    finally:
        run_log.content_changed = content_changed
        set_content_changed(content_changed)
        run_log.write()


if __name__ == "__main__":
    main()
