.PHONY: test status demo private-site published clean

PYTHON ?= python3

test:
	$(PYTHON) -m unittest discover -s tests -v

status:
	$(PYTHON) scripts/pipeline.py status

demo:
	$(PYTHON) scripts/build_site.py --demo --out dist

private-site:
	$(PYTHON) scripts/build_site.py --private --out private/site

published:
	$(PYTHON) scripts/build_site.py --published --out dist

clean:
	rm -rf dist private/site
