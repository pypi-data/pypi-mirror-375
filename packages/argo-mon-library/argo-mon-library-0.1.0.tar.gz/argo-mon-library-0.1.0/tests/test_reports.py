import json
import unittest
from datetime import datetime

from httmock import HTTMock

from pymod import ArgoMonitoringService, Report

from .monmocks import ReportMocks


class TestReports(unittest.TestCase):
    def setUp(self):
        self.mon = ArgoMonitoringService("localhost", "s3cr3t")
        self.mon2 = ArgoMonitoringService("127.0.0.1", "S3CR3T")
        self.ReportMocks = ReportMocks()

    def testInstances(self):
        with HTTMock(
            self.ReportMocks.list_reports_mock, self.ReportMocks.list_reports_mock2
        ):
            reports = self.mon.reports
            reports2 = self.mon2.reports
            self.assertNotEqual(reports[0].name, reports2[0].name)

    def testReportListing(self):
        with HTTMock(self.ReportMocks.list_reports_mock):
            reports = self.mon.reports
            self.assertEqual(len(list(reports)), 1)

    def _validateReportData(self, report: Report):
        self.assertEqual(report.id, "efd48668-e24a-4a2c-a53f-3f388664b691")
        self.assertEqual(report.tenant, "TENANT01")
        self.assertEqual(report.disabled, False)
        self.assertEqual(report.name, "REPORT01")
        self.assertEqual(report.description, "REPORT01 A/R report")
        self.assertEqual(
            report.created_on,
            datetime.strptime("2025-03-06 12:53:27", "%Y-%m-%d %H:%M:%S"),
        )
        self.assertEqual(
            report.updated_on,
            datetime.strptime("2025-03-06 12:53:27", "%Y-%m-%d %H:%M:%S"),
        )
        self.assertEqual(report.computations.ar, True)
        self.assertEqual(report.computations.status, True)
        self.assertIn("flapping", report.computations.trends)
        self.assertIn("status", report.computations.trends)
        self.assertIn("tags", report.computations.trends)
        self.assertEqual(report.thresholds.availability, 80)
        self.assertEqual(report.thresholds.reliability, 90)
        self.assertEqual(report.thresholds.uptime, 0.8)
        self.assertEqual(report.thresholds.unknown, 0.1)
        self.assertEqual(report.thresholds.downtime, 0.1)
        self.assertEqual(len(report.profiles), 3)
        self.assertEqual("5c3218ea-3f67-4d4c-b3ce-f650b8ed8e68", report.profiles[0].id)
        self.assertEqual("ARGO_MON", report.profiles[0].name)
        self.assertEqual("metric", report.profiles[0].type)
        self.assertEqual("ede2a9f7-e754-47fa-8e76-449e3925fbd4", report.profiles[1].id)
        self.assertEqual("core", report.profiles[1].name)
        self.assertEqual("aggregation", report.profiles[1].type)
        self.assertEqual("be1fbf37-77f3-4a9e-b268-a6a9a0830ef5", report.profiles[2].id)
        self.assertEqual("ops", report.profiles[2].name)
        self.assertEqual("operations", report.profiles[2].type)
        self.assertEqual(len(report.filter_tags), 1)
        self.assertEqual("FT1", report.filter_tags[0].name)
        self.assertEqual("val", report.filter_tags[0].value)
        self.assertEqual("cntx", report.filter_tags[0].context)
        self.assertEqual("PROJECT", report.topology_schema.group.type)
        self.assertEqual("SERVICEGROUPS", report.topology_schema.group.group.type)

    def testGetReportByIndex(self):
        with HTTMock(self.ReportMocks.list_reports_mock):
            reports = self.mon.reports
            report = reports[0]
            self.assertIsNotNone(report)
            self._validateReportData(report)

    def testGetReportByName(self):
        with HTTMock(self.ReportMocks.list_reports_mock):
            reports = self.mon.reports
            report = reports.by_name("REPORT01")
            self.assertIsNotNone(report)
            self._validateReportData(report)

    def testGetReportByID(self):
        with HTTMock(self.ReportMocks.get_report_mock):
            report = self.mon.reports["efd48668-e24a-4a2c-a53f-3f388664b691"]
            self.assertIsNotNone(report)
            self._validateReportData(report)

    def testReportJSON(self):
        with HTTMock(self.ReportMocks.get_report_mock):
            report = self.mon.reports["efd48668-e24a-4a2c-a53f-3f388664b691"]
            self.assertIsNotNone(report)
            jsons = str(report)
            try:
                j = json.loads(jsons)
            except json.decoder.JSONDecodeError:
                self.fail("Invalid JSON representation")
            self.assertIsNotNone(j)
            self.assertTrue('"id": "efd48668-e24a-4a2c-a53f-3f388664b691"' in jsons)
            self.assertTrue('"tenant": "TENANT01"' in jsons)
            self.assertTrue('"disabled": false' in jsons)
            self.assertTrue('"name": "REPORT01"' in jsons)
            self.assertTrue('"description": "REPORT01 A/R report"' in jsons)
            self.assertTrue('"created": "2025-03-06 12:53:27"' in jsons)
            self.assertTrue('"updated": "2025-03-06 12:53:27"' in jsons)
            self.assertTrue(
                '"computations": {"ar": true, "status": true, "trends": ["flapping", "status", "tags"]}'
                in jsons
            )
            self.assertTrue(
                '"thresholds": {"availability": 80, "reliability": 90, "uptime": 0.8, "unknown": 0.1, "downtime": 0.1}'
                in jsons
            )
            self.assertTrue(
                '"topology_schema": {"group": {"type": "PROJECT", "group": {"type": "SERVICEGROUPS"}}}'
                in jsons
            )
            self.assertTrue(
                (
                    '"profiles": [{"id": "5c3218ea-3f67-4d4c-b3ce-f650b8ed8e68", "name": "ARGO_MON", "type": "metric"},'
                    ' {"id": "ede2a9f7-e754-47fa-8e76-449e3925fbd4", "name": "core", "type": "aggregation"},'
                    ' {"id": "be1fbf37-77f3-4a9e-b268-a6a9a0830ef5", "name": "ops", "type": "operations"}]'
                )
                in jsons
            )
            self.assertTrue(
                '"filter_tags": [{"name": "FT1", "value": "val", "context": "cntx"}]}'
                in jsons
            )
