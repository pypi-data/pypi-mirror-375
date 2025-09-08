#!/usr/bin/env python
import sys
from argparse import ArgumentParser
from datetime import datetime

from argo_mon_library import ArgoMonitoringService

if __name__ == "__main__":
    parser = ArgumentParser(description="Simple Argo Monitoring A/R fetch example")
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
        help="start date for report results, in YYYY-MM-DD format",
    )
    parser.add_argument(
        "--end-date",
        type=str,
        help="optional end date for report results, in YYYY-MM-DD format (default: same as start date)",
    )
    parser.add_argument(
        "--supergroup",
        type=str,
        default="all",
        help="optionally filter report results for a specific supergroup, by name (default: don't filter)",
    )
    parser.add_argument(
        "--group",
        type=str,
        default="all",
        help="optionally filter report results for a specific group, by name (default: don't filter)",
    )
    parser.add_argument(
        "--monthly",
        help="get report results with monthly granularity (default: daily)",
        action="store_true",
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

    try:
        mon = ArgoMonitoringService(args.host, api_key)
        results = (
            mon.period(
                datetime.strptime(args.start_date, "%Y-%m-%d"),
                datetime.strptime(args.end_date, "%Y-%m-%d"),
                granularity="monthly" if args.monthly else "daily",
            )
            .reports.by_name(args.report)
            .results
        )
        if args.supergroup == "all":
            supergroups = results.supergroups
        else:
            supergroups = [results.supergroups.by_name(args.supergroup)]
        for supergroup in supergroups:
            for result in supergroup.results:
                print(
                    supergroup.type + ":",
                    supergroup.name,
                    result.date,
                    "A/R: {0:.2f}/{1:.2f}".format(
                        float(result.availability), float(result.reliability)
                    ),
                )
            if args.group == "all":
                groups = supergroup.groups
            else:
                groups = [supergroup.groups.by_name(args.group)]
            for group in groups:
                for result in group.results:
                    print(
                        "  ",
                        group.type + ":",
                        group.name,
                        result.date,
                        "A/R: {0:.2f}/{1:.2f}, Uptime: {2}, Downtime: {3}, Unknown: {4}".format(
                            float(result.availability),
                            float(result.reliability),
                            result.uptime,
                            result.downtime,
                            result.unknown,
                        ),
                    )
    except Exception as e:
        print("Error while iterating report results:", str(e))
