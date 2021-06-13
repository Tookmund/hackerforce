# Heroku Backup

This tutorial assumes you have access to a remote always-running Linux x86\_64
machine, like, for example, from your CS Department.


## Authorizing Heroku

Little bit of clarification:
We have Heroku, the service which helps developers deploy their apps.

We also the `heroku` command line command, which is used to interface with the Heroku service.
This is the easiest way to access Heroku the service from a lab machine. Lab machines do not have web browsers
(they're all accessed with the command line). 

By authorizing Heroku, we mean giving accessibility of Heroku the service to a lab machine. We are allowing
access to a specific user in the Heroku service.

This is a little tricky, since you can't necessarily follow the simple step
of `heroku login`, since Heroku will detect the IP address mismatch and
prevent you from continuing.

Instead you need to create a new authorization through the Heroku website
("Account Settings" > "Applications" > "Create authorization")

Then you need to copy the Authorization token and put it in
[`~/.netrc`](https://devcenter.heroku.com/articles/authentication):
```
machine api.heroku.com
	login YOUR@EMAIL
	password AUTHORIZATION_TOKEN
```
You'll want to protect this file with `chmod 600 ~/.netrc` to ensure
no one else can read it (this assumes you trust your system administrators,
of course).

An equivalent command `chmod go-rwx`. Let's break this down:
`g` = group
`o` = owner
`-` = delete
`r` = read access
`w` = write access
`x` = execute access

## Backup Script

Next, put the following in `~/hackerforce-backup.sh`:

```bash
#!/bin/sh
# Script for installing the Heroku CLI and backing up hackerforce
set -e

# Replace with whatever your hackerforce instance is
# e.g. myhackerforce.herokuapp.com would be myhackerforce
HACKERFORCE=MYHACKERFORCE

cd "$HOME"

if [ ! -d heroku ]
then
    HEROKUTAR=heroku-linux-x64.tar.gz
    wget "https://cli-assets.heroku.com/$HEROKUTAR"
    tar xzvf "$HEROKUTAR"
    rm "$HEROKUTAR"
fi
export PATH="$PATH:$HOME/heroku/bin"

heroku update

if [ ! -d hackerforce-backups ]
then
    mkdir hackerforce-backups
    chmod 700 hackerforce-backups
fi

cd hackerforce-backups

heroku run -a "$HACKERFORCE" -- python manage.py dumpdata > "$(date --iso-8601=seconds).json"
```

After that make sure to mark it executable and run it, to make sure it actually
works. If it functions correctly, you should have two new folders: `heroku`
and `hackerforce-backups`, and `hackerforce-backups` should contain a JSON file
with your backups.

## Cron Job

For this to be useful, it has to be run regularly.
This is precisely what cron allows you to do.

Run `crontab -e` and add the following lines:
```
MAILTO=YOUR@EMAIL
7	4	*	*	*	./hackerforce-backup.sh
```
(Note that this technically only works on Debian/Ubuntu-based machines,
because only their version of cron respects environment variables set in
crontabs)

This will backup at 4:07 AM every morning.

Assuming your machine has a working email setup, this will email you once
a day about your backups so you can keep an eye on them.

If you don't care use this instead, without the MAILTO:
```
7	4	*	*	*	./hackerforce-backup.sh > /dev/null 2>&1
```
If you don't add the `/dev/null` bit, Cron will still attempt to send emails,
probably to your local account, which is usually pointless and just takes up
space.

## Restoring
To restore a backup `mybackup.json`, use the heroku CLI again:
```
heroku run --no-tty -a myhackerforce -- python manage.py loaddata -e contenttypes --format=json - < mybackup.json
```
If your backup file begins with the line "Downloading the sponsorship packet to: {} /app/website/static/sponsorship.pdf"
you'll need to remove this line in order for the data to load successfully.
