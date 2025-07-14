# rel2bib

Convert Relaton YAML file to BibXML

## Setting up

```
pip install -r requirements.txt
```

## RFC BibXML

* Clone RFC relaton data
```
git clone --depth 1  https://github.com/ietf-tools/relaton-data-rfcs.git
```

* Generate BibXML files
```
python rfc.py
```

## Internet-Draft BibXML

* Clone I-D relaton data
```
git clone --depth 1  https://github.com/ietf-tools/relaton-data-ids.git
```

* Generate BibXML files
```
python id.py
```

## IANA BibXML

* Clone IANA relaton data
```
git clone --depth 1  https://github.com/ietf-tools/relaton-data-iana.git
```

* Generate BibXML files
```
python iana.py
```
