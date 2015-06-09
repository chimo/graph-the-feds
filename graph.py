# CLI arguments
import argparse

# Utils
import sys
import signal
import tldextract
from Queue import Queue
from urlparse import urlparse
from collections import Counter

# Graph
from extlib.gexf import Gexf

# RDF to parse FOAF
from rdflib import URIRef, Graph, Namespace
from rdflib.namespace import FOAF
from rdflib.plugins.sparql import prepareQuery

def parse(foaf_url):
    global gexf_graph
    global parsedFOAFS
    global queuedFOAFS

    g = Graph()

    try:
        g.load(foaf_url)
    except Exception:
        print "Can't fetch " + foaf_url
        return

    SIOC = Namespace("http://rdfs.org/sioc/ns#")

    acctID = URIRef(g.value(URIRef(foaf_url), FOAF.maker) + "#acct")
    root_accountName = str(g.value(acctID, FOAF.accountName))
    root_webfinger = root_accountName + "@" + urlparse(foaf_url).hostname

    subscriptions = prepareQuery(
        """SELECT ?accountName ?accountProfilePage
           WHERE {
              ?person sioc:follows ?b .
              ?b foaf:accountName ?accountName .
              ?b foaf:accountProfilePage ?accountProfilePage .
           }""",
        initNs = { "foaf": FOAF, "sioc": SIOC })

    subscribers = prepareQuery(
        """SELECT ?accountName ?accountProfilePage
           WHERE {
              ?b sioc:follows ?person .
              ?b foaf:accountName ?accountName .
              ?b foaf:accountProfilePage ?accountProfilePage .
           }""",
        initNs = { "foaf": FOAF, "sioc": SIOC })

    gexf_graph.addNode(root_webfinger, root_webfinger)

    for subscription in g.query(subscriptions, initBindings={'person': acctID}):
        accountProfilePage = str(subscription.accountProfilePage) + "/foaf"
        accountName = str(subscription.accountName)
        if (blacklisted(accountProfilePage) is False):
            hostname = urlparse(accountProfilePage).hostname
            webfinger = accountName + "@" + hostname
            gexf_graph.addNode(webfinger, webfinger)
            gexf_graph.addEdge(root_webfinger + webfinger, root_webfinger, webfinger)
            if accountProfilePage not in parsedFOAFS:
                queuedFOAFS.put(accountProfilePage)

    for subscriber in g.query(subscribers, initBindings={'person': acctID}):
        accountProfilePage = str(subscriber.accountProfilePage) + "/foaf"
        accountName = str(subscriber.accountName)
        if (blacklisted(accountProfilePage) is False):
            hostname = urlparse(accountProfilePage).hostname
            webfinger = accountName + "@" + hostname
            gexf_graph.addNode(webfinger, webfinger)
            gexf_graph.addEdge(webfinger + root_webfinger, root_webfinger, webfinger)
            if accountProfilePage not in parsedFOAFS:
                queuedFOAFS.put(accountProfilePage)

def blacklisted(url):
    blacklisted = ["identi.ca", "status.net"]
    extracted = tldextract.extract(url)
    hostname = "{}.{}".format(extracted.domain, extracted.suffix)

    if hostname in blacklisted:
        print "Ignoring: " + url
        return True
    else:
        return False

# Write graph and exit
def terminate(a, b):
    output_file = open("out/graph.gexf", "w")
    gexf.write(output_file)

    output_file.close()

    print("Done")
    sys.exit(0)

# CLI Arguments
parser = argparse.ArgumentParser()
parser.add_argument("profile_url")
parser.add_argument("-m", "--max", default=5)
args = parser.parse_args()

# Init things
parsedFOAFS = {}
queuedFOAFS = Queue()
max_foafs = args.max
gexf = Gexf("Test", "Testing things")
gexf_graph = gexf.addGraph("directed", "static", "Still testing stuff")

signal.signal(signal.SIGINT, terminate)
queuedFOAFS.put(args.profile_url + "/foaf")

# Start parsing
while ((queuedFOAFS.empty() is not True) and (len(parsedFOAFS) <= max_foafs)):
    print str(len(parsedFOAFS)) + " of " + str(max_foafs)
    curr = queuedFOAFS.get()
    parsedFOAFS[curr] = True
    parse(curr)

terminate("a", "b")

