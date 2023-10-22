import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import io
import sqlite3
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='.', intents=intents)

conn = sqlite3.connect('tickets.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS tickets (id INTEGER PRIMARY KEY, service_name TEXT, price REAL, responsible TEXT, user TEXT, email TEXT, notes TEXT, generated_at DATETIME)''')
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

        embed.set_field_at(0, name="Passo 4", value="Digite o nome do cliente:")
        await ctx.send(embed=embed)
        msg = await bot.wait_for('message', check=check, timeout=60)
        ticket_info['user'] = msg.content

        embed.set_field_at(0, name="Passo 5", value="Digite o email:")
        await ctx.send(embed=embed)
        msg = await bot.wait_for('message', check=check, timeout=60)
        ticket_info['email'] = msg.content

        embed.set_field_at(0, name="Passo 6", value="Digite suas observações (opcional):")
        await ctx.send(embed=embed)
        msg = await bot.wait_for('message', check=check, timeout=60)
        ticket_info['notes'] = msg.content

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
    ticket_image = Image.new('RGB', (600, 800), color='#e9e5cd')
    draw = ImageDraw.Draw(ticket_image)

    font_size = 20
    font = ImageFont.truetype("cour.ttf", font_size)

    draw.text((10, 10), f'TICKET FISCAL', fill='black', font=font)

    y_offset = 40
    draw.text((10, y_offset), f'ID: {ticket_info["id"]}', fill='black', font=font)
    y_offset += 30
    draw.text((10, y_offset), f'Serviço: {ticket_info["service_name"]}', fill='black', font=font)
    y_offset += 30
    draw.text((10, y_offset), f'Preço: ${ticket_info["price"]:.2f}', fill='black', font=font)
    y_offset += 30
    draw.text((10, y_offset), f'Reponsável: {ticket_info["responsible"]}', fill='black', font=font)
    y_offset += 30
    draw.text((10, y_offset), f'Usuário: {ticket_info["user"]}', fill='black', font=font)
    y_offset += 30
    draw.text((10, y_offset), f'Email: {ticket_info["email"]}', fill='black', font=font)
    y_offset += 40

    if 'notes' in ticket_info:
        draw.text((10, y_offset), 'NOTAS:', fill='black', font=font)
        y_offset += 30
        notes = ticket_info['notes'].split('\n')
        for note in notes:
            draw.text((10, y_offset), note, fill='black', font=font)
            y_offset += 30

    current_time = datetime.now().strftime("%Y-%m-%d")
    draw.text((10, 670), f'Gerado em: {current_time}', fill='black', font=font)

    phrase = "TL STORE systems"
    draw.text((10, 770), phrase, fill='black', font=font)

    c.execute("INSERT INTO tickets (id, service_name, price, responsible, user, email, notes, generated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              (ticket_info["id"], ticket_info["service_name"], ticket_info["price"], ticket_info["responsible"], ticket_info["user"], ticket_info["email"], ticket_info.get('notes', ''), current_time))
    conn.commit()

    image_buffer = io.BytesIO()
    ticket_image.save(image_buffer, format='PNG')
    image_buffer.seek(0)

    embed = discord.Embed(title="Ticket Fiscal Gerado", color=discord.Colour(0xFFFFFF))
    embed.set_image(url="attachment://ticket.png")
    await ctx.send(embed=embed, file=discord.File(image_buffer, filename='ticket.png'))

@bot.command(name='tickets')
async def list_tickets(ctx):
    c.execute("SELECT id, service_name, price, responsible, user, email, notes, generated_at FROM tickets")
    tickets = c.fetchall()

    if not tickets:
        await ctx.send("Nenhum ticket foi gerado ainda.")
    else:
        for ticket in tickets:
            await send_ticket_image(ctx, ticket)

async def send_ticket_image(ctx, ticket):
    ticket_image = Image.new('RGB', (600, 800), color='#e9e5cd')
    draw = ImageDraw.Draw(ticket_image)

    font_size = 20
    font = ImageFont.truetype("cour.ttf", font_size)

    draw.text((10, 10), f'TICKET FISCAL', fill='black', font=font)

    y_offset = 40
    draw.text((10, y_offset), f'ID: {ticket[0]}', fill='black', font=font)
    y_offset += 30
    draw.text((10, y_offset), f'Serviço: {ticket[1]}', fill='black', font=font)
    y_offset += 30
    draw.text((10, y_offset), f'Preço: ${ticket[2]:.2f}', fill='black', font=font)
    y_offset += 30
    draw.text((10, y_offset), f'Reponsável: {ticket[3]}', fill='black', font=font)
    y_offset += 30
    draw.text((10, y_offset), f'Usuário: {ticket[4]}', fill='black', font=font)
    y_offset += 30
    draw.text((10, y_offset), f'Email: {ticket[5]}', fill='black', font=font)
    y_offset += 40

    if ticket[6]:
        draw.text((10, y_offset), 'NOTAS:', fill='black', font=font)
        y_offset += 30
        notes = ticket[6].split('\n')
        for note in notes:
            draw.text((10, y_offset), note, fill='black', font=font)
            y_offset += 30

    current_time = ticket[7][:10]
    draw.text((10, 670), f'Gerado em: {current_time}', fill='black', font=font)

    phrase = "TL STORE systems"
    draw.text((10, 770), phrase, fill='black', font=font)

    image_buffer = io.BytesIO()
    ticket_image.save(image_buffer, format='PNG')
    image_buffer.seek(0)

    embed = discord.Embed(title=f"Ticket Fiscal #{ticket[0]}", color=discord.Colour(0xFFFFFF))
    embed.set_image(url="attachment://ticket.png")
    await ctx.send(embed=embed, file=discord.File(image_buffer, filename='ticket.png'))

@bot.command(name='cleartickets')
async def clear_tickets(ctx):
    c.execute("DELETE FROM tickets")
    conn.commit()
    await ctx.send("Todos os tickets foram excluídos com sucesso.")

bot.run('SEU_TOKEN_AQUI')
