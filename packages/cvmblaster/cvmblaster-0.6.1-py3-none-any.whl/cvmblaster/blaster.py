import os
import re
import sys
import pandas as pd
import subprocess
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Tuple
import logging


# supress deprecation warnings
with warnings.catch_warnings():
    warnings.simplefilter('ignore', category=DeprecationWarning)
    from Bio.Blast import NCBIXML
    from Bio import SeqIO
    from Bio.Seq import Seq
    from Bio.SeqRecord import SeqRecord


# Configure logging system for the entire application
# This sets up a centralized logging system that will be used throughout the pipeline
logging.basicConfig(
    # Set minimum log level to INFO (INFO, WARNING, ERROR, CRITICAL will be shown)
    level=logging.INFO,
    # Format: timestamp - level - message
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'  # Date format: YYYY-MM-DD HH:MM:SS
)
# Create a logger instance for this module
# This allows us to use logger.info(), logger.error(), etc. throughout the code
logger = logging.getLogger(__name__)


class Blaster():
    def __init__(self, inputfile, database, output, threads, minid=90, mincov=60, blast_type='blastn'):
        self.inputfile = os.path.abspath(inputfile)
        self.database = database
        self.minid = int(minid)
        self.mincov = int(mincov)
        self.temp_output = os.path.join(os.path.abspath(output), 'temp.xml')
        self.threads = threads
        self.blast_type = blast_type

    def biopython_blast(self):
        hsp_results = {}
        # biopython no longer support the NcbiblastnCommandline
        # replace NcbiblastnCommandline using subprocess with blastn

        # cline = NcbiblastnCommandline(query=self.inputfile, db=self.database, dust='no',
        #                               evalue=1E-20, out=self.temp_output, outfmt=5,
        #                               perc_identity=self.minid, max_target_seqs=50000,
        #                               num_threads=self.threads)
        # print(cline)
        # print(self.temp_output)
        if self.blast_type == 'blastn':
            cline = [self.blast_type, '-query', self.inputfile, '-db', self.database,
                     '-dust', 'no', '-evalue', '1E-20', '-out', self.temp_output,
                     '-outfmt', '5', '-perc_identity', str(
                         self.minid), '-max_target_seqs', '50000',
                     '-num_threads', str(self.threads)]
        elif self.blast_type == 'blastx':
            cline = [self.blast_type, '-query', self.inputfile, '-db', self.database,
                     '-evalue', '1E-20', '-out', self.temp_output,
                     '-outfmt', '5', '-max_target_seqs', '50000',
                     '-num_threads', str(self.threads)]
        else:
            print('Wrong blast type, exit ...')
            sys.exit(1)

        # stdout, stderr = cline()
        # print(cline)

        # Run the command using subprocess
        result = subprocess.run(
            cline, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Capture the output and error
        stdout = result.stdout
        stderr = result.stderr

        # Print or handle the output and error as needed
        # print(stdout)
        # if stderr:
        #     print(f"Error: {stderr}")

        if result.returncode != 0:
            error_msg = f"Command failed: {' '.join(cline)}\nStderr: {stderr}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        result_handler = open(self.temp_output)

        blast_records = NCBIXML.parse(result_handler)
        df_final = pd.DataFrame()

        # solve local variable referenced before assignment
        loop_check = 0
        save = 0

        for blast_record in blast_records:

            # if blast_record.alignments:
            #     print("QUERY: %s" % blast_record.query)
            # else:
            #     for alignment in blast_record.alignments:
            for alignment in blast_record.alignments:
                for hsp in alignment.hsps:
                    strand = 0

                    query_name = blast_record.query
                    # print(query_name)
                    # print(alignment.title)
                    target_gene = alignment.title.partition(' ')[2]

                    # Get gene name and accession number from target_gene
                    gene = target_gene.split('___')[0]
                    accession = target_gene.split('___')[2]
                    classes = target_gene.split('___')[3]  # 增加种类
                    # print(classes)
                    # print(target_gene)
                    sbjct_length = alignment.length  # The length of matched gene
                    # print(sbjct_length)
                    sbjct_start = hsp.sbjct_start
                    sbjct_end = hsp.sbjct_end
                    gaps = hsp.gaps  # gaps of alignment
                    query_string = str(hsp.query)  # Get the query string
                    sbjct_string = str(hsp.sbjct)
                    identities_length = hsp.identities  # Number of indentity bases
                    # contig_name = query.replace(">", "")
                    query_start = hsp.query_start
                    query_end = hsp.query_end
                    # length of query sequence
                    query_length = len(query_string)

                    # calculate identities
                    perc_ident = (int(identities_length)
                                  / float(query_length) * 100)
                    IDENTITY = "%.2f" % perc_ident
                    # print("Identities: %s " % perc_ident)

                    # coverage = ((int(query_length) - int(gaps))
                    #             / float(sbjct_length))
                    # print(coverage)

                    perc_coverage = (((int(query_length) - int(gaps))
                                      / float(sbjct_length)) * 100)
                    COVERAGE = "%.2f" % perc_coverage

                    # print("Coverage: %s " % perc_coverage)

                    # cal_score is later used to select the best hit
                    cal_score = perc_ident * perc_coverage

                    # Calculate if the hit is on minus strand
                    if sbjct_start > sbjct_end:
                        temp = sbjct_start
                        sbjct_start = sbjct_end
                        sbjct_end = temp
                        strand = 1
                        query_string = str(
                            Seq(str(query_string)).reverse_complement())
                        sbjct_string = str(
                            Seq(str(sbjct_string)).reverse_complement())

                    if strand == 0:
                        strand_direction = '+'
                    else:
                        strand_direction = '-'

                    if perc_coverage >= self.mincov and perc_ident >= self.minid:
                        loop_check += 1
                        hit_id = "%s:%s_%s:%s" % (
                            query_name, query_start, query_end, target_gene)
                        # print(hit_id)
                        # hit_id = query_name
                        # print(hit_id)
                        best_result = {
                            'FILE': os.path.basename(self.inputfile),
                            'SEQUENCE': query_name,
                            'GENE': gene,
                            'START': query_start,
                            'END': query_end,
                            'SBJSTART': sbjct_start,
                            'SBJEND': sbjct_end,
                            'STRAND': strand_direction,
                            # 'COVERAGE':
                            'GAPS': gaps,
                            "%COVERAGE": COVERAGE,
                            "%IDENTITY": IDENTITY,
                            # 'DATABASE':
                            'ACCESSION': accession,
                            'CLASSES': classes,
                            'QUERY_SEQ': query_string,
                            'SBJCT_SEQ': sbjct_string,
                            'cal_score': cal_score,
                            'remove': 0
                            # 'PRODUCT': target_gene,
                            # 'RESISTANCE': target_gene
                        }
                        # print(best_result)

                        # solve local variable referenced before assignment
                        if best_result:
                            save = 1

                            if hsp_results:
                                tmp_results = hsp_results
                                save, hsp_results = Blaster.filter_results(
                                    save, best_result, tmp_results)

                    if save == 1:
                        hsp_results[hit_id] = best_result
        # close file handler, then remove temp file
        result_handler.close()
        os.remove(self.temp_output)
        # print(self.inputfile)
        if loop_check == 0:
            df = pd.DataFrame(columns=['FILE', 'SEQUENCE', 'GENE', 'START', 'END', 'SBJSTART',
                                       'SBJEND', 'STRAND', 'GAPS', '%COVERAGE', '%IDENTITY', 'ACCESSION', 'CLASSES'])
        else:
            df = Blaster.resultdict2df(hsp_results)
        # print(hsp_results)
        return df, hsp_results

    @staticmethod
    def process_row(row: pd.Series, mincov: float) -> Tuple[str, int]:
        """Process a single row of the blast results DataFrame.

        Args:
            row: DataFrame row containing blast results
            mincov: Minimum coverage threshold

        Returns:
            Tuple of (gene, result) or None if no match
        """
        try:
            gene, num = re.match('^(\w+)[_-](\d+)', row['sseqid']).group(1, 2)
            num = int(num)
            hlen = row['slen']
            alen = row['length']
            nident = row['nident']

            if nident * 100 / hlen < mincov:
                return None

            if hlen == alen and nident == hlen:  # exact match
                return (gene, num)
            elif alen == hlen and nident != hlen:  # new allele
                return (gene, f'~{num}')
            elif alen != hlen and nident == hlen:  # partial match
                return (gene, f'{num}?')
            return None
        except (AttributeError, ValueError):
            return None

    @staticmethod
    def merge_results(current_result: Dict, new_gene: str, new_value: any) -> bool:
        """Merge new results with existing results.

        Returns:
            bool: True if the result was merged, False if it was skipped
        """
        if new_gene not in current_result:
            return True

        if isinstance(new_value, int):  # exact match
            if not re.search(r'[~\?]', str(current_result[new_gene])):
                old_num = int(current_result[new_gene])
                if new_value < old_num:
                    print(
                        f'Found additional allele match, replace {new_gene}:{old_num} -> {new_value}')
                    return True
                else:
                    print(
                        f'Found additional allele match, but the allele number {new_value} is greater or equal to stored one {new_gene}:{old_num}, skip...')
            else:  # replace not perfect match
                return True
        return False

    def process_blast_results(self, df: pd.DataFrame) -> Dict:
        """Process blast results using multiple threads.

        Args:
            df: DataFrame containing blast results

        Returns:
            Dictionary containing processed results
        """
        result = {}

        # Create a thread pool
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            # Process rows in parallel
            future_to_row = {
                executor.submit(Blaster.process_row, row, self.mincov): row
                for _, row in df.iterrows()
            }

            # Collect results
            for future in as_completed(future_to_row):
                processed_result = future.result()
                if processed_result is None:
                    continue

                gene, value = processed_result
                if Blaster.merge_results(result, gene, value):
                    result[gene] = value

        return result

    def mlst_blast(self):
        cline = [self.blast_type, '-query', self.inputfile, '-db', self.database, '-dust', 'no', '-ungapped',
                 '-word_size', '32', '-evalue', '1E-20', '-out', self.temp_output,
                 '-outfmt', '6 sseqid slen length nident', '-perc_identity', str(
                     self.minid),
                 '-max_target_seqs', '1000000',
                 '-num_threads', str(self.threads)]

        # print(cline)

        # Run the command using subprocess
        cline_result = subprocess.run(
            cline, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Capture the output and error
        stdout = cline_result.stdout
        stderr = cline_result.stderr

        # Print or handle the output and error as needed
        # print(stdout)
        # if stderr:
        #     print(f"Error: {stderr}")
        if cline_result.returncode != 0:
            error_msg = f"Command failed: {' '.join(cline)}\nStderr: {stderr}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        df = pd.read_csv(self.temp_output, sep='\t', names=[
            'sseqid', 'slen', 'length', 'nident'])
        # print(df)

        result = Blaster.process_blast_results(self, df)

        # Remove temp blastn output file
        os.remove(self.temp_output)
        return result

    @ staticmethod
    def filter_results(save, best_result, tmp_results):
        """
        remove the best hsp with coverage lt mincov
        参考bn的耐药基因过滤
        """

        new_query_name = best_result['SEQUENCE']
        new_query_start = best_result['START']
        new_query_end = best_result['END']
        new_sbjct_start = best_result['SBJSTART']
        new_sbjct_end = best_result['SBJEND']
        coverage = best_result['%COVERAGE']
        new_cal_score = best_result['cal_score']
        new_gene = best_result["GENE"]
        # print(new_gene)
        keys = list(tmp_results.keys())

        for hit in keys:
            remove_old = 0
            hit_data = tmp_results[hit]
            old_query_name = hit_data['SEQUENCE']
            if new_query_name == old_query_name:
                old_query_start = hit_data['START']
                old_query_end = hit_data['END']
                old_sbjct_start = hit_data['SBJSTART']
                old_sbjct_end = hit_data['SBJEND']
                old_cal_score = hit_data['cal_score']
                old_gene = hit_data['GENE']
                # print(old_gene)
                hit_union_length = (max(old_query_end, new_query_end)
                                    - min(old_query_start, new_query_start))
                hit_lengths_sum = ((old_query_end - old_query_start)
                                   + (new_query_end - new_query_start))
                overlap_len = (hit_lengths_sum - hit_union_length)

                if overlap_len <= 0:  # two genes without overlap, save all of them
                    continue
                # solve bug
                # else:  # tow genes with overlap
                #     if (old_query_start == new_query_start) and (old_query_end == new_query_end):
                #         if new_gene == old_gene:
                #             if new_cal_score > old_cal_score:
                #                 remove_old = 1
                #             elif new_cal_score == old_cal_score:
                #                 save = 1
                #             else:
                #                 save = 0
                #         else:
                #             save = 1
                #     elif (old_query_start != new_query_start) or (old_query_end != new_query_end):
                #         if new_gene == old_gene:
                #             if new_cal_score > old_cal_score:
                #                 remove_old = 1
                #             elif new_cal_score == old_cal_score:
                #                 save = 1
                #             else:
                #                 save = 0
                #         else:
                #             save = 1
                #     else:
                #         pass
                else:  # two genes with overlap
                    if (old_query_start == new_query_start) and (old_query_end == new_query_end):
                        if new_cal_score > old_cal_score:
                            remove_old = 1
                        elif new_cal_score == old_cal_score:
                            if new_gene == old_gene:
                                save = 0
                            else:
                                save = 1
                        else:
                            save = 0
                    elif (old_query_start != new_query_start) or (old_query_end != new_query_end):
                        if new_cal_score > old_cal_score:
                            remove_old = 1
                        elif new_cal_score == old_cal_score:
                            save = 1
                        else:
                            save = 0
                    else:
                        pass
            if remove_old == 1:
                del tmp_results[hit]
        return save, tmp_results

    @staticmethod
    def resultdict2df(result_dict):
        df_final = pd.DataFrame()
        col_dict = {'FILE': '',
                    'SEQUENCE': '',
                    'GENE': '',
                    'START': '',
                    'END': '',
                    'SBJSTART': '',
                    'SBJEND': '',
                    'STRAND': '',
                    'GAPS': '',
                    "%COVERAGE": '',
                    "%IDENTITY": '',
                    'ACCESSION': '',
                    'CLASSES': '',
                    'QUERY_SEQ': '',
                    'SBJCT_SEQ': '',
                    'cal_score': '',
                    'remove': ''}
        if len(result_dict.keys()) == 0:
            df_final = pd.DataFrame.from_dict(col_dict, orient='index')
        else:
            for key in result_dict.keys():
                hit_data = result_dict[key]
                df_tmp = pd.DataFrame.from_dict(hit_data, orient='index')
                df_final = pd.concat([df_final, df_tmp], axis=1)
        df_result = df_final.T
        df_result = df_result.drop(
            labels=['QUERY_SEQ', 'SBJCT_SEQ', 'cal_score', 'remove'], axis=1)
        return df_result

    @staticmethod
    def makeblastdb(file, name, db_type='nucl'):

        # cline = NcbimakeblastdbCommandline(
            # dbtype="nucl", out=name, input_file=file)
        # replace NcbimakeblastdbCommandline with makeblastdb command
        command = ['makeblastdb', '-hash_index', '-dbtype',
                   str(db_type), '-out', name, '-in', file]
        # print(command)
        logger.info(f"Making {name} database...")
        result = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # stdout, stderr = cline()
        # Capture the output and error
        stdout = result.stdout
        stderr = result.stderr
        # Print or handle the output and error as needed
        # print(stdout)
        if result.returncode != 0:
            error_msg = f"Command failed: {' '.join(command)}\nStderr: {stderr}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        logger.info(f'Finish creating {name} database')

    @staticmethod
    def get_arg_seq(file_base, result_dict, out_path):
        """
        save gene sequence
        """
        nucl_records = []
        prot_records = []
        prot_file = file_base + 'ARGs_prot.fasta'
        nucl_file = file_base + 'ARGs_nucl.fasta'
        prot_path = os.path.join(out_path, prot_file)
        nucl_path = os.path.join(out_path, nucl_file)
        if len(result_dict.keys()) == 0:
            logger.info(f'No ARGs were found in {file_base}...')
        else:
            for key in result_dict.keys():
                hit_data = result_dict[key]
                # file = os.path.splitext(str(hit_data['FILE']))[0]
                # outfile = os.path.join(
                # out_path, file + str('_ARGs_nucl.fasta'))
                nucl_sequence = Seq(str(hit_data['QUERY_SEQ']))
                trim = len(nucl_sequence) % 3
                if trim != 0:
                    nucl_sequence = nucl_sequence + Seq('N' * (3 - trim))
                prot_sequence = nucl_sequence.replace('-', 'N').translate(
                    table=11, to_stop=True, gap='-')

                id = str(hit_data['SEQUENCE'] +
                         '_' + hit_data['GENE']) + str('_' + hit_data['ACCESSION'])
                name = str(hit_data['ACCESSION'])

                nucl_record = SeqRecord(nucl_sequence,
                                        id=id,
                                        name=name,
                                        description='')
                nucl_records.append(nucl_record)

                prot_record = SeqRecord(prot_sequence,
                                        id=id,
                                        name=name,
                                        description='')
                prot_records.append(prot_record)

            SeqIO.write(nucl_records, nucl_path, 'fasta')
            SeqIO.write(prot_records, prot_path, 'fasta')

    @staticmethod
    def is_fasta(file):
        """
        chcek if the input file is fasta format
        """
        try:
            with open(file, "r") as handle:
                fasta = SeqIO.parse(handle, "fasta")
                # False when `fasta` is empty, i.e. wasn't a FASTA file
                return any(fasta)
        except:
            logger.error(f'The input file {file} is not a valid fasta file.')
            return False
