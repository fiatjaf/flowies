flowi.es was a service once hosted on Heroku that appeared on https://flowi.es/.

Here's a screenshot:

![](https://archive.is/vAI85/9e927553477ad25c3dd6f47fbf5166facfe46abc/scr.png)

and an archived version of the landing page: http://archive.is/vAI85

To run, it used a CouchDB instance with the design docs given in `./ddocs` and run the crontab lines `./crontab`, plus the Heroku dyno defined in `./Procfile`.

There was also a helper server that just fetched each user rendered site from CouchDB and served it on `http://*.on.flowi.es/` domains (yes, the entire sites were rendered on CouchDB using view and list functions). That was written in Go and, since it fitted in a single file, it's included here on `./web.go` for brevity.

Anyway, you don't wanna run this.
