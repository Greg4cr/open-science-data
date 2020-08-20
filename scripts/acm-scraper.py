#!/usr/bin/env python3

import requests as req

def parsePages(text):
    #papers = [["title","venue","year","citations(acm)","available","reusable","functional","replicated","reproduced"]]
    papers = []

    paper = ["","","","0","0","0","0","0","0"]
    lines = text.split("\n")
    for lNum in range(len(lines)):
        if lines[lNum] == "<!-- END OF XSLT -->":
            if paper[2] == "" or paper[2] == "Unknown":
                print(paper)
            elif int(paper[2]) >= 2017:
                papers.append(paper)
            paper = ["","","","0","0","0","0","0","0"]
        elif "data-title=\"Artifacts Available\"" in lines[lNum]:
            paper[4] = "1"
        elif "data-title=\"Artifacts Evaluated &amp; Reusable\"" in lines[lNum]:
            paper[5] = "1"
        elif "data-title=\"Artifacts Evaluated &amp; Functional\"" in lines[lNum]:
            paper[6] = "1"
        elif "data-title=\"Results Replicated\"" in lines[lNum]:
            paper[7] = "1"
        elif "data-title=\"Results Reproduced\"" in lines[lNum]:
            paper[8] = "1"
        elif "class=\"issue-item__title\"" in lines[lNum]:
            title = lines[lNum].split(">")[3]
              
            # Title may span two lines
            while "</a" not in title:
                lNum += 1
                title = title + " " + lines[lNum].lstrip()

            title = title.replace(",","")
            title = title.replace("\"","")
            title = title.replace("&amp;"," and ")
            paper[0] = title[:title.index("<")]
        elif "<span class=\"citation\">" in lines[lNum]:
            citations = lines[lNum].split(">")[5]
            citations = citations.replace(",","")
            paper[3] = citations[:citations.index("<")]
        elif "class=\"issue-item__detail\">" in lines[lNum]:
            # Conference title and date in same div. Get whole div and then split
            venue = lines[lNum]
            while "</div>" not in venue:
                lNum += 1
                venue = venue + " " + lines[lNum].lstrip()
            
            venueName = venue.split("title=\"")[1]
            paper[1] = venueName[:venueName.index(":")]

            try: 
                year = venue.split("span")[4]
                paper[2] = year[year.index(" ") + 1 : year.index(",")]
            except:
                paper[2] = "Unknown"

    return papers

def numResults(text):
    lines = text.split("\n")
    
    for line in lines:
        if "class=\"result__count\"" in line:
            results = line.split("class=\"result__count\">")[1]
            results = results[:results.index(" Results")]
            results = results.replace(",","")
            return int(results)

    return -1

venue_ids = ["fse","issta","icse","ase"]

papers = [["title","venue","year","citations(acm)","available","reusable","functional","replicated","reproduced"]]

for venue in venue_ids:
    # How many pages do we need to page through? 
    results = req.get("https://dl.acm.org/topic/conference-collections/"+venue+"?pageSize=50")
    howMany = numResults(results.text)

    numPages = int(howMany/50)
    if howMany%50 != 0:
        numPages += 1

    # Parse first page of results (we already got it)
    print("Processing page 1 of " + str(numPages) + " results for " + venue)
    newPapers = parsePages(results.text)
    papers.extend(newPapers)

    # Get each additional page of results and parse
    for page in range(1, numPages):
        print("Processing page " + str(page + 1) + " of " + str(numPages) + " results for " + venue)
        results = req.get("https://dl.acm.org/topic/conference-collections/"+venue+"?pageSize=50&startPage="+str(page))
        newPapers = parsePages(results.text)
        papers.extend(newPapers)

# Print papers to CSV

f = open("output.csv", "w")

for paper in papers:
    f.write(",".join(paper) + "\n")

f.close()
