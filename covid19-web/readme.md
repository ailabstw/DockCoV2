# Develop

```sh
apt-get update
apt-get install wget
wget https://repo.anaconda.com/archive/Anaconda3-2020.02-Linux-x86_64.sh
bash Anaconda3-2020.02-Linux-x86_64.sh
pip install django==3.0.4 pymysql==0.9.3 gunicorn==20.0.4

cd covid19
```

### Initialize DB schema
```sh
python manage.py migrate
```
If you got error like this:
```
Traceback (most recent call last):
  File "manage.py", line 21, in <module>
    main()
  File "manage.py", line 17, in main
    execute_from_command_line(sys.argv)
  File "/root/anaconda3/lib/python3.7/site-packages/django/core/management/__init__.py", line 401, in execute_from_command_line
    utility.execute()
  File "/root/anaconda3/lib/python3.7/site-packages/django/core/management/__init__.py", line 377, in execute
    django.setup()
  File "/root/anaconda3/lib/python3.7/site-packages/django/__init__.py", line 24, in setup
    apps.populate(settings.INSTALLED_APPS)
  File "/root/anaconda3/lib/python3.7/site-packages/django/apps/registry.py", line 114, in populate
    app_config.import_models()
  File "/root/anaconda3/lib/python3.7/site-packages/django/apps/config.py", line 211, in import_models
    self.models_module = import_module(models_module_name)
  File "/root/anaconda3/lib/python3.7/importlib/__init__.py", line 127, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
  File "<frozen importlib._bootstrap>", line 1006, in _gcd_import
  File "<frozen importlib._bootstrap>", line 983, in _find_and_load
  File "<frozen importlib._bootstrap>", line 967, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 677, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 728, in exec_module
  File "<frozen importlib._bootstrap>", line 219, in _call_with_frames_removed
  File "/root/anaconda3/lib/python3.7/site-packages/django/contrib/auth/models.py", line 2, in <module>
    from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
  File "/root/anaconda3/lib/python3.7/site-packages/django/contrib/auth/base_user.py", line 47, in <module>
    class AbstractBaseUser(models.Model):
  File "/root/anaconda3/lib/python3.7/site-packages/django/db/models/base.py", line 121, in __new__
    new_class.add_to_class('_meta', Options(meta, app_label))
  File "/root/anaconda3/lib/python3.7/site-packages/django/db/models/base.py", line 325, in add_to_class
    value.contribute_to_class(cls, name)
  File "/root/anaconda3/lib/python3.7/site-packages/django/db/models/options.py", line 208, in contribute_to_class
    self.db_table = truncate_name(self.db_table, connection.ops.max_name_length())
  File "/root/anaconda3/lib/python3.7/site-packages/django/db/__init__.py", line 28, in __getattr__
    return getattr(connections[DEFAULT_DB_ALIAS], item)
  File "/root/anaconda3/lib/python3.7/site-packages/django/db/utils.py", line 207, in __getitem__
    backend = load_backend(db['ENGINE'])
  File "/root/anaconda3/lib/python3.7/site-packages/django/db/utils.py", line 111, in load_backend
    return import_module('%s.base' % backend_name)
  File "/root/anaconda3/lib/python3.7/importlib/__init__.py", line 127, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
  File "/root/anaconda3/lib/python3.7/site-packages/django/db/backends/mysql/base.py", line 37, in <module>
    raise ImproperlyConfigured('mysqlclient 1.3.13 or newer is required; you have %s.' % Database.__version__)
django.core.exceptions.ImproperlyConfigured: mysqlclient 1.3.13 or newer is required; you have 0.9.3.
```
Please go to `/root/anaconda3/lib/python3.7/site-packages/django/db/backends/mysql/base.py`. 
Put a `pass` inside `if` and comment line like this:
```python
if version < (1, 3, 13):
    pass
    # raise ImproperlyConfigured('mysqlclient 1.3.13 or newer is required; you have %s.' % Database.__version__)
```
reference: https://stackoverflow.com/questions/55657752/django-installing-mysqlclient-error-mysqlclient-1-3-13-or-newer-is-required

### Initialize DB data
```sh
# DrugInfo
python manage.py druginfo_init 20200901 

# NHIDrugInfo
python manage.py nhidruginfo_init 20200520 

# CidProteinScore  
python manage.py cidproteinscore_init cidproteinscore_all_protease  
python manage.py cidproteinscore_init cidproteinscore_all_polymerase  
python manage.py cidproteinscore_init cidproteinscore_all_papainlike  
python manage.py cidproteinscore_init cidproteinscore_all_ace2  
python manage.py cidproteinscore_init cidproteinscore_all_spike_rbd  
python manage.py cidproteinscore_init cidproteinscore_all_nucleocapsid  
python manage.py cidproteinscore_init cidproteinscore_all_tmprss2  

# RelatedDocuments
python manage.py relateddocuments_init metadata/related_documents.csv

# DrugScreening
python manage.py drugscreening_init metadata/Drug_screening.tsv

# GSEA Score
python manage.py gseascore_init metadata/GSEA_score.tsv

# Similarity
python manage.py drugsimilarity_init 20200520

```

### Decompress compound structure and docking structure files
```sh
cd covid19/static
tar zxvf compound_structure.tar.gz
tar zxvf docking_structure.tar.gz
```

### Run server
```sh
cd ../
python manage.py runserver
```
http://localhost:8000/drugs