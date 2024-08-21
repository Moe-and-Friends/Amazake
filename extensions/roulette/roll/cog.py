import logging
import random

from . import action, debounce, stats
from ..config import config

from asyncio import sleep
from datetime import timedelta
from discord import Member, Message, User, Role
from discord.ext.commands import Bot, Cog, guild_only
from typing import Set


class Roll(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.logger = logging.getLogger("roulette.roll")
        self.logger.info("Loaded Roll cog")

    async def cog_command_error(self, ctx, error: Exception) -> None:
        self.logger.warning(str(error))

    @Cog.listener()
    @guild_only()
    async def on_message(self, message: Message):
        if message.author == self.bot.user:
            self.logger.debug(f"Ignoring self message: {message.id}")
            return

        if message.author.bot:
            self.logger.debug(f"Ignoring bot message: {message.id}")
            return

        # Get user's permission status.
        is_administrator = self._is_admin(message.author)
        # All administrators are implicitly moderators and are protected
        is_moderator = self._is_moderator(message.author) or is_administrator

        if str(message.channel.id) not in config.channels():
            if not (is_administrator or is_moderator):
                self.logger.debug(f"Ignoring message (channel not observed): {message.id}")
                return

        # Check message against all match patterns
        is_match = False
        for pattern in config.roll_match_patterns():
            if pattern.search(message.content):
                is_match = True
                break
        if not is_match:
            self.logger.debug(f"Ignoring message (no match): {message.id}")
            return

        self.logger.info(
            f"Processing message from user {message.author.name}: [{str(message.id)[-4:]}]: {message.content}...")

        should_debounce = not is_moderator and not is_administrator and debounce.should_debounce(message.author.id)
        if should_debounce:
            self.logger.info(f"Debouncing message ...{str(message.id)[-4:]} from {message.author.name}")
            return

        # At this point, an action will be taken. Send a typing notification indicator.
        async with message.channel.typing():

            # Determine the targets for this rollout command.
            targets = await self._determine_targets(message)
            self.logger.debug(f"Starting roll for users: {', '.join([member.name for member in targets])}")

            for target in targets:
                self.logger.info(f"Now processing roll for user: {target.name}")
                effect = action.fetch()

                if configured_delay := config.roll_timeout_response_delay_seconds():
                    delay = random.randint(1, configured_delay)
                    self.logger.debug(f"Artificially waiting {delay} seconds before continuing")
                    await sleep(delay)

                if isinstance(effect, action.Timeout):
                    self.logger.info(f"Rolled timeout of length {effect.duration_label} for {target.name}")
                    await self._timeout(timedelta(minutes=effect.duration), effect.duration_label, message, target)
                else:
                    self.logger.critical("Received an unsupported action type.")
                    continue

    def _is_protected(self, member: Member) -> bool:
        protected = set(config.protected())
        is_protected = not protected.isdisjoint(set([str(role.id) for role in member.roles]))
        self.logger.debug(f"User {member.name}'s protected status: {is_protected}")
        return is_protected

    def _is_moderator(self, member: Member) -> bool:
        moderators = set(config.moderator())
        is_moderator = not moderators.isdisjoint(set([str(role.id) for role in member.roles]))
        self.logger.debug(f"User {member.name}'s mod status: {is_moderator}")
        return is_moderator

    def _is_admin(self, user: User | Member) -> bool:
        is_admin = str(user.id) in config.administrator()
        self.logger.debug(f"User {user.name}'s admin status: {is_admin}")
        return is_admin

    def _get_timeout_roles(self, message: Message) -> Set[Role]:
        role_ids = config.timeout_roles()
        timeout_roles = set()
        for role_id in role_ids:
            timeout_roles.add(action.Role(role_id))
        return timeout_roles
    
    async def _determine_mentions(self, message: Message) -> Set[Member]:
        """
        This is an investigative workaround to find all mentions + replies in a message.
        The Discord API doesn't always fetch reference (replied-to) messages, likely to reduce API calls. But this bot
        still needs it to enable mods+ to trigger rolls for other users via reply-mention.

        This function will filter out Users (e.g. DMs) only.
        """
        # Mentions are only supported in Guilds. Filter out User mentions (i.e. in DMs).
        mentions = set([mention for mention in message.mentions if isinstance(mention, Member)])
        # If there are mentions already (usual case), then the API worked okay and return immediately.
        if mentions:
            mentioned_users = [mention.name for mention in mentions]
            self.logger.debug(f'Using mentions provided by the API: {", ".join(mentioned_users)}')
            return mentions

        # If the message outright doesn't have a reference, there is no reply mention.
        # Early return if so.
        if not message.reference or not message.reference.message_id:
            self.logger.debug("Message doesn't have any references, so returning empty collection of mentions.")
            return set()

        # Fetch the responded-to message from Discord.
        reference_message = await message.channel.get_partial_message(message.reference.message_id).fetch()
        if reference_message:
            self.logger.debug(f"Fetched reference message {reference_message.id} from the Discord API")
        else:
            self.logger.warning(f"Unable to resolve reference message {reference_message.id} from the Discord API. Assuming no mentions...")
            return set()

        reference_message_author = await message.guild.fetch_member(reference_message.author.id)
        if reference_message_author:
            self.logger.debug(f"Fetched reference message author {reference_message_author.name}")
        else:
            self.logger.warning(f"Unable to fetch reference message author from the Discord API. Assuming no mentions...")
            return set()

        # Note: It's okay to return mentions of the bot itself.
        return {reference_message_author}

    async def _determine_targets(self, message: Message) -> Set[Member]:
        """
        Determines the actual targets of a given message.
        :param message: The message event to process
        :return: A list of Discord Members that the roll is targeting.
        """
        is_moderator = self._is_moderator(message.author)
        is_administrator = self._is_admin(message.author)

        # Check if user *can* even mention first, to reduce fetch calls to the API.
        if not is_moderator and not is_administrator:
            self.logger.debug("Message author cannot roll for others - returning author as target.")
            return {message.author}

        # Ignore mentions of the bot user itself.
        mentions = set([mention for mention in await self._determine_mentions(message) if mention.id != self.bot.user.id])
        if len(mentions) > 0:
            self.logger.debug("User is a moderator or administrator, targeting mentioned users instead.")
            return mentions

        self.logger.debug("Didn't find any mentions, returning message author as target.")
        return {message.author}

    async def _timeout(self,
                       duration: timedelta,
                       duration_label: str,
                       message: Message,
                       target: Member):

        is_self = target == message.author
        self.logger.debug(f"Message is targeting self: {is_self}")

        timeout_roles = self._get_timeout_roles(message)

        # If target is protected, respond with a safe message and return immediately.
        if self._is_protected(target) or self._is_moderator(target) or self._is_admin(target):
            if is_self:
                self.logger.info("Responding with protected message for self")
                reply = random.choice(config.roll_timeout_protected_messages_self())
                await message.reply(reply.format(user_name=target.display_name,
                                                 duration_label=duration_label))
            else:
                self.logger.info("Responding with protected message for targeted user")
                reply = random.choice(config.roll_timeout_protected_messages_other())
                await message.reply(reply.format(user_name=target.display_name,
                                                 duration_label=duration_label))
            return

        # Non-native mutes aren't supported yet.
        if duration > timedelta(days=28):
            self.logger.warning(f"Received a mute for {duration_label}. This duration is currently unsupported.")
            await message.reply("Sorry, something went wrong. Please roll again!")
            return

        await target.timeout(duration, reason=f"Timed out for {duration_label} via Roulette")
        self.logger.info(f"Timed {target.name} out for {duration_label}")

        await target.add_roles(*timeout_roles, reason = f"Timed out for {duration_label} via Roulette")
        self.logger.info(f"Applied timeout roles to {target.name}")

        if is_self:
            self.logger.info("Responding with affected message for self")
            reply = random.choice(config.roll_timeout_affected_messages_self())
            await message.reply(reply.format(user_name=target.display_name,
                                             duration_label=duration_label))
        else:
            self.logger.info("Responding with affected message for targeted user")
            reply = random.choice(config.roll_timeout_affected_messages_other())
            await message.reply(reply.format(user_name=target.display_name,
                                             duration_label=duration_label))

        stats.timeout_record_stats(duration, message)
