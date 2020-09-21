import pickle
import pandas as pd

from search.models import GSEAScore
from django.core.management.base import BaseCommand

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('input_file', type=str)

    def handle(self, **options):

        df = pd.read_csv(options['input_file'], sep='\t')
        relateddocuments = [
            GSEAScore(
                cmap_instance = row['cmap_instance'],
                drugbank_id = row['drugbank_id'],
                name = row['name'],
                dose = row['dose'],
                cell_line = row['cell_line'],
                mers1_es = row['mers1_es'],
                mers1_p = row['mers1_p'],
                sars1_es = row['sars1_es'],
                sars1_p = row['sars1_p'],
                sars2_es = row['sars2_es'],
                sars2_p = row['sars2_p']
            )
            for _, row in df.iterrows()
        ]

        GSEAScore.objects.bulk_create(relateddocuments)
        self.stdout.write(self.style.SUCCESS('Successfully init GSEAScore'))