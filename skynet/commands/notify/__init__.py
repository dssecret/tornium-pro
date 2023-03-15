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

from skynet.commands.notify import stakeouts

_notify_commands = {"stakeout": stakeouts.stakeouts}
_notify_autocomplete = {"stakeout": stakeouts.stakeout_autocomplete}


def notify_switchboard(interaction, *args, **kwargs):
    if interaction["data"]["options"][0]["name"] in _notify_commands:
        return _notify_commands[interaction["data"]["options"][0]["name"]](interaction, *args, **kwargs)

    return {}


def notify_autocomplete_switchboard(interaction, *args, **kwargs):
    if interaction["data"]["options"][0]["nane"] in _notify_autocomplete:
        return _notify_autocomplete[interaction["data"]["options"][0]["name"]](interaction, *args, **kwargs)
