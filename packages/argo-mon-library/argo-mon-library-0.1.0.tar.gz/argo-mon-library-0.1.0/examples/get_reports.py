#!/usr/bin/env python
import sys
from argparse import ArgumentParser

from argo_mon_library import ArgoMonitoringService

if __name__ == "__main__":
    parser = ArgumentParser(description="Simple Argo Monitoring metric fetch example")
    parser.add_argument(
        "--host",
        type=str,
        default="api.devel.mon.argo.grnet.gr",
        help="FQDN of Argo Monitoring Service",
    )
    parser.add_argument(
        "--api-key", type=str, required=True, help="API key"
    )
    parser.add_argument(
        "-f",
        help="treat the API key argument as a path to a file holding the key",
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

    mon = ArgoMonitoringService(args.host, api_key)
    i = 0
    try:
        for m in mon.reports:
            i += 1
            print("Report #{0}".format(i))
            print("  ID: {0}".format(m.id))
            print("  Name: {0}".format(m.name))
            print("  Description: {0}".format(m.description))
            print("  Thresholds:")
            print("    - Availability: {0}%".format(m.thresholds.availability))
            print("    - Reliability: {0}%".format(m.thresholds.reliability))
            print("    - Uptime: {0}".format(m.thresholds.uptime))
            print("    - Unknown: {0}".format(m.thresholds.unknown))
            print("    - Downtime: {0}".format(m.thresholds.downtime))
            print("  Topology Schema:")
            g = m.topology_schema.group
            i = 0
            while g is not None:
                print(" {0} ↳ {1}".format("".join([" " for x in range(0, i)]), g.type))
                g = g.group
                i = i + 2

    except Exception as e:
        print("Error while iterating reports:", str(e))
