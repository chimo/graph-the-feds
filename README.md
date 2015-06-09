Graph the Feds
==================

This script crawls FOAF files from GNU social profiles and attempts to graph
the connections between instances and users.

## Requirements

Python 2 (tested with 2.7.10)
tldextract (tested with 1.6)
rdflib (tested with 4.2.0)

## Usage

Give the script a profile to start crawling and it'll go on from there.  
Optionally give it a maximum number of FOAF files to fetch and parse (defaults to 5).

`python2 ./graph.py http://example.org/profile --max=5`

To stop the script before it reached "max", press Ctrl+C. The script should terminate
gracefully and generate a .gexf file with the data it had time to collect.

Once the data collection is done, run the following to convert the data to json:  
`python2 ./extlib/InteractiveVis/server/gexf2Json.py out/graph.gexf out/data.json`

To see the graph, open ./out/index.html in your browser.

## Demo

You can find an example of the results here: http://sandbox.chromic.org/graph/out/index.html  
The script fetched approximately 55 FOAFs to generate that graph.

## Note

This is a work-in-progress. I don't know python that well. Pull-requests welcome!

