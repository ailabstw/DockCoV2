from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, JsonResponse, Http404
from django.views import View
from django.db.models import F, Q
from django.db.models.aggregates import Max
from django.core import serializers
from django import forms
from .models import DrugScreening, GSEAScore, DrugInfo, CidProteinScore, NHIDrugInfo, RelatedDocuments, DrugSimilarity
import math
import json
from datetime import date
import os
from itertools import chain

NUM_PER_PAGE = 10
PROTEIN = {
    'protease': '3CLpro',
    'polymerase': 'RdRp', 
    'helicase': 'Helicase',
    'ace2': 'ACE2',
    'papainlike': 'PLpro',
    'spike_rbd': 'spike RBD',
    'nucleocapsid': 'N protein',
    'tmprss2': 'TMPRSS2',
}

class SearchForm(forms.Form):
    """form for search
    """
    term = forms.CharField(max_length=50, initial='', required=False)
    protein_type = forms.CharField(max_length=50, initial='', required=False)
    drug_source = forms.CharField(max_length=50, initial='', required=False)
    page = forms.IntegerField(initial=1, required=False)

class DetailForm(forms.Form):
    """form for detail
    """
    cid = forms.CharField(max_length=50, initial='', required=False)
    protein_type = forms.CharField(max_length=50, initial='', required=False)

class TopListForm(forms.Form):
    """form for filter
    """
    protein_type = forms.CharField(max_length=50, initial='', required=False)
    sort_by = forms.CharField(max_length=50, initial='', required=False)
    rows = forms.IntegerField(initial=10, required=False)

class DownloadForm(forms.Form):
    """form for download
    """
    task = forms.CharField(max_length=10, initial='', required=False)
    cid = forms.CharField(max_length=50, initial='', required=False)
    protein_type = forms.CharField(max_length=50, initial='', required=False)
    file_name = forms.CharField(max_length=50, initial='', required=False)

class Index(View):
    """index page view
    """
    def get(self, request):
        """handle get request
        """

        # Get top 10 list order by -popular_views
        protein_num = CidProteinScore.objects.values('protein_type').distinct().count()
        score_list = CidProteinScore.objects.select_related().filter(drug__show=True).order_by('-drug__popular_views', 'docking_score')[:int(protein_num * 20)]

        top10 = {}
        for s in score_list:
            if s.drug.drug_name in top10:
                if s.docking_score < top10[s.drug.drug_name].docking_score:
                    top10[s.drug.drug_name] = s
            else:
                top10[s.drug.drug_name] = s

        protein_type = CidProteinScore.objects.values('protein_type').distinct()

        data = {
            'score_list': list(top10.values())[:10],
            'protein_type': protein_type,
            'protein': PROTEIN,
            'detail': {'pose_score': {}},
        }


        return render(request, 'index.html', data)

