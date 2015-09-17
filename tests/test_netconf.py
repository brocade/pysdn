#!/usr/bin/python

import unittest
import sys


class TestNetConfSamples(unittest.TestCase):
    sys.path.insert(0, '../samples/samplenetconf/demos')

    def test_netconf1(self):
        from vr_demo1 import vr_demo_1
        assert vr_demo_1() is None

    def test_netconf2(self):
        from vr_demo2 import vr_demo_2
        assert vr_demo_2() is None

    def test_netconf3(self):
        from vr_demo3 import vr_demo_3
        assert vr_demo_3() is None

    def test_netconf4(self):
        from vr_demo4 import vr_demo_4
        assert vr_demo_4() is None

    def test_netconf5(self):
        from vr_demo5 import vr_demo_5
        assert vr_demo_5() is None

    def test_netconf6(self):
        from vr_demo6 import vr_demo_6
        assert vr_demo_6() is None

    def test_netconf7(self):
        from vr_demo7 import vr_demo_7
        assert vr_demo_7() is None

    def test_netconf8(self):
        from vr_demo8 import vr_demo_8
        assert vr_demo_8() is None

    def test_netconf9(self):
        from vr_demo9 import vr_demo_9
        assert vr_demo_9() is None


# Not currently working --------------->>>

#  def test_netconf10(self):
#      from vr_demo10 import vr_demo_10
#      assert vr_demo_10() is None

#  def test_netconf11(self):
#      from vr_demo11 import vr_demo_11
#      assert vr_demo_11() is None

#  def test_netconf12(self):
#      from vr_demo12 import vr_demo_12
#      assert vr_demo_12() is None

# <<<------------   Not currently working

    def test_netconf13(self):
        from vr_demo13 import vr_demo_13
        assert vr_demo_13() is None

    def test_netconf14(self):
        from vr_demo14 import vr_demo_14
        assert vr_demo_14() is None

    def test(self):
        from ctrl_demo1 import nc_demo_1
        assert nc_demo_1() is None

    def test_nc2(self):
        from ctrl_demo2 import nc_demo_2
        assert nc_demo_2() is None

    def test_nc3(self):
        from ctrl_demo3 import nc_demo_3
        assert nc_demo_3() is None

    def test_nc4(self):
        from ctrl_demo4 import nc_demo_4
        assert nc_demo_4() is None

    def test_nc5(self):
        from ctrl_demo5 import nc_demo_5
        assert nc_demo_5() is None

    def test_nc6(self):
        from ctrl_demo6 import nc_demo_6
        assert nc_demo_6() is None

    def test_nc7(self):
        from ctrl_demo7 import nc_demo_7
        assert nc_demo_7() is None

    def test_nc8(self):
        from ctrl_demo8 import nc_demo_8
        assert nc_demo_8() is None

    def test_nc9(self):
        from ctrl_demo9 import nc_demo_9
        assert nc_demo_9() is None

    def test_nc10(self):
        from ctrl_demo10 import nc_demo_10
        assert nc_demo_10() is None

    def test_nc11(self):
        from ctrl_demo11 import nc_demo_11
        assert nc_demo_11() is None

    def test_nc12(self):
        from ctrl_demo12 import nc_demo_12
        assert nc_demo_12() is None

    def test_nc13(self):
        from ctrl_demo13 import nc_demo_13
        assert nc_demo_13() is None

if __name__ == '__main__':
    # unittest.main()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestNetConfSamples)
    unittest.TextTestRunner(verbosity=2).run(suite)
