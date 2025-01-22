-- `faction` is the API response for the series of selections used
---@class Faction
---@field members table
---@field name string
faction = faction

---@class FlyingMember
---@field tid integer
---@field name string
---@field destination string?
---@field earliest_departure_time integer?
---@field landed boolean?
---@field hospital_until_time integer?

---@class State
---@field members table<string, FlyingMember[]>
---@field last_update_time integer
---@field initialized boolean
state = state
-- If `state.initialized` is nil or false, the data required for this is not initialized in the database
-- and people already flying will have inaccurate flight landing times calculated
-- TODO: Add time started injected by underlying Elixir code

if state.members == nil then
  state.members = {}
end

if state.initialized == nil then
  state.initialized = false
elseif state.initialized == false then
  state.initialized = true
end

function string.split(match_string)
  local ret_table = {}

  for token in string.gmatch(match_string, "%S+") do
    table.insert(ret_table, token)
  end

  return ret_table
end

function string.starts_with(match_string, starts)
  return string.sub(match_string, 1, #starts) == starts
end

function string.gmatch(str, pattern)
  -- Used to override gmatch implementation that isn't implemented in luerl
  -- Taken from https://github.com/rvirding/luerl/issues/150

  local callable = {
    nextPos = 0,
    str = str,
    pattern = pattern
  }
  local mt = {}

  function mt.__call(table)
    local match_start, match_end = string.find(table.str, table.pattern, table.nextPos)

    if(match_start == nil) then
      return nil;
    else
      table.nextPos = match_end + 1;
      return string.sub(table.str, match_start, match_end)
    end
  end

  setmetatable(callable, mt)
  return callable
end

function table.join(tbl, seperator)
  local ret_string = ""

  for i, token in pairs(tbl) do
    if i == 1 then
      ret_string = token
    else
      ret_string = ret_string .. seperator .. token
    end
  end

  return ret_string
end

function table.find(tbl, expected_value)
  for index, value in ipairs(tbl) do
    if value == expected_value then
      return index
    end
  end

  return nil
end

--- Try to insert data into a table of arrays
---@param tbl table<string, table>
---@param key string
---@param value any
local function try_insert_array(tbl, key, value)
  if not tbl[key] then
    tbl[key] = {}
  end

  table.insert(tbl[key], value)
end

--- Extract the destination string from a user's status
---@param status_string string user.status.description
---@return string? Destination of the user (or current location if abroad)
local function get_destination(status_string)
  local destination_words = string.split(status_string)

  if string.starts_with(status_string, "Traveling") then
    return table.join({ table.unpack(destination_words, 3, #destination_words) }, " ")
  elseif string.starts_with(status_string, "Returning") then
    return table.join({ table.unpack(destination_words, 5, #destination_words) }, " ")
  elseif string.starts_with(status_string, "In") and string.find(status_string, "hospital") ~= nil then
    local hospital_index = table.find(destination_words, "hospital")
    return table.join({ table.unpack(destination_words, 3, hospital_index) }, " ")
  elseif string.starts_with(status_string, "In") then
    return table.join({ table.unpack(destination_words, 2, #destination_words) }, " ")
  end

  return nil
end

--- Format the username for a member
---@param member FlyingMember
---@return string Formatted member string
local function format_username(member)
  return string.format("%s [%d]", member.name, member.tid)
end

-- Iterate over the faction members
for member_id, member_data in pairs(faction.members) do
  local destination = get_destination(member_data.status.description)

  ---@type FlyingMember
  local member_table = {
    tid = member_id,
    name = member_data.name,
    destination = destination,
  }

  if string.starts_with(member_data.status.description, "In hospital") or string.starts_with(member_data.status.description, "In jail") then
    -- TODO: Better handle this case
    -- e.g. "In hospital for 4 mins "
    destination = nil
  elseif string.starts_with(member_data.status.description, "Traveling") then
    -- The faction member is flying
    member_table.landed = false
  elseif string.starts_with(member_data.status.description, "Returning") then
    -- The faction member is flying back to Torn
    member_table.landed = false
  elseif member_data.status.state == "Abroad" then
    -- The faction member is abroad in a certain country
    member_table.hospital_until_time = nil
    member_table.landed = true
  elseif member_data.status.state == "Hospital" and string.starts_with(member_data.status.description, "In a ") and string.find(member_data.status.description, "hospital") then
    -- The faction member is in the hospital abroad
    member_table.hospital_until_time = member_data.status
    member_table.landed = true
  end

  if destination ~= nil then
    try_insert_array(state.members, destination, member_table)
  end
end

local render_state = {
  faction_name = faction.name,
  flying_members = {},
  hospital_members = {},
  abroad_members = {},
}

for destination, destination_members in pairs(state.members) do
  for _, member in pairs(destination_members) do
    if member.landed and member.hospital_until_time ~= nil then
      try_insert_array(render_state.hospital_members, destination, {
        username = format_username(member),
      })
    elseif member.landed then
      try_insert_array(render_state.abroad_members, destination, {
        username = format_username(member),
      })
    else
      try_insert_array(render_state.flying_members, destination, {
        username = format_username(member),
        regular_landing_time = 0,
      })
    end
  end
end

-- For simplicity, the message will always be updated to avoid issues with data changing between API calls
return true, render_state, state
