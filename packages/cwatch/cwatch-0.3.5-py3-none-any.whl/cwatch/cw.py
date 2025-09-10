"""cwatch is a tool to monitor cyberbro for changes for questions."""

import hashlib
import importlib.metadata
import ipaddress
import json
import socket
import sqlite3
import sys
import time
import tomllib
from datetime import datetime
from http.client import HTTPException
from pathlib import Path
from typing import Any, cast

import httpcore
import httpx
import jsondiff


def submit_request(configuration, name) -> dict:
    """Submit question to Cyberbro."""
    data: dict[str, dict] = {
        "text": name,
        "engines": configuration["cyberbro"]["engines"],
    }
    try:
        r: httpx.Response = httpx.post(
            url=configuration["cyberbro"]["url"] + "/analyze", json=data
        )
    except (httpcore.ConnectError, HTTPException):
        return {}
    try:
        return json.loads(r.text)
    except Exception as err:
        print(f"Error submitting request: {r.text}. Error was {err}")
        return {}


def get_response(configuration, link) -> dict:
    """Get the response from Cyberbro."""
    done: bool = False
    r: httpx.Response | None = None
    connect_error_count: int = 0

    while not done:
        try:
            r = httpx.get(url=configuration["cyberbro"]["url"] + link)
        except HTTPException:
            time.sleep(1)
            continue
        except httpcore.ConnectError:
            if connect_error_count > 5:  # noqa: PLR2004
                print("Can't connect to server. Exiting.")
                sys.exit(1)
            connect_error_count += 1
            time.sleep(1)
            continue
        if r.text != "[]\n":
            done = True
        else:
            time.sleep(1)

    assert r is not None
    return json.loads(r.text)


def setup_database(configuration) -> None:
    """Create database."""
    conn: sqlite3.Connection = sqlite3.connect(
        database=configuration["cwatch"]["DB_FILE"]
    )
    cursor: sqlite3.Cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS json_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            json_hash TEXT NOT NULL,
            json_content TEXT NOT NULL
        )
    """
    )
    conn.commit()
    conn.close()


def calculate_hash(json_data) -> str:
    """Function to calculate a hash for a JSON object."""
    json_string: str = json.dumps(obj=json_data, sort_keys=True)
    return hashlib.sha256(string=json_string.encode(encoding="utf-8")).hexdigest()


def save_json_data(configuration, item, json_data) -> None:
    """Save JSON data if changes are detected."""
    conn: sqlite3.Connection = sqlite3.connect(
        database=configuration["cwatch"]["DB_FILE"]
    )
    cursor: sqlite3.Cursor = conn.cursor()

    # Calculate hash for the current JSON
    json_hash: str = calculate_hash(json_data=json_data)

    # Insert the new JSON data
    cursor.execute(
        """
        INSERT INTO json_data (target, timestamp, json_hash, json_content)
        VALUES (?, ?, ?, ?)
    """,
        (item, datetime.now().isoformat(), json_hash, json.dumps(json_data)),
    )

    conn.commit()
    conn.close()


def handle_abuseipdb(change) -> dict:
    """Remove change from abuseipdb if no relevant changes."""
    report = True
    if isinstance(change["abuseipdb"], list) and len(change["abuseipdb"]) == 2:  # noqa: PLR2004
        if (
            "reports" in change["abuseipdb"][1]
            and "risk_score" in change["abuseipdb"][1]
        ):
            if (
                change["abuseipdb"][1]["reports"] == 0
                and change["abuseipdb"][1]["risk_score"] == 0
            ):
                report = False
        else:
            report = False
    if "reports" in change["abuseipdb"] and "risk_score" in change["abuseipdb"]:
        if (
            change["abuseipdb"]["reports"] == 0
            and change["abuseipdb"]["risk_score"] == 0
        ):
            report = False
    if not report:
        change.pop("abuseipdb")
    return change


def handle_shodan(change) -> dict:
    """Remove change from shodan if change is to null."""
    if "link" not in change["shodan"]:
        change.pop("shodan")
    return change


def handle_threatfox(change) -> dict:
    """Remove change from threatfox if no matches."""
    report = True
    try:
        if isinstance(change["threatfox"], list) and len(change["threatfox"]) == 2:  # noqa: PLR2004
            if (
                "count" in change["threatfox"][1]
                and change["threatfox"][1]["count"] == 0
                and "malware_printable" in change["threatfox"][1]
                and change["threatfox"][1]["malware_printable"] == []
            ):
                report = False
            elif change["threatfox"][1] is None:
                report = False
        if change["threatfox"] is None or ("count" in change["threatfox"]):
            if (
                change["threatfox"]["count"] == 0
                and change["threatfox"]["malware_printable"] == []
            ):
                report = False
    except (TypeError, KeyError, RuntimeError):
        # If the key is not present, we assume no matches
        report = False
    if not report:
        change.pop("threatfox")
    return change


def handle_virustotal(change) -> dict:
    """Remove change from virustotal if no matches."""
    report = True

    # Check if this is a detection_ratio change with 0 detections
    if "virustotal" in change and isinstance(change["virustotal"], dict):
        if "detection_ratio" in change["virustotal"]:
            detection_change = change["virustotal"]["detection_ratio"]
            if isinstance(detection_change, list) and len(detection_change) == 2:  # noqa: PLR2004
                old_ratio, new_ratio = detection_change
                # Check if both old and new ratios start with "0/"
                if (
                    isinstance(old_ratio, str)
                    and isinstance(new_ratio, str)
                    and old_ratio.startswith("0/")
                    and new_ratio.startswith("0/")
                ):
                    # Both ratios have 0 detections, filter out this change
                    report = False

    if isinstance(change["virustotal"], list) and len(change["virustotal"]) == 2:  # noqa: PLR2004
        if change["virustotal"][1] is None:
            report = False
        elif (
            "community_score" in change["virustotal"][1]
            and change["virustotal"][1]["community_score"] == 0
            and "total_malicious" in change["virustotal"][1]
            and change["virustotal"][1]["total_malicious"] == 0
        ):
            report = False
    if change["virustotal"] is None or ("community_score" in change["virustotal"]):
        if (
            change["virustotal"]["community_score"] == 0
            and change["virustotal"]["total_malicious"] == 0
        ):
            report = False
    if not report:
        change.pop("virustotal")
    return change


def format_value_change(old_val: Any, new_val: Any) -> str:
    """Format a value change in a human-readable way."""
    if isinstance(old_val, dict | list) and isinstance(new_val, dict | list):
        return f"Updated from {len(old_val) if hasattr(old_val, '__len__') else 'N/A'} to {len(new_val) if hasattr(new_val, '__len__') else 'N/A'} items"
    if old_val is None:
        return f"Added: {new_val}"
    if new_val is None:
        return f"Removed: {old_val}"
    return f"Changed from '{old_val}' to '{new_val}'"


def format_engine_changes(engine: str, change_data: Any) -> str:
    """Format changes for a specific engine in a human-readable way."""
    if isinstance(change_data, list) and len(change_data) == 2:  # noqa: PLR2004
        old_val, new_val = change_data
        return format_value_change(old_val, new_val)
    elif isinstance(change_data, dict):
        changes = []
        for key, value in change_data.items():
            # Skip None, empty strings, empty lists, and empty dicts
            if value is None or value in ("", [], {}):
                continue
            if isinstance(value, list) and len(value) == 2:  # noqa: PLR2004
                # Also skip if both old and new values are None/empty
                old_val, new_val = value
                if (old_val is None or old_val in ("", [], {})) and (
                    new_val is None or new_val in ("", [], {})
                ):
                    continue
                changes.append(f"  - {key}: {format_value_change(value[0], value[1])}")
            else:
                changes.append(f"  - {key}: {value}")
        return "\n".join(changes) if changes else "No meaningful changes"
    else:
        # Skip None values at the top level
        if change_data is None:
            return "No data"
        return str(change_data)


def generate_markdown_summary(target: str, changes: dict | list) -> str:
    """Generate a markdown summary of changes."""
    lines = [f"## Changes for {target}"]

    # Handle case where changes might be a list instead of dict
    if isinstance(changes, list):
        for item in changes:
            if isinstance(item, dict):
                for engine, change_data in item.items():
                    formatted_change = format_engine_changes(engine, change_data)
                    if formatted_change not in ["No meaningful changes", "No data"]:
                        lines.append(f"\n### {engine.title()}")
                        lines.append(formatted_change)
            else:
                lines.append(f"\n{item!s}")
    else:
        # Original dict handling
        for engine, change_data in changes.items():
            formatted_change = format_engine_changes(engine, change_data)
            if formatted_change not in ["No meaningful changes", "No data"]:
                lines.append(f"\n### {engine.title()}")
                lines.append(formatted_change)

    return "\n".join(lines) + "\n"


def has_meaningful_data(data: dict) -> bool:
    """Check if data contains meaningful information worth reporting for new entries."""
    # Check for risk scores
    if isinstance(data.get("abuseipdb"), dict):
        risk_score = data["abuseipdb"].get("risk_score", 0)
        if risk_score > 0:
            return True

    if isinstance(data.get("ipquery"), dict):
        risk_score = data["ipquery"].get("risk_score", 0)
        if risk_score > 0:
            return True

    # Check for VirusTotal hits
    if isinstance(data.get("virustotal"), dict):
        total_malicious = data["virustotal"].get("total_malicious", 0)
        if total_malicious > 0:
            return True

    # Check for ThreatFox matches
    if isinstance(data.get("threatfox"), dict):
        count = data["threatfox"].get("count", 0)
        if count > 0:
            return True

    # Check for PhishTank database presence
    if isinstance(data.get("phishtank"), dict):
        in_database = data["phishtank"].get("in_database", False)
        if in_database:
            return True

    return False


def filter_new_entry_data(data: dict, target: str) -> dict:  # noqa: PLR0912
    """Filter new entry data to only show meaningful information."""
    if not isinstance(data, dict):
        return data

    filtered_data = {}

    # Always include basic identification
    if "observable" in data:
        filtered_data["observable"] = data["observable"]
    if "type" in data:
        filtered_data["type"] = data["type"]

    # Include services only if they have meaningful data
    for service, service_data in data.items():
        # Skip None or empty values
        if service_data is None or service_data in ([], {}):
            continue

        if service == "abuseipdb" and isinstance(service_data, dict):
            risk_score = service_data.get("risk_score", 0)
            if risk_score > 0:
                filtered_data[service] = service_data

        elif service == "virustotal" and isinstance(service_data, dict):
            total_malicious = service_data.get("total_malicious", 0)
            if total_malicious > 0:
                filtered_data[service] = service_data

        elif service == "threatfox" and isinstance(service_data, dict):
            count = service_data.get("count", 0)
            if count > 0:
                filtered_data[service] = service_data

        elif service == "phishtank" and isinstance(service_data, dict):
            in_database = service_data.get("in_database", False)
            if in_database:
                filtered_data[service] = service_data

        elif service == "ipquery" and isinstance(service_data, dict):
            risk_score = service_data.get("risk_score", 0)
            if risk_score > 0:
                filtered_data[service] = service_data

        # Skip Shodan links unless there's meaningful data
        elif service == "shodan" and isinstance(service_data, dict):
            # Only include if it has more than just a link
            if len(service_data) > 1 or not service_data.get("link"):
                filtered_data[service] = service_data

        # Skip Abusix if the abuse email matches the target domain
        elif service == "abusix" and isinstance(service_data, dict):
            abuse_email = service_data.get("abuse", "")
            if isinstance(abuse_email, str) and "@" in abuse_email:
                abuse_domain = abuse_email.split("@")[1]
                # Only include if abuse domain doesn't match target domain
                if not target.endswith(abuse_domain):
                    filtered_data[service] = service_data

        # Include other basic services only if they provide useful info
        elif service in ["observable", "type"]:
            continue  # Already handled above

        # Skip services that are commonly empty/uninteresting for new entries
        elif service in ["google", "google_safe_browsing", "rdap", "github"]:
            if service_data and service_data not in ([], {}):
                # Only include if it has actual content
                if isinstance(service_data, dict) and any(
                    v for v in service_data.values()
                ):
                    filtered_data[service] = service_data
                elif isinstance(service_data, list) and service_data:
                    filtered_data[service] = service_data

    return filtered_data


def handle_changes(
    configuration,
    target: str,
    changes: dict,
    all_changes: list | None = None,
    is_new: bool = False,
) -> bool:
    """Handle changes."""
    # Apply filtering to reduce noise
    if "abuseipdb" in changes:
        changes = handle_abuseipdb(change=changes)
    if "shodan" in changes:
        changes = handle_shodan(change=changes)
    if "threatfox" in changes:
        changes = handle_threatfox(change=changes)
    if "virustotal" in changes:
        changes = handle_virustotal(change=changes)

    # For new entries, apply additional filtering
    if is_new:
        # Get the latest data to check for meaningful content
        conn = sqlite3.connect(database=configuration["cwatch"]["DB_FILE"])
        cursor = conn.cursor()
        cursor.execute(
            "SELECT json_content FROM json_data WHERE target = ? ORDER BY id DESC LIMIT 1",
            (target,),
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            latest_data = json.loads(row[0])[0]  # Get the first item from the list
            if not has_meaningful_data(latest_data):
                # No meaningful data found, don't report this new entry
                return False

    if changes != {} or is_new:
        # Store changes for detailed appendix
        if all_changes is not None:
            all_changes.append(
                {"target": target, "changes": changes.copy(), "is_new": is_new}
            )

        # Always show human-readable summary
        if is_new:
            print(f"## New target: {target}")
            print("Initial data collected - no comparison available yet.")
            print("")
        else:
            print(generate_markdown_summary(target, changes))
        return True
    return False


def detect_changes(configuration, item, all_changes: list | None = None) -> bool:
    """Detect changes in json."""
    conn: sqlite3.Connection = sqlite3.connect(
        database=configuration["cwatch"]["DB_FILE"]
    )
    cursor: sqlite3.Cursor = conn.cursor()
    changed: bool = False

    # Fetch the last two entries
    cursor.execute(
        """
        SELECT json_content FROM json_data WHERE target = ?
        ORDER BY id DESC LIMIT 2
    """,
        (item,),
    )
    rows: list[Any] = cursor.fetchall()

    if len(rows) == 2:  # noqa: PLR2004
        old_json: dict = json.loads(rows[1][0])[0]
        new_json: dict = json.loads(rows[0][0])[0]
        changes: dict = compare_json(
            configuration=configuration, old=old_json, new=new_json
        )
        changed = handle_changes(
            configuration=configuration,
            target=item,
            changes=changes,
            all_changes=all_changes,
            is_new=False,
        )
    elif len(rows) == 1:
        # New target - show as initial data
        changed = handle_changes(
            configuration=configuration,
            target=item,
            changes={},
            all_changes=all_changes,
            is_new=True,
        )

    conn.close()
    return changed


def compare_json(configuration, old, new) -> dict:
    """Compare json objects."""
    verbose: bool = configuration["cwatch"].get("verbose", False)
    json_diff: str = cast(str, jsondiff.diff(old, new, syntax="symmetric", dump=True))
    diff: dict = json.loads(json_diff)

    # Apply configured filters
    for engine in configuration["cwatch"].get("ignore_engines", []):
        if engine in diff:
            removed: dict = diff.pop(engine)
            if verbose:
                print(f"Removed diff in {engine}: {removed}")
    for combo in configuration["cwatch"].get("ignore_engines_partly", []):
        engine: str = combo[0]
        part: str = combo[1]
        if engine in diff:
            if part in diff[engine]:
                removed = diff[engine].pop(part)
                if verbose:
                    print(f"Removed diff in {engine}->{part}: {removed}")
            if diff[engine] == {}:
                diff.pop(engine)
    return diff


def report_header(configuration) -> None:
    """Print header in report mode."""
    print(configuration["cwatch"]["header"])
    print("=" * len(configuration["cwatch"]["header"]))
    print("")
    print(f"Report generation start at {datetime.now().isoformat()}")
    print("")
    print("Will report changes in the following engines.")
    engines: list = configuration["cyberbro"]["engines"]
    engines.sort()
    for engine in engines:
        if engine not in configuration["cwatch"]["ignore_engines"]:
            print(f"- {engine}")
    print("")
    if configuration["cwatch"]["ignore_engines_partly"]:
        print("Ignore change if the only change is in one of:")
        for combo in configuration["cwatch"]["ignore_engines_partly"]:
            print(f"- {combo[0]} -> {combo[1]}")
        print("")


def generate_detailed_appendix(configuration, all_changes: list) -> None:
    """Generate detailed JSON diff appendix."""
    if not all_changes:
        return

    print("\n---\n")
    print("## Detailed Changes (JSON Diff)\n")

    for item in all_changes:
        target = item["target"]
        changes = item["changes"]
        is_new = item.get("is_new", False)

        print(f"### {target}\n")
        if is_new:
            print("*New target - no previous data for comparison*\n")
        else:
            print("```json")
            print(json.dumps(changes, indent=2))
            print("```\n")


def report_footer(configuration, all_changes: list | None = None) -> None:
    """Print footer in report mode."""
    # Always generate detailed appendix if we have changes
    if all_changes:
        generate_detailed_appendix(configuration, all_changes)

    print("")
    print(f"Report done at {datetime.now().isoformat()}.")
    if configuration["cwatch"].get("footer"):
        print("")
        print(configuration["cwatch"]["footer"])
    print("")
    print(
        f"Report generated with cwatch {importlib.metadata.version(distribution_name='cwatch')}."
    )


def get_targets(configuration, targets) -> list:
    """Get targets for check."""
    domain: str
    for domain in configuration["iocs"]["domains"]:
        public_ip = False
        try:
            # Handle IP addresses in domain list
            if (
                ipaddress.ip_address(address=domain)
                and not ipaddress.ip_address(address=domain).is_private
                and domain not in targets
            ):
                targets.append(domain)
                continue
            elif ipaddress.ip_address(address=domain).is_private:
                continue
        except ValueError:
            pass
        try:
            addresses = socket.getaddrinfo(
                host=domain, port="http", proto=socket.IPPROTO_TCP
            )
        except Exception as err:
            print(f"Error looking up ip for domain {domain}: {err}")
            sys.exit(1)
        for address in addresses:
            ip: str = str(address[4][0])
            if ip not in targets and not ipaddress.ip_address(address=ip).is_private:
                public_ip = True
        if public_ip and domain not in targets:
            targets.append(domain)
        for address in addresses:
            ip = str(address[4][0])
            if ip not in targets and not ipaddress.ip_address(address=ip).is_private:
                targets.append(ip)
    return targets


def main() -> None:
    """Main function."""
    targets: list[str] = []
    changes: bool = False
    all_changes: list = []

    with open(file="cwatch.toml", mode="rb") as file:
        conf: dict[str, Any] = tomllib.load(file)

    # Always show report header
    report_header(configuration=conf)

    if not Path(conf["cwatch"]["DB_FILE"]).is_file():
        setup_database(configuration=conf)

    # Create list with domains and their IP addresses
    get_targets(configuration=conf, targets=targets)

    # Check for changes
    print(f"Will check {len(targets)} hosts.")
    print("")
    item: str
    for item in targets:
        if not conf["cwatch"].get("quiet", False):
            print(f"Checking for changes for: {item}")
        request_id: dict = submit_request(configuration=conf, name=item)
        if not request_id or request_id == {}:
            print(f"Error submitting request for {item}.")
            continue
        results_json: dict = get_response(configuration=conf, link=request_id["link"])
        save_json_data(configuration=conf, item=item, json_data=results_json)
        if detect_changes(configuration=conf, item=item, all_changes=all_changes):
            changes = True

    if not changes:
        print("")
        print("No changes to report.")

    # Always show detailed appendix
    report_footer(configuration=conf, all_changes=all_changes)


# Call main if used as a program.
if __name__ == "__main__":
    main()
