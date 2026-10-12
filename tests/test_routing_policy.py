import unittest
from dataclasses import replace
from routing_policy import Health, target

class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.writer = Health(True, False, False, True)
        self.reserve = Health(True, True, True, True)
    def test_normal_requests_use_only_writer(self):
        for method in ('GET','HEAD','POST','PATCH','DELETE'):
            self.assertEqual(target(method,self.writer,self.reserve),'primary')
    def test_failed_writer_allows_reads_only(self):
        failed = replace(self.writer,reachable=False)
        for method in ('GET','HEAD'):
            self.assertEqual(target(method,failed,self.reserve),'read-only-reserve')
        for method in ('POST','PATCH','DELETE'):
            self.assertEqual(target(method,failed,self.reserve),'unavailable')
    def test_invalid_reserve_fails_closed(self):
        failed = replace(self.writer,reachable=False)
        for reserve in (replace(self.reserve,read_only=False), replace(self.reserve,in_recovery=False),
                        replace(self.reserve,compatible=False),replace(self.reserve,replay_lag_seconds=121),
                        replace(self.reserve,replay_lag_seconds=-1)):
            self.assertEqual(target('GET',failed,reserve),'unavailable')
    def test_services_failure_does_not_interrupt_writer(self):
        self.assertEqual(target('POST',self.writer,replace(self.reserve,reachable=False)),'primary')

if __name__ == '__main__':
    unittest.main()
