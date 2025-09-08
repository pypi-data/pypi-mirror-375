import json
import unittest

from httmock import HTTMock

from pymod import ArgoMonitoringService, ReportResults

from .monmocks import ReportMocks


class TestReportResults(unittest.TestCase):
    def setUp(self):
        self.mon = ArgoMonitoringService("localhost", "s3cr3t")
        self.ReportMocks = ReportMocks()

    def _validateReportResultsData(self, results: ReportResults):
        self.assertIsNotNone(results)
        self.assertIsNotNone(results.supergroups)
        self.assertEqual(len(results.supergroups), 1)
        self.assertEqual(results.supergroups[0].name, "TENANT01")
        self.assertEqual(results.supergroups[0].type, "PROJECT")
        self.assertIsNotNone(results.supergroups[0].results)
        self.assertEqual(len(results.supergroups[0].results), 1)
        self.assertEqual(str(results.supergroups[0].results[0].date), "2025-06-01 00:00:00")
        self.assertEqual(results.supergroups[0].results[0].availability, "100")
        self.assertEqual(results.supergroups[0].results[0].reliability, "100")
        self.assertIsNotNone(results.supergroups[0].groups)
        self.assertEqual(len(results.supergroups[0].groups), 1)
        self.assertEqual(results.supergroups[0].groups[0].name, "ARGO_MON")
        self.assertEqual(results.supergroups[0].groups[0].type, "SERVICEGROUPS")
        self.assertIsNotNone(results.supergroups[0].groups[0].results)
        self.assertEqual(len(results.supergroups[0].groups[0].results), 1)
        self.assertEqual(str(results.supergroups[0].groups[0].results[0].date), "2025-06-01 00:00:00")
        self.assertEqual(results.supergroups[0].groups[0].results[0].availability, "100")
        self.assertEqual(results.supergroups[0].groups[0].results[0].reliability, "100")
        self.assertEqual(results.supergroups[0].groups[0].results[0].unknown, "0")
        self.assertEqual(results.supergroups[0].groups[0].results[0].uptime, "1")
        self.assertEqual(results.supergroups[0].groups[0].results[0].downtime, "0")

    def testGetReportResults(self):
        with HTTMock(
            self.ReportMocks.list_reports_mock,
            self.ReportMocks.get_report_results_mock
        ):
            results = self.mon.reports[0].results
            self.assertIsNotNone(results)
            self._validateReportResultsData(results)

    def testGetReportResultsJSON(self):
        with HTTMock(
            self.ReportMocks.list_reports_mock,
            self.ReportMocks.get_report_results_mock
        ):
            results = self.mon.reports[0].results
            self.assertIsNotNone(results)
            jsons = str(results)
            try:
                j = json.loads(jsons)
            except json.decoder.JSONDecodeError:
                self.fail("Invalid JSON representation")
            self.assertIsNotNone(j)
            self.assertTrue('"name": "TENANT01"' in jsons)
            self.assertTrue('"type": "PROJECT"' in jsons)
            self.assertTrue('"date": "2025-06-01"' in jsons)
            self.assertTrue('"availability": "100"' in jsons)
            self.assertTrue('"reliability": "100"' in jsons)
            self.assertTrue('"unknown": "0"' in jsons)
            self.assertTrue('"uptime": "1"' in jsons)
            self.assertTrue('"downtime": "0"' in jsons)
