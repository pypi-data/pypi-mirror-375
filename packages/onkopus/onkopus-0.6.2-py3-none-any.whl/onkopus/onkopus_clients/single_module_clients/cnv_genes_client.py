import datetime, traceback, copy
import adagenes.tools
import adagenes.tools.module_requests as req
from onkopus.conf import read_config as config
from adagenes.tools import generate_variant_dictionary
import onkopus as op

def collect_affected_genes(json_body):

    genes_str = ''
    cds_str = ''
    utr_str = ''

    response = []
    for res in json_body:
        for gene in res["genes"]:
            #gene_name = gene["gene_name"]
            #print(gene)
            response.append( gene )

    return response


def get_qid_list(vcf_lines):

    qid_dc = {}
    qid_list = []

    for var in vcf_lines.keys():
        print(vcf_lines[var])

        if "mutation_type" in vcf_lines[var]:
            if vcf_lines[var]["mutation_type"] == "cnv":

                qid = var
                qid = qid.replace("_DEL", "")
                qid = qid.replace("_DUP", "")
                qid = qid.replace("_CNV", "")

                qid_list.append(qid)
                qid_dc[qid] = var

    return qid_dc, qid_list


class CNASphereGenesClient:
    def __init__(self, genome_version, error_logfile=None):
        self.genome_version = genome_version
        self.url_pattern = config.cna_genes_src
        self.srv_prefix = config.cna_genes_srv_prefix
        self.extract_keys = config.cna_genes_keys
        self.info_lines = config.cna_genes_info_lines
        self.error_logfile = error_logfile

        self.qid_key = "q_id"
        if (self.genome_version == "hg19") or (self.genome_version == "GRCh37"):
            self.qid_key = "q_id_hg19"

    def process_data(self, vcf_lines, input_format='json'):

        #print("Annotate CNAs ",vcf_lines)

        mut_types = False
        if (len(list(vcf_lines.keys())) == 5) and ("cnvs" in list(vcf_lines.keys())):
            vcf_lines_cp = copy.deepcopy(vcf_lines)
            vcf_lines = vcf_lines["cnvs"]
            mut_types = True

        if input_format == 'vcf':
            keys = ['POS_hg38']
            annotations = adagenes.tools.parse_vcf.extract_annotations_vcf(vcf_lines, keys)
        else:
            keys = ['POS_hg38']
            annotations = adagenes.tools.parse_vcf.extract_annotations_json(vcf_lines, config.variant_data_key, keys)
        pos_hg38_list = copy.deepcopy(annotations["POS_hg38"])
        #print("hg38 positions: ",pos_hg38_list)

        if self.genome_version != "hg38":
            print("Error: GENCODE genomic only possible for hg38 requests")
            return vcf_lines
        qid_list = copy.deepcopy(annotations['q_id'])
        #qid_list = copy.deepcopy(list(vcf_lines.keys()))

        #variant_dc, liftover_dc = adagenes.tools.parse_genomic_data.generate_liftover_qid_list(qid_list, pos_hg38_list)

        #qid_list = list(vcf_lines.keys())
        #qid_list = list(liftover_dc.keys())
        qid_dc, qid_list = get_qid_list(vcf_lines)

        while True:
            max_length = int(config.config["DEFAULT"]["MODULE_BATCH_SIZE"])
            if max_length > len(qid_list):
                max_length = len(qid_list)
            qids_partial = qid_list[0:max_length]
            qids_partial = adagenes.tools.filter_alternate_alleles(qids_partial)

            genompos_str = ','.join(qids_partial)
            # adagenes.tools.parse_vcf.extract_annotations_json_part(vcf_lines, config.uta_adapter_srv_prefix,[config.uta_genomic_keys[0]],
            #                                                     qids_partial)[config.uta_genomic_keys[0]]
            #gene_names_partial =  op.get_gene_names(vcf_lines)
            #gene_names_str = ",".join(gene_names_partial)
            #http://localhost:10980/CNV/v1/hg38/get_cnv_genes?cnv=chr1:100000-2000000,chr2:2000-3000
            query = 'cnv=' + genompos_str
            query = '?' + query + '&response_type=grouped'

            try:
                json_body = req.get_connection(query, self.url_pattern, "hg38")

                for result in json_body:
                        #annotations = []
                        #print(qid_dc.keys())

                        qid = result["header"]["qid"]

                        if qid not in qid_dc.keys():
                        #if qid not in vcf_lines:
                            continue
                        #qid = json_obj[self.qid_key]

                        try:
                            genes = collect_affected_genes(result["data"])
                            qid_orig = qid_dc[qid]
                            vcf_lines[qid_orig][self.srv_prefix] = genes

                        except:
                            if self.error_logfile is not None:
                                cur_dt = datetime.datetime.now()
                                date_time = cur_dt.strftime("%m/%d/%Y, %H:%M:%S")
                                print(cur_dt, ": error processing variant response: ", qid, ';', traceback.format_exc(), file=self.error_logfile+str(date_time)+'.log')
                            else:
                                print(cur_dt, ": error processing variant response: ", qid, ';', traceback.format_exc())
            except:
                print(": error processing variant response: ;", traceback.format_exc())
                if self.error_logfile is not None:
                    print("error processing request: ", annotations, file=self.error_logfile+str(date_time)+'.log')

            for i in range(0,max_length):
                #del gene_names[0] #gene_names.remove(qid)
                #del variant_exchange[0]  #variant_exchange.remove(qid)
                del qid_list[0] # qid_list.remove(qid)
            if len(qid_list) == 0:
                break

        if mut_types is True:
            vcf_lines_cp["cnvs"] = vcf_lines
            return vcf_lines_cp

        return vcf_lines
