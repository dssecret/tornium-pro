# Copyright (C) 2021-2023 tiksan
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

defmodule Tornium.Discord.Events.GuildMemberAdd do
  require Logger

  @spec handle(guild_id :: integer(), new_member :: Nostrum.Struct.Guild.Member.t()) :: nil
  def handle(guild_id, new_member) do
    # Verify members on join if the server has that feature enabled
    case Nostrum.Cache.UserCache.get(new_member.user_id) do
      {:ok, user} ->
        Tornium.Guild.Verify.handle(guild_id, user, new_member)

      {:error, reason} ->
        Logger.debug([
          "Failed to get user ",
          new_member.user_id,
          " for verification on join from the cache due to ",
          reason
        ])
    end
  end
end
