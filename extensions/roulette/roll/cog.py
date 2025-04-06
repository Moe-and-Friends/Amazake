import logging
import random

from . import debounce
from ..action.timeout import Timeout
from ..config import config
from ..identifiers import identifiers
from ..roles.roles import get_timeout_role

from api_extensions import members
from asyncio import sleep
from database.redis_client import get_redis
from datetime import datetime, timedelta, timezone
from discord import Forbidden, HTTPException, Member, Message
from discord.ext.commands import Bot, Cog, guild_only
from extensions.roulette.roll import permissions, timeout
from typing import Set

_redis_client = get_redis()


class Roll(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.logger.info("Loaded Roll cog")

    async def cog_command_error(self, ctx, error: Exception) -> None:
        self.logger.warning(error)

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
        is_administrator = permissions.is_admin(message.author)
        # All administrators are implicitly moderators and are protected
        is_moderator = permissions.is_moderator(message.author) or is_administrator

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
                effect = self.fetch_action()

                if configured_delay := config.roll_timeout_response_delay_seconds():
                    delay = random.randint(1, configured_delay)
                    self.logger.debug(f"Artificially waiting {delay} seconds before continuing")
                    await sleep(delay)

                match effect:
                    case Timeout():
                        await timeout.native_timeout(effect, message, target)
                    case _:
                        self.logger.critical("Received an unsupported action type.")
                        await message.reply("Sorry, something went wrong. Please contact an administrator!")
                        continue

    def fetch_action(self) -> Timeout | None:
        """
        Fetches an action (i.e. timeout) to apply to the user.
        :return: One of the action types.
        """
        rolls = config.rolls()

        # Create a list of weights used to determine actions.
        weights: list[int] = [r.weight for r in rolls]
        actions: list[Timeout | None] = [r.action for r in rolls]
        self.logger.debug("Loaded {count} roll weights.".format(count=int(len(weights))))

        action = random.choices(population=actions, weights=weights, k=1)[0]
        return action

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
        if not reference_message:
            self.logger.warning(
                f"Unable to resolve reference message {reference_message.id} from the Discord API. Assuming no mentions...")
            return set()
        self.logger.debug(f"Fetched reference message {reference_message.id} from the Discord API")

        reference_message_author = await members.get_member(reference_message.author.id, message.guild)
        if not reference_message_author:
            self.logger.warning(
                f"Unable to fetch reference message author from the Discord API. Assuming no mentions...")
            return set()
        self.logger.debug(f"Fetched reference message author {reference_message_author.name}")

        # Note: It's okay to return mentions of the bot itself.
        return {reference_message_author}

    async def _determine_targets(self, message: Message) -> Set[Member]:
        """
        Determines the actual targets of a given message.
        :param message: The message event to process
        :return: A list of Discord Members that the roll is targeting.
        """
        is_moderator = permissions.is_moderator(message.author)
        is_administrator = permissions.is_admin(message.author)

        # Check if user *can* even mention first, to reduce fetch calls to the API.
        if not is_moderator and not is_administrator:
            self.logger.debug("Message author cannot roll for others - returning author as target.")
            return {message.author}

        # Ignore mentions of the bot user itself.
        mentions = set(
            [mention for mention in await self._determine_mentions(message) if mention.id != self.bot.user.id])
        if len(mentions) > 0:
            self.logger.debug("User is a moderator or administrator, targeting mentioned users instead.")
            return mentions

        self.logger.debug("Didn't find any mentions, returning message author as target.")
        return {message.author}

    async def _DO_NOT_USE_apply_timeout_roles(self, target: Member, duration_label: str) -> bool:
        """
        Applies the specified timeout roll onto a user.
        :return: Whether the role was applied.
        """
        role = await get_timeout_role(target.guild)
        if not role:
            raise RuntimeError(f"Timeout role doesn't seem to exist. Please check your config.")

        try:
            await target.add_roles(role,
                                   reason=f"Applying role as part of Mutebot Timeout of duration {duration_label}")
            self.logger.info(f"Applied timeout role to user {target.name}")
        except Forbidden:
            raise RuntimeError(f"Bot doesn't have sufficient permissions to apply role {role.id} ({role.name}).")
        except HTTPException:
            self.logger.critical(
                f"Adding role {role.id} ({role.name}) failed for no apparent reason. Please investigate!")
            return False
        return True

    async def _DO_NOT_USE_record_timeout_in_redis(self, duration: timedelta, member: Member):
        """
        Record a timeout into Redis (for future processing).
        :param duration: The duration of the timeout that will be applied.
        :param member: The member to time out.
        """

        # Calculate the time the user will be *unmuted* at.
        # Because Mutebot instances can be deployed across a variety of timezones, prefer to always use a timezone-aware
        # datetime object in UTC. (Don't use datetime.utcnow()).
        unmute_time = datetime.now(timezone.utc) + duration

        # Use Redis' ZADD to store users' mute types in a ranked fashion.
        # The unmute time (in unixtime) represents the score.
        # See: https://redis.io/docs/latest/commands/zadd/
        key = f"{identifiers.PACKAGE_KEY}_{config.guild()}"
        resp = _redis_client.zadd(name=key, mapping={member.id: unmute_time.timestamp()}, ch=True)

        if resp != 1:
            return RuntimeError(f"Redis reported {resp} scores were updated for user {member.id} ({member.name})")

        self.logger.info(
            f"Recorded timeout for user {member.id} ({member.name}) expiring at {unmute_time.strftime('%c')}")
        return True
