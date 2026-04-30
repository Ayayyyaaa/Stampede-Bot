import discord
from discord.ext import commands
import datetime
from zoneinfo import ZoneInfo
import config
from src.scores import add_member_if_absent


class MemberApprovalView(discord.ui.View):
    """
    Buttons sent to the mod log channel when a new member joins.
    - ✅ Accept  : gives MEMBER role + adds to club member list
    - ❌ Reject  : kicks the member after a confirmation step
    - 🔕 Ignore  : dismisses the notification (no action)
    """

    def __init__(self, member: discord.Member, guild_config: dict):
        super().__init__(timeout=None)   # persistent until a mod acts
        self.member = member
        self.guild_config = guild_config
        self.handled = False             # prevent double-clicks


    def _is_colead(self, interaction: discord.Interaction) -> bool:
        return any(r.id == self.guild_config["COLEAD"] for r in interaction.user.roles)

    async def _mark_handled(self, interaction: discord.Interaction, embed: discord.Embed):
        """Disables all buttons and edits the original message."""
        self.handled = True
        for item in self.children:
            item.disabled = True
        self.stop()
        await interaction.response.edit_message(embed=embed, view=self)


    @discord.ui.button(
        label="Accept",
        style=discord.ButtonStyle.success,
        emoji=discord.PartialEmoji(name="players", id=1496861469583867987, animated=False),
    )
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.handled:
            await interaction.response.send_message("<a:research:1488144464835776622> This request has already been handled.", ephemeral=True)
            return
        if not self._is_colead(interaction):
            await interaction.response.send_message("❌ You don't have the permissions to do that.", ephemeral=True)
            return

        guild = interaction.guild
        member = guild.get_member(self.member.id)

        if member is None:
            await interaction.response.send_message(
                "❌ This member is no longer on the server.", ephemeral=True
            )
            return

        role = guild.get_role(self.guild_config["MEMBER"])
        if role:
            try:
                await member.add_roles(role, reason=f"Accepted by {interaction.user.display_name}")
            except discord.HTTPException as e:
                await interaction.response.send_message(f"❌ Could not assign role: {e}", ephemeral=True)
                return

        # Add to club member list with Discord account linked
        add_member_if_absent(
            guild_id=guild.id,
            name=member.display_name,
            discord_id=member.id
        )

        # Send a welcome message in the announcement channel
        salon_annonce = guild.get_channel(self.guild_config.get("SALON_NEW_MEMBERS"))
        club_name = self.guild_config.get("Name", guild.name)
        rules_id = self.guild_config.get("rules", "")
        advices_id = self.guild_config.get("advices", self.guild_config.get("advice", ""))

        if salon_annonce:
            welcome_embed = discord.Embed(
                title=f"<:Raja:1488127825859838103> Welcome in {club_name} ! <:Raja:1488127825859838103>",
                description=(
                    f"Congratulations **{member.display_name}**, you've been accepted by "
                    f"**{interaction.user.display_name}** !\nYou're now a {club_name} member !\n"
                ),
                color=discord.Color.dark_purple()
            )
            if member.avatar:
                welcome_embed.set_thumbnail(url=member.avatar.url)
            welcome_embed.add_field(
                name="<a:research:1488144464835776622> Useful channels",
                value=f"• Read the rules in <#{rules_id}> <:list:1499364068702818434>\n• Ask your questions in <#{advices_id}>\n",
                inline=False
            )
            welcome_embed.add_field(
                name="<:faction:1488292952618045440> Choose your faction",
                value=(
                    "Use **/faction [faction-name]** to choose :\n\n"
                    " <:Cobra:1487161398017392791> **Cobra** \n"
                    " <:Griffin:1487161459707478237> **Griffin** \n"
                    " <:Crane:1487161429458026639> **Crane** \n"
                    " <:Mantis:1487161330455674892> **Mantis** \n"
                    " <:Kodiak:1487161368086974646> **Kodiak** \n"
                    " <:Howler:1487161297765138644> **Howler** "
                ),
                inline=False
            )
            await salon_annonce.send(content=f"Welcome {member.mention} !", embed=welcome_embed)

        # Update the mod notification embed
        result_embed = discord.Embed(
            title="<:players:1496861469583867987> Member accepted",
            description=(
                f"**{member.display_name}** has been accepted by {interaction.user.mention}.\n"
                f"Role <@&{self.guild_config['MEMBER']}> assigned and added to the club list."
            ),
            color=discord.Color.green(),
            timestamp=datetime.datetime.now(ZoneInfo("Europe/Paris"))
        )
        if member.avatar:
            result_embed.set_thumbnail(url=member.avatar.url)
        result_embed.set_footer(text=f"Action by {interaction.user.display_name}")

        await self._mark_handled(interaction, result_embed)

    # ── Reject ────────────────────────────────────────────────────────────────

    @discord.ui.button(
        label="Reject",
        style=discord.ButtonStyle.danger,
        emoji=discord.PartialEmoji(name="optis", id=1488294635519479918, animated=False),
    )
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.handled:
            await interaction.response.send_message("<a:research:1488144464835776622> This request has already been handled.", ephemeral=True)
            return
        if not self._is_colead(interaction):
            await interaction.response.send_message("❌ You don't have the permissions to do that.", ephemeral=True)
            return

        # Show a confirmation step before kicking
        confirm_embed = discord.Embed(
            title="<a:malric:1489283373342916740> Confirm rejection",
            description=(
                f"Are you sure you want to **kick** {self.member.mention} "
                f"(**{self.member.display_name}**) from the server?\n\n"
                "They will receive a private message informing them."
            ),
            color=discord.Color.orange()
        )
        if self.member.avatar:
            confirm_embed.set_thumbnail(url=self.member.avatar.url)

        await interaction.response.send_message(
            embed=confirm_embed,
            view=RejectConfirmView(self, interaction.user),
            ephemeral=True
        )

    # ── Ignore ────────────────────────────────────────────────────────────────

    @discord.ui.button(
        label="Ignore",
        style=discord.ButtonStyle.secondary,
        emoji=discord.PartialEmoji(name="notif", id=1496819951296839811),
    )
    async def ignore(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.handled:
            await interaction.response.send_message("<a:research:1488144464835776622> This request has already been handled.", ephemeral=True)
            return
        if not self._is_colead(interaction):
            await interaction.response.send_message("❌ You don't have the permissions to do that.", ephemeral=True)
            return

        result_embed = discord.Embed(
            title="<a:research:1488144464835776622> Notification dismissed",
            description=(
                f"**{self.member.display_name}** — no action taken.\n"
                f"Dismissed by {interaction.user.mention}."
            ),
            color=discord.Color.light_grey(),
            timestamp=datetime.datetime.now(ZoneInfo("Europe/Paris"))
        )
        if self.member.avatar:
            result_embed.set_thumbnail(url=self.member.avatar.url)
        result_embed.set_footer(text=f"Action by {interaction.user.display_name}")

        await self._mark_handled(interaction, result_embed)


# ── Vue de confirmation du kick ───────────────────────────────────────────────

class RejectConfirmView(discord.ui.View):
    """Ephemeral confirmation before actually kicking the member."""

    def __init__(self, parent_view: MemberApprovalView, mod: discord.Member):
        super().__init__(timeout=60)
        self.parent_view = parent_view
        self.mod = mod

    async def on_timeout(self):
        # Silently expire — the ephemeral message will just become stale
        self.stop()
    @discord.ui.button(
        label="Yes, kick them",
        style=discord.ButtonStyle.danger,
        emoji=discord.PartialEmoji(name="optis", id=1488294635519479918, animated=False),
    )
    async def confirm_kick(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.mod.id:
            await interaction.response.send_message("❌ That button doesn't belong to you.", ephemeral=True)
            return

        self.stop()
        guild = interaction.guild
        member = guild.get_member(self.parent_view.member.id)

        if member is None:
            await interaction.response.edit_message(
                content="❌ This member has already left the server.", embed=None, view=None
            )
            return

        # DM the rejected member
        club_name = self.parent_view.guild_config.get("Name", guild.name)
        try:
            dm_embed = discord.Embed(
                title=f"Application to {club_name}",
                description=(
                    "Unfortunately, your application to join the club has not been accepted at this time.\n"
                    "Feel free to apply again later!"
                ),
                color=discord.Color.red()
            )
            await member.send(embed=dm_embed)
        except discord.HTTPException:
            pass   # DMs may be closed — don't block the kick

        try:
            await member.kick(reason=f"Application rejected by {interaction.user.display_name}")
        except discord.HTTPException as e:
            await interaction.response.edit_message(
                content=f"❌ Could not kick member: {e}", embed=None, view=None
            )
            return

        # Update the parent mod notification embed
        result_embed = discord.Embed(
            title="<:optis:1488294635519479918> Member rejected",
            description=(
                f"**{self.parent_view.member.display_name}** has been kicked by {interaction.user.mention}.\n"
                "A private message was sent to inform them."
            ),
            color=discord.Color.red(),
            timestamp=datetime.datetime.now(ZoneInfo("Europe/Paris"))
        )
        if self.parent_view.member.avatar:
            result_embed.set_thumbnail(url=self.parent_view.member.avatar.url)
        result_embed.set_footer(text=f"Action by {interaction.user.display_name}")

        await self.parent_view._mark_handled(interaction, result_embed)

        # Close the ephemeral confirmation message
        await interaction.edit_original_response(
            content="<a:nyx:1489283483376292004> Member kicked.", embed=None, view=None
        )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary, emoji="↩️")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.mod.id:
            await interaction.response.send_message("❌ That button doesn't belong to you.", ephemeral=True)
            return
        self.stop()
        await interaction.response.edit_message(content="<a:zykan:1489280289027915997> Rejection cancelled.", embed=None, view=None)


# ── Cog principal ─────────────────────────────────────────────────────────────

class MemberApprovalCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild_config = config.GUILDS.get(member.guild.id)
        if not guild_config:
            return

        log_channel_id = guild_config.get("SALON_NEW_MEMBERS")
        if not log_channel_id:
            return

        log_channel = self.bot.get_channel(log_channel_id)
        if not log_channel:
            return

        club_name = guild_config.get("Name", member.guild.name)

        # Build the notification embed
        embed = discord.Embed(
            title="<:announcement:1496817320440500335> New member request",
            description=(
                f"{member.mention} (**{member.display_name}**) just joined **{club_name}**.\n\n"
                f"Account created: <t:{int(member.created_at.timestamp())}:R>\n"
                f"Joined at: <t:{int(member.joined_at.timestamp())}:R>"
            ),
            color=discord.Color.blurple(),
            timestamp=datetime.datetime.now(ZoneInfo("Europe/Paris"))
        )

        if member.avatar:
            embed.set_thumbnail(url=member.avatar.url)
        else:
            embed.set_thumbnail(url=member.default_avatar.url)

        embed.add_field(
            name="<:usefull:1488293835137093683> Actions",
            value=(
                "<:players:1496861469583867987> **Accept** — Gives the Member role and adds to the club list\n"
                "<:optis:1488294635519479918> **Reject** — Kicks the member (with confirmation)\n"
                "<:notif:1496819951296839811> **Ignore** — Dismisses this notification"
            ),
            inline=False
        )
        embed.set_footer(text=f"User ID: {member.id}")

        colead_role = member.guild.get_role(guild_config["COLEAD"])
        ping = colead_role.mention if colead_role else ""

        view = MemberApprovalView(member=member, guild_config=guild_config)
        await log_channel.send(content=ping, embed=embed, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(MemberApprovalCog(bot))
