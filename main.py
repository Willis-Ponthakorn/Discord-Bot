import discord
from discord.ext import commands
from discord import app_commands, ui
import os
from typing import Optional

token = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix='!', intents=intents)
serverID = discord.Object(id=os.getenv("SERVER_ID"))
announcementChannelID = int(os.getenv("ANNOUNCEMENT_CHANNEL_ID"))

@bot.event
async def on_ready():
    print(f'Logged in as, {bot.user.name}')

    try:
        synced = await bot.tree.sync(guild=serverID)
        print(f'Synced: {synced}')

    except Exception as e:
        print(f'Error: {e}')

@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    # Ignore the bot's own reaction
    if payload.user_id == bot.user.id:
        return

    # Check if the emoji is the red X
    if str(payload.emoji) == '❌':
        channel = bot.get_channel(payload.channel_id)
        if not channel: return

        try:
            message = await channel.fetch_message(payload.message_id)

            # Security: Only allow deletion if the user's ID is mentioned in the announcement text
            # This identifies them as the original "Announcer"
            if f"<@{payload.user_id}>" in message.content:
                await message.delete()
        except discord.NotFound:
            pass  # Message already deleted
        except Exception as e:
            print(f"Error deleting message: {e}")

class AnnouncementModal(ui.Modal):
    def __init__(self, attachment: Optional[discord.Attachment] = None):
        super().__init__(title='สร้างประกาศใหม่')
        self.attachment = attachment

    announcement_title = ui.TextInput(
        label='หัวข้อ',
        placeholder='ใส่หัวข้อประกาศที่นี่...',
        style=discord.TextStyle.short,
    )

    announcement_message = ui.TextInput(
        label='รายละเอียด',
        placeholder='ใส่ข้อความประกาศ... (ขึ้นบรรทัดใหม่ได้)',
        style=discord.TextStyle.paragraph,
        max_length=1500,
    )

    async def on_submit(self, interaction: discord.Interaction):
        # We need to defer because uploading files can sometimes take a second
        await interaction.response.defer(ephemeral=True)

        channel = bot.get_channel(announcementChannelID)

        announcement_text = (
            f"# 📢 หัวข้อ: {self.announcement_title.value}\n"
            f"{self.announcement_message.value}\n\n"
            f"-# ข้อความนี้ถูกประกาศจาก {interaction.user.mention}\n"
            f"||@everyone||\n"
        )

        # Convert the attachment to a discord.File
        file = None
        if self.attachment:
            file = await self.attachment.to_file()

        # Send the text and the file together
        sent_msg = await channel.send(content=announcement_text, file=file)

        await interaction.followup.send("ประกาศเสร็จสิ้น!", ephemeral=True)


@bot.tree.command(name="announce", description="ใช้ประกาศข้อมูลสำคัญๆ (แนบรูปภาพได้)", guild=serverID)
@app_commands.describe(image="แนบรูปภาพที่ต้องการประกาศ")
async def announce(interaction: discord.Interaction, image: Optional[discord.Attachment] = None):
    # This opens the popup box for the user and carries the image over
    await interaction.response.send_modal(AnnouncementModal(attachment=image))

bot.run(token)




