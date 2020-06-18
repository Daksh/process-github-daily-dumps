from pymongo import MongoClient
from time import time
import csv, os

urls = []

with open("urls.txt") as f:
    for l in f:
        url = l.strip()
        urls.append(url)

client = MongoClient()

for url in urls:
    date = url[url.index('mongo-dump')+11:url.index('.tar.gz')]
    if os.path.isfile(date+'.csv'):
        print("Skipping URL ("+url+") as",date+'.csv',"file exists")
        continue
    cmd = 'axel -n 16 '+url
    print("Starting download:",cmd)
    if os.system(cmd)!=0: exit()

    tarName = url[url.index('mongo-dump'):url.index('.gz')+3]
    inputDir = tarName[tarName.index('20'):tarName.index('.tar.gz')]
    cmd = 'mkdir '+inputDir+' && tar -C '+inputDir+'/ -xvf '+tarName
    print("Extracting the compressed file:",cmd)
    if os.system(cmd)!=0: exit()

    cmd = 'rm '+tarName
    print("Removing tar file:",cmd)
    if os.system(cmd)!=0: exit()


    print("Deleting `test` db from mongo before we start")
    client.drop_database('test') # Remove the DB from Mongo
    print()

    print("Importing data from",inputDir+'/dump/github/commits.bson')

    # Import Mongo Dump
    cmd = 'mongorestore -d test -c mydatabase '+inputDir+'/dump/github/commits.bson'
    print("Running command:",cmd)
    if os.system(cmd)!=0: exit()


    db = client['test']
    collection = db['mydatabase']

    people = {}

    start = time()

    num = 0
    for commit in collection.find():
        num+=1
        if 'author' in commit['commit']:
            email = commit['commit']['author']['email']
            name = commit['commit']['author']['name']

            if 'author' in commit and commit['author']!=None:
                author = commit['author']
            else:
                author = {}

            author['email'] = email
            author['name'] = name

            if ('noreply.github' not in email) and email not in people:
                people[ email ] = author

        if 'committer' in commit['commit']:
            email = commit['commit']['committer']['email']
            name = commit['commit']['committer']['name']

            if 'committer' in commit and commit['committer']!=None:
                committer = commit['committer']
            else:
                committer = {}

            committer['email'] = email
            committer['name'] = name

            if ('noreply.github' not in email) and email not in people:
                people[ email ] = committer
        else:
            print("Error in else", commit)
            break
        
    print(num,"commits processed in",time()-start,"seconds")

    col = set()
    for v in people.values():
        for k in v.keys():
            col.add(k)
    col = list(col)        

    for e in people:
        for c in col:
            if c not in people[e]:
                people[e][c] = ''

    print("Storing the results in",'people_'+inputDir+'.csv')
    with open('people_'+inputDir+'.csv', 'w', newline='') as csvfile:
        fieldnames = ['name', 'email', 'html_url','organizations_url', 'node_id', 'login', 'id', 'avatar_url', 'events_url', 'followers_url', 'site_admin', 'received_events_url', 'following_url', 'gists_url', 'starred_url', 'type', 'subscriptions_url', 'repos_url', 'url', 'gravatar_id']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for v in people.values():
            writer.writerow(v)

    print("\nAll done, removing the data from MongoDB\n")
    client.drop_database('test') # Remove the DB from Mongo

    cmd = 'rm -rf '+inputDir
    print("Removing uncompressed directory:",cmd)
    if os.system(cmd)!=0: exit()

    print('\n')
