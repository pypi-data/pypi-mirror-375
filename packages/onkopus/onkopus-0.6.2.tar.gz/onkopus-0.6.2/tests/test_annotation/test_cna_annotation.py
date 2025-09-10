import unittest
import os
import onkopus as op
import adagenes as ag


class TestCNAAnnotation(unittest.TestCase):

    def test_cna_annotation(self):
        cna_id = "chr15:30103918-34000000_DEL"
        data = { cna_id:{ "variant_data": { "CHROM": 15, "POS":30103918, "POS2": 30644082 },"mutation_type": "cnv" }}
        bframe = ag.BiomarkerFrame(data)
        #print(bframe.data)
        data = op.annotate_cnas(bframe.data)
        #print(data)
        self.assertEqual(set(list(data[cna_id].keys())),
                         {'type', 'gencode_cna', 'mdesc', 'variant_data', 'mutation_type','protein_domains', 'dgidb',
                          'cna_genes','cnvoyant', 'xcnv','isv','tada','dbcnv'},
                         "")
        #self.assertEqual(len(data[cna_id]["gencode_cna"]["cds"]),128,"")
        self.assertEqual(len(data[cna_id]["cna_genes"]),22,"")

    def test_cna_annotation_file(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + "/../test_files/cnv_sample.vcf"
        bframe = op.read_file(infile, genome_version="hg38")
        print("bframe keys ",bframe.data.keys())
        #data = {"chr15:30103918><DEL>": {"variant_data": {"CHROM": 15, "POS": 30103918, "POS2": 30644082},
        #                                 "mutation_type": "cnv"}}
        #bframe = ag.BiomarkerFrame(data)
        #print(bframe.data)
        data = op.annotate_cnas(bframe.data)
        #print("annotated data ", data)

        cna_id = "chr1:844347-6477436_DEL"
        self.assertEqual(set(list(data[cna_id].keys())),
                         {'type', 'gencode_cna', 'mdesc', 'variant_data', 'mutation_type', 'protein_domains',
                          'info_features','orig_identifier', 'dgidb', 'cna_genes','cnvoyant', 'xcnv','isv','dbcnv',
                          'tada'},
                         "")
        self.assertEqual(len(data[cna_id]["gencode_cna"]["cds"]), 2, "")
        self.assertEqual(data[cna_id]["variant_data"]["POS2"], "714338", "")
