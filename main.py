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

c.execute('''CREATE TABLE IF NOT EXISTS tickets (id INTEGER PRIMARY KEY, service_name TEXT, initial_price REAL, taxes TEXT, responsible TEXT, user TEXT, notes TEXT, generated_at DATETIME)''')
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

        embed.set_field_at(0, name="Passo 2", value="Digite o preço inicial do serviço:")
        await ctx.send(embed=embed)
        msg = await bot.wait_for('message', check=check, timeout=60)
        ticket_info['initial_price'] = float(msg.content)

        embed.set_field_at(0, name="Passo 3", value="Deseja adicionar taxas? (sim/não)")
        await ctx.send(embed=embed)
        msg = await bot.wait_for('message', check=check, timeout=60)
        add_taxes = msg.content.lower() == "sim"
        taxes = []

        if add_taxes:
            while True:
                embed.set_field_at(0, name="Taxa", value="Digite o nome da taxa (ou 'fim' para concluir):")
                await ctx.send(embed=embed)
                msg = await bot.wait_for('message', check=check, timeout=60)
                tax_name = msg.content
                if tax_name.lower() == 'fim':
                    break
                embed.set_field_at(0, name="Taxa", value=f"Digite o valor da taxa '{tax_name}' (em dólares):")
                await ctx.send(embed=embed)
                msg = await bot.wait_for('message', check=check, timeout=60)
                tax_value = float(msg.content)
                taxes.append((tax_name, tax_value))

            total_tax = sum(tax[1] for tax in taxes)
        else:
            total_tax = 0.0

        total_price = ticket_info['initial_price'] + total_tax

        embed.set_field_at(0, name="Passo 4", value="Digite o nome do responsável:")
        await ctx.send(embed=embed)
        msg = await bot.wait_for('message', check=check, timeout=60)
        ticket_info['responsible'] = msg.content

        embed.set_field_at(0, name="Passo 5", value="Digite o nome do usuário:")
        await ctx.send(embed=embed)
        msg = await bot.wait_for('message', check=check, timeout=60)
        ticket_info['user'] = msg.content

        embed.set_field_at(0, name="NOTAS", value="Digite suas observações (opcional):")
        await ctx.send(embed=embed)
        msg = await bot.wait_for('message', check=check, timeout=60)
        ticket_info['notes'] = msg.content

        await generate_and_send_ticket(ctx, total_price, taxes)
    except TimeoutError:
        await ctx.send("Tempo esgotado. A criação do ticket foi cancelada.")

def generate_ticket_id():
    c.execute("SELECT MAX(id) FROM tickets")
    result = c.fetchone()
    if result[0]:
        return result[0] + 1
    else:
        return 1

async def generate_and_send_ticket(ctx, total_price, taxes):
    ticket_image = Image.new('RGB', (400, 500), color='#e9e5cd')
    draw = ImageDraw.Draw(ticket_image)

    font_size = 20
    font = ImageFont.truetype("cour.ttf", font_size)

    draw.text((10, 10), f'ID: {ticket_info["id"]}', fill='black', font=font)
    draw.text((10, 40), f'Serviço: {ticket_info["service_name"]}', fill='black', font=font)
    draw.text((10, 70), f'Preço Inicial: ${ticket_info["initial_price"]:.2f}', fill='black', font=font)

    if taxes:
        y_position = 100
        for i, (tax_name, tax_value) in enumerate(taxes):
            draw.text((10, y_position), f'{tax_name}: ${tax_value:.2f}', fill='black', font=font)
            y_position += 30
        draw.line([(10, y_position), (390, y_position)], fill='black', width=2)

    if 'notes' in ticket_info:
        y_position += 30
        draw.text((10, y_position), 'NOTAS:', fill='black', font=font)
        y_position += 30
        draw.text((10, y_position), ticket_info['notes'], fill='black', font=font)
        draw.line([(10, y_position + 30), (390, y_position + 30)], fill='black', width=2)

    y_position += 30
    draw.text((10, y_position), f'Valor Total: ${total_price:.2f}', fill='black', font=font)

    y_position += 100
    draw.text((10, y_position), f'Data e Hora: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', fill='black', font=font)
    y_position += 30
    draw.text((10, y_position), "TL STORE systems", fill='black', font=font)

    c.execute("INSERT INTO tickets (id, service_name, initial_price, taxes, responsible, user, notes, generated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              (ticket_info["id"], ticket_info["service_name"], ticket_info["initial_price"], str(taxes), ticket_info["responsible"], ticket_info["user"], ticket_info.get("notes", ""), datetime.now()))
    conn.commit()

    image_buffer = io.BytesIO()
    ticket_image.save(image_buffer, format='PNG')
    image_buffer.seek(0)

    embed = discord.Embed(title="Ticket Fiscal Gerado", color=discord.Colour(0xFFFFFF))
    embed.set_image(url="attachment://ticket.png")
    await ctx.send(embed=embed, file=discord.File(image_buffer, filename='ticket.png'))

@bot.command(name='tickets')
async def list_tickets(ctx):
    c.execute("SELECT id, service_name, initial_price, taxes, responsible, user, notes, generated_at FROM tickets")
    tickets = c.fetchall()

    if not tickets:
        await ctx.send("Nenhum ticket foi gerado ainda.")
    else:
        message = "Lista de Tickets:\n"
        for ticket in tickets:
            message += f"ID: {ticket[0]}, Serviço: {ticket[1]}, Preço Inicial: ${ticket[2]:.2f}\n"
            taxes = eval(ticket[3])
            if taxes:
                message += "Taxas:\n"
                for tax_name, tax_value in taxes:
                    message += f"{tax_name}: ${tax_value:.2f}\n"
            if ticket[6]:
                message += f'NOTAS: {ticket[6]}\n'
            message += f'Gerado em: {ticket[7]}\n\n'

        await ctx.send(message)

@bot.command(name='cleartickets')
async def clear_tickets(ctx):
    c.execute("DELETE FROM tickets")
    conn.commit()
    await ctx.send("Todos os tickets foram excluídos com sucesso.")

bot.run('SEU TOKEN AQUI')
