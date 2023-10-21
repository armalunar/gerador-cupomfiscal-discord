import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import io
import random
import sqlite3

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='.', intents=intents)

conn = sqlite3.connect('tickets.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS tickets (id INTEGER PRIMARY KEY, service_name TEXT, price REAL, responsible TEXT, user TEXT)''')
conn.commit()

ticket_info = {}

@bot.event
async def on_ready():
    print(f'Bot está online como {bot.user.name}')

@bot.command(name='ticket')
async def start_ticket(ctx):
    ticket_info['id'] = generate_ticket_id()
    
    embed = discord.Embed(title="Criando um novo ticket fiscal", color=0x00ff00)
    embed.add_field(name="Passo 1", value="Digite o nome do serviço:")
    await ctx.send(embed=embed)
    
    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel

    try:
        msg = await bot.wait_for('message', check=check, timeout=60)
        ticket_info['service_name'] = msg.content

        embed.set_field_at(0, name="Passo 2", value="Digite o preço do item:")
        await ctx.send(embed=embed)
        msg = await bot.wait_for('message', check=check, timeout=60)
        ticket_info['price'] = float(msg.content)
        
        embed.set_field_at(0, name="Passo 3", value="Digite o nome do responsável:")
        await ctx.send(embed=embed)
        msg = await bot.wait_for('message', check=check, timeout=60)
        ticket_info['responsible'] = msg.content
        
        embed.set_field_at(0, name="Passo 4", value="Digite o nome do usuário:")
        await ctx.send(embed=embed)
        msg = await bot.wait_for('message', check=check, timeout=60)
        ticket_info['user'] = msg.content
        
        await generate_and_send_ticket(ctx)
    except TimeoutError:
        await ctx.send("Tempo esgotado. A criação do ticket foi cancelada.")

def generate_ticket_id():
    c.execute("SELECT MAX(id) FROM tickets")
    result = c.fetchone()
    if result[0]:
        return result[0] + 1
    else:
        return 1

async def generate_and_send_ticket(ctx):
    ticket_image = Image.new('RGB', (400, 300), color='#e9e5cd')
    draw = ImageDraw.Draw(ticket_image)

    font_size = 20
    font = ImageFont.truetype("cour.ttf", font_size)

    draw.text((10, 10), f'ID: {ticket_info["id"]}', fill='black', font=font)
    draw.text((10, 40), f'Serviço: {ticket_info["service_name"]}', fill='black', font=font)
    draw.text((10, 70), f'Preço: ${ticket_info["price"]:.2f}', fill='black', font=font)
    draw.text((10, 100), f'Responsável: {ticket_info["responsible"]}', fill='black', font=font)
    draw.text((10, 130), f'Usuário: {ticket_info["user"]}', fill='black', font=font)

    phrase = "TL STORE systems"
    draw.text((10, 260), phrase, fill='black', font=font)

    c.execute("INSERT INTO tickets (id, service_name, price, responsible, user) VALUES (?, ?, ?, ?, ?)",
              (ticket_info["id"], ticket_info["service_name"], ticket_info["price"], ticket_info["responsible"], ticket_info["user"]))
    conn.commit()

    image_buffer = io.BytesIO()
    ticket_image.save(image_buffer, format='PNG')
    image_buffer.seek(0)

    embed = discord.Embed(title="Ticket Fiscal Gerado", color='#ffffff')
    embed.set_image(url="attachment://ticket.png")
    await ctx.send(embed=embed, file=discord.File(image_buffer, filename='ticket.png'))

@bot.command(name='tickets')
async def list_tickets(ctx):
    c.execute("SELECT id, service_name, price, responsible, user FROM tickets")
    tickets = c.fetchall()

    if not tickets:
        await ctx.send("Nenhum ticket foi gerado ainda.")
    else:
        message = "Lista de Tickets:\n"
        for ticket in tickets:
            message += f"ID: {ticket[0]}, Serviço: {ticket[1]}, Preço: ${ticket[2]:.2f}, Responsável: {ticket[3]}, Usuário: {ticket[4]}\n"

        await ctx.send(message)

@bot.command(name='cleartickets')
async def clear_tickets(ctx):
    c.execute("DELETE FROM tickets")
    conn.commit()
    await ctx.send("Todos os tickets foram excluídos com sucesso.")

bot.run('MTE2NTQxMzg2NDk3Njk1MzQ3NQ.GPdVvw.brFT4Tdtk0pRZAzWSqFVtHDdEk2btrMoMrPcRg')
