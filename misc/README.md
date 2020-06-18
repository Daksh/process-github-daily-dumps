## Some of the commands we use (executed using `os` in python)

### Download
`axel -n 16 http://ghtorrent-downloads.ewi.tudelft.nl/mongo-daily/mongo-dump-2019-06-10.tar.gz`

### Extract a Daily Dump (in a folder for that dump)
`mkdir 2019-06-09 && tar -C 2019-06-09/ -xvf mongo-dump-2019-06-09.tar.gz`

### Restructure the extracted dump
`mv 2019-06-09/dump/github/* 2019-06-09/ && rm -rf 2019-06-09/dump`

### Import data in mongoDB
`mongorestore -d db_name -c collection_name /path/file.bson` ([Ref](https://stackoverflow.com/a/27310491))

`mongorestore -d test -c mydatabase dump/github/commits.bson`

### Extract our data
`python3 script.py > out.log`
 
### Cleanup
`rm -r dump/`
`mongo`
