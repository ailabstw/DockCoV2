import pickle

from search.models import DrugSimilarity, DrugInfo
from django.core.management.base import BaseCommand

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('input_file_date', type=str)

    def handle(self, **options):

        input_file_date = options['input_file_date']

        with open('search/model_data/drugsimilarity_init_{}.pickle'.format(input_file_date), 'rb') as f:
            insert_data = pickle.load(f)


        drugsimilaritys = []
        for idx, row in enumerate(insert_data):
            # if row['dice_similarity_score'] < 0.7:
            #     continue

            if idx % 1000000 == 0:
                self.stdout.write('{}/{}'.format(idx, len(insert_data)))
                DrugSimilarity.objects.bulk_create(drugsimilaritys)
                drugsimilaritys = []

            obj = DrugSimilarity(drug1_cid=row['drug1'], drug2_cid=row['drug2'], dice_similarity_score=row['dice_similarity_score'])
            drugsimilaritys.append(obj)

        DrugSimilarity.objects.bulk_create(drugsimilaritys)

        self.stdout.write(self.style.SUCCESS('Successfully init DrugSimilarity'))