class Search(View):
    """search page view
    """
    def get(self, request):
        """handle get request
        """
        form = SearchForm(request.GET)
        if not form.is_valid():
            return render(request, 'search.html', {})

        page = int(form.cleaned_data['page']) if form.cleaned_data['page'] != None else 1
        protein_type = form.cleaned_data['protein_type'] if form.cleaned_data['protein_type'] != None else ''
        drug_source = form.cleaned_data['drug_source'] if form.cleaned_data['drug_source'] != None else ''

        # get search result
        start_pointer = (page - 1) * NUM_PER_PAGE
        end_pointer = page * NUM_PER_PAGE

        # query drug_name first
        search_filter = Q(drug__show=True)

        if form.cleaned_data['term'].isdigit():
            # search by cid
            search_filter = search_filter & Q(drug__cid=form.cleaned_data['term'])
        else:
            # search by keyword
            search_filter = search_filter & Q(drug__drug_name__istartswith=form.cleaned_data['term'])
        
        if protein_type != '':
            search_filter = search_filter & Q(protein_type=protein_type)
        if drug_source != '':
            if drug_source == 'nhi':
                search_filter = search_filter & Q(drug__drug_source__icontains='nhi')
            else:
                search_filter = search_filter & (Q(drug__drug_source__icontains='l4200') | Q(drug__drug_source__icontains='fda'))
        drug_name_search_list = CidProteinScore.objects.select_related().filter(search_filter).order_by('docking_score').values('drug__cid', 'drug__drug_name', 'docking_score', 'protein_type', 'drug__drug_source', 'drug__cas')

        # then query drug_synonyms
        search_filter = Q(drug__show=True)

        if not form.cleaned_data['term'].isdigit():
            # search by keyword
            search_filter = search_filter & Q(drug__drug_synonyms__icontains=form.cleaned_data['term']) & ~Q(drug__drug_name__istartswith=form.cleaned_data['term'])
        
            if protein_type != '':
                search_filter = search_filter & Q(protein_type=protein_type)
            if drug_source != '':
                if drug_source == 'nhi':
                    search_filter = search_filter & Q(drug__drug_source__icontains='nhi')
                else:
                    search_filter = search_filter & (Q(drug__drug_source__icontains='l4200') | Q(drug__drug_source__icontains='fda'))
            drug_synonyms_search_list = CidProteinScore.objects.select_related().filter(search_filter).order_by('docking_score').values('drug__cid', 'drug__drug_name', 'docking_score', 'protein_type', 'drug__drug_source', 'drug__cas')

            search_list = list(chain(drug_name_search_list, drug_synonyms_search_list))

        else:
            search_list = drug_name_search_list

        total_cnt = len(search_list)
        search_list = search_list[start_pointer:end_pointer]

        # add one for each search
        cid_list = [element['drug__cid'] for element in search_list]
        DrugInfo.objects.filter(cid__in=cid_list).update(popular_views=F('popular_views') + 1)

        protein_type = CidProteinScore.objects.values('protein_type').distinct()

        for s in search_list:
            if '/' in s['drug__cas']:
                tmp_1, tmp_2, tmp_3 = s['drug__cas'].split('/')
                tmp_1 = tmp_1 if not tmp_1.startswith('19') else tmp_1[2:]
                tmp_2 = '0' + tmp_2 if len(tmp_2) == 1 else tmp_2
                s['drug__cas'] = '{}-{}-{}'.format(tmp_1, tmp_2, tmp_3) 

        data = {
            'search_list': search_list,
            'protein': PROTEIN,
            'protein_type': protein_type,
            'total_cnt': total_cnt,
            'form': form,
            'current_page': page,
            'max_page': math.ceil(total_cnt / NUM_PER_PAGE),
            'page_offset': start_pointer,
            'detail': {'pose_score': {}},
        }

        return render(request, 'search.html', data)

