import pickle
import pandas as pd

from search.models import DrugScreening
from django.core.management.base import BaseCommand

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('input_file', type=str)

    def handle(self, **options):

        df = pd.read_csv(options['input_file'], sep='\t')
        relateddocuments = [
            DrugScreening(
                drugbank_id = row['drugbank_id'],
                name = row['name'],
                z_score_pan = row['z_score_pan'],
                z_score_sars = row['z_score_sars'],
                z_score_mers = row['z_score_mers'],
                z_score_ibv = row['z_score_ibv'],
                z_score_mhv = row['z_score_mhv'],
                p_value_pan = row['p_value_pan'],
                p_value_sars = row['p_value_sars'],
                p_value_mers = row['p_value_mers'],
                p_value_ibv = row['p_value_ibv'],
                p_value_mhv = row['p_value_mhv']
            )
            for _, row in df.iterrows()
        ]

        DrugScreening.objects.bulk_create(relateddocuments)
        self.stdout.write(self.style.SUCCESS('Successfully init DrugScreening'))