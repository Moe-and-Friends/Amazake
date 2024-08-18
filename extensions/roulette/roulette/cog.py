import logging
import random

from . import action, debounce, stats
from ..config import config

from datetime import timedelta
from discord import Member, Message, User
from discord.ext.commands import Bot, Cog, guild_only
from typing import Set


class Roulette(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.logger = logging.getLogger("roulette")
        self.logger.info("Loaded Roulette cog")

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
        for pattern in config.match_patterns():
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
            targets = self._determine_targets(message)
            self.logger.debug(f"Starting roulette for users: {', '.join([member.name for member in targets])}")

            for target in targets:
                self.logger.info(f"Now processing roulette for user: {target.name}")
                effect = action.fetch()
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

    def _determine_targets(self, message: Message) -> Set[Member]:
        """
        Determines the actual targets of a given message.
        :param message: The message event to process
        :return: A list of Discord Members that the roll is targeting.
        """
        is_moderator = self._is_moderator(message.author)
        is_administrator = self._is_admin(message.author)

        # Ignore mentions of the bot user itself.
        mentions = set([mention for mention in message.mentions if mention.id != self.bot.user.id])
        if (is_moderator or is_administrator) and len(mentions) > 0:
            self.logger.debug("User is a moderator or administrator, targeting mentioned users instead.")
            return mentions

        self.logger.debug("Targeting the message author.")
        return {message.author}

    async def _timeout(self,
                       duration: timedelta,
                       duration_label: str,
                       message: Message,
                       target: Member):

        is_self = target == message.author
        self.logger.debug(f"Message is targeting self: {is_self}")

        # If target is protected, respond with a safe message and return immediately.
        if self._is_protected(target) or self._is_moderator(target) or self._is_admin(target):
            if is_self:
                self.logger.info("Responding with protected message for self")
                reply = random.choice(config.timeout_protected_messages_self())
                await message.reply(reply.format(timeout_user_name=target.display_name,
                                                 timeout_duration_label=duration_label))
            else:
                self.logger.info("Responding with protected message for targeted user")
                reply = random.choice(config.timeout_protected_messages_other())
                await message.reply(reply.format(timeout_user_name=target.display_name,
                                                 timeout_duration_label=duration_label))
            return

        # Non-native mutes aren't supported yet.
        if duration > timedelta(days=28):
            self.logger.warning(f"Received a mute for {duration_label}. This duration is currently unsupported.")
            await message.reply("Sorry, something went wrong. Please roll again!")
            return

        await target.timeout(duration, reason=f"Timed out for {duration_label} via Roulette")
        self.logger.info(f"Timed {target.name} out for {duration_label}")

        if is_self:
            self.logger.info("Responding with affected message for self")
            reply = random.choice(config.timeout_affected_messages_self())
            await message.reply(reply.format(timeout_user_name=target.display_name,
                                             timeout_duration_label=duration_label))
        else:
            self.logger.info("Responding with affected message for targeted user")
            reply = random.choice(config.timeout_affected_messages_other())
            await message.reply(reply.format(timeout_user_name=target.display_name,
                                             timeout_duration_label=duration_label))

        stats.timeout_record_stats(duration, message)