class Detail(View):
    """detail page
    """
    def get(self, request):
        form = DetailForm(request.GET)
        if not form.is_valid():
            return render(request, 'detail.html', {})

        query_list = CidProteinScore.objects.select_related().filter(drug__cid=form.cleaned_data['cid'], protein_type=form.cleaned_data['protein_type'], drug__show=True)

        # get detail data
        detail = {}
        detail['pose_score'] = {}

        if query_list:
            drug = query_list[0]
            if '/' in drug.drug.cas:
                tmp_1, tmp_2, tmp_3 = drug.drug.cas.split('/')
                tmp_1 = tmp_1 if not tmp_1.startswith('19') else tmp_1[2:]
                tmp_2 = '0' + tmp_2 if len(tmp_2) == 1 else tmp_2
                drug.drug.cas = '{}-{}-{}'.format(tmp_1, tmp_2, tmp_3)

            detail['drug'] = drug
            drugbank_id = drug.drug.drugbank_id
            detail['pubchem'] = drug.drug.cid

            
            # Taiwan NHI data
            detail['taiwannhi'] = {}
            today = date.today()
            year = str(int(today.strftime('%Y')) - 1911)
            month = str(today.strftime('%m'))
            day = str(today.strftime('%d'))
            detail['todaydate'] = year + month + day

            name_list = [drug.drug.drug_name.upper(), drug.drug.drug_name.lower(), drug.drug.drug_name]
            nhi_filter = (
                            Q(main_ingredient_name__icontains=name_list[0]) | 
                            Q(second_ingredient_name__icontains=name_list[0]) | 
                            Q(third_ingredient_name__icontains=name_list[0]) | 
                            Q(fourth_ingredient_name__icontains=name_list[0]) | 
                            Q(fifth_ingredient_name__icontains=name_list[0]) | 
                            Q(sixth_ingredient_name__icontains=name_list[0])
                        )
            for name in name_list[1:]:
                nhi_filter = nhi_filter | (
                        Q(main_ingredient_name__icontains=name) | 
                        Q(second_ingredient_name__icontains=name) | 
                        Q(third_ingredient_name__icontains=name) | 
                        Q(fourth_ingredient_name__icontains=name) | 
                        Q(fifth_ingredient_name__icontains=name) | 
                        Q(sixth_ingredient_name__icontains=name)
                    )
            detail['taiwannhi'][drug.drug.cid] = NHIDrugInfo.objects.filter(nhi_filter)

            # Drug Screening
            detail['drugscreening'] = DrugScreening.objects.filter(drugbank_id=drugbank_id)

            # GSEA score
            detail['gseascore'] = GSEAScore.objects.filter(drugbank_id=drugbank_id)

            # Related document
            related_documents = RelatedDocuments.objects.filter(cid=drug.drug.cid)
            detail['relateddocuments'] = []
            for rd in related_documents:
                for title, link in zip(rd.titles.split(';'), rd.urls.split(';')):
                    detail['relateddocuments'].append({'title': title, 'link': link})

            # DrugLikeness
            # rule of 5
            detail['ruleof5'] = {
                'final_call': 'VIOLATED',
                'failed_rule': []
            }

            if drug.drug.num_hdonors > 5:
                detail['ruleof5']['failed_rule'].append('More than 5 hydrogen bond donors. ({})'.format(drug.drug.num_hdonors))
            if drug.drug.num_hacceptors > 10:
                detail['ruleof5']['failed_rule'].append('More than 10 hydrogen bond acceptors. ({})'.format(drug.drug.num_hacceptors))
            if drug.drug.mol_weight >= 500:
                detail['ruleof5']['failed_rule'].append('Molecular mass is over 500 daltons. ({:.2f})'.format(drug.drug.mol_weight))
            if drug.drug.mol_logp >= 5:
                detail['ruleof5']['failed_rule'].append('Octanol-water partition coefficient (log P) exceeds 5. ({:.2f})'.format(drug.drug.mol_logp))

            if not detail['ruleof5']['failed_rule']:
                detail['ruleof5']['final_call'] = 'PASS'
                detail['ruleof5']['failed_rule'].append('-')

            # Ghose filter
            detail['ghose'] = {
                'final_call': 'VIOLATED',
                'failed_rule': []
            }
            # - 480 >= molecular weight >= 160
            if drug.drug.mol_weight > 480:
                detail['ghose']['failed_rule'].append('Molecular mass is over 480 daltons. ({:.2f})'.format(drug.drug.mol_weight))
            if drug.drug.mol_weight < 160:
                detail['ghose']['failed_rule'].append('Molecular mass is lower than 160 daltons. ({:.2f})'.format(drug.drug.mol_weight))
            # - 5.6 >= logp >= 0.4
            if drug.drug.mol_logp > 5.6:
                detail['ghose']['failed_rule'].append('Octanol-water partition coefficient (log P) exceeds 5.6. ({:.2f})'.format(drug.drug.mol_logp))
            if drug.drug.mol_logp < 0.4:
                detail['ghose']['failed_rule'].append('Octanol-water partition coefficient (log P) does not exceed 0.4. ({:.2f})'.format(drug.drug.mol_logp))
            # - 70 >= number_of_atoms >= 20
            if drug.drug.number_of_atoms > 70:
                detail['ghose']['failed_rule'].append('Atom count is over 70. ({:.2f})'.format(drug.drug.number_of_atoms))
            if drug.drug.number_of_atoms < 20:
                detail['ghose']['failed_rule'].append('Atom count is lower than 20. ({:.2f})'.format(drug.drug.number_of_atoms))
            # - 130 >= molar_refractivity >= 40
            if drug.drug.molar_refractivity > 130:
                detail['ghose']['failed_rule'].append('Molar refractivity exceeds 130. ({:.2f})'.format(drug.drug.molar_refractivity))
            if drug.drug.molar_refractivity < 40:
                detail['ghose']['failed_rule'].append('Molar refractivity does not exceed 40. ({:.2f})'.format(drug.drug.molar_refractivity))

            if not detail['ghose']['failed_rule']:
                detail['ghose']['final_call'] = 'PASS'
                detail['ghose']['failed_rule'].append('-')


            # Veber filter
            detail['veber'] = {
                'final_call': 'VIOLATED',
                'failed_rule': []
            }
            # - rotatable_bonds <= 10
            if drug.drug.rotatable_bonds > 10:
                detail['veber']['failed_rule'].append('More than 10 rotatable bonds. ({:.2f})'.format(drug.drug.rotatable_bonds))

            # - topological_surface_area_mapping <= 140:
            if drug.drug.topological_surface_area_mapping > 140:
                detail['veber']['failed_rule'].append('Topological polar surface area exceeds 140. ({:.2f})'.format(drug.drug.topological_surface_area_mapping))

            if not detail['veber']['failed_rule']:
                detail['veber']['final_call'] = 'PASS'
                detail['veber']['failed_rule'].append('-')

            # ROES filter
            detail['roes'] = {
                'final_call': 'VIOLATED',
                'failed_rule': []
            }
            # - 500 >= molecular_weight >= 200
            if drug.drug.mol_weight > 480:
                detail['roes']['failed_rule'].append('Molecular mass is over 500 daltons. ({:.2f})'.format(drug.drug.mol_weight))
            if drug.drug.mol_weight < 160:
                detail['roes']['failed_rule'].append('Molecular mass is lower than 200 daltons. ({:.2f})'.format(drug.drug.mol_weight))
            # - 5 >= logp >= 0
            if drug.drug.mol_logp > 5:
                detail['roes']['failed_rule'].append('Octanol-water partition coefficient (log P) exceeds 5. ({:.2f})'.format(drug.drug.mol_logp))
            if drug.drug.mol_logp < 0:
                detail['roes']['failed_rule'].append('Octanol-water partition coefficient (log P) does not exceed 0. ({:.2f})'.format(drug.drug.mol_logp))
            # - 5 >= h_bond_donor >= 0
            if drug.drug.num_hdonors > 5:
                detail['roes']['failed_rule'].append('More than 5 hydrogen bond donors. ({})'.format(drug.drug.num_hdonors))
            if drug.drug.num_hdonors < 0:
                detail['roes']['failed_rule'].append('Lower than 0 hydrogen bond donors. ({})'.format(drug.drug.num_hdonors))
            # - 10 >= h_bond_acceptors >= 0
            if drug.drug.num_hacceptors > 10:
                detail['roes']['failed_rule'].append('More than 10 hydrogen bond acceptors. ({})'.format(drug.drug.num_hacceptors))
            if drug.drug.num_hacceptors < 0:
                detail['roes']['failed_rule'].append('Lower than 0 hydrogen bond acceptors. ({})'.format(drug.drug.num_hacceptors))
            # - 2 >= formal_charge
            if drug.drug.formal_charge > 2:
                detail['roes']['failed_rule'].append('Drug formal charge exceeds 2. ({})'.format(drug.drug.formal_charge))
            # - 8 >= rotatable_bonds >= 0
            if drug.drug.rotatable_bonds > 8:
                detail['roes']['failed_rule'].append('More than 10 rotatable bonds. ({:.2f})'.format(drug.drug.rotatable_bonds))
            if drug.drug.rotatable_bonds < 0:
                detail['roes']['failed_rule'].append('Lower than 0 rotatable bonds. ({:.2f})'.format(drug.drug.rotatable_bonds))
            # - 50 >= heavy_atoms >= 15
            if drug.drug.heavy_atoms > 50:
                detail['roes']['failed_rule'].append('More than 50 heavy atoms. ({:.2f})'.format(drug.drug.heavy_atoms))
            if drug.drug.heavy_atoms < 15:
                detail['roes']['failed_rule'].append('Lower than 15 heavy atoms. ({:.2f})'.format(drug.drug.heavy_atoms))

            if not detail['roes']['failed_rule']:
                detail['roes']['final_call'] = 'PASS'
                detail['roes']['failed_rule'].append('-')

            # similarity
            detail['similarity'] = DrugSimilarity.objects.filter(drug1_cid=drug.drug.cid)

            # different poses data
            file_path = os.path.join(settings.STATIC_ROOT, 'docking_structure', form.cleaned_data['cid'], form.cleaned_data['protein_type'], 'log.txt')

            pose_score = {}
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                flag = False
                
                for line in lines:
                    if line == '-----+------------+----------+----------\n':
                        flag = True
                        continue
                    if line == 'Writing output ... done.\n':
                        break
                    if flag:
                        elements = line.split()
                        pose_score[elements[0]] = elements[1]
            detail['pose_score'] = pose_score

        data = {
            'detail': detail,
            'protein': PROTEIN,
        }

        return render(request, 'detail.html', data)

