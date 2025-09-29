from mischief.interface import TextMischief


class FatFuck(TextMischief):
    mischief_name = "fat-fuck"
    mischief_description = "Fat Fuck"
    
    def check(self, normalized_text, message):
        return normalized_text == 'fat fuck' and message.author.id != self.bot.user.id
    
    async def execute(self, normalized_text, message):
        await message.channel.send(message.content)