from mischief.interface import TextMischief


class kysResponse(TextMischief):
    mischief_name = "kys"
    mischief_description = "deletes any KILL YOURSELF messeges and replaces them with a friendly reminder to keep yourself safe"
    
    def check(self, normalized_text, message):
        return any(badword in normalized_text for badword in ['kill yourself', 'kys']) and message.author.id != self._bot.user.id
    
    async def execute(self, normalized_text, message):
        await message.channel.send("https://tenor.com/view/kys-keep-yourself-safe-low-tier-god-gif-24664025")
        await message.delete()