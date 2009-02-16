from unittest import TestCase

from cq2utils import CallTrace
from merescocore.framework import be, Observable
from merescocore.components.http import IpFilter

class IpFilterTest(TestCase):

    def assertValidIp(self,  address, ipranges=[], ips=[]):
        self._assertValidIp(address, ipranges, ips, passed=True)

    def assertInvalidIp(self,  address, ipranges=[], ips=[]):
        self._assertValidIp(address, ipranges, ips, passed=False)


    def _assertValidIp(self, address, ipranges, ips, passed):
        self.observer = CallTrace('Observer')

        dna = be(
            (Observable(),
                (IpFilter(allowedIps=ips, allowedIpRanges=ipranges),
                    (self.observer, )
                )
            )
        )

        list(dna.all.handleRequest(Client=address))
        if passed:
            self.assertEquals(1, len(self.observer.calledMethods))
            self.assertEquals('handleRequest', self.observer.calledMethods[0].name)
        else:
            self.assertEquals(0, len(self.observer.calledMethods))

    def testFilterSingleIp(self):
        pass

    def testInRanges(self):
        self.assertValidIp('192.168.1.0', ipranges=[('192.168.1.0', '192.168.1.255')])
        self.assertValidIp('192.168.1.128', ipranges=[('192.168.1.0', '192.168.1.255')])
        self.assertValidIp('192.168.1.128', ipranges=[('192.168.2.0', '192.168.2.255'), ('192.168.1.0', '192.168.1.255')])

    def testNotInRanges(self):
        self.assertInvalidIp('192.168.2.128', ipranges=[('192.168.1.0', '192.168.1.255')])
        self.assertInvalidIp('192.168.1.255', ipranges=[('192.168.1.0', '192.168.1.255')])
        self.assertInvalidIp('192.168.2.0', ipranges=[('192.168.1.0', '192.168.1.255')])
        self.assertInvalidIp('192.168.0.255', ipranges=[('192.168.1.0', '192.168.1.255')])

    def testConvertToNumber(self):
        iprange = IpFilter()

        self.assertEquals(3232235776, iprange._convertToNumber('192.168.1.0'))
        self.assertEquals(0, iprange._convertToNumber('0.0.0.0'))