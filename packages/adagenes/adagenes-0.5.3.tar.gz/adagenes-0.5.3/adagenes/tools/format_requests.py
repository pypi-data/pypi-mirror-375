import os, gzip, traceback


def vcf_to_bed(file_path, cnvs_only=False):
    """
    Converts a file in Variant Call Format (VCF) into a Browser Extensible Data (BED) file.
    The CNV end position must be available as an END feature in the INFO column.
    If the SVTYPE feature is available in the INFO column, it will be included in the generated BED file.

    :param infile:
    :param cnvs_only: Includes only copy number variants (CNVs) in the output file if set to true, i.e. variants that
            include <DEL> or <DUP> in the ALT column
    :return:
    """
    if file_path.endswith('.vcf.gz'):
        outfile_src = file_path[:-7] + '.bed'
    elif file_path.endswith('.vcf'):
        outfile_src = file_path[:-4] + '.bed'
    else:
        raise ValueError("Unsupported file format. Only .vcf and .vcf.gz are supported.")


    file_name, file_extension = os.path.splitext(file_path)
    input_format_recognized = file_extension.lstrip(".")

    if input_format_recognized == "gz":
        infile = gzip.open(file_path, 'rt')
    else:
        infile = open(file_path, 'r')

    outfile = open(outfile_src, "w")

    for line in infile:
        try:
            if line.startswith('##'):
                continue
            elif line.startswith('#CHROM'):
                continue

            fields = line.strip().split('\t')
            chromosome, pos, ref_base, alt_base = fields[0], fields[1], fields[3], fields[4]
            info = fields[7]
            chr_prefix = ""
            if not chromosome.startswith("chr"):
                chr_prefix = "chr"

            # CNVs
            change = ""
            pos2 = ""
            if alt_base == "<DEL>" or alt_base == "<DUP>":
                info_features = info.split(";")
                for feature in info_features:
                    elements = feature.split("=")
                    if len(elements) > 1:
                        key = elements[0]
                        if key == "END":
                            pos2 = elements[1]
                            alt_base = pos2 + alt_base
                        elif key == "SVTYPE":
                            change = elements[1]

            # TODO inversions, translocations

            if pos2 != "":
                bed_line = f"{chromosome}\t{pos}\t{pos2}\t{change}"
                print(bed_line, file=outfile)


        except:
            print("VCF reader: Error parsing line ", line)
            print(traceback.format_exc())

    outfile.close()
    infile.close()

    print("Generated BED file: ", outfile_src)

def separate_unidentified_snvs(annotated_data):
    """
    Separates gene names and protein change that could not be identified by the Coordinates Converter

    :param annotated_data:
    :return:
    """
    snvs = {}
    unidentified_snvs = {}
    for var in annotated_data.keys():
        identified = True
        if "status" in annotated_data[var]["variant_data"]:
            if annotated_data[var]["variant_data"]["status"] == "error":
                identified = False

        if identified:
            annotated_data[var]["mutation_type"] = "snv"
        else:
            annotated_data[var]["mutation_type"] = "unidentified"

    return annotated_data
