# Copyright (C) 2021-2023 tiksan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from flask import Blueprint, render_template, request, send_from_directory
from flask_login import current_user, fresh_login_required

import utils
from controllers.decorators import token_required

mod = Blueprint("baseroutes", __name__)


@mod.route("/")
@mod.route("/index")
def index():
    extensions = [extension.name for extension in utils.tornium_ext.TorniumExt.__iter__()]

    return render_template("index.html", extensions=extensions)


@mod.route("/settings")
@fresh_login_required
@token_required(setnx=True)
def settings(*args, **kwargs):
    if current_user.key == "":
        obfuscated_key = "Not Set"
    else:
        obfuscated_key = current_user.key[:6] + "*" * 10

    return render_template(
        "settings.html",
        enabled_mfa=current_user.security,
        obfuscated_key=obfuscated_key,
        discord_linked="Not Linked" if current_user.discord_id in ("", None, 0) else "Linked",
    )


@mod.route("/static/toast.js")
@mod.route("/static/favicon.svg")
@mod.route("/static/logo.svg")
@mod.route("/static/utils.js")
@mod.route("/static/bot/oc.js")
@mod.route("/static/bot/stakeouts.js")
@mod.route("/static/bot/guild.js")
@mod.route("/static/bot/verify.js")
@mod.route("/static/faction/armory.js")
@mod.route("/static/faction/banking.js")
@mod.route("/static/faction/bankingaa.js")
@mod.route("/static/faction/chain.js")
@mod.route("/static/faction/members.js")
@mod.route("/static/fonts/JetBrainsMono-Light.woff2")
@mod.route("/static/stats/db.js")
@mod.route("/static/stats/list.js")
@mod.route("/static/torn/factions.js")
@mod.route("/static/torn/users.js")
def static():
    return send_from_directory("static", request.path[8:])


@mod.route("/robots.txt")
@mod.route("/userscripts/tornium-assists.user.js")
def base_statics():
    return send_from_directory("static", request.path[1:])
