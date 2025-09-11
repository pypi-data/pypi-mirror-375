__all__ = [
    'dshell_respond_interaction'
]

from types import NoneType
from discord import Interaction, Embed
from pycordViews import EasyModifiedViews


async def dshell_respond_interaction(ctx: Interaction, content: str = None, delete=None, mention: bool = None, embeds=None, view=None):
    """
    Responds to a message interaction on Discord
    """

    if delete is not None and not isinstance(delete, (int, float)):
        raise Exception(f'Delete parameter must be a number (seconds) or None, not {type(delete)} !')

    mention_author = mention if mention is not None else False

    from .._DshellParser.ast_nodes import ListNode

    if not isinstance(embeds, (ListNode, Embed, NoneType)):
        raise Exception(f'Embeds must be a list of Embed objects or a single Embed object, not {type(embeds)} !')

    if embeds is None:
        embeds = ListNode([])

    elif isinstance(embeds, Embed):
        embeds = ListNode([embeds])

    if not isinstance(view, (EasyModifiedViews, NoneType)):
        raise Exception(f'Channel must be an UI or None, not {type(view)} !')

    sended_message = await ctx.response.send_message(
                                     content=str(content),
                                     ephemeral=not mention_author,
                                     delete_after=delete,
                                     embeds=embeds,
                                     view=view)

    return sended_message.id

