import pickle

from search.models import NHIDrugInfo
from django.core.management.base import BaseCommand

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('input_file_date', type=str)

    def handle(self, **options):

        input_file_date = options['input_file_date']

        with open('search/model_data/nhidruginfo_init_{}.pickle'.format(input_file_date), 'rb') as f:
            insert_data = pickle.load(f)

        i = 0
        batch_size = 10000
        while i < len(insert_data):
            nhidruginfos = [
                NHIDrugInfo(
                    new_mark = row['new_mark'], 
                    oral = row['oral'],
                    single_or_compound = row['single_or_compound'],
                    code = row['code'],
                    price = row['price'],
                    price_start_date = row['price_start_date'],
                    price_end_date = row['price_end_date'],
                    english_name = row['english_name'],
                    volume = row['volume'],
                    unit = row['unit'],
                    main_ingredient_name = row['main_ingredient_name'],
                    main_ingredient_volume = row['main_ingredient_volume'],
                    main_ingredient_unit = row['main_ingredient_unit'],
                    dosage = row['dosage'],
                    company_name = row['company_name'],
                    category_code = row['category_code'],
                    quality_category_code = row['quality_category_code'],
                    chinese_name = row['chinese_name'],
                    category_name = row['category_name'],
                    second_ingredient_name = row['second_ingredient_name'],
                    second_ingredient_volume = row['second_ingredient_volume'],
                    second_ingredient_unit = row['second_ingredient_unit'],
                    third_ingredient_name = row['third_ingredient_name'],
                    third_ingredient_volume = row['third_ingredient_volume'],
                    third_ingredient_unit = row['third_ingredient_unit'],
                    fourth_ingredient_name = row['fourth_ingredient_name'],
                    fourth_ingredient_volume = row['fourth_ingredient_volume'],
                    fourth_ingredient_unit = row['fourth_ingredient_unit'],
                    fifth_ingredient_name = row['fifth_ingredient_name'],
                    fifth_ingredient_volume = row['fifth_ingredient_volume'],
                    fifth_ingredient_unit = row['fifth_ingredient_unit'],
                    sixth_ingredient_name = row['sixth_ingredient_name'],
                    sixth_ingredient_volume = row['sixth_ingredient_volume'],
                    sixth_ingredient_unit = row['sixth_ingredient_unit'],
                    production_company = row['production_company'],
                    atc_code = row['atc_code'],
                    less_than_five_year = row['less_than_five_year'],
                )
                for row in insert_data[i:i+batch_size]
            ]
            NHIDrugInfo.objects.bulk_create(nhidruginfos)
            self.stdout.write(self.style.SUCCESS('Insert NHIDrugInfo from row {} to row {}.'.format(i, i+batch_size)))
            i += batch_size

        self.stdout.write(self.style.SUCCESS('Successfully init NHIDrugInfo'))




        

        
        