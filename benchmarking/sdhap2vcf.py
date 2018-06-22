#!/usr/bin/python3
import sys, os
import argparse

"""
Transform unphased VCF (input) to phased VCF (output) using phasing results
from SDhaP.
"""

def main():
    parser = argparse.ArgumentParser("build phased VCF from SDhaP output")
    parser.add_argument('--sdhap', dest='sdhap', type=str, required=True)
    parser.add_argument('--vcf', dest='vcf', type=str, required=True)
    parser.add_argument('-o', dest='outfile', type=str, required=True)
    args = parser.parse_args()

    idx2phase = {}
    with open(args.sdhap, 'r') as sdhap:
        block = 0
        for line in sdhap:
            if line[0] == 'B':
                block += 1
                continue
            line = line.split('\t')
            idx = int(line[0])
            haps = [str(int(line[1])-1), str(int(line[2])-1)]
            phase = "|".join(haps)
            idx2phase[idx] = [phase, block]

    # parse through VCF
    # substitute GT field by phased haplotypes
    # add phase set tag

    idx = -1
    unphased = 0
    artifacts = 0
    with open(args.vcf, 'r') as vcf_in:
        with open(args.outfile, 'w') as vcf_out:
            for line in vcf_in:
                if line[0] == '#':
                    # copy header
                    vcf_out.write(line)
                    continue
                idx += 1
                # check genotype field
                format = line.split('\t')[8]
                gt_idx = format.split(':').index('GT')
                data = line.rstrip('\n').split('\t')[9]
                gt = data.split(':')[gt_idx]
                pos = line.split('\t')[1]
                new_line = line.split('\t')[0:8]
                if idx in idx2phase:
                    [phase, block] = idx2phase[idx]
                    if set(gt.split('/')) != set(phase.split('|')):
                        # print(idx, pos, gt, phase, block)
                        artifacts += 1
                    data_split = data.split(':')
                    data_split[gt_idx] = phase
                    data_split.append(str(block))
                    format += ":PS"
                    data = ":".join(data_split)
                else:
                    unphased += 1
                new_line.append(format)
                new_line.append(data)
                vcf_out.write('\t'.join(new_line) + '\n')
    print("{} variants considered".format(idx+1))
    print("{} phased".format(len(idx2phase)))
    print("{} unphased".format(unphased))
    print("{} artifacts".format(artifacts))
    return

if __name__ == '__main__':
    sys.exit(main())