import requests
from intelxapi import intelx
import json
import time
import argparse
import json
import re
import bleach

parser = argparse.ArgumentParser(
    description="Quick search with Intelx",
    epilog="Usage: intelx_viz --domain 'sejm.pl'"
)

parser.add_argument('--phonebook', help="Set the domain for phonebook")
parser.add_argument('--search', help="Set the domain to search", type=str)
# parser.add_argument('--input', help="Input from file", action="store_true")

args = parser.parse_args()

phonebook = args.phonebook
# input = args.input
search = args.search

key = "KEY"
intelx = intelx(key, ua='IX Maltego Transform/3')


def phonebooksearch(term, maxresults=1000, buckets=[], timeout=5, datefrom="", dateto="", sort=4, media=0,
                    terminate=[], target=0):
    """
		Conduct a phonebook search based on a search term.
		Other arguments have default values set, however they can be overridden to complete an advanced search.
		"""
    results = []
    done = False
    search_id = intelx.PHONEBOOK_SEARCH(term, maxresults, buckets, timeout, datefrom, dateto, sort, media, terminate,
                                        target)
    if (len(str(search_id)) <= 3):
        print(f"[!] intelx.PHONEBOOK_SEARCH() Received {intelx.get_error(search_id)}")
    while done == False:
        time.sleep(1)  # lets give the backend a chance to aggregate our data
        r = intelx.query_pb_results(search_id, maxresults)
        results.append(r)
        maxresults -= len(r['selectors'])
        if (r['status'] == 1 or r['status'] == 2 or maxresults <= 0):
            if (maxresults <= 0):
                intelx.INTEL_TERMINATE_SEARCH(search_id)
            done = True
    return results


def extractEmails(line):
    match = re.findall(r'[\w\.-]+@[\w\.-]+', line)
    return match


def search(term, maxresults=100000000000000, buckets=[], timeout=5, datefrom="", dateto="", sort=4, media=0,
           terminate=[]):
    results = []
    done = False
    search_id = intelx.INTEL_SEARCH(term, maxresults, buckets, timeout, datefrom, dateto, sort, media, terminate)
    if (len(str(search_id)) <= 3):
        print(f"[!] intelx.INTEL_SEARCH() Received {intelx.get_error(search_id)}")
    while done == False:
        time.sleep(1)  # lets give the backend a chance to aggregate our data
        r = intelx.query_results(search_id, maxresults)
        for a in r['records']:
            results.append(a)
        maxresults -= len(r['records'])
        if (r['status'] == 1 or r['status'] == 2 or maxresults <= 0):
            if (maxresults <= 0):
                intelx.INTEL_TERMINATE_SEARCH(search_id)
            done = True
    return {'records': results}

def make_viz(domain):
    print("[*] Creating viz for " + domain)
    with open(domain + '.json', 'r') as email:
        emails = json.load(email)

    return_dict = {"name": domain, 'children': []}

    for c, i in enumerate(emails):
        helper_to_check_leak_category = []
        if not i == "other":
            c = c - 1
            return_dict['children'].append({"name": i, 'children': []})
            for c2, j in enumerate(emails[i]):
                if j['bucket'] not in helper_to_check_leak_category:
                    try:
                        return_dict['children'][c]['children'].append({"name": j['bucket'], 'children': [
                            {"name": j['name'], 'systemid': j['systemid'], 'line': j['line']}]})
                        helper_to_check_leak_category.append(j['bucket'])
                    except Exception as e:
                        print(str(e))

                else:
                    for c3, k in enumerate(return_dict['children'][c]['children']):
                        if k['name'] == j['bucket']:
                            return_dict['children'][c]['children'][c3]['children'].append(
                                {"name": j['name'], 'systemid': j['systemid'], 'line': j['line']})

                    # return_dict['children'][c]['children'][c2]['children'][c2]['children']
                    helper_to_check_leak_category.append(j['bucket'])
                    pass



    with open('graph_json.json', 'w') as f:
        f.write(json.dumps(return_dict, indent=4))

    print("JSON for visualization have been saved to graph_json.json\n You can now run 'python3 -m http.server' and check the viz")



def make_html(domain):
    print("[*] Creating new html file for " + domain)
    with open(domain + '.json', 'r') as f:
        data = json.load(f)

    html = ""
    for i in data:
        html = html + "<h2>" + i + "</h2>"
        for j in data[i]:
            html = html + "<b>" + j['name'] + "</b>" + "<br>" + "<a href=https://intelx.io/?did=" + j[
                'systemid'] + ">" + bleach.clean(j['line']) + "</a> <br><br>"

    with open(args.search + '.html', 'w') as html_file:
        html_file.write(html)

    print("[*] HTML has been saved to " + args.search + '.html')

if phonebook:
    print("[i] Checking " + phonebook + " in Phonebook")
    results = phonebooksearch(term=phonebook, target=0)
    try:
        with open(phonebook + "_emails.txt", 'w') as emails:
            for selector in results[0]['selectors']:
                if selector['selectorvalue'].startswith("http"):
                    pass
                else:
                    print("[*] " + selector['selectorvalue'])
                    emails.write(selector['selectorvalue'] + "\n")
    except Exception as e:
        print("[*] Can't find " + phonebook + "_emails.txt file")

    print("Results have been saved to " + phonebook+"_emails.txt")



elif search:
    tst = {'other': []}

    t = args.search
    res = search(term=t)

    with open(args.search + "_emails.txt", 'r') as f:
        emails = f.read().splitlines()


    for email in emails:
        tst.update({email: []})
    print('[*] Checking leaks for ' + args.search)
    print("[*] Found " + str(len(res['records'])) + " records")
    for c,i in enumerate(res['records']):
        view = intelx.FILE_VIEW(i['type'], i['media'], i['storageid'], i['bucket'])
        print("[i] Checking " + str(c))
        for line in view.splitlines():
            if t in line.lower():
                ems = extractEmails(line.lower())
                for email in emails:
                    if email in ems:
                        print("[*] Found email " + email)
                        help_dict = {'systemid': i['systemid'], 'bucket': i['bucket'], 'name': i['name'],
                                     'line': line}
                        tst[email].append(help_dict)

                if not ems:
                    print("[*] Found domain " + args.search)
                    help_dict = {'systemid': i['systemid'], 'bucket': i['bucket'], 'name': i['name'], 'line': line}
                    tst['other'].append(help_dict)

    with open(args.search + '.json', 'w') as f:
        f.write(json.dumps(tst, indent=4))

    print("[*] JSON has been saved to "+ args.search + '.json')

    make_html(args.search)

    make_viz(args.search)
