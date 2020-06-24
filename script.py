from pymongo import MongoClient
from time import time
import csv, os, logging

def cleanup(tarName):
    logging.info("[cleanup] Removing the data from MongoDB")
    client.drop_database('test') # Remove the DB from Mongo

    logging.info("[cleanup] Checking for file: "+tarName)
    if os.path.isfile(tarName):
        cmd = 'rm '+tarName
        logging.info("[cleanup] Removing tar file: "+cmd)
        if os.system(cmd)!=0:
            logging.critical("[cleanup] Error when removing tar file")

logging.basicConfig(
    filename='script.log',
    filemode='w', #can do 'a' for append
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s : %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S ",
)

urls = []

with open("urls.txt") as f:
    for l in f:
        url = l.strip()
        urls.append(url)

# Create the output directory if it does not exist
if not os.path.exists('output'):
    os.mkdir('output')
os.chdir('output')

client = MongoClient()

for url in urls:
    date = url[url.index('mongo-dump')+11:url.index('.tar.gz')]
    tarName = url[url.index('mongo-dump'):url.index('.gz')+3]

    if os.path.isfile('people_'+date+'.csv'):
        logging.warning("Skipping URL ("+url+") as people_"+date+".csv file exists")
        continue
    cmd = 'axel -q -n 16 '+url
    logging.info("Starting download: "+cmd)
    if os.system(cmd)!=0: 
        logging.critical("Error in axel | skipping "+url)
        cleanup(tarName)
        continue

    inputDir = tarName[tarName.index('20'):tarName.index('.tar.gz')]
    cmd = 'mkdir '+inputDir+' && tar -C '+inputDir+'/ -xvf '+tarName
    logging.info("Extracting the compressed file: "+cmd)
    if os.system(cmd)!=0: 
        logging.critical("Error when extracting file | skipping "+url)
        cleanup(tarName)
        continue

    cmd = 'rm '+tarName
    logging.info("Removing tar file: "+cmd)
    if os.system(cmd)!=0:
        logging.critical("Error when removing tar file | skipping "+url)
        continue

    logging.info("Deleting `test` db from mongo before we start")
    client.drop_database('test') # Remove the DB from Mongo

    logging.info("Importing data from "+inputDir+'/dump/github/commits.bson')

    # Import Mongo Dump
    cmd = 'mongorestore -d test -c mydatabase '+inputDir+'/dump/github/commits.bson'
    logging.info("Running command: "+cmd)
    if os.system(cmd)!=0: exit()


    db = client['test']
    collection = db['mydatabase']

    people = {}

    start = time()

    num = 0
    for commit in collection.find():
        num+=1
        if 'commit' in commit and 'author' in commit['commit']:
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

        if 'commit' in commit and 'committer' in commit['commit']:
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
            logging.error("Error [in else]")
            break
        
    logging.info(str(num)+" commits processed in "+str(time()-start)+" seconds")

    col = set()
    for v in people.values():
        for k in v.keys():
            col.add(k)
    col = list(col)        

    for e in people:
        for c in col:
            if c not in people[e]:
                people[e][c] = ''

    logging.info("Storing the results in people_"+inputDir+".csv")
    with open('people_'+inputDir+'.csv', 'w', newline='') as csvfile:
        fieldnames = ['name', 'email', 'html_url','organizations_url', 'node_id', 'login', 'id', 'avatar_url', 'events_url', 'followers_url', 'site_admin', 'received_events_url', 'following_url', 'gists_url', 'starred_url', 'type', 'subscriptions_url', 'repos_url', 'url', 'gravatar_id']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for v in people.values():
            writer.writerow(v)

    logging.info("All done, removing the data from MongoDB")
    client.drop_database('test') # Remove the DB from Mongo

    cmd = 'rm -rf '+inputDir
    logging.info("Removing uncompressed directory: "+cmd)
    if os.system(cmd)!=0: 
        logging.critical("Error when removing uncompressed directory | skipping "+url)
        continue
