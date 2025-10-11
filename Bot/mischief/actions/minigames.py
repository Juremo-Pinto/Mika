from mischief.interface import TextMischief


class MINIGAMES(TextMischief):
    mischief_name = 'minigames'
    mischief_description = "reacts with pandemonium emote every time there is 'minigame' in a message"
    
    def check(self, normalized_text, message):
        return 'minigame' in normalized_text
    
    async def execute(self, normalized_text, message):
        await message.add_reaction("<:MINIGAMES:1400192834073530400>")