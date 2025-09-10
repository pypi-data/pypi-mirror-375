import os


def parse_report(report_path: str) -> list[str]:
    """
    Read a report with sections '## TO COMPRESS ##' / '## REMAINING ##'
    and return just the list of file paths under TO COMPRESS.
    """
    to_compress: list[str] = []
    try:
        with open(report_path, "r") as rpt:
            section = None
            for line in rpt:
                line = line.strip()
                # Identify section headers
                if line == "## TO COMPRESS ##":
                    section = "to"
                    continue
                if line.startswith("## "):
                    section = None
                    continue

                if section == "to" and line:
                    # Skip comments and lines in parentheses
                    if line.startswith("#") or line.startswith("("):
                        continue
                    # Extract first token and validate as a path
                    token = line.split()[0]
                    # Only include if it looks like a file path
                    if os.path.splitext(token)[1]:
                        to_compress.append(token)
    except Exception as e:
        raise RuntimeError(f"Failed to parse report '{report_path}': {e}")
    return to_compress
