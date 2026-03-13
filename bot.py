import discord
from discord import app_commands
from discord.ui import View, Button
import os

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

class TicketView(View):
    def __init__(self, emoji: str):
        super().__init__(timeout=None)
        self.emoji = emoji
        
    @discord.ui.button(label="Tạo Ticket", style=discord.ButtonStyle.primary, custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: Button):
        guild = interaction.guild
        user = interaction.user
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        channel = await guild.create_text_channel(
            name=f"ticket-{user.name}",
            overwrites=overwrites
        )
        
        close_view = CloseTicketView()
        await channel.send(f"{user.mention} Có khách hàng tới này!", view=close_view)
        await interaction.response.send_message(f"Đã tạo ticket tại {channel.mention}", ephemeral=True)

class CloseTicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        
    @discord.ui.button(label="Close", style=discord.ButtonStyle.danger, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        confirm_view = ConfirmCloseView(interaction.channel)
        await interaction.response.send_message("Bạn có chắc chắn muốn xóa ticket này?", view=confirm_view, ephemeral=True)

class ConfirmCloseView(View):
    def __init__(self, channel):
        super().__init__(timeout=None)
        self.channel = channel
        
    @discord.ui.button(label="Xác nhận", style=discord.ButtonStyle.danger, custom_id="confirm_close")
    async def confirm_close(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Đang xóa ticket...", ephemeral=True)
        await self.channel.delete()

class FeedbackView(View):
    def __init__(self, channel: discord.TextChannel, user: discord.User):
        super().__init__(timeout=None)
        self.channel = channel
        self.user = user
        
    @discord.ui.button(label="5 ⭐️", style=discord.ButtonStyle.success, custom_id="star_5")
    async def star_5(self, interaction: discord.Interaction, button: Button):
        await self.send_feedback(interaction, "5 ⭐️")
        
    @discord.ui.button(label="4 ⭐️", style=discord.ButtonStyle.success, custom_id="star_4")
    async def star_4(self, interaction: discord.Interaction, button: Button):
        await self.send_feedback(interaction, "4 ⭐️")
        
    @discord.ui.button(label="3 ⭐️", style=discord.ButtonStyle.primary, custom_id="star_3")
    async def star_3(self, interaction: discord.Interaction, button: Button):
        await self.send_feedback(interaction, "3 ⭐️")
        
    @discord.ui.button(label="2 ⭐️", style=discord.ButtonStyle.secondary, custom_id="star_2")
    async def star_2(self, interaction: discord.Interaction, button: Button):
        await self.send_feedback(interaction, "2 ⭐️")
        
    @discord.ui.button(label="1 ⭐️", style=discord.ButtonStyle.danger, custom_id="star_1")
    async def star_1(self, interaction: discord.Interaction, button: Button):
        await self.send_feedback(interaction, "1 ⭐️")
        
    async def send_feedback(self, interaction: discord.Interaction, rating: str):
        await interaction.response.send_message(f"Cảm ơn bạn đã đánh giá {rating}!", ephemeral=True)
        await self.channel.send(f"Quý khách {self.user.mention} đã đánh giá {rating}.")

@tree.command(name="createticket", description="Tạo hệ thống ticket")
@app_commands.describe(
    channel="Channel để gửi tin nhắn ticket",
    description="Mô tả cho ticket",
    emoji="Emoji cho nút ticket"
)
async def createticket(interaction: discord.Interaction, channel: discord.TextChannel, description: str, emoji: str):
    view = TicketView(emoji)
    button = view.children[0]
    button.emoji = emoji
    
    embed = discord.Embed(description=description, color=discord.Color.blue())
    await channel.send(embed=embed, view=view)
    await interaction.response.send_message(f"Đã tạo hệ thống ticket tại {channel.mention}", ephemeral=True)

@tree.command(name="feedback", description="Gửi yêu cầu feedback")
@app_commands.describe(
    channel="Channel để gửi kết quả feedback",
    user="User cần đánh giá"
)
async def feedback(interaction: discord.Interaction, channel: discord.TextChannel, user: discord.User):
    view = FeedbackView(channel, user)
    
    embed = discord.Embed(description="Cho tụi mình xin 1 feedback nhé! Xin cảm ơn.", color=discord.Color.gold())
    
    try:
        await user.send(embed=embed, view=view)
        await interaction.response.send_message(f"Đã gửi yêu cầu feedback cho {user.mention}", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message(f"Không thể gửi tin nhắn cho {user.mention}. Họ có thể đã tắt DM.", ephemeral=True)

@client.event
async def on_ready():
    await tree.sync()
    print(f'{client.user} đã sẵn sàng!')

client.run('token_bot_o_day')