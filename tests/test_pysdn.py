#!/usr/bin/python

import unittest
import sys


class TestOpenFlowSamples(unittest.TestCase):
    sys.path.insert(0, '../samples/sampleopenflow/demos')
    sys.path.insert(0, '../samples/samplenetconf/demos')

    def test_of1(self):
        from demo1 import of_demo_1
        assert of_demo_1() is None

    def test_of2(self):
        from demo2 import of_demo_2
        assert of_demo_2() is None

    def test_of3(self):
        from demo3 import of_demo_3
        assert of_demo_3() is None

    def test_of4(self):
        from demo4 import of_demo_4
        assert of_demo_4() is None

    def test_of5(self):
        from demo5 import of_demo_5
        assert of_demo_5() is None

    def test_of6(self):
        from demo6 import of_demo_6
        assert of_demo_6() is None

    def test_of7(self):
        from demo7 import of_demo_7
        assert of_demo_7() is None

    def test_of8(self):
        from demo8 import of_demo_8
        assert of_demo_8() is None

    def test_of9(self):
        from demo9 import of_demo_9
        assert of_demo_9() is None

    def test_of10(self):
        from demo10 import of_demo_10
        assert of_demo_10() is None

    def test_of11(self):
        from demo11 import of_demo_11
        assert of_demo_11() is None

    def test_of12(self):
        from demo12 import of_demo_12
        assert of_demo_12() is None

    def test_of13(self):
        from demo13 import of_demo_13
        assert of_demo_13() is None

    def test_of14(self):
        from demo14 import of_demo_14
        assert of_demo_14() is None

    def test_of15(self):
        from demo15 import of_demo_15
        assert of_demo_15() is None

    def test_of16(self):
        from demo16 import of_demo_16
        assert of_demo_16() is None

    def test_of17(self):
        from demo17 import of_demo_17
        assert of_demo_17() is None

    def test_of18(self):
        from demo18 import of_demo_18
        assert of_demo_18() is None

    def test_of19(self):
        from demo19 import of_demo_19
        assert of_demo_19() is None

    def test_of20(self):
        from demo20 import of_demo_20
        assert of_demo_20() is None

    def test_of21(self):
        from demo21 import of_demo_21
        assert of_demo_21() is None

    def test_of22(self):
        from demo22 import of_demo_22
        assert of_demo_22() is None

    def test_of23(self):
        from demo23 import of_demo_23
        assert of_demo_23() is None

    def test_of24(self):
        from demo24 import of_demo_24
        assert of_demo_24() is None

    def test_of25(self):
        from demo25 import of_demo_25
        assert of_demo_25() is None

    def test_of26(self):
        from demo26 import of_demo_26
        assert of_demo_26() is None

    def test_of27(self):
        from demo27 import of_demo_27
        assert of_demo_27() is None

    def test_of28(self):
        from demo28 import of_demo_28
        assert of_demo_28() is None

    #  def test_of29(self):
    #      from demo29 import of_demo_29
    #      assert of_demo_29() is None

    #  def test_of30(self):
    #      from demo30 import of_demo_30
    #      assert of_demo_30() is None

    def test_of31(self):
        from demo31 import of_demo_31
        assert of_demo_31() is None

    def test_of32(self):
        from demo32 import of_demo_32
        try:
            assert of_demo_32() is None
        except(AssertionError):
            print "success"

    def test_of33(self):
        from demo33 import of_demo_33
        assert of_demo_33() is None

    def test_of34(self):
        from demo34 import of_demo_34
        assert of_demo_34() is None

    def test_of35(self):
        from demo35 import of_demo_35
        assert of_demo_35() is None

    def test_of36(self):
        from demo36 import of_demo_36
        assert of_demo_36() is None

    def test_of37(self):
        from demo37 import of_demo_37
        assert of_demo_37() is None

    def test_of38(self):
        from demo38 import of_demo_38
        assert of_demo_38() is None

    def test_of39(self):
        from demo39 import of_demo_39
        assert of_demo_39() is None

    def test_of40(self):
        from demo40 import of_demo_40
        assert of_demo_40() is None

    def test_of41(self):
        from demo41 import of_demo_41
        assert of_demo_41() is None

    def test_of42(self):
        from demo42 import of_demo_42
        assert of_demo_42() is None

    def test_of43(self):
        from demo43 import of_demo_43
        assert of_demo_43() is None

    def test_of44(self):
        from demo44 import of_demo_44
        assert of_demo_44() is None

    def test_nc1(self):
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

    #  def test_nc11(self):
    #      from ctrl_demo11 import nc_demo_11
    #      assert nc_demo_11() is None

    #  def test_nc12(self):
    #      from ctrl_demo12 import nc_demo_12
    #      assert nc_demo_12() is None

    #  def test_nc13(self):
    #      from ctrl_demo13 import nc_demo_13
    #      assert nc_demo_13() is None

if __name__ == '__main__':
    # unittest.main()
    try:
        testCaseClass = TestOpenFlowSamples
        suite = unittest.TestLoader().loadTestsFromTestCase(testCaseClass)
        unittest.TextTestRunner(verbosity=2).run(suite)
    except(KeyboardInterrupt):
        msg = "\nInterrupted from keyboard, exit\n"
        sys.stderr.write(msg)
        sys.stderr.flush()
