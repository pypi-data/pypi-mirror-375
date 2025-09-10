import os

os.environ["ONKOPUS_MODULE_SERVER2"] = "134.76.19.66"
os.environ["ONKOPUS_MODULE_PROTOCOL2"] = "http"

import unittest
import adagenes as ag
import onkopus as op


class DSTestCase(unittest.TestCase):

    def test_ds_client(self):
        genome_version = 'hg38'

        data = {"chr1:100000-200000_DEL": {}, "chr2:200000-1900000_DUP": {}}
        bframe = ag.BiomarkerFrame(data)
        print(bframe.data)

        #variant_data = op.GENCODECNAClient(genome_version).process_data(bframe.data)
        variant_data = op.CNASphereGenesClient(genome_version).process_data(bframe.data)
        print(variant_data)

        variant_data = op.DosageSensitivityClient(genome_version).process_data(variant_data)

        print("keys ", variant_data)
        print(variant_data["chr2:200000-1900000_DUP"]["dosage_sensitivity"])
        self.assertEqual(variant_data["chr2:200000-1900000_DUP"]["dosage_sensitivity"]['MYT1L']["chrom"], "chr2", "")

