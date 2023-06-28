

import argparse
import json

from AutoSurvey.pdf_generation.pdf_generator import PDFGenerator

def main():
    parser = argparse.ArgumentParser(description='Generate PDF from JSON')
    parser.add_argument('-i', '--input', dest='input', help='Input JSON file')
    parser.add_argument('-o', '--output', dest='output', help='Output PDF file')
    args = parser.parse_args()

    with open(args.input, "r") as fin:
        sections_data=json.load(fin)

    PDFGenerator.generate_pdf( sections_data, output_file=args.output, with_subsections=True)


main()