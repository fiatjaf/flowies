package main

import (
	"encoding/base64"
	"os"
	"strconv"
	"strings"

	"github.com/valyala/fasthttp"
)

func main() {
	PORT := os.Getenv("PORT")
	BASEDOMAIN := os.Getenv("BASEDOMAIN")
	if BASEDOMAIN == "" {
		BASEDOMAIN = "cantillon.alhur.es:" + PORT
	}
	full := os.Getenv("COUCHDB_URL")
	frag := strings.Split(full, "/")[2]
	userpass := strings.Split(frag, "@")[0]
	COUCHDB_AUTH := base64.StdEncoding.EncodeToString([]byte(userpass))
	COUCHDB_URL := "https://" + strings.Split(full, "@")[1]

	client := fasthttp.Client{}

	h := func(ctx *fasthttp.RequestCtx) {
		domain := string(ctx.URI().Host())
		if strings.HasSuffix(domain, BASEDOMAIN) {
			domain = strings.Split(domain, ".")[0]
		}
		key := domain + "~" + string(ctx.Path())
		url := COUCHDB_URL + "/_design/sites/_list/page/pages?key=\"" + key + "\""

		req := fasthttp.AcquireRequest()
		req.Header.Add("Authorization", "Basic "+COUCHDB_AUTH)
		req.SetRequestURI(url)
		resp := fasthttp.AcquireResponse()

		err := client.Do(req, resp)
		if err != nil {
			ctx.Error("Error when loading '"+url+"': "+err.Error(), 503)
			return
		}
		code := resp.StatusCode()
		if code != fasthttp.StatusOK {
			ctx.Error("Unexpected code when loading '"+url+"': "+strconv.Itoa(code), code)
			return
		}
		ctx.SetContentType("text/html; charset=utf8")
		ctx.SetBody(resp.Body())
	}

	fasthttp.ListenAndServe(":"+PORT, h)
}
