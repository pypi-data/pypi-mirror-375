import argparse
import sys
from typing import List

from ying.plog import run_command
from ying.notify import resolve_endpoint, send_notification


class ProgressLog(object):
    def plog(self, cmd, mode):
        run_command(cmd, mode)

def main():
    parser = argparse.ArgumentParser(description="Ying CLI")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    plog_parser = subparsers.add_parser("plog", help="Run a command and log progress")
    plog_parser.add_argument("cmd", help="Shell command to run (quote if it contains spaces)")
    plog_parser.add_argument("-m", "--mode", default="r", help="Mode for run_command (default: r)")

    notify_parser = subparsers.add_parser("notify", help="Send a notification")
    notify_parser.add_argument("-t", "--title", required=False, help="Notification title (optional)")
    notify_parser.add_argument(
        "-b",
        "--body",
        required=False,
        help="Notification body. If omitted, stdin is read (if piped)",
    )
    notify_parser.add_argument("-v", "--verbose", action="count", default=0, help="Increase verbosity; repeat for more detail")
    notify_parser.add_argument("--url", dest="url_opts", action="append", default=[], help="Destination URL (repeatable)")
    notify_parser.add_argument("urls", nargs="*", help="Destination URLs (positional)")

    args = parser.parse_args()

    if args.subcommand == "plog":
        progress = ProgressLog()
        progress.plog(args.cmd, args.mode)
        return

    if args.subcommand == "notify":
        # Merge URLs provided via --url and positional args, preserving order and removing duplicates
        merged_urls: List[str] = []
        for url in list(args.url_opts or []) + list(args.urls or []):
            if url not in merged_urls:
                merged_urls.append(url)

        if not merged_urls:
            sub = "--url or positional URLs"
            raise SystemExit(f"notify: at least one destination URL must be provided via {sub}")

        endpoint = resolve_endpoint()

        # Title (optional)
        title_value = args.title or ""

        # Body: prefer --body; otherwise read from stdin if available
        body_value = args.body
        used_stdin = False
        if body_value is None:
            try:
                if not sys.stdin.isatty():
                    body_value = sys.stdin.read()
                    used_stdin = True
            except Exception:
                body_value = None
        if body_value is None:
            body_value = ""

        if args.verbose:
            print(f"notify: endpoint={endpoint}")
            print(f"notify: title={title_value}")
            print(f"notify: body length={len(body_value)} (stdin={used_stdin})")
            print(f"notify: urls={merged_urls}")

        try:
            resp = send_notification(title_value, body_value, merged_urls, endpoint)
        except Exception as err:
            raise SystemExit(f"notify: request failed: {err}")

        if args.verbose and args.verbose >= 2:
            print(f"notify: response status={resp.status_code}")
            try:
                print(f"notify: response body={resp.text}")
            except Exception:
                pass
        else:
            print("OK")
        return


if __name__ == "__main__":
    main()