class DrugList(View):
    """drug list search
    """

    def get(self, request):  # pylint: disable=unused-argument
        """get
        """
        drug_list = [d['drug_synonyms'].split(';') for d in DrugInfo.objects.filter(show=True).values('drug_synonyms').distinct()]
        drug_list = [item for sublist in drug_list for item in sublist]

        data = {
            'data': {
                'symbols': drug_list,
            },
        }
        return HttpResponse(json.dumps(data), content_type="application/json")

class Downloads(View):
    """download page
    """
    def get(self, request):

        download_list = [
            {'title': 'Proteins (.pdbqt)',
            'description': 'All protein structure files, including ACE2, spike protein, 3C-like protease (3CLpro), RNA-dependent RNA polymerase (RdRp), Papain-like protease (PLpro), nucleocapsid (N) protein, human angiotensin-converting enzyme 2 (ACE2) and transmembrane serine protease family member II (TMPRSS2).',
            'filename': 'protein.tar.gz',
            },
            {'title': 'Ligands (.pdbqt)',
            'description': 'All ligand structure files and position information with best docking pose (best docking score).',
            'filename': 'best_pose.tar.gz',
            },
            {'title': 'Ligands with all poses (.pdbqt)',
            'description': 'All ligand structure files and position information with all docking poses.',
            'filename': 'all_poses.tar.gz',
            }

        ]

        data = {
            'download_list': download_list,
        }

        return render(request, 'downloads.html', data)


