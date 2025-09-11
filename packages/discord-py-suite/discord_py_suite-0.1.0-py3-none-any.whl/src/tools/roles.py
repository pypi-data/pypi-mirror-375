"""Discord role management FastMCP tools."""

from typing import Any, Dict, Optional, List, Tuple
import discord
from loguru import logger

try:
    from fastmcp import FastMCP
except ImportError:
    logger.error("FastMCP not installed. Please run: uv add fastmcp>=2.12.0")
    raise


def register_roles_tools(app: FastMCP, client: discord.Client, config: Any) -> None:
    """Register Discord role management tools with FastMCP app."""

    @app.tool()
    async def discord_create_role(
        guild_id: str,
        name: str,
        color: Optional[int] = None,
        permissions: Optional[int] = None,
        mentionable: Optional[bool] = None,
        hoisted: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Create a new role in a Discord guild."""
        try:
            guild = client.get_guild(int(guild_id))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guild_id} not found or bot not in guild",
                }

            # Check bot permissions
            bot_member = guild.get_member(client.user.id) if client.user else None
            if not bot_member or not bot_member.guild_permissions.manage_roles:
                return {"success": False, "error": "Bot lacks manage_roles permission"}

            # Prepare role kwargs
            # Prepare role creation parameters
            role_color = (
                discord.Color(color) if color is not None else discord.Color.default()
            )
            if color is not None and not (0 <= color <= 0xFFFFFF):
                return {
                    "success": False,
                    "error": "Color must be between 0 and 0xFFFFFF",
                }

            role_permissions = (
                discord.Permissions(permissions)
                if permissions is not None
                else discord.Permissions()
            )

            role = await guild.create_role(
                name=name,
                color=role_color,
                permissions=role_permissions,
                mentionable=mentionable if mentionable is not None else False,
                hoist=hoisted if hoisted is not None else False,
            )

            return {
                "success": True,
                "data": {
                    "role_id": str(role.id),
                    "name": role.name,
                    "color": role.color.value,
                    "permissions": role.permissions.value,
                    "mentionable": role.mentionable,
                    "hoisted": role.hoist,
                    "position": role.position,
                    "managed": role.managed,
                    "created_at": role.created_at.isoformat(),
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid guild ID format"}
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks permission to create roles"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error creating role: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_edit_role(
        guild_id: str,
        role_id: str,
        name: Optional[str] = None,
        color: Optional[int] = None,
        permissions: Optional[int] = None,
        mentionable: Optional[bool] = None,
        hoisted: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Edit an existing role in a Discord guild."""
        try:
            guild = client.get_guild(int(guild_id))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guild_id} not found or bot not in guild",
                }

            role = guild.get_role(int(role_id))
            if not role:
                return {"success": False, "error": f"Role {role_id} not found in guild"}

            # Check bot permissions
            bot_member = guild.get_member(client.user.id) if client.user else None
            if not bot_member or not bot_member.guild_permissions.manage_roles:
                return {"success": False, "error": "Bot lacks manage_roles permission"}

            # Check role hierarchy
            if (
                role >= bot_member.top_role
                and not bot_member.guild_permissions.administrator
            ):
                return {
                    "success": False,
                    "error": "Cannot modify roles higher than bot's top role",
                }

            # Prepare role kwargs
            role_kwargs: Dict[str, Any] = {}

            if name is not None:
                role_kwargs["name"] = name

            if color is not None:
                if not (0 <= color <= 0xFFFFFF):
                    return {
                        "success": False,
                        "error": "Color must be between 0 and 0xFFFFFF",
                    }
                role_kwargs["color"] = discord.Color(color)

            if permissions is not None:
                role_kwargs["permissions"] = discord.Permissions(permissions)

            if mentionable is not None:
                role_kwargs["mentionable"] = mentionable

            if hoisted is not None:
                role_kwargs["hoist"] = hoisted

            # Only update if there are changes
            if role_kwargs:
                await role.edit(**role_kwargs)

            return {
                "success": True,
                "data": {
                    "role_id": str(role.id),
                    "name": role.name,
                    "color": role.color.value,
                    "permissions": role.permissions.value,
                    "mentionable": role.mentionable,
                    "hoisted": role.hoist,
                    "position": role.position,
                    "managed": role.managed,
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid guild or role ID format"}
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks permission to edit roles"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error editing role: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_delete_role(guild_id: str, role_id: str) -> Dict[str, Any]:
        """Delete a role from a Discord guild."""
        try:
            guild = client.get_guild(int(guild_id))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guild_id} not found or bot not in guild",
                }

            role = guild.get_role(int(role_id))
            if not role:
                return {"success": False, "error": f"Role {role_id} not found in guild"}

            # Check bot permissions
            bot_member = guild.get_member(client.user.id) if client.user else None
            if not bot_member or not bot_member.guild_permissions.manage_roles:
                return {"success": False, "error": "Bot lacks manage_roles permission"}

            # Check role hierarchy
            if (
                role >= bot_member.top_role
                and not bot_member.guild_permissions.administrator
            ):
                return {
                    "success": False,
                    "error": "Cannot delete roles higher than bot's top role",
                }

            # Cannot delete managed roles or @everyone
            if role.managed or role == guild.default_role:
                return {
                    "success": False,
                    "error": "Cannot delete managed roles or @everyone role",
                }

            await role.delete()

            return {"success": True, "data": {"deleted_role_id": role_id}}

        except ValueError:
            return {"success": False, "error": "Invalid guild or role ID format"}
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks permission to delete roles"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error deleting role: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_get_role(guild_id: str, role_id: str) -> Dict[str, Any]:
        """Get details of a specific role in a Discord guild."""
        try:
            guild = client.get_guild(int(guild_id))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guild_id} not found or bot not in guild",
                }

            role = guild.get_role(int(role_id))
            if not role:
                return {"success": False, "error": f"Role {role_id} not found in guild"}

            return {
                "success": True,
                "data": {
                    "role_id": str(role.id),
                    "name": role.name,
                    "color": role.color.value,
                    "permissions": role.permissions.value,
                    "mentionable": role.mentionable,
                    "hoisted": role.hoist,
                    "position": role.position,
                    "managed": role.managed,
                    "created_at": role.created_at.isoformat(),
                    "member_count": sum(
                        1 for member in guild.members if role in member.roles
                    ),
                    "color_hex": str(role.color),
                    "permissions_list": [
                        perm for perm, value in role.permissions if value
                    ],
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid guild or role ID format"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error getting role: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_list_roles(
        guild_id: str, include_member_count: Optional[bool] = False
    ) -> Dict[str, Any]:
        """List all roles in a Discord guild."""
        try:
            guild = client.get_guild(int(guild_id))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guild_id} not found or bot not in guild",
                }

            roles_data = []
            for role in sorted(guild.roles, key=lambda r: r.position, reverse=True):
                role_data = {
                    "role_id": str(role.id),
                    "name": role.name,
                    "color": role.color.value,
                    "permissions": role.permissions.value,
                    "mentionable": role.mentionable,
                    "hoisted": role.hoist,
                    "position": role.position,
                    "managed": role.managed,
                    "created_at": role.created_at.isoformat(),
                    "color_hex": str(role.color),
                }

                if include_member_count:
                    role_data["member_count"] = sum(
                        1 for member in guild.members if role in member.roles
                    )

                roles_data.append(role_data)

            return {
                "success": True,
                "data": {"guild_id": guild_id, "roles": roles_data},
            }

        except ValueError:
            return {"success": False, "error": "Invalid guild ID format"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error listing roles: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_assign_role(
        guild_id: str, user_id: str, role_id: str
    ) -> Dict[str, Any]:
        """Assign a role to a user in a Discord guild."""
        try:
            guild = client.get_guild(int(guild_id))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guild_id} not found or bot not in guild",
                }

            member = guild.get_member(int(user_id))
            if not member:
                return {
                    "success": False,
                    "error": f"Member {user_id} not found in guild",
                }

            role = guild.get_role(int(role_id))
            if not role:
                return {"success": False, "error": f"Role {role_id} not found in guild"}

            # Check bot permissions
            bot_member = guild.get_member(client.user.id) if client.user else None
            if not bot_member or not bot_member.guild_permissions.manage_roles:
                return {"success": False, "error": "Bot lacks manage_roles permission"}

            # Check role hierarchy
            if (
                role >= bot_member.top_role
                and not bot_member.guild_permissions.administrator
            ):
                return {
                    "success": False,
                    "error": "Cannot assign roles higher than bot's top role",
                }

            # Check if member already has the role
            if role in member.roles:
                return {"success": False, "error": "Member already has this role"}

            await member.add_roles(role)

            return {
                "success": True,
                "data": {
                    "member_id": str(member.id),
                    "role_id": str(role.id),
                    "member_name": member.name,
                    "role_name": role.name,
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid guild, user, or role ID format"}
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks permission to assign roles"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error assigning role: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_unassign_role(
        guild_id: str, user_id: str, role_id: str
    ) -> Dict[str, Any]:
        """Remove a role from a user in a Discord guild."""
        try:
            guild = client.get_guild(int(guild_id))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guild_id} not found or bot not in guild",
                }

            member = guild.get_member(int(user_id))
            if not member:
                return {
                    "success": False,
                    "error": f"Member {user_id} not found in guild",
                }

            role = guild.get_role(int(role_id))
            if not role:
                return {"success": False, "error": f"Role {role_id} not found in guild"}

            # Check bot permissions
            bot_member = guild.get_member(client.user.id) if client.user else None
            if not bot_member or not bot_member.guild_permissions.manage_roles:
                return {"success": False, "error": "Bot lacks manage_roles permission"}

            # Check role hierarchy
            if (
                role >= bot_member.top_role
                and not bot_member.guild_permissions.administrator
            ):
                return {
                    "success": False,
                    "error": "Cannot unassign roles higher than bot's top role",
                }

            # Check if member has the role
            if role not in member.roles:
                return {"success": False, "error": "Member does not have this role"}

            # Cannot remove managed roles or @everyone
            if role.managed or role == guild.default_role:
                return {
                    "success": False,
                    "error": "Cannot remove managed roles or @everyone role",
                }

            await member.remove_roles(role)

            return {
                "success": True,
                "data": {
                    "member_id": str(member.id),
                    "role_id": str(role.id),
                    "member_name": member.name,
                    "role_name": role.name,
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid guild, user, or role ID format"}
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks permission to unassign roles"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error unassigning role: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_get_role_members(guild_id: str, role_id: str) -> Dict[str, Any]:
        """Get all members with a specific role in a Discord guild."""
        try:
            guild = client.get_guild(int(guild_id))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guild_id} not found or bot not in guild",
                }

            role = guild.get_role(int(role_id))
            if not role:
                return {"success": False, "error": f"Role {role_id} not found in guild"}

            members_with_role = [
                {
                    "member_id": str(member.id),
                    "member_name": member.name,
                    "member_display_name": member.display_name,
                    "joined_at": member.joined_at.isoformat()
                    if member.joined_at
                    else None,
                    "top_role": {
                        "id": str(member.top_role.id),
                        "name": member.top_role.name,
                        "color": member.top_role.color.value,
                    }
                    if member.top_role != member.guild.default_role
                    else None,
                }
                for member in guild.members
                if role in member.roles
            ]

            return {
                "success": True,
                "data": {
                    "role_id": str(role.id),
                    "role_name": role.name,
                    "member_count": len(members_with_role),
                    "members": members_with_role,
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid guild or role ID format"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error getting role members: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_set_role_permissions(
        guild_id: str, role_id: str, permissions: int
    ) -> Dict[str, Any]:
        """Set permissions for a role in a Discord guild."""
        try:
            guild = client.get_guild(int(guild_id))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guild_id} not found or bot not in guild",
                }

            role = guild.get_role(int(role_id))
            if not role:
                return {"success": False, "error": f"Role {role_id} not found in guild"}

            # Check bot permissions
            bot_member = guild.get_member(client.user.id) if client.user else None
            if not bot_member or not bot_member.guild_permissions.manage_roles:
                return {"success": False, "error": "Bot lacks manage_roles permission"}

            # Check role hierarchy
            if (
                role >= bot_member.top_role
                and not bot_member.guild_permissions.administrator
            ):
                return {
                    "success": False,
                    "error": "Cannot modify permissions for roles higher than bot's top role",
                }

            # Cannot modify permissions for managed roles
            if role.managed:
                return {
                    "success": False,
                    "error": "Cannot modify permissions for managed roles",
                }

            old_permissions = role.permissions.value
            await role.edit(permissions=discord.Permissions(permissions))

            return {
                "success": True,
                "data": {
                    "role_id": str(role.id),
                    "role_name": role.name,
                    "old_permissions": old_permissions,
                    "new_permissions": role.permissions.value,
                    "permissions_list": [
                        perm for perm, value in role.permissions if value
                    ],
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid guild or role ID format"}
        except discord.Forbidden:
            return {
                "success": False,
                "error": "Bot lacks permission to set role permissions",
            }
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error setting role permissions: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_get_role_permissions(
        guild_id: str, role_id: str
    ) -> Dict[str, Any]:
        """Get current permissions for a role in a Discord guild."""
        try:
            guild = client.get_guild(int(guild_id))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guild_id} not found or bot not in guild",
                }

            role = guild.get_role(int(role_id))
            if not role:
                return {"success": False, "error": f"Role {role_id} not found in guild"}

            permissions_list = [perm for perm, value in role.permissions if value]

            return {
                "success": True,
                "data": {
                    "role_id": str(role.id),
                    "role_name": role.name,
                    "permissions_value": role.permissions.value,
                    "permissions_list": permissions_list,
                    "permissions_count": len(permissions_list),
                    "permissions_hex": hex(role.permissions.value),
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid guild or role ID format"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error getting role permissions: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_clone_role(
        guild_id: str, source_role_id: str, name: str
    ) -> Dict[str, Any]:
        """Clone a role with the same permissions, color, and settings."""
        try:
            guild = client.get_guild(int(guild_id))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guild_id} not found or bot not in guild",
                }

            source_role = guild.get_role(int(source_role_id))
            if not source_role:
                return {
                    "success": False,
                    "error": f"Source role {source_role_id} not found in guild",
                }

            # Check bot permissions
            bot_member = guild.get_member(client.user.id) if client.user else None
            if not bot_member or not bot_member.guild_permissions.manage_roles:
                return {"success": False, "error": "Bot lacks manage_roles permission"}

            # Clone the role with same settings
            cloned_role = await guild.create_role(
                name=name,
                color=source_role.color,
                permissions=source_role.permissions,
                mentionable=source_role.mentionable,
                hoist=source_role.hoist,
            )

            return {
                "success": True,
                "data": {
                    "source_role_id": str(source_role.id),
                    "source_role_name": source_role.name,
                    "new_role_id": str(cloned_role.id),
                    "new_role_name": cloned_role.name,
                    "permissions_cloned": True,
                    "color_cloned": True,
                    "settings_cloned": True,
                },
            }

        except ValueError:
            return {"success": False, "error": "Invalid guild or role ID format"}
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks permission to clone roles"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error cloning role: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    @app.tool()
    async def discord_reorder_roles(
        guild_id: str, role_positions: List[Tuple[str, int]]
    ) -> Dict[str, Any]:
        """Reorder roles by changing their positions in a Discord guild."""
        try:
            guild = client.get_guild(int(guild_id))
            if not guild:
                return {
                    "success": False,
                    "error": f"Guild {guild_id} not found or bot not in guild",
                }

            # Parse role positions
            role_orders = []
            for role_id_str, position in role_positions:
                role = guild.get_role(int(role_id_str))
                if not role:
                    return {
                        "success": False,
                        "error": f"Role {role_id_str} not found in guild",
                    }
                role_orders.append((role, position))

            # Check bot permissions
            bot_member = guild.get_member(client.user.id) if client.user else None
            if not bot_member or not bot_member.guild_permissions.manage_roles:
                return {"success": False, "error": "Bot lacks manage_roles permission"}

            # Check role hierarchy - bot can't reorder roles above its own highest role
            bot_top_role = bot_member.top_role
            for role, position in role_orders:
                if (
                    role.position >= bot_top_role.position
                    and not bot_member.guild_permissions.administrator
                ):
                    return {
                        "success": False,
                        "error": "Cannot reorder roles higher than bot's top role",
                    }

            # Reorder roles
            await guild.edit_role_positions(
                positions={role: pos for role, pos in role_orders}
            )

            # Get updated role positions
            updated_roles = []
            for role_id_str, position in role_positions:
                role = guild.get_role(int(role_id_str))
                if role is not None:
                    updated_roles.append(
                        {
                            "role_id": str(role.id),
                            "role_name": role.name,
                            "new_position": position,
                            "current_position": role.position,
                        }
                    )

            return {"success": True, "data": {"reordered_roles": updated_roles}}

        except ValueError:
            return {
                "success": False,
                "error": "Invalid guild ID or role position format",
            }
        except discord.Forbidden:
            return {"success": False, "error": "Bot lacks permission to reorder roles"}
        except discord.HTTPException as e:
            return {"success": False, "error": f"Discord API error: {e}"}
        except Exception as e:
            logger.error(f"Error reordering roles: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    # Log tool registration
    logger.info("Registered 12 Discord role management tools")
