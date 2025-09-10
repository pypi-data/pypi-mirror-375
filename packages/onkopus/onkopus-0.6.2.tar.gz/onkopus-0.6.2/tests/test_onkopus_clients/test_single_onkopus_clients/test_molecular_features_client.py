import unittest, copy, os
import onkopus as op
import adagenes as ag

class MolFeatAnnotationTestCase(unittest.TestCase):

    def test_molfeat_hg19(self):
        data = {"chr7:140453136A>T":{}}
        genome_version="hg19"
        variant_data = ag.LiftoverAnnotationClient(genome_version=genome_version).process_data(data)
        print(variant_data)
        variant_data = op.UTAAdapterClient(genome_version=genome_version).process_data(variant_data)
        variant_data = op.MolecularFeaturesClient(
            genome_version=genome_version).process_data(variant_data)
        self.assertEqual(variant_data["chr7:140453136A>T"]["molecular_features"]["aromaticity_alt"], 0, "")
        self.assertEqual(variant_data["chr7:140453136A>T"]["molecular_features"]["aromaticity_diff"], 0, "")

    def test_molfeat_client(self):
        #genome_version = 'hg19'
        genome_version = 'hg38'

        #data = {"chr17:7681744T>C": {}, "chr10:8115913C>T": {}}
        data = {"chr7:140753336A>T":{}}

        variant_data = op.UTAAdapterClient(genome_version=genome_version).process_data(data)
        variant_data = op.MolecularFeaturesClient(
            genome_version=genome_version).process_data(variant_data)

        #print("Response ",variant_data)
        self.assertEqual(variant_data["chr7:140753336A>T"]["molecular_features"]["aromaticity_alt"],0,"")

    def test_molfeat_export(self):
        genome_version = 'hg38'
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + "/../../test_files/somaticMutations.l520.protein.vcf"
        outfile = __location__ + "/../../test_files/somaticMutations.l520.protein.molfeat.vcf"

        data = {"chr7:140753336A>T": {}}

        #variant_data = op.UTAAdapterClient(genome_version=genome_version).process_data(data)
        magic_obj = op.MolecularFeaturesClient(
            genome_version=genome_version)
        #op.write_file(outfile, variant_data)

        ag.process_file(infile, outfile, magic_obj=magic_obj)

        file = open(outfile)
        contents = file.read()[0:500]
        print(contents)
        contents_expected = ('chr7\t21744592\t0\tA\tAG\t0\t0\t0;POS_hg19=21784210;POS_hg38=21744592;;\n'
 'chr10\t8073950\t0\tC\tT\t0\t0\t'
 '0;POS_hg19=8115913;POS_hg38=8073950;UTA_Adapter_gene_name=GATA3;UTA_Adapter_variant_exchange=T421M;UTA_Adapter_input_data=chr10:g.8073950C>T;UTA_Adapter_transcript=NM_001002295.2;UTA_Adapter_variant=NP_001002295.1:p.(Thr421Met);UTA_Adapter_variant_exchange_long=Thr421Met;molecular_features_molecular_weight_alt=149.2113;molecular_features_molecular_weight_ref=119.1192;molecular_features_molecular_weight_diff=')
        self.assertEqual(contents, contents_expected, "")
        file.close()

    def test_molfeat_export_writefile(self):
        # genome_version = 'hg19'
        genome_version = 'hg38'
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + "/../../test_files/somaticMutations.l520.protein.vcf"
        outfile = __location__ + "/../../test_files/molfeat.export_test.vcf"

        # data = {"chr17:7681744T>C": {}, "chr10:8115913C>T": {}}
        data = {"chr7:140753336A>T": {}}

        variant_data = op.UTAAdapterClient(genome_version=genome_version).process_data(data)
        variant_data = op.MolecularFeaturesClient(
            genome_version=genome_version).process_data(variant_data)

        # print("Response ",variant_data)
        self.assertEqual(variant_data["chr7:140753336A>T"]["molecular_features"]["aromaticity_alt"], 0, "")

        op.write_file(outfile, variant_data, file_type="vcf")

        file = open(outfile)
        contents = file.read()[0:700]
        print(contents)
        contents_expected = ('##reference=hg38\n'
 '#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n'
 'chr7\t140753336\t.\tA\tT\t.\t.\t'
 'CHROM=7;POS_hg38=140753336;REF=A;ALT=T;gene_name=BRAF;variant_exchange=V600E;transcript=NM_004333.6;variant_exchange_long=Val600Glu;molecular_weight_alt=147.1293;molecular_weight_ref=117.1463;molecular_weight_diff=29.98;charge_at_pH_7_4_ref=-0.47684917889778056;charge_at_pH_7_4_alt=-1.3305060940156797;charge_at_pH_7_4_diff=-0.85;aromaticity_ref=0;aromaticity_alt=0;aromaticity_diff=0.0;flexibility_ref_str=low;flexibility_alt_str=high;flexibility_ref=0;flexibility_alt=2;flexibility_diff=2.0;ionizable_ref=0;ionizable_alt=1;ionizable_diff=1.0;polarity_ref_str=nonpolar;polarity_alt_str=polar;polarity_ref=0;polarity_a')
        self.assertEqual(contents_expected,contents,"")
        file.close()

    def test_molfeat_special_vars(self):
        genome_version = 'hg38'
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        infile = __location__ + "/../../test_files/cl_sample.vcf"
        outfile = __location__ + "/../../test_files/cl_sample.molfeat.vcf"

        bframe = op.read_file(infile)
        print(bframe.data)
        self.assertEqual(len(bframe.data.keys()),22, "")

        #variant_data = op.UTAAdapterClient(genome_version=genome_version).process_data(data)
        magic_obj = op.MolecularFeaturesClient(
            genome_version=genome_version)
        #op.write_file(outfile, variant_data)

        #ag.process_file(infile, outfile, magic_obj=magic_obj)

        bframe.data = op.MolecularFeaturesClient(genome_version=genome_version).process_data(bframe.data)

        #file = open(outfile)
        #contents = file.read()[0:60]
        #contents_expected = """n"""
        #self.assertEqual(contents, contents_expected, "")
        #file.close()
        self.assertEqual(bframe.data["chr19:13135702G>A"]["molecular_features"]["h_bond_acceptor_alt"],0,"")

