# IntelX visualization

Script gathers information about leaks for particular domain in IntelX and present it on a tree view graph.

# Installation
```
git clone
pip install -r requirements.txt
```

Add your IntelX API key on line 25

# Usage
```
└─# python3 intelx_viz.py -h           
usage: intelx_viz.py [-h] [--phonebook PHONEBOOK] [--search SEARCH]

Quick search with Intelx

optional arguments:
  -h, --help            show this help message and exit
  --phonebook PHONEBOOK
                        Set the domain for phonebook
  --search SEARCH       Set the domain to search

Usage: intelx_viz.py --phonbebook 'sejm.pl'
```

# Detailed usage

## Step 1

Run script to obtain email addresses for your target. 
```
└─# python3 intelx_viz.py --phonebook mon.gov.pl
[i] Checking mon.gov.pl in Phonebook
[*] [REDACTED]@mon.gov.pl
[*] [REDACTED]@mon.gov.pl
...
[*] [REDACTED]@mon.gov.pl
Results have been saved to mon.gov.pl_emails.txt
```

File with emails inside will be saved to "mon.gov.pl_emails.txt"

## Step 2

Previously collected emails will be checked against given domain and information about leaks & emails extracted.
```
└─# python3 intelx_viz.py --search mon.gov.pl                                                                                                                                              2 ⨯
[*] Checking leaks for wiosnabiedronia.pl
[*] Found [REDACTED] records
[i] Checking 1
[*] Found domain mon.gov.pl
...
[i] Checking 31
[*] Found email [REDACTED]@mon.gov.pl
[i] Checking 32
[*] Found email [REDACTED]@mon.gov.pl
[*] JSON has been saved to mon.gov.pl.json
[*] Creating new html file for mon.gov.pl
[*] HTML has been saved to mon.gov.pl.html
[*] Creating viz for mon.gov.pl
[*] JSON for visualization have been saved to graph_json.json
[*] You can now run 'python3 -m http.server' and check the viz
```

## Step 3
Run webserver with Python
```
python3 -m http.server
```

Go to localhost:8000 and check graph.html
Also, HTML page is generated and named "mon.gov.pl.html"

For each new run, graph_json.json will be overwritten.

# Screenshots

## Viz
![](https://www.offensiveosint.io/content/images/2021/07/image-12.png)

![](https://www.offensiveosint.io/content/images/2021/07/image-13.png)

# HTML
![](https://www.offensiveosint.io/content/images/2021/07/image-14.png)
