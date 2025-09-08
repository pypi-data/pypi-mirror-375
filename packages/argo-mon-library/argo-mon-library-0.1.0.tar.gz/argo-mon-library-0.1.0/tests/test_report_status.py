import json
import unittest

from httmock import HTTMock

from pymod import ArgoMonitoringService, ReportStatus

from .monmocks import ReportMocks


class TestReportStatus(unittest.TestCase):
    def setUp(self):
        self.mon = ArgoMonitoringService("localhost", "s3cr3t")
        self.ReportMocks = ReportMocks()

    def _validateReportStatusData(self, status: ReportStatus):
        self.assertIsNotNone(status.groups)
        self.assertEqual(len(status.groups), 1)
        self.assertIsNotNone(status.groups[0].statuses)
        self.assertEqual(status.groups[0].name, "ARGO_MON")
        self.assertEqual(status.groups[0].type, "SERVICEGROUPS")
        self.assertEqual(len(status.groups[0].statuses), 2)
        self.assertEqual(str(status.groups[0].statuses[0].timestamp), "2025-06-01 00:00:00")
        self.assertEqual(status.groups[0].statuses[0].value, "OK")
        self.assertEqual(str(status.groups[0].statuses[1].timestamp), "2025-06-01 23:59:59")
        self.assertEqual(status.groups[0].statuses[1].value, "OK")
        self.assertIsNotNone(status.groups[0].endpoints)
        self.assertEqual(len(status.groups[0].endpoints), 1)
        self.assertEqual(status.groups[0].endpoints[0].hostname, "www.example.com")
        self.assertEqual(status.groups[0].endpoints[0].service, "www.example.com-example.api")
        self.assertEqual(status.groups[0].endpoints[0].id, "EXAMPLE01")
        self.assertEqual(status.groups[0].endpoints[0].url, "https://www.example.com/api/action?foo=bar")
        self.assertEqual(len(status.groups[0].endpoints[0].statuses), 2)
        self.assertEqual(str(status.groups[0].endpoints[0].statuses[0].timestamp), "2025-06-01 00:00:00")
        self.assertEqual(status.groups[0].endpoints[0].statuses[0].value, "OK")
        self.assertEqual(str(status.groups[0].endpoints[0].statuses[1].timestamp), "2025-06-01 23:59:59")
        self.assertEqual(status.groups[0].endpoints[0].statuses[1].value, "OK")

    def testGetReportStatus(self):
        with HTTMock(
            self.ReportMocks.list_reports_mock,
            self.ReportMocks.get_report_status_mock
        ):
            status = self.mon.reports[0].status
            self.assertIsNotNone(status)
            self._validateReportStatusData(status)

    def testGetReportStatusJSON(self):
        with HTTMock(
            self.ReportMocks.list_reports_mock,
            self.ReportMocks.get_report_status_mock
        ):
            status = self.mon.reports[0].status
            self.assertIsNotNone(status)
            jsons = str(status)
            try:
                j = json.loads(jsons)
            except json.decoder.JSONDecodeError:
                self.fail("Invalid JSON representation")
            self.assertIsNotNone(j)
            self.assertTrue('"name": "ARGO_MON"' in jsons)
            self.assertTrue('"type": "SERVICEGROUPS"' in jsons)
            self.assertTrue('"timestamp": "2025-06-01T00:00:00Z"' in jsons)
            self.assertTrue('"timestamp": "2025-06-01T23:59:59Z"' in jsons)
            self.assertTrue('"value": "OK"' in jsons)
            self.assertTrue('"hostname": "www.example.com"' in jsons)
            self.assertTrue('"service": "www.example.com-example.api"' in jsons)
            self.assertTrue('"ID": "EXAMPLE01"' in jsons)
            self.assertTrue('"URL": "https://www.example.com/api/action?foo=bar"' in jsons)
