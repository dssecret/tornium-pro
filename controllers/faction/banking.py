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

import datetime
import typing

from flask import redirect, render_template, request
from flask_login import current_user, login_required
from peewee import DoesNotExist
from tornium_celery.tasks.api import discordget, discordpatch
from tornium_celery.tasks.misc import send_dm
from tornium_commons.errors import DiscordError
from tornium_commons.formatters import commas, torn_timestamp
from tornium_commons.models import Faction, FactionPosition, Server, User, Withdrawal
from tornium_commons.skyutils import SKYNET_GOOD

import utils
from controllers.faction.decorators import aa_required


@login_required
@aa_required
def banking_aa():
    return render_template("faction/banking_aa.html")


@login_required
@aa_required
def banking_data():
    start = int(request.args.get("start"))
    length = int(request.args.get("length"))
    ordering = int(request.args.get("order[0][column]"))
    ordering_direction = request.args.get("order[0][dir]")
    withdrawals = []

    withdrawals_db = Withdrawal.select().where(Withdrawal.faction_tid == current_user.faction.tid)

    if ordering == 0:
        withdrawals_db = withdrawals_db.order_by(utils.table_order(ordering_direction, Withdrawal.wid))
    elif ordering == 1:
        withdrawals_db = withdrawals_db.order_by(utils.table_order(ordering_direction, Withdrawal.amount))
    elif ordering == 2:
        withdrawals_db = withdrawals_db.order_by(utils.table_order(ordering_direction, Withdrawal.requester))
    elif ordering == 4:
        withdrawals_db = withdrawals_db.order_by(utils.table_order(ordering_direction, Withdrawal.fulfiller))
    elif ordering == 5:
        withdrawals_db = withdrawals_db.order_by(utils.table_order(ordering_direction, Withdrawal.time_fulfilled))
    else:
        withdrawals_db = withdrawals_db.order_by(utils.table_order(ordering_direction, Withdrawal.time_requested))

    withdrawals_db = withdrawals_db[start : start + length]

    withdrawal: Withdrawal
    for withdrawal in withdrawals_db:
        if withdrawal.status == 0:
            fulfiller_str = "Not Fulfilled"
        elif withdrawal.status == 1:
            fulfiller_str = User.user_str(withdrawal.fulfiller)
        elif withdrawal.status == 2:
            fulfiller_str = f"Cancelled by {User.user_str(withdrawal.fulfiller)}"
        elif withdrawal.status == 3:
            fulfiller_str = "Cancelled by System"
        else:
            fulfiller_str = "Unknown Status"

        time_fulfilled = (
            torn_timestamp(withdrawal.time_fulfilled.to_timestamp()) if withdrawal.time_fulfilled is not None else ""
        )

        withdrawals.append(
            [
                withdrawal.wid,
                f"${withdrawal.amount:,}" if withdrawal.cash_request else f"{withdrawal.amount:,} points",  # noqa: E712
                User.user_str(withdrawal.requester),
                torn_timestamp(withdrawal.time_requested),
                fulfiller_str,
                time_fulfilled,
            ]
        )

    data = {
        "draw": request.args.get("draw"),
        "recordsTotal": Withdrawal.select().count(),
        "recordsFiltered": Withdrawal.select().where(Withdrawal.faction_tid == current_user.faction.tid).count(),
        "data": withdrawals,
    }
    return data


@login_required
def banking():
    if current_user.faction is None:
        return render_template("faction/banking.html", banking_enabled=False)

    banker_positions: typing.Iterable[FactionPosition] = FactionPosition.select(
        FactionPosition.name, FactionPosition.give_money, FactionPosition.give_points, FactionPosition.adjust_balances
    ).where(
        (FactionPosition.faction_tid == current_user.faction.tid)
        & (
            (FactionPosition.give_money == True)  # noqa: E712
            | (FactionPosition.give_points == True)  # noqa: E712
            | (FactionPosition.adjust_balances == True)  # noqa: E712
        )
    )
    bankers = []

    banker_position: FactionPosition
    for banker_position in banker_positions:
        user: User
        for user in User.select(User.name, User.tid, User.last_action).where(
            User.faction_position == banker_position.pid
        ):
            bankers.append(
                {
                    "name": user.name,
                    "tid": user.tid,
                    "last_action": user.last_action.to_timestamp(),
                    "position": banker_position.name,
                    "money": banker_position.give_money,
                    "points": banker_position.give_points,
                    "adjust": banker_position.adjust_balances,
                }
            )

    if current_user.faction.leader is not None:
        bankers.append(
            {
                "name": current_user.faction.leader.name,
                "tid": current_user.faction.leader.tid,
                "last_action": current_user.faction.leader.last_action.to_timestamp(),
                "position": "Leader",
                "money": True,
                "points": True,
                "adjust": True,
            }
        )

    if current_user.faction.coleader is not None:
        bankers.append(
            {
                "name": current_user.faction.coleader.name,
                "tid": current_user.faction.coleader.tid,
                "last_action": current_user.faction.coleader.last_action.to_timestamp(),
                "position": "Co-leader",
                "money": True,
                "points": True,
                "adjust": True,
            }
        )

    guild: typing.Optional[Server] = current_user.faction.guild

    if guild is None or str(current_user.faction.tid) not in guild.banking_config:
        banking_enabled = False
    else:
        banking_enabled = guild.banking_config[str(current_user.faction.tid)]["channel"]

    return render_template(
        "faction/banking.html",
        banking_enabled=banking_enabled,
        faction=current_user.faction,
        bankers=bankers,
    )


