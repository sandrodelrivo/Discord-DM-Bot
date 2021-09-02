# DM Assistant bot using GPT-3

import discord
import openai
import numbers

BOT_TOKEN = open("bot_token.txt", "r").readline()
intents = discord.Intents.default()
intents.messages = True

openai.organization = ""
openai.api_key = ""

client = discord.Client(intents=intents)

# OPEN_AI PROMPTS
DIALOGUE_PROMPT = 'The following is a conversation between a friendly bot that assists DMs in Dungeons and' \
                  ' Dragons and a human. ' \
                  '\n' \
                  'AI: Hello human!\n' \
                  'Human: Hey, I am excited to receive your generated RPG content!\n' \
                  'AI: Awesome, I look forward to making magic items, places, npcs, and more!\n' \
                  'Human: Yea, I appreciate it!\n' \
                  'AI: Let\'s make a campaign together!\n' \
                  'Human: '

MAGIC_ITEM_PROMPT = 'This is a repository of magic items with backstories.\n' \
                    'Name: Armblade\n' \
                    'Item Type: Weapon\n' \
                    'Magic Effect: An Armblade is a magic weapon that attaches to your arm, becoming inseparable from you as long as you are attuned to it. To attune to this item, you must hold it against your forearm for the entire attunement period. As a bonus action, you can retract the Armblade into your forearm or extend it from there. While it is extended, you can use the weapon as if you were holding it, and you cannot use that hand for other purposes.\n' \
                    'Backstory: The Armblade was forged by the legendary forge-master Edmus Tallen for his son, the knight Desmond who lost his fighting hand in battle.\n\n' \
                    'Name: Spellguard\n' \
                    'Item Type: Armor\n' \
                    'Magic Effect: When wearing this armor, you can cast Shield as a reaction.\n' \
                    'Backstory: The Spellguard armor is thought to have been created by an ancient order of mages who were obsessed with protecting their students from the dangers of the outside world. The order lasted for only a few centuries before it was all but wiped out by a devastating plague.\n' \
                    '\nName:'

NAME_PROMPT = 'The following is a list of English names: John, Elizabeth, Richard, Gregory, Mary, Godard\n' \
              'The following is a list of '

NPC_PROMPT = '###\n'\
            'Name: Dorothea\n'\
            'Profession: Singer\n'\
            'Personality: Friendly\n'\
            'Backstory: Dorothea was raised in the countryside but moved to the capital after the war destroyed her home town. She had a beautiful singing voice and so began to sing at a popular tavern. Before long she had attracted the attention of powerful people and became a professional musician.\n'\
            'Plot Hooks: Dorothea has found out about a plot involving the nobility attempting to assimilate the king.\n'\
            '###\n\n'\
            '###\n'\
            'Name:'

GENERATE_DESCRIPTION_PROMPT = 'The following text is flavor text for an RPG game.\n\n'\
'This is a description of a dark cave: The cave before you is pitch black, no light illuminating its inside. Beneath your feet you can feel the squish of damp moss, and smell the scent of fresh water below.\n\n'\
'This is a description of a friendly merchant: The merchant is tall and handsome, with dark black hair and a nice smile.\n\n'\
'This is a description of a '


@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))


@client.event
async def on_message(message):

    if message.author == client.user:
        return

    print("Received a message:", message.content)
    if message.content.startswith('$msg'):
        await on_convo(message)
    if message.content.startswith('$gen'):
        await on_gen(message)


async def on_convo(message):
    print("Message:", message.content[4:])
    prompt_text = DIALOGUE_PROMPT + message.content[4:] + "\nAI:"
    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt_text,
        max_tokens=30,
        stop=['\n'])

    text = response.choices[0].text
    print(text)
    await message.channel.send(text)


async def generate_magic_item(num, name_seed=''):
    response_text = ''
    if name_seed != '':
        name_seed = ' ' + name_seed
    prompt_text = MAGIC_ITEM_PROMPT + name_seed
    print(prompt_text)

    for x in range(num):
        response = openai.Completion.create(
            engine="davinci",
            prompt=prompt_text,
            max_tokens=250,
            stop=['Name:', 'name:'])

        response_text += '\nName:' + name_seed + response.choices[0].text

    print(response_text)
    return response_text


async def generate_desc(prompt, length=50):
    prompt_text = GENERATE_DESCRIPTION_PROMPT + prompt + ":"
    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt_text,
        max_tokens=length,
        stop=['\n']
        )

    return response.choices[0].text


async def generate_npcs(num):
    response_text = ''
    prompt_text = NPC_PROMPT
    print(prompt_text)

    for x in range(num):
        response = openai.Completion.create(
            engine="davinci",
            prompt=prompt_text,
            max_tokens=250,
            stop=['Name:', 'name:', '###'])

        response_text += '\n\n' + response.choices[0].text

    print(response_text)
    return response_text


async def generate_names(name_seed='fantasy'):
    response_text = ''
    prompt_text = NAME_PROMPT + name_seed + ' names:'
    print(prompt_text)
    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt_text,
        frequency_penalty=1,
        max_tokens=100,
        stop=['\n'])

    response_text = response.choices[0].text

    print(response_text)
    return response_text


async def on_gen(message):
    command = message.content[5:]
    print(command)
    args = command.split()

    gen_type = args[0]
    num = 0

    if gen_type == 'item' or gen_type == 'npc':
        num = int(args[1])
        if num < 1:
            return -1
    print("Gen Type", gen_type)

    if gen_type == 'desc':
        print("DESCRIPTION!!!!")
        if isinstance(args[len(args)-1], numbers.Number):
            print("First branch????")
            num = args[len(args)-1]
            args.pop(len(args) - 1)
            args.pop(0)
            prompt = " ".join(args)
            print(prompt)
        else:
            print("Second branch???")
            args.pop(0)
            prompt = " ".join(args)
            print("prompt: ", prompt)

    if gen_type == 'item':
        if len(args) > 2:
            response = await generate_magic_item(num, " ".join(args[2:]))
        else:
            response = await generate_magic_item(num)
    elif gen_type == 'name':
        response = await generate_names(args[1])
    elif gen_type == 'npc':
        response = await generate_npcs(num)
    elif gen_type == 'desc':
        if num != 0:
            response = await generate_desc(prompt, num)
        else:
            response = await generate_desc(prompt)

    while len(response) > 1999:
        await message.channel.send(response[0:1999])
        response = response[2000:]

    await message.channel.send(response)


client.run(BOT_TOKEN)
