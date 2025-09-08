#!/usr/bin/env python
import sys
from argparse import ArgumentParser
from datetime import datetime

from argo_mon_library import ArgoMonitoringService

if __name__ == "__main__":
    parser = ArgumentParser(description="Simple Argo Monitoring status fetch example")
    parser.add_argument(
        "--host",
        type=str,
        default="api.devel.mon.argo.grnet.gr",
        help="FQDN of Argo Monitoring Service",
    )
    parser.add_argument("--api-key", type=str, required=True, help="API key")
    parser.add_argument(
        "-f",
        help="treat the API key argument as a path to a file holding the key",
        action="store_true",
    )
    parser.add_argument("--report", type=str, required=True, help="report name")
    parser.add_argument(
        "--start-date",
        type=str,
        required=True,
        help="start date for report status, in YYYY-MM-DD format",
    )
    parser.add_argument(
        "--end-date",
        type=str,
        help="optional end date for report status, in YYYY-MM-DD format (default: same as start date)",
    )
    args = parser.parse_args()

    if args.f:
        try:
            with open(args.api_key, "r") as keyfile:
                api_key = keyfile.read()
        except Exception as e:
            print("Error while reading API key from file:", str(e), file=sys.stderr)
            exit(1)
    else:
        api_key = args.api_key

    if args.end_date is None:
        args.end_date = args.start_date
    try:
        mon = ArgoMonitoringService(args.host, api_key)
        for group in (
            mon.period(
                datetime.strptime(args.start_date, "%Y-%m-%d"),
                datetime.strptime(args.end_date, "%Y-%m-%d"),
            )
            .reports.by_name(args.report)
            .status.groups
        ):
            for endpoint in group.endpoints:
                for status in endpoint.statuses:
                    print(
                        group.name,
                        "[" + endpoint.id + "]",
                        status.timestamp,
                        status.value,
                    )
    except Exception as e:
        print("Error while iterating report status data:", str(e))
