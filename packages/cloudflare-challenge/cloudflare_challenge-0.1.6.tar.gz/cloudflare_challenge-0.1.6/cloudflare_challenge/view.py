from __future__ import annotations

import os
import platform
from dataclasses import dataclass
from typing import Sequence

from flask import abort
from flask import Blueprint
from flask import current_app
from flask import Flask
from flask import make_response
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask.helpers import get_template_attribute
from werkzeug.wrappers.response import Response

from .mailer import sendmail

# don't use dynamic id such as uuid.uuid4() since we might hit different flask processes
UNIQUEID = "not-found-on-any-page-ever-435acd15-77df"
COOKIE = "cf-challenge-passed"

CF_NAME = "cloudflare-challenge"


def get_challenge() -> Challenge:
    """Get configuration info"""
    return current_app.extensions[CF_NAME]  # type: ignore[no-any-return]


def has_clearance(use_path: bool) -> Response | None:
    """Check if we have a CloudFlare clearance cookie"""
    if request.headers.get("X-Requested-With"):
        # Ajax call; we can't really do anything
        return None
    if request.cookies.get("cf_clearance"):
        return None
    if request.cookies.get(COOKIE):
        return None  # we are going around is circles with this redirect

    # None values are ignored
    return redirect(
        url_for("cloudflare.challenge", redirect=request.path if use_path else None),
    )


def is_valid_url(url: str) -> bool:
    return url.startswith("/")


cf = Blueprint("cloudflare", __name__, template_folder="templates")


@cf.route("/cloudflare-challenge.html")
def challenge() -> str:
    """Render html page with challenge iframe inside"""
    url = url_for("cloudflare.iframe")
    cfdata = get_challenge()
    if cfdata.redirect_to is not None:
        redirect_to = url_for(cfdata.redirect_to)
    else:
        redirect_ = request.args.get("redirect")
        if redirect_ and is_valid_url(redirect_):
            redirect_to = redirect_
        else:
            redirect_to = "/"  # fallback

    return render_template(
        "cloudflare-challenge.html",
        challenge=url,
        redirect_to=redirect_to,
        cf_main_template=cfdata.cf_main_template,
        challenge_id=UNIQUEID,
    )


@cf.route("/cloudflare-iframe.html")
def iframe() -> str:
    """Page that will automatically force an form upload of an image or provoke challenge"""
    cfdata = get_challenge()
    action_url = url_for("cloudflare.action")

    return render_template(
        "cloudflare-iframe.html",
        action=action_url,
        image_name=os.path.basename(cfdata.image_filename),
        image_url=url_for("static", filename=cfdata.image_filename),
        visible="visible" if current_app.debug else "hidden",
    )


@cf.route("/cloudflare-action", methods=["POST"])
def action() -> Response:
    """If we get here then CloudFlare has let us through after a possible challenge"""
    content_type: str | None = "text/plain"
    file = request.files.get("file")
    if file:
        content_type = file.headers.get("mimetype")
        if not content_type:
            content_type = file.headers.get("Content-Type")
    # javascript on the client will detect the presence of UNIQUEID Element
    # and redirect the page to Challenge.redirect_to
    resp = make_response(
        f'<div id="{UNIQUEID}" style="visibility:hidden">'
        f"content-type=<code>{content_type}</code></div>",
    )
    # resp = jsonify({"id": UNIQUEID, "content_type": content_type})
    max_age = current_app.config.get("CF_MAX_AGE", 5 * 60)
    resp.set_cookie(COOKIE, "yes", max_age=max_age, samesite="Strict")

    if current_app.debug and file:
        data = file.read()
        current_app.logger.info(
            "received file: %s[%s] of size %d",
            file.filename,
            content_type,
            len(data),
        )
    return resp


@cf.route("/cloudflare-problem")
def problem() -> str:
    url = request.values.get("url")
    if url is None:
        # just a bot?
        abort(404)
    current_app.logger.error("Cloudflare challenge detected for url=%s", url)
    try:
        sendmail(
            f'Cloudflare challenge occured for "{url}" on '
            f"server={request.root_url} ({platform.node()})",
        )
    except Exception as e:  # pylint: disable=broad-except
        current_app.logger.error("can't send email %s", e)
    return "OK"


@dataclass
class Challenge:
    """Challenge configuration info"""

    # image filename for `url_for('static', filename=image_filename)`
    image_filename: str
    redirect_to: str | None  # endpoint
    cf_main_template: str  # template into which to put iframe


def mklist(uwl: str | Sequence[str] | None) -> list[str]:
    ret = []
    if uwl is not None:
        if isinstance(uwl, str):
            ret.append(uwl)
        else:
            ret.extend(uwl)
    return [str(s) for s in ret]


WHITE = ("cloudflare.", "static")


def get_white_list(app: Flask) -> tuple[str, ...]:
    ret = mklist(app.config.get("CF_WHITE_LIST"))
    if ret == ["*"]:
        return ("*",)
    ret.extend(WHITE)
    return tuple(set(ret))


def get_black_list(app: Flask) -> tuple[str, ...]:
    ret = mklist(app.config.get("CF_BLACK_LIST"))
    return tuple(s for s in ret if not s.startswith(WHITE))


def create_challenge(app: Flask) -> Challenge | None:
    image_filename = app.config.get("CF_IMAGE_FILENAME")
    if image_filename is None:
        return None
    return Challenge(
        image_filename=image_filename,
        redirect_to=app.config.get("CF_REDIRECT_TO"),
        cf_main_template=app.config.get("CF_MAIN_TEMPLATE", "cloudflare-main.html"),
    )


def init_app(app: Flask, url_prefix: str = "/") -> None:
    """register challenge blueprint"""
    if CF_NAME in app.extensions:
        return
    cf_data = create_challenge(app)
    if cf_data is None:
        return

    white_list = get_white_list(app)

    black_list = get_black_list(app)

    use_path = cf_data.redirect_to is None

    app.extensions[CF_NAME] = cf_data

    if black_list or white_list != ("*",):

        @app.before_request
        def check() -> Response | None:
            endpoint = request.endpoint
            if not endpoint:  # maybe 404
                return None
            if endpoint.startswith(black_list):
                return has_clearance(use_path)
            if endpoint.startswith(white_list) or endpoint.endswith(".static"):
                return None
            return has_clearance(use_path)

    app.register_blueprint(cf, url_prefix=url_prefix)

    with app.app_context():
        cf_challenge = get_template_attribute("cloudflare-macros.html", "cf_challenge")
        if cf_challenge:
            app.jinja_env.globals["cf_challenge"] = cf_challenge
