import pickle

from search.models import DrugInfo, CidProteinScore
from django.core.management.base import BaseCommand

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('input_file', type=str)

    def handle(self, *args, **options):

        input_file = options['input_file']

        with open('search/model_data/{}.pickle'.format(input_file), 'rb') as f:
            insert_data = pickle.load(f)

        cidproteinscores = []
        for row in insert_data:
            self.stdout.write(self.style.SUCCESS(row['cid']))
            druginfo = DrugInfo.objects.get(cid=row['cid'])

            try:
                obj = CidProteinScore.objects.get(drug=druginfo, protein_type=row['protein_type'])
                self.stdout.write(self.style.WARNING("Exists"))
            except CidProteinScore.DoesNotExist:
                obj = CidProteinScore(drug=druginfo, protein_type=row['protein_type'], docking_score=row['docking_score'])
                obj.save()

        self.stdout.write(self.style.SUCCESS('Successfully init CidProteinScore with file {}'.format(input_file)))