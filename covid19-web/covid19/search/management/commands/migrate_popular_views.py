from search.models import DrugInfo, CidProteinScore, Score
from django.core.management.base import BaseCommand
from django.db.models import Q

class Command(BaseCommand):
    def handle(self, **options):

        score = Score.objects.filter(~Q(popular_views=0)).values('cid', 'popular_views').distinct()

        for s in score:
            cid = s['cid']
            popular_views = s['popular_views']

            if len(DrugInfo.objects.filter(cid=cid)) > 0:
                self.stdout.write(self.style.SUCCESS(cid))
                DrugInfo.objects.filter(cid=cid).update(popular_views=popular_views)
            else:
                self.stdout.write(self.style.WARNING(cid))

        self.stdout.write(self.style.SUCCESS('Successfully update popular_views data from Score to DrugInfo'))