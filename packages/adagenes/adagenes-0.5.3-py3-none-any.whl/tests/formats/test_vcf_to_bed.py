import unittest, os
import adagenes as ag

class VCF2BEDTestCase(unittest.TestCase):

    def test_vcf2bed(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + "/../test_files/GRCh38.variant_call.clinical.conflicting_or_other.vcf.gz"
        ag.vcf_to_bed(infile)
