install:
	pip install -r requirements.txt
	python setup.py develop

sandbox: install
	-rm -f sandbox/db.sqlite
	sandbox/manage.py syncdb --noinput
	sandbox/manage.py migrate
	sandbox/manage.py loaddata sandbox/fixtures/auth.json countries.json
	sandbox/manage.py oscar_import_catalogue sandbox/fixtures/catalogue.csv

coverage:
	py.test --cov oscar_sagepay --cov-report html tests/
