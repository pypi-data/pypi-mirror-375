# CloudFlare-Challenge

Ensure that we can do a cloudflare challenge in flask

## Rationale

If you Flask server is behind a CloudFlare wall then any upload of data may provoke
a "challenge" of the "I'm not a robot" kind.

Instead of returning the response to your browser query, CloudFlare sends
back an html page with a 403 HTTP status which will interogate your browser internals and leave a cookie `cf_clearance`
-- _if_ you "pass" the challenge!.

This is of course a _disaster_ if you have used Ajax to send the request.

The idea here is to get that sweet, sweet CloudFlare cookie `cf_clearance` as soon as possible or at least before
you do any ajax requests.

Basically if there is no `cf_clearance` cookie for a request this Blueprint will redirect to
a "managed" page where it will automatically upload an image to provoke the CloudFlare challenge --
then check for success.

Once your browser has the `cf_clearance` cookie then `CloudFlare-Challenge`
will leave your app alone.

This "solution" is not ideal but it maybe better than weird failures of your ajax requests that will
ultimately confuse/anger your users.

**The big assumption here is that an upload of an image will provoke the CloudFlare challenge. If
it doesn't then don't use this package!**

## Configuration

You will need to set 1-5 configuration variables

```python
# path to a static image (required) e.g:
CF_IMAGE_FILENAME = "img/Three-pink-daisies.jpeg"
# endpoint to redirect to after challenge
CF_REDIRECT_TO = None
# template to inherit from. Defaults to one provided by cloudflare_challenge.
CF_MAIN_TEMPLATE = None
# list of endpoint prefixes that will be white/black listed
# can be just a string
CF_WHITE_LIST = ()
CF_BLACK_LIST = ()
```

If `CF_IMAGE_FILENAME` is missing or None then the blueprint will _silently_ not be registered even
if `init_app` is called. `init_app` is indempotent.

The image filename will be used by `url_for('static', filename=CF_IMAGE_FILENAME)` to
generate a url. The image should be large enough to provoke a challenge. Choose an image
that will already be cached in your brower such as a banner image in your flask landing page.

If you specify a template (`CF_MAIN_TEMPLATE`) it should have a `content` block
(for html, this is where the iframe is blatted).

If `CF_REDIRECT_TO` is missing or None then steps will be taken to redirect back to
the original page that prompted the redirection to the challenge page otherwise it will
redirect back to `/`. **Remember:** `CF_REDIRECT_TO` expects a flask _endpoint_ not a URL.

White listed endpoints won't trigger a check for CloudFlare cookies, headers etc.
Use this for "static" images, css etc (the `static` endpoint is already white listed).

You can blacklist flask endpoints -- possibly endpoints that generate html with forms in them
and thus might trigger the challenge.

The black list is checked first then the white list.

Either way, Ajax requests (with a `X-Requested-With` header) will not trigger the challenge page (no point really since
this doesn't help -- too late!).

It is maybe the best to black list endpoints that generate html forms for the user to fill out, or
any page that might send an ajax request due to user interaction. You will want to trigger the
challenge **before** any Ajax/form upload is undertaken.

## Usage

Basic usage

```python
from flask import Flask
from cloudflare_challenge import init_app

app = Flask(__name__)
app.config.from_pyfile("config.py") # say
init_app(app, url_prefix='/someprefix')
```

## Client Side

If you are using jQuery on a page to enable Ajax then you can ensure Challenges
are detected by adding to your page:

```jinja
    {% if cf_challenge is defined %}
    {{ cf_challenge(use_toastr=True) }}
    {% endif %}
```
Then Ajax challenges will be detected and logged.


If, in addition you set `MAIL_SERVER` _and_ `CF_MAIL_RECIPIENT`, then cloudflare-challenge will attempt to
send an email too.

If you only want this part then set `CF_WHITE_LIST = '*'`


Otherwise using `fetch`

```js
    function ok_for_cloudflare(resp) {
        const ret = resp.headers.get("cf-mitigated") === "challenge"
        if (window.toastr) {
            toastr.error(
            `Cloudflare has issued a challenge to a request. To continue the challenge click
                    <a class="btn btn-outline-primary" href="{{url_for('cloudflare.challenge')}}" target="cloudflare">here</a>`,
            null,
            { timeOut: 0, closeButton: true, html: true }
            )
        }
        return ret
    }
    resp = fetch(some_url)
    if (!ok_for_cloudflare(resp)) {
        // do something!
    }
```
