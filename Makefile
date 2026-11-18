.PHONY: test status audit demo private-site published release clean

PYTHON ?= python3

test:
	$(PYTHON) -m unittest discover -s tests -v

status:
	$(PYTHON) scripts/pipeline.py status

audit:
	$(PYTHON) scripts/pipeline.py audit-git

demo:
	$(PYTHON) scripts/build_site.py --demo --out dist

private-site:
	$(PYTHON) scripts/build_site.py --private --out private/site

published:
	$(PYTHON) scripts/build_site.py --published --out dist
	mkdir -p private && (cd dist && zip -rq ../private/latent-space-cn-site.zip .)

release: test audit published
	git add catalog/ site/ README.md Makefile scripts/ web/ tests/ .github/ .gitignore
	@if ! git diff --cached --quiet; then \
		git commit -m "$${MSG:-Update published essays and catalog}"; \
	fi
	git push -u origin main

clean:
	rm -rf dist private/site
