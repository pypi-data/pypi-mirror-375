__all__ = [
    'dshell_respond_interaction',
    'dshell_defer_interaction'
]

from types import NoneType
from discord import Interaction, Embed
from pycordViews import EasyModifiedViews


async def dshell_respond_interaction(ctx: Interaction, content: str = None, delete=None, mentions: bool = None, hide: bool = False, embeds=None, view=None) -> int:
    """
    Responds to a message interaction on Discord
    """

    if not isinstance(ctx, Interaction):
        raise Exception(f'Respond to an interaction must be used in an interaction context, not {type(ctx)} !')

    if delete is not None and not isinstance(delete, (int, float)):
        raise Exception(f'Delete parameter must be a number (seconds) or None, not {type(delete)} !')

    if not isinstance(mentions, (NoneType, bool)):
        raise Exception(f'Mention parameter must be a boolean or None, not {type(mentions)} !')

    if not isinstance(hide, bool):
        raise Exception(f'Hide parameter must be a boolean, not {type(hide)} !')

    allowed_mentions = mentions if mentions is not None else False

    from .._DshellParser.ast_nodes import ListNode

    if not isinstance(embeds, (ListNode, Embed, NoneType)):
        raise Exception(f'Embeds must be a list of Embed objects or a single Embed object, not {type(embeds)} !')

    if embeds is None:
        embeds = ListNode([])

    elif isinstance(embeds, Embed):
        embeds = ListNode([embeds])

    if not isinstance(view, (EasyModifiedViews, NoneType)):
        raise Exception(f'View must be an UI bloc or None, not {type(view)} !')

    sended_message = await ctx.response.send_message(
                                     content=str(content),
                                     ephemeral=hide,
                                     allowed_mentions=allowed_mentions,
                                     delete_after=delete,
                                     embeds=embeds,
                                     view=view)

    return sended_message.id

async def dshell_defer_interaction(ctx: Interaction, hide: bool = False) -> bool:
    """
    Defer a message interaction on Discord
    """

    if not isinstance(ctx, Interaction):
        raise Exception(f'Respond to an interaction must be used in an interaction context, not {type(ctx)} !')

    if not isinstance(hide, bool):
        raise Exception(f'Hide parameter must be a boolean, not {type(hide)} !')

    await ctx.response.defer(ephemeral=hide)

    return True