@login_required
def user_banking_data():
    start = int(request.args.get("start"))
    length = int(request.args.get("length"))
    ordering = int(request.args.get("order[0][column]"))
    ordering_direction = request.args.get("order[0][dir]")
    withdrawals = []

    withdrawals_db = Withdrawal.select().where(Withdrawal.faction_tid == current_user.faction.tid)

    if ordering == 0:
        withdrawals_db = withdrawals_db.order_by(utils.table_order(ordering_direction, Withdrawal.wid))
    elif ordering == 1:
        withdrawals_db = withdrawals_db.order_by(utils.table_order(ordering_direction, Withdrawal.amount))
    elif ordering == 3:
        withdrawals_db = withdrawals_db.order_by(utils.table_order(ordering_direction, Withdrawal.fulfiller))
    elif ordering == 4:
        withdrawals_db = withdrawals_db.order_by(utils.table_order(ordering_direction, Withdrawal.time_fulfilled))
    else:
        withdrawals_db = withdrawals_db.order_by(utils.table_order(ordering_direction, Withdrawal.time_requested))

    withdrawals_db = withdrawals_db[start : start + length]

    withdrawal: Withdrawal
    for withdrawal in withdrawals_db:
        if withdrawal.status == 0:
            fulfiller_str = "Not Fulfilled"
        elif withdrawal.status == 1:
            fulfiller_str = User.user_str(withdrawal.fulfiller)
        elif withdrawal.status == 2:
            fulfiller_str = f"Cancelled by {User.user_str(withdrawal.fulfiller)}"
        elif withdrawal.status == 3:
            fulfiller_str = "Cancelled by System"
        else:
            fulfiller_str = "Unknown Status"

        time_fulfilled = (
            torn_timestamp(withdrawal.time_fulfilled.to_timestamp()) if withdrawal.time_fulfilled is not None else ""
        )

        withdrawals.append(
            [
                withdrawal.wid,
                f"${withdrawal.amount:,}" if withdrawal.cash_request else f"{withdrawal.amount:,} points",
                torn_timestamp(withdrawal.time_requested),
                fulfiller_str,
                time_fulfilled,
            ]
        )

    data = {
        "draw": request.args.get("draw"),
        "recordsTotal": Withdrawal.select().count(),
        "recordsFiltered": Withdrawal.select().where(Withdrawal.requester == current_user.tid).count(),
        "data": withdrawals,
    }
    return data