class DownloadFile(View):
    """download pdbqt
    """

    def get(self, request):
        form = DownloadForm(request.GET)

        if not form.is_valid():
            raise Http404

        if form.cleaned_data['task'] == "ligand":
            file_path = os.path.join(settings.STATIC_ROOT, 'docking_structure', form.cleaned_data['cid'], form.cleaned_data['protein_type'], 'best.pdbqt')
            if os.path.exists(file_path):
                with open(file_path, 'rb') as fh:
                    response = HttpResponse(fh.read(), content_type="application/octet-stream")
                    response['Content-Disposition'] = 'inline; filename=' + '{}.pdbqt'.format(form.cleaned_data['cid'])
                    return response
        elif form.cleaned_data['task'] == "protein":
            file_path = os.path.join(settings.STATIC_ROOT, 'protein', '{}.pdbqt'.format(form.cleaned_data['protein_type']))
            if os.path.exists(file_path):
                with open(file_path, 'rb') as fh:
                    response = HttpResponse(fh.read(), content_type="application/octet-stream")
                    response['Content-Disposition'] = 'inline; filename=' + '{}.pdbqt'.format(form.cleaned_data['protein_type'])
                    return response
        elif form.cleaned_data['task'] == "file":
            file_path = os.path.join(settings.STATIC_ROOT, 'download_files', '{}'.format(form.cleaned_data['file_name']))
            if os.path.exists(file_path):
                with open(file_path, 'rb') as fh:
                    response = HttpResponse(fh.read(), content_type="application/octet-stream")
                    response['Content-Disposition'] = 'inline; filename=' + '{}'.format(form.cleaned_data['file_name'])
                    return response

        raise Http404

class TopList(View):
    """top list 
    """
    def get(self, request):
        form = TopListForm(request.GET)
        if not form.is_valid():
            return HttpResponse(json.dumps(''), content_type="application/json")

        if form.cleaned_data['sort_by'] == 'docking_score':
            sort_by = 'docking_score'
        elif form.cleaned_data['sort_by'] == 'popular_views':
            sort_by = '-drug__popular_views'

        protein_type = [form.cleaned_data['protein_type']] if form.cleaned_data['protein_type'] != 'all' else list(PROTEIN.keys())
        rows = int(form.cleaned_data['rows'])

        top_list = CidProteinScore.objects.select_related().all().order_by(sort_by).filter(protein_type__in=protein_type, drug__show=True).values('drug__drug_name', 'docking_score', 'protein_type', 'drug__popular_views', 'drug__drug_source')[:rows]

        return JsonResponse(list(top_list), safe=False)

