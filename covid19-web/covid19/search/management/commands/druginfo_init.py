import pickle

from search.models import DrugInfo
from django.core.management.base import BaseCommand

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('input_file_date', type=str)

    def handle(self, **options):

        def to_int(s):
            try:
                result = int(s)
            except:
                result = 0
            return result

        def to_float(s):
            try:
                result = float(s)
            except:
                result = 0.0
            return result

        input_file_date = options['input_file_date']

        with open('search/model_data/druginfo_init_{}.pickle'.format(input_file_date), 'rb') as f:
            insert_data = pickle.load(f)

        druginfos = []
        for row in insert_data:
            if 'metadata' in row:
                druginfos.append(
                    DrugInfo(
                        cid = to_int(row['cid']),
                        cas = row['cas'],
                        drug_name = row['drug_name'],
                        drug_synonyms = row['drug_synonyms'],
                        popular_views = to_int(row['popular_views']),
                        drug_source = row['drug_source'],
                        drugbank_id = row['drugbank_id'],
                        show = row['show'],
                        inchi = row['metadata']['InChI'],
                        inchikey = row['metadata']['InChIKey'],
                        smiles = row['metadata']['SMILES'],
                        chembl_id = row['metadata']['ChEMBL ID'],
                        chembl4303805_activities = to_float(row['metadata']['ChEMBL4303805 activities']),
                        chembl4303819_activities = to_float(row['metadata']['ChEMBL4303819 activities']),
                        chembl4303810_activities = to_float(row['metadata']['ChEMBL4303810 activities']),
                        chembl_smiles = row['metadata']['ChEMBL SMILES'],
                        formula = row['metadata']['Formula'],
                        kegg_compound_id = row['metadata']['KEGG Compound ID'],
                        kegg_drug_id = row['metadata']['KEGG Drug ID'],
                        drugbank_smiles = row['metadata']['DrugBank SMILES'],
                        pert_iname = row['metadata']['pert_iname'],
                        clinical_phase = row['metadata']['clinical_phase'],
                        moa = row['metadata']['moa'],
                        target = row['metadata']['target'],
                        disease_area = row['metadata']['disease_area'],
                        indication = row['metadata']['indication'],
                        canonical_smiles = row['metadata']['Canonical_SMILES'],
                        num_hdonors = to_int(row['metadata']['num_hdonors']),
                        num_hacceptors = to_int(row['metadata']['num_hacceptors']),
                        mol_weight = to_float(row['metadata']['mol_weight']),
                        mol_logp = to_float(row['metadata']['mol_logp']),

                        rotatable_bonds = to_int(row['metadata']['rotatable_bonds']),
                        number_of_atoms = to_int(row['metadata']['number_of_atoms']),
                        molar_refractivity = to_float(row['metadata']['molar_refractivity']),
                        topological_surface_area_mapping = to_float(row['metadata']['topological_surface_area_mapping']),
                        formal_charge = to_float(row['metadata']['formal_charge']),
                        heavy_atoms = to_int(row['metadata']['heavy_atoms']),
                        num_of_rings = to_int(row['metadata']['num_of_rings']),

                        num_active_fragments = to_int(row['metadata']['num_active_fragments']),
                        active_fragments = row['metadata']['active_fragments']
                    )
                )
            else:
                druginfos.append(
                    DrugInfo(
                        cid = row['cid'],
                        cas = row['cas'],
                        drug_name = row['drug_name'],
                        drug_synonyms = row['drug_synonyms'],
                        popular_views = row['popular_views'],
                        drug_source = row['drug_source'],
                        drugbank_id = row['drugbank_id'],
                        show = row['show']
                    )
                )

        DrugInfo.objects.bulk_create(druginfos)
        self.stdout.write(self.style.SUCCESS('Successfully init DrugInfo'))