def fulfill(guid: str):
    try:
        withdrawal: Withdrawal = Withdrawal.get(Withdrawal.guid == guid)
    except DoesNotExist:
        return (
            render_template(
                "errors/error.html",
                title="Unknown Withdrawal",
                error="The passed withdrawal could not be found in the database.",
            ),
            400,
        )

    if withdrawal.cash_request:
        send_link = (
            f"https://www.torn.com/factions.php?step=your#/tab=controls&option=give-to-user&giveMoneyTo="
            f"{withdrawal.requester}&money={withdrawal.amount}"
        )
    else:
        send_link = (
            f"https://www.torn.com/factions.php?step=your#/tab=controls&option=give-to-user&givePointsTo="
            f"{withdrawal.requester}&points={withdrawal.amount}"
        )

    if withdrawal.status == 1:
        return render_template(
            "errors/error.html",
            title="Can't Fulfill Request",
            error=f"This request has already been fulfilled at {torn_timestamp(withdrawal.time_fulfilled.to_timestamp())}.",
        )
    elif withdrawal.status == 2:
        return render_template(
            "errors/error.html",
            title="Can't Fulfill Request",
            error=f"This request has already been cancelled at {torn_timestamp(withdrawal.time_fulfilled.to_timestamp())}.",
        )
    elif withdrawal.status == 3:
        return render_template(
            "errors/error.html",
            title="Can't Fulfill Request",
            error=f"This request has already been cancelled by the system at {torn_timestamp(withdrawal.time_fulfilled.to_timestamp())}.",
        )

    try:
        faction: Faction = Faction.select(Faction.guild).where(Faction.tid == withdrawal.faction_tid).get()
    except DoesNotExist:
        return (
            render_template(
                "errors/error.html",
                title="Faction Not Found",
                error="The requester's faction could not be located in the database.",
            ),
            400,
        )

    if faction.guild is None:
        return (
            render_template(
                "errors/error.html",
                title="Missing Configuration",
                error="The server's vault configuration is not properly set. Please contact a server administrator or "
                "faction AA member to do so.",
            ),
            400,
        )
    elif faction.tid not in faction.guild.factions:
        return (
            render_template(
                "errors/error.html",
                title="Permission Denied",
                error="The faction is not set up to be in the specified server.",
            ),
            403,
        )
    elif faction.guild.banking_config.get(str(faction.tid), {"channel": "0"})["channel"] == "0":
        return (
            render_template(
                "errors/error.html",
                title="Missing Configuration",
                error="The server's vault configuration is not properly set. Please contact a server administrator or "
                "faction AA member to do so.",
            ),
            400,
        )

    channels = discordget(f"guilds/{faction.guild.sid}/channels")
    banking_channel = None

    for channel in channels:
        if channel["id"] == faction.guild.banking_config[str(faction.tid)]["channel"]:
            banking_channel = channel
            break

    if banking_channel is None:
        return (
            render_template(
                "errors/error.html",
                title="Unknown Channel",
                error="The banking channel withdrawal requests are sent to could not be found.",
            ),
            400,
        )

    requester: typing.Optional[User]
    try:
        requester = User.select(User.name, User.tid, User.discord_id).where(User.tid == withdrawal.requester).get()
    except DoesNotExist:
        requester = None

    try:
        if current_user.is_authenticated:
            fulfiller_str = f"{current_user.name} [{current_user.tid}]"
        else:
            fulfiller_str = "someone"

        discordpatch.delay(
            f"channels/{banking_channel['id']}/messages/{withdrawal.withdrawal_message}",
            payload={
                "embeds": [
                    {
                        "title": f"Vault Request #{withdrawal.wid}",
                        "description": f"This request has been fulfilled by {fulfiller_str}",
                        "fields": [
                            {
                                "name": "Original Request Amount",
                                "value": f"{commas(withdrawal.amount)} {'Cash' if withdrawal.cash_request else 'Points'}",
                            },
                            {
                                "name": "Original Requester",
                                "value": f"N/A [{withdrawal.requester}]"
                                if requester is None
                                else requester.user_str_self(),
                            },
                        ],
                        "timestamp": datetime.datetime.utcnow().isoformat(),
                        "color": SKYNET_GOOD,
                    }
                ],
                "components": [
                    {
                        "type": 1,
                        "components": [
                            {
                                "type": 2,
                                "style": 5,
                                "label": "Faction Vault",
                                "url": "https://www.torn.com/factions.php?step=your#/tab=controls&option=give-to-user",
                            },
                            {
                                "type": 2,
                                "style": 5,
                                "label": "Fulfill",
                                "url": f"https://tornium.com/faction/banking/fulfill/{withdrawal.guid}",
                            },
                            {
                                "type": 2,
                                "style": 3,
                                "label": "Fulfill Manually",
                                "custom_id": "faction:vault:fulfill",
                            },
                            {
                                "type": 2,
                                "style": 4,
                                "label": "Cancel",
                                "custom_id": "faction:vault:cancel",
                            },
                        ],
                    }
                ],
            },
        )
    except DiscordError as e:
        return utils.handle_discord_error(e)

    if current_user.is_authenticated:
        withdrawal.fulfiller = current_user.tid
    else:
        withdrawal.fulfiller = -1

    withdrawal.time_fulfilled = datetime.datetime.utcnow()
    withdrawal.save()

    if requester.discord_id not in (None, "", 0):
        send_dm.delay(
            requester.discord_id,
            payload={
                "embeds": [
                    {
                        "title": "Vault Request Fulfilled",
                        "description": f"Your vault request #{withdrawal.wid} has been fulfilled by someone.",
                        "timestamp": datetime.datetime.utcnow().isoformat(),
                        "color": SKYNET_GOOD,
                    }
                ]
            },
        )

    return redirect(send_link)
