import traceback, copy
import datetime
import adagenes.tools.module_requests as req
from onkopus.conf import read_config as config
import adagenes.tools
import adagenes as ag
import re


class ClassifyCNVClient:

    def __init__(self, genome_version, error_logfile=None):
        self.genome_version = genome_version
        self.url_pattern = config.classifycnv_src
        self.srv_prefix = config.classifycnv_srv_prefix
        self.extract_keys = config.classifycnv_keys
        self.info_lines = config.classifycnv_info_lines
        self.error_logfile = error_logfile

        self.qid_key = "q_id"
        #if (self.genome_version == "hg19") or (self.genome_version == "GRCh37"):
        #    self.qid_key = "q_id_hg19"

    def process_data(self, vcf_lines):

        # Filtering
        vcf_linesf = adagenes.tools.filter_wildtype_variants(vcf_lines)

        qid_dc = {}
        if self.genome_version == "hg38":
            qid_list = copy.deepcopy(list(vcf_linesf.keys()))
        else:
            qid_dc, qid_list = ag.tools.generate_qid_list_from_other_reference_genome(vcf_linesf)
            self.genome_version = "hg38"
            retransform = True
        #qid_dc, qid_list = ag.tools.generate_qid_list_from_other_reference_genome(vcf_linesf)
        #print("qiddc ",qid_dc)
        #self.genome_version = "hg38"

        while True:
            max_length = int(config.config["DEFAULT"]["MODULE_BATCH_SIZE"])
            if max_length > len(qid_list):
                max_length = len(qid_list)
            qids_partial = qid_list[0:max_length]
            print("vars ",qids_partial)
            variants = ','.join(adagenes.tools.filter_alternate_alleles(qids_partial))

            try:
                #json_body = req.get_connection(variants, self.url_pattern, self.genome_version)
                json_body = req.get_connection(variants, self.url_pattern, "hg38")

                for qid in json_body.keys():
                        print(qid)
                        qid_orig = qid
                        pattern = re.compile(r'(chr[0-9XYMN]+)_([0-9]+)_([0-9]+)_([A-Z]+)')
                        qid = pattern.sub(r'\1:\2-\3_\4', qid)
                        try:
                            #if qid in qid_dc:
                            #    qid_orig = qid_dc[qid]
                            #else:
                            #    qid_orig = qid
                            #print("qid orig ",qid_orig)
                            #vcf_lines[qid_orig][self.srv_prefix] = json_obj
                            print("keys ",vcf_lines.keys())
                            vcf_lines[qid][self.srv_prefix] = json_body[qid_orig]
                        except:
                            cur_dt = datetime.datetime.now()
                            date_time = cur_dt.strftime("%m/%d/%Y, %H:%M:%S")
                            msg = date_time + ": Error (ClinVar client): " + ": error processing variant response: ", qid, ';', traceback.format_exc()
                            print(traceback.format_exc())


            except:
                if self.error_logfile is not None:
                    print("error processing request: ", variants, file=self.error_logfile)

            for i in range(0, max_length):
                del qid_list[0] #qid_list.remove(qid)
            if len(qid_list) == 0:
                break

        return vcf_lines
