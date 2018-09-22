from util import default


owners = default.get("conf.json").owners
helper = default.get("conf.json").helpers

def is_owner(ctx):
    return ctx.author.id in owners

def is_helper(ctx):
    return ctx.author.id in helper
