import pickle
import pandas as pd

from search.models import RelatedDocuments
from django.core.management.base import BaseCommand

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('input_file', type=str)

    def handle(self, **options):

        df = pd.read_csv(options['input_file'])
        relateddocuments = [
            RelatedDocuments(
                cid = row['PubChem CID'],
                titles = row['Titles'],
                urls = row['URLs']
            )
            for _, row in df.iterrows()
        ]

        RelatedDocuments.objects.bulk_create(relateddocuments)
        self.stdout.write(self.style.SUCCESS('Successfully init RelatedDocuments'))