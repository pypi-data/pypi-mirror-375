#!/bin/bash
:<<author
Author: legendzdy@dingtalk.com
Data: 20250718
Description:
This a pipeline of HiChIP from Legendzdy. Of course, this means there is a possibility for other ways. Use at your own discretion.
CMD: nohup legendzdy_neopipeline.sh -c /config.csv -i /inputs -o /outputs -s human -r /reference -p prefix &
author

usage() {
    echo "Usage:"
    echo "  legendzdy_neopipeline.sh [-c/--config /config.csv] [-i/--inputs /inputs] [-o/--outputs /outputs] [-r/--reference /reference] [-s/--species human mouse other] [-p/--prefix prefix]"
    echo "Description:"
    echo "    -c | --config, config file, default: false"
    echo "    -i | --inputs, input dir, default: /inputs"
    echo "    -o | --outputs, output dir, default: /outputs"
    echo "    -r | --reference, reference dir, default: /reference."
    echo "    -s | --species, species [human,mouse,other]."
    echo "    -p | --prefix, prefix of output dir."
    echo "    -h | --help, help info."
    exit 1
}
# set defult
WKD=`pwd`
INPUT=${WKD}/inputs/test
WORKDIR=${WKD}/outputs
REF=${WKD}/reference
CONFIGFILE=/inputs/config.csv

PARSED_ARGUMENTS=$(getopt -a -o c:i:o:r:s:p:h --long config:,inputs:,outputs:,reference:,species:,prefix:,help -- "$@")
if [ $? -ne 0 ]; then usage; exit 1;fi
eval set -- ${PARSED_ARGUMENTS}
while true; do
    case $1 in
        -c|--config)     CONFIGFILE=$2; shift 2;;
        -i|--inputs)     INPUT=$2; shift 2;;
        -o|--outputs)    WORKDIR=$2; shift 2;;
        -r|--reference)  REF=$2; shift 2;;
        -s|--species)    SPECIES=$2; shift 2;;
        -p|--prefix)     PREFIX=$2; shift 2;;
        --)              shift; break;;
        -h|--help)       usage; exit 1;;
        ?)               usage; exit 1;;
    esac
done

echo -e "\e[1;36m run modole start ...... \e[0m"
docker run --rm \
    -v ${INPUT}:/inputs \
    -v ${WORKDIR}:/outputs \
    -v ${REF}:/reference \
    legendzdy/module_start:1.0.0 \
    --config=${CONFIGFILE} 

echo -e "\e[1;36m run neoantigen ...... \e[0m"
NUM=`cat ${WORKDIR}/config/sample|wc -l`
cat ${WORKDIR}/config/sample|xargs -P $NUM -i -t bash -e -c \
"
mkdir -p ${WORKDIR}/01_SNP_calling/{}
chmod 777 ${WORKDIR}/01_SNP_calling/{}
docker run --rm \
    -v ${INPUT}/{}:/inputs \
    -v ${WORKDIR}:/outputs \
    -v ${REF}:/reference-genome \
    legendzdy/neoantigen:1.0.0 \
    --configfile=/inputs/idh1_config.yaml > ${WORKDIR}/log/neoantigen_{}.log
"

echo -e "\e[1;36m run neoantigen ...... \e[0m"

NUM=`cat ${WORKDIR}/config/sample|wc -l`
cat ${WORKDIR}/config/sample|xargs -P $NUM -i -t bash -e -c \
'
mkdir -p '"${WORKDIR}"'/02_SNP_annotated/{}
docker run --rm \
    -v '"${WORKDIR}"'/config/VEP_plugins:/plugins \
    -v '"${INPUT}"':/inputs \
    -v '"${WORKDIR}"':/outputs \
    -v '"${REF}"':/reference \
    ensemblorg/ensembl-vep:latest bash -c \
    "
    vep --input_file /outputs/01_SNP_calling/{}/final.vcf \
        --output_file /outputs/02_SNP_annotated/{}/final.annotated.vcf \
        --format vcf --vcf --symbol --terms SO --tsl --biotype \
        --hgvs --fasta /reference/fasta/genome.fa --offline --cache \
        --plugin Frameshift --plugin Wildtype --pick --transcript_version
    "
'

echo -e "\e[1;36m run vatools count ...... \e[0m"

NUM=`cat ${WORKDIR}/config/sample|wc -l`
cat ${WORKDIR}/config/sample|xargs -P $NUM -i -t bash -e -c \
'
mkdir -p '"${WORKDIR}"'/02_SNP_annotated/{}
docker run --rm \
    -v '"${WORKDIR}"'/config/VEP_plugins:/plugins \
    -v '"${INPUT}"':/inputs \
    -v '"${WORKDIR}"':/outputs \
    -v '"${REF}"':/reference \
    ensemblorg/ensembl-vep:latest bash -c \
    "
    vep --input_file /outputs/01_SNP_calling/{}/final.vcf \
        --output_file /outputs/02_SNP_annotated/{}/final.annotated.vcf \
        --format vcf --vcf --symbol --terms SO --tsl --biotype \
        --hgvs --fasta /reference/fasta/genome.fa --offline --cache \
        --plugin Frameshift --plugin Wildtype --pick --transcript_version
    
    vcf-genotype-annotator <input.vcf> <sample_name> 0/1 -o <gt_annotated.vcf>
    "
'



cat ./config/sample|while read i;
do
sample=$i
docker run --rm \
    -v $(pwd):/sfs \
    griffithlab/vatools:latest bash -c \
    """
    vcf-genotype-annotator /sfs/inputs/20250604_libilian/${sample}.strelka.vcf TUMOR 0/1 -o /sfs/outputs/OUT_20250604_libilian/${sample}.strelka.withGT.vcf
    """

docker run --rm \
    -v $(pwd)/config/VEP_plugins:/plugins \
    -v $(pwd)/reference/vep/homo_sapiens:/opt/vep/.vep/homo_sapiens \
    -v $(pwd):/sfs \
    ensemblorg/ensembl-vep:latest bash -c \
    """
    vep -i /sfs/outputs/OUT_20250604_libilian/${sample}.strelka.withGT.vcf -o /sfs/outputs/OUT_20250604_libilian/${sample}.strelka.vep.vcf --vcf --symbol --terms SO --plugin Wildtype --plugin Downstream --plugin Frameshift --tsl --cache
    """ 

docker run --rm \
    -v $(pwd):/sfs \
    griffithlab/pvactools:latest bash -c \
    """
    # pvacseq generate_protein_fasta /sfs/outputs/OUT_20250604_libilian/${sample}.strelka.vep.vcf 17 /sfs/outputs/OUT_20250604_libilian/${sample}.17_mutant_peptides.txt --sample-name TUMOR
    # pvacseq generate_protein_fasta /sfs/outputs/OUT_20250604_libilian/${sample}.strelka.vep.vcf 29 /sfs/outputs/OUT_20250604_libilian/${sample}.29_mutant_peptides.txt --sample-name TUMOR
    pvacseq generate_protein_fasta /sfs/outputs/OUT_20250604_libilian/${sample}.strelka.vep.vcf 4 /sfs/outputs/OUT_20250604_libilian/${sample}.9_mutant_peptides.txt --sample-name TUMOR
    """ 
done

