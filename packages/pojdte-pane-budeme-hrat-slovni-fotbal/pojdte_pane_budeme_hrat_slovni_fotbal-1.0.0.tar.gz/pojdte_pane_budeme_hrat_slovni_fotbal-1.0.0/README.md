## **tacrpy**

# NLP version, pokus

Python knihovna, která slouží pro práci s daty a vypracování analýz TA ČR

## Prerekvizity

- Python 3.9+

## Práce s repozitářem

1) Naklonuj si tento repozitář:

   `git clone git@git.tacr.cz:data-team/tacrpy.git`

2) Přejdi do složky _'tacrpy'_

   `cd tacrpy`

3) Vytvoř si virtuální prostředí

   `python -m venv .venv`

4) Aktivuj si virtuální prostředí

   `.venv\Scripts\activate`

5) Nainstaluj požadavky

   `pip install -r requirements.txt`

## Generování dokumentace
### Prerekvizity

- Sphinx (`pip install sphinx`)
- Read The Docs Theme (`pip install sphinx_rtd_theme`)

### Generování dokumentace
1) Naklonuj si tento repozitář:

   `git clone git@git.tacr.cz:data-team/tacrpy.git`
2) Přejdi do adresáře _'docs'_:

   `cd docs`
3) Spusť _'sphinx-apidoc'_ pro vygenerování souborů dokumentace

   `sphinx-apidoc -f -o source ../tacrpy`
4) Pro vygenerování html dokumentace:
   
   `make.bat clean`

   `make.bat html`

5) Vygenerovaná dokumentace se nachází v adresáři _'docs/build/html'_

## Release nové verze knihovny

### Prerekvizity

- Twine (`pip install twine`)
- Účet na PyPI (https://pypi.org/)
- role Owner nebo Maintainer v projektu tacrpy (správce rolí: David Šulc)

### Nový release knihovny
1) Mergni do masteru podle conventional commits (https://www.conventionalcommits.org/en/v1.0.0/)

2) Je třeba v merge requestu změnit commit message

3) Hotovo

### Aktualizace dokumentace na Pypi
1) přihlásím se k dafos serveru na WinSCP

2) vygeneruju dokumentaci

3) nahraju na server všechno kromě build info souboru
