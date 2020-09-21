import pickle

from search.models import DrugInfo, CidProteinScore
from django.core.management.base import BaseCommand

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('command', type=str)
        parser.add_argument('output_file', type=str)

    def handle(self, *args, **options):

        command = options['command']
        output_file = options['output_file']

        if command == 'cidproteinscore_cid_protein_type':
            results = list(CidProteinScore.objects.select_related().values('drug__cid', 'protein_type'))

            results_by_cid = {}
            for r in results:
                if str(r['drug__cid']) in results_by_cid:
                    results_by_cid[str(r['drug__cid'])].append(r['protein_type'])
                else:
                    results_by_cid[str(r['drug__cid'])] = [r['protein_type']]

            with open(output_file, 'wb') as f:
                pickle.dump(results_by_cid, f, protocol=pickle.HIGHEST_PROTOCOL)

        self.stdout.write(self.style.SUCCESS('Successfully output {} to {}'.format(command, output_file)))
