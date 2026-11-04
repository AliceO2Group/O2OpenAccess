#!/usr/bin/env python3
"""Render ccdb-local.service from ccdb-local.service.j2 (same directory as this script).

Defaults:
  user/group  root/root when run as root (effective UID 0), otherwise the
              invoking user and its primary group. --user without --group
              uses that user's primary group.
  --jar       ./local.jar, written as its realpath (symlinks resolved)
  --address   *
  --port      10080
"""

import argparse
import grp
import os
import pwd
import re
import sys
from pathlib import Path

try:
    import jinja2
except ImportError:
    sys.exit("ERROR: jinja2 not found (EL: dnf install python3-jinja2; Debian/Ubuntu: apt install python3-jinja2)")

TEMPLATE = Path(__file__).resolve().parent / "ccdb-local.service.j2"

# Values are written unquoted into Environment= lines: whitespace, quotes and
# backslashes would be parsed by systemd's word splitting and break the value.
UNSAFE = re.compile(r'[\s"\'\\]')


def unit_value(name: str, value: str) -> str:
    if UNSAFE.search(value):
        sys.exit(f"ERROR: {name} {value!r} contains whitespace, quotes or backslashes")
    # '%' starts a systemd specifier (%h, %u, ...); '%%' is a literal '%'.
    return value.replace("%", "%%")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-r", "--repository", required=True, help="FILE_REPOSITORY_LOCATION (made absolute)")
    ap.add_argument("-j", "--jar", default="local.jar", help="path to local.jar (default: ./local.jar)")
    ap.add_argument("-u", "--user", help="service User=")
    ap.add_argument("-g", "--group", help="service Group=")
    ap.add_argument("-a", "--address", default="*", help='TOMCAT_ADDRESS, comma-separated list allowed (default: "*")')
    ap.add_argument("-p", "--port", type=int, default=10080, help="TOMCAT_PORT (default: 10080)")
    ap.add_argument("-o", "--output", help="output file (default: stdout)")
    args = ap.parse_args()

    # --- user / group ---
    if args.user:
        try:
            pw = pwd.getpwnam(args.user)
        except KeyError:
            sys.exit(f"ERROR: user {args.user!r} does not exist")
        user = args.user
        default_group = grp.getgrgid(pw.pw_gid).gr_name
    elif os.geteuid() == 0:
        user, default_group = "root", "root"
    else:
        user = pwd.getpwuid(os.geteuid()).pw_name
        default_group = grp.getgrgid(os.getegid()).gr_name

    group = args.group or default_group
    try:
        grp.getgrnam(group)
    except KeyError:
        sys.exit(f"ERROR: group {group!r} does not exist")

    # --- paths ---
    jar = os.path.realpath(args.jar)
    if not os.path.isfile(jar):
        sys.exit(f"ERROR: {args.jar!r} -> {jar!r} is not a file")
    repository = os.path.abspath(args.repository)

    # --- endpoint ---
    if not 1 <= args.port <= 65535:
        sys.exit(f"ERROR: port {args.port} out of range 1-65535")

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(TEMPLATE.parent)),
        undefined=jinja2.StrictUndefined,  # a misspelled variable is an error, not an empty string
        keep_trailing_newline=True,
    )
    text = env.get_template(TEMPLATE.name).render(
        ccdb_user=unit_value("user", user),
        ccdb_group=unit_value("group", group),
        ccdb_repository=unit_value("repository", repository),
        ccdb_jar=unit_value("jar", jar),
        ccdb_address=unit_value("address", args.address),
        ccdb_port=args.port,
    )

    if args.output:
        Path(args.output).write_text(text)
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
