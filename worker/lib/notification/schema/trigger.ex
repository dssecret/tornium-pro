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

defmodule Tornium.Schema.Trigger do
  use Ecto.Schema

  # TODO: Add time_created and last_updated fields

  @type t :: %__MODULE__{
          tid: Ecto.UUID.t(),
          name: String.t(),
          description: String.t(),
          owner: Tornium.Schema.User.t(),
          resource: :user | :faction | :company | :torn | :faction_v2,
          selections: List,
          code: String.t(),
          public: boolean(),
          official: boolean()
        }

  @primary_key {:tid, Ecto.UUID, autogenerate: true}
  schema "notification_trigger" do
    field(:name, :string)
    field(:description, :string)
    belongs_to(:owner, Tornium.Schema.User, references: :tid)

    field(:resource, Ecto.Enum, values: [:user, :faction, :company, :torn, :faction_v2])
    field(:selections, {:array, :string})
    field(:code, :string)

    field(:public, :boolean)
    field(:official, :boolean)
  end
end
