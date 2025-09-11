import gzip
from bamurai.utils import smart_open
import logging
from itertools import zip_longest

def get_hto(args):
    """
    Extracts HTO information from 10x FASTQ files.
    """
    r1_file = args.r1
    r2_file = args.r2
    barcode_len = args.bc_len
    umi_len = args.umi_len
    output_file = args.output
    hashtag_len = args.hashtag_len
    hashtag_left_buffer = args.hashtag_left_buffer

    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        level=logging.INFO
    )
    logging.info(f"Starting HTO extraction")
    logging.info(f"R1 file: {r1_file}")
    logging.info(f"R2 file: {r2_file}")
    logging.info(f"Barcode length: {barcode_len}, UMI length: {umi_len}, Hashtag length: {hashtag_len}, Hashtag left buffer: {hashtag_left_buffer}")
    logging.info(f"Output file: {output_file}")

    r1_open = gzip.open if r1_file.endswith('.gz') else open
    r2_open = gzip.open if r2_file.endswith('.gz') else open

    with r1_open(r1_file, 'rt') as f_r1, r2_open(r2_file, 'rt') as f_r2:
        with smart_open(output_file, 'wt', encoding='utf-8') as out_f:
            out_f.write("read_name\tcell_barcode\tumi\thto\tbc_qual\tumi_qual\thto_qual\n")
            read_count = 0
            log_interval = 100_000

            while True:
                r1_lines = [f_r1.readline() for _ in range(4)]
                r2_lines = [f_r2.readline() for _ in range(4)]
                if not r1_lines[0] or not r2_lines[0]:
                    break

                read_name = r1_lines[0].strip().split()[0][1:]  # Remove '@' and take first word
                r1_seq = r1_lines[1].strip()
                r2_seq = r2_lines[1].strip()
                r1_qual = r1_lines[3].strip()
                r2_qual = r2_lines[3].strip()

                cell_barcode = r1_seq[:barcode_len]
                umi = r1_seq[barcode_len:(barcode_len + umi_len)]
                hto = r2_seq[hashtag_left_buffer:(hashtag_left_buffer + hashtag_len)]

                # Quality extraction and average calculation
                bc_qual_str = r1_qual[:barcode_len]
                umi_qual_str = r1_qual[barcode_len:(barcode_len + umi_len)]
                hto_qual_str = r2_qual[hashtag_left_buffer:(hashtag_left_buffer + hashtag_len)]

                def avg_qual(qstr):
                    if not qstr:
                        return 0
                    return round(sum(ord(c) - 33 for c in qstr) / len(qstr), 2)

                bc_qual = avg_qual(bc_qual_str)
                umi_qual = avg_qual(umi_qual_str)
                hto_qual = avg_qual(hto_qual_str)

                out_f.write(f"{read_name}\t{cell_barcode}\t{umi}\t{hto}\t{bc_qual}\t{umi_qual}\t{hto_qual}\n")
                read_count += 1
                if read_count % log_interval == 0:
                    logging.info(f"Processed {read_count} reads...")
                    if log_interval == 100_000 and read_count >= 1_000_000:
                        log_interval = 1_000_000
                    elif log_interval == 1_000_000 and read_count >= 10_000_000:
                        log_interval = 10_000_000

            logging.info(f"Finished HTO extraction. Total reads processed: {read_count}")
