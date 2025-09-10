import unittest, os
import adagenes as ag
from adagenes.tools.client_mgt import get_reader, get_writer


class TestBEDReader(unittest.TestCase):

    def test_bed_reader(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        genome_version = 'hg19'

        infile = __location__ + "/../test_files/GRCh38.variant_call.clinical.conflicting_or_other.bed"
        bframe = ag.read_file(infile, genome_version=genome_version)
        #print(list(bframe.data.keys())[0])
        #print(bframe)
        self.assertEqual(len(list(bframe.data.keys())), 1340, "")



