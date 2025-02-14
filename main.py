import io
import discord
from discord.ext import commands
import asyncio
import sqlite3
import random

intents = discord.Intents.default()
intents.message_content = True


db = sqlite3.connect('bot.db')
cur = db.cursor()

bot = commands.Bot(command_prefix='$',intents=intents)

# GLOBAL VARIABLES
game_data = {}
PONTOS_BONUS = 100  # Points bonus
SALDO_BONUS = 10    # Coins bonus

# FUNCTIONS
async def show_messagebox(ctx, title, color):
    em = discord.Embed(title=title, color=color)
    await ctx.send(embed=em)

def get_prio(user_id):
    cur.execute("""
        SELECT Cargo.prioridade 
        FROM Usuario
        INNER JOIN UsuarioCargo ON Usuario.id_usuario = UsuarioCargo.fk_id_usuario
        INNER JOIN Cargo ON UsuarioCargo.fk_id_cargo = Cargo.id_cargo
        WHERE Usuario.id_usuario = ?
    """, (user_id,))
    result = cur.fetchone()
    return result[0] if result else None

# Begin SQL Queries

update_query = "UPDATE Usuario SET saldo = ? WHERE id_usuario = ?"

fetch_saldo_query = "SELECT saldo FROM Usuario WHERE id_usuario = ?"

insert_user_query = "INSERT INTO Usuario(id_usuario,nome,pontos,saldo) VALUES (?,?,?,?)"

delete_user_query = "DELETE FROM Usuario WHERE id_usuario = ?"

pk_tabela_query = "SELECT l.name FROM pragma_table_info(?) as l WHERE l.pk = 1"

n_pk_tabela_query = "SELECT l.name FROM pragma_table_info(?) as l WHERE l.pk <> 1"

# End SQL Queries



async def check_achievements(ctx, user_id):
    try:
        cur.execute('SELECT acertos, streak, streak_max FROM Estatistica WHERE fk_id_usuario = ?', (user_id,))
        stats = cur.fetchone()

        if not stats:
            return

        acertos, streak, streak_max = stats

        # (target, achievement_name)
        achievements = [
            (1, 'Primeiro Problema'),
            (5, '5 Corretos'),
            (10, '10 Corretos'),
            (5, 'Sequencia de 5'),
            (10, 'Sequencia de 10'),
        ]

        for target, achievement_name in achievements:
            # id_achievement
            cur.execute('SELECT id_conquista, recompensa FROM Conquista WHERE nome = ?', (achievement_name,))
            achievement = cur.fetchone()

            if not achievement:
                print(f"Conquista '{achievement_name}' não encontrada.")
                continue

            achievement_id, reward = achievement

            # If unlocked
            cur.execute('''
                SELECT completo FROM UsuarioConquista
                WHERE fk_id_usuario = ? AND fk_id_conquista = ?
            ''', (user_id, achievement_id))
            unlocked = cur.fetchone()

            if unlocked:
                print(f"Usuário {user_id} já possui a conquista '{achievement_name}'.")
                continue

            # Check criteria
            if (achievement_name == 'Primeiro Problema' and acertos >= 1) or \
               (achievement_name == '5 Corretos' and acertos >= 5) or \
               (achievement_name == '10 Corretos' and acertos >= 10) or \
               (achievement_name == 'Sequencia de 5' and streak >= 5) or \
               (achievement_name == 'Sequencia de 10' and streak >= 10):
                # Unlock + reward
                cur.execute('''
                    INSERT INTO UsuarioConquista (fk_id_usuario, fk_id_conquista, completo, completo_em)
                    VALUES (?, ?, TRUE, datetime('now'))
                ''', (user_id, achievement_id))
                db.commit()
                cur.execute('UPDATE Usuario SET saldo = saldo + ? WHERE id_usuario = ?', (reward, user_id))
                db.commit()

                await ctx.send(f"🎉 Parabéns! Você desbloqueou a conquista '{achievement_name}' e ganhou {reward} moedas!")
    except Exception as e:
        print(f"Error: {e}")
############################ EVENTS ############################
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_guild_join(guild):
    try:
        cur.execute('''
            INSERT OR IGNORE INTO Servidor (id_servidor, nome)
            VALUES (?, ?)
        ''', (guild.id, guild.name))
        db.commit()
        print(f"Bot registrado no servidor: {guild.name} (ID: {guild.id})")
    except Exception as e:
        print(f"Error: {e}")
################################################################
@bot.command(name='register', help='Registra usuário.')
async def register(ctx):
    user_id = ctx.author.id
    user_name = ctx.author.name
    server_id = ctx.guild.id  # Server id
    try:
        cur.execute('SELECT id_usuario FROM Usuario WHERE id_usuario = ?', (user_id,))
        user_exists = cur.fetchone()

        if not user_exists:
            cur.execute('INSERT INTO Usuario (id_usuario, nome) VALUES (?, ?)', (user_id, user_name))
            db.commit()

        cur.execute('SELECT 1 FROM UsuarioServidor WHERE fk_id_usuario = ? AND fk_id_servidor = ?', (user_id, server_id))
        relation_exists = cur.fetchone()

        if relation_exists:
            await show_messagebox(ctx, "Você já está registrado neste servidor!", discord.Color.red())
            return

        cur.execute('INSERT INTO UsuarioServidor (fk_id_usuario, fk_id_servidor) VALUES (?, ?)', (user_id, server_id))
        db.commit()

        cur.execute('SELECT id_cargo FROM Cargo WHERE prioridade = 1 LIMIT 1')
        role_data = cur.fetchone()

        if not role_data:
            await show_messagebox(ctx, "CARGO FALTA.", discord.Color.red())
            return

        role_id = role_data[0]  # Get lowest prio id
        cur.execute('INSERT INTO UsuarioCargo (fk_id_usuario, fk_id_cargo) VALUES (?, ?)', (user_id, role_id))
        db.commit()

        await show_messagebox(ctx, "Registro concluído com sucesso!", discord.Color.green())

    except Exception as e:
        print(f"ERROR: {e}")
        await show_messagebox(ctx, "ERRO.", discord.Color.red())

@bot.command(name="removeuser", help="Remove usuário.")
async def removeuser(ctx, user_id: int):
    try:
        user_priority = get_prio(ctx.author.id)
        if user_priority < 5:
            await ctx.send("É preciso ser administrador para usar este comando.")
            return

        cur.execute("SELECT id_usuario FROM Usuario WHERE id_usuario = ?", (user_id,))
        user_exists = cur.fetchone()

        if not user_exists:
            await ctx.send("Usuário não encontrado.")
            return
        # Remove later
        cur.execute("DELETE FROM UsuarioServidor WHERE fk_id_usuario = ?", (user_id,))
        cur.execute("DELETE FROM UsuarioCargo WHERE fk_id_usuario = ?", (user_id,))
        cur.execute("DELETE FROM UsuarioItem WHERE fk_id_usuario = ?", (user_id,))
        cur.execute("DELETE FROM UsuarioConquista WHERE fk_id_usuario = ?", (user_id,))
        cur.execute("DELETE FROM Estatistica WHERE fk_id_usuario = ?", (user_id,))
        cur.execute("DELETE FROM ComandoLog WHERE fk_id_usuario = ?", (user_id,))

        cur.execute("DELETE FROM Usuario WHERE id_usuario = ?", (user_id,))
        db.commit()

        await ctx.send(f"Usuário `{user_id}` removido com sucesso.")

    except Exception as e:
        print(f"ERROR: {e}")
        await ctx.send("ERRO.")

@bot.command(name="registeruser", help="Registra um usuário com ID e nome no servidor.")
async def registeruser(ctx, user_id: int, user_name: str):
    try:
        user_priority = get_prio(ctx.author.id)

        if user_priority < 5:
            await show_messagebox(ctx, "Sem permissão.", discord.Color.red())
            return

        server_id = ctx.guild.id

        # Register USER
        cur.execute("SELECT 1 FROM Usuario WHERE id_usuario = ?", (user_id,))
        if not cur.fetchone():
            cur.execute("INSERT INTO Usuario (id_usuario, nome) VALUES (?, ?)", (user_id, user_name))
            db.commit()

        # Register in PRESENT server
        cur.execute("SELECT 1 FROM UsuarioServidor WHERE fk_id_usuario = ? AND fk_id_servidor = ?", (user_id, server_id))
        if cur.fetchone():
            await show_messagebox(ctx, "Usuário já está registrado neste servidor.", discord.Color.orange())
            return
        cur.execute("INSERT INTO UsuarioServidor (fk_id_usuario, fk_id_servidor) VALUES (?, ?)", (user_id, server_id))
        db.commit()

        await show_messagebox(ctx, f"Usuário {user_name} ({user_id}) registrado no servidor com sucesso!", discord.Color.green())

    except Exception as e:
        print(f"ERROR: {e}")
        await show_messagebox(ctx, "Erro.", discord.Color.red())


@bot.command(name="edituser", help="Edita o ID ou nome de um usuário (Apenas prioridade 5).")
async def edituser(ctx, old_id: int, new_value: str):
    try:
        user_priority = get_prio(ctx.author.id)
        if user_priority < 5:
            await show_messagebox(ctx, "Sem permissão.", discord.Color.red())
            return

        # User exists?
        cur.execute("SELECT id_usuario, nome FROM Usuario WHERE id_usuario = ?", (old_id,))
        user_data = cur.fetchone()

        if not user_data:
            await show_messagebox(ctx, "Usuário não encontrado.", discord.Color.orange())
            return

        # <id> <newid> | <newname>
        if new_value.isdigit():
            new_id = int(new_value)
            # ID unique?
            cur.execute("SELECT 1 FROM Usuario WHERE id_usuario = ?", (new_id,))
            if cur.fetchone():
                await show_messagebox(ctx, "O ID especificado já está em uso.", discord.Color.red())
                return

            cur.execute("UPDATE Usuario SET id_usuario = ? WHERE id_usuario = ?", (new_id, old_id))
            db.commit()

            await show_messagebox(ctx, f"ID do usuário alterado de {old_id} para {new_id}.", discord.Color.green())

        else:
            cur.execute("UPDATE Usuario SET nome = ? WHERE id_usuario = ?", (new_value, old_id))
            db.commit()

            await show_messagebox(ctx, f"Nome do usuário {old_id} alterado para {new_value}.", discord.Color.green())

    except Exception as e:
        print(f"ERROR: {e}")
        await show_messagebox(ctx, "ERRO.", discord.Color.red())

@bot.command(name="assignrole", help="Atribui um cargo a um usuário.")
async def assignrole(ctx, user_id: int, priority: int):
    try:
        user_priority = get_prio(ctx.author.id)
        if user_priority < 5:
            await show_messagebox(ctx, "Você não tem permissão para usar este comando.", discord.Color.red())
            return
        cur.execute("SELECT id_usuario FROM Usuario WHERE id_usuario = ?", (user_id,))
        user_exists = cur.fetchone()

        if not user_exists:
            await show_messagebox(ctx, "Usuário não encontrado.", discord.Color.orange())
            return

        cur.execute("SELECT id_cargo FROM Cargo WHERE prioridade = ? LIMIT 1", (priority,))
        role_data = cur.fetchone()

        if not role_data:
            await show_messagebox(ctx, "Cargo não existe.", discord.Color.red())
            return

        role_id = role_data[0]

        cur.execute("SELECT 1 FROM UsuarioCargo WHERE fk_id_usuario = ? AND fk_id_cargo = ?", (user_id, role_id))
        role_exists = cur.fetchone()

        if role_exists:
            await show_messagebox(ctx, "O usuário já possui este cargo.", discord.Color.orange())
            return

        cur.execute("INSERT INTO UsuarioCargo (fk_id_usuario, fk_id_cargo) VALUES (?, ?)", (user_id, role_id))
        db.commit()

        await show_messagebox(ctx, f"Cargo de prioridade {priority} atribuído ao usuário {user_id}.", discord.Color.green())

    except Exception as e:
        print(f"ERROR: {e}")
        await show_messagebox(ctx, "ERRO.", discord.Color.red())


@bot.command(name='showmembers', help='Mostra membros registrados do servidor atual.')
async def showmembers(ctx):
    server_id = ctx.guild.id
    try:
        cur.execute("""
            SELECT Usuario.nome, Cargo.nome, Cargo.prioridade 
            FROM Usuario
            INNER JOIN UsuarioServidor ON Usuario.id_usuario = UsuarioServidor.fk_id_usuario
            INNER JOIN UsuarioCargo ON Usuario.id_usuario = UsuarioCargo.fk_id_usuario
            INNER JOIN Cargo ON UsuarioCargo.fk_id_cargo = Cargo.id_cargo
            WHERE UsuarioServidor.fk_id_servidor = ?
            ORDER BY Cargo.prioridade DESC
        """, (server_id,))

        members = cur.fetchall()

        if not members:
            await show_messagebox(ctx, "Nenhum membro registrado neste servidor.", discord.Color.red())
            return

        # Print list
        member_list = "\n".join(f"{member[0]} - {member[1]}" for member in members) # prioridade {member[2]}
        await show_messagebox(ctx, f"Membros registrados:\n{member_list}", discord.Color.blue())

    except Exception as e:
        print(f"Error: {e}")
        await show_messagebox(ctx, "ERRO.", discord.Color.red())

@bot.command(name='game', help='Gera problema aleatório.')
async def game(ctx):
    try:
        # Check if registered; if not, break
        cur.execute('SELECT id_usuario FROM Usuario WHERE id_usuario = ?', (ctx.author.id,))
        user_exists = cur.fetchone()
        if not user_exists:
            await ctx.send("Comando não disponível. É preciso estar registrado.")
            return
        # Random problem
        operand1 = random.randint(0, 10)
        operand2 = random.randint(0, 10)
        operator = random.choice(['+', '-', '*'])
        # Calculate and store
        if operator == '+':
            answer = operand1 + operand2
        elif operator == '-':
            answer = operand1 - operand2
        elif operator == '*':
            answer = operand1 * operand2
        # Question string
        question = f"{operand1} {operator} {operand2}"
        # Store question data
        game_data[ctx.author.id] = answer

        await ctx.send(f"Resolva: {question}")

        # Answer
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        msg = await bot.wait_for('message', timeout=10.0, check=check)

        # If correct
        if int(msg.content) == answer:
            # Update statistics
            cur.execute('''
                INSERT OR IGNORE INTO Estatistica (fk_id_usuario, acertos, total, streak, streak_max)
                VALUES (?, 0, 0, 0, 0)
            ''', (ctx.author.id,))
            cur.execute('''
                UPDATE Estatistica
                SET acertos = acertos + 1, total = total + 1, streak = streak + 1
                WHERE fk_id_usuario = ?
            ''', (ctx.author.id,))
            cur.execute('''
                UPDATE Estatistica
                SET streak_max = MAX(streak, streak_max)
                WHERE fk_id_usuario = ?
            ''', (ctx.author.id,))
            db.commit()

            # Check achievement in loop
            await check_achievements(ctx, ctx.author.id)

            # Reward; NEEDS MODIFIER
            cur.execute('UPDATE Usuario SET pontos = pontos + ? WHERE id_usuario = ?', (PONTOS_BONUS, ctx.author.id))
            cur.execute('UPDATE Usuario SET saldo = saldo + ? WHERE id_usuario = ?', (SALDO_BONUS, ctx.author.id))
            db.commit()

            await ctx.send(f"Resposta correta! Você ganhou {PONTOS_BONUS} pontos e {SALDO_BONUS} moedas.")
        else:
            # Reset streak
            cur.execute('''
                UPDATE Estatistica
                SET streak = 0, total = total + 1
                WHERE fk_id_usuario = ?
            ''', (ctx.author.id,))
            db.commit()

            await ctx.send(f"Resposta incorreta. A resposta correta era {answer}.")
    except asyncio.TimeoutError:
        await ctx.send("Tempo esgotado.")
    except ValueError:
        await ctx.send("Resposta inválida. Digite um número inteiro.")
    except Exception as e:
        print(f"Error: {e}")
        await ctx.send("ERRO.")

@bot.command(name='shop', help='Mostra itens disponíveis.')
async def shop(ctx):
    try:
        cur.execute('SELECT id_usuario FROM Usuario WHERE id_usuario = ?', (ctx.author.id,))
        user_exists = cur.fetchone()

        if not user_exists:
            await ctx.send("Comando não disponível. É preciso estar registrado.")
            return

        cur.execute('SELECT nome, preco FROM Item')
        
        # Fetch items
        items = cur.fetchall()
        # Database check; if entry error, break
        if not items:
            await ctx.send("Sem itens na loja.")
            return

        # Embed, add items, fields, send
        embed = discord.Embed(title="Loja de Itens", description="Aqui estão os itens disponíveis para compra:", color=discord.Color.blue())
        for item in items:
            nome, preco = item
            embed.add_field(name = nome, value = f"{preco} moedas", inline = False)
        await ctx.send(embed=embed)

    except Exception as e:
        print(f"Error: {e}")
        await ctx.send("ERRO.")

@bot.command(name='buy', help='Compra um item da loja.')
async def buy(ctx, item_name: str):
    try:
        cur.execute('SELECT id_usuario, saldo FROM Usuario WHERE id_usuario = ?', (ctx.author.id,))
        user = cur.fetchone()
        if not user:
            await ctx.send("Comando não disponível. É preciso estar registrado.")
            return
        # No argument
        if item_name == None:
            await ctx.send("É necessário providenciar o nome do item.")
            return
        
        user_id, user_saldo = user

        # Check item name; no item, break
        cur.execute('SELECT id_item, preco FROM Item WHERE nome = ?', (item_name,))
        item = cur.fetchone()
        if not item:
            await ctx.send(f"Item '{item_name}' não encontrado na loja.")
            return

        item_id, item_price = item

        # Check if owned; if so, break
        cur.execute('SELECT fk_id_item FROM UsuarioItem WHERE fk_id_usuario = ? AND fk_id_item = ?', (user_id, item_id))
        item_owned = cur.fetchone()
        if item_owned:
            await ctx.send(f"Usuário já possui '{item_name}'.")
            return
        # Check coins; not enough, break
        if user_saldo < item_price:
            await ctx.send(f"Saldo insuficiente. É preciso {item_price} moedas para adquirir o item '{item_name}'. Saldo atual: {user_saldo} moedas.")
            return
        # Buy
        new_saldo = user_saldo - item_price
        cur.execute('UPDATE Usuario SET saldo = ? WHERE id_usuario = ?', (new_saldo, user_id))
        # Add item
        cur.execute('INSERT INTO UsuarioItem (fk_id_usuario, fk_id_item) VALUES (?, ?)', (user_id, item_id))
        db.commit()

        await ctx.send(f"Item '{item_name}' adquirido! Saldo atual: {new_saldo} moedas.")
    except Exception as e:
        print(f"Error: {e}")
        await ctx.send("ERRO.")

############################################ CONSULTAS SUGERIDAS ############################################
@bot.command(name='checkach', help='Verifica quais usuários têm uma conquista específica.')
async def checkach(ctx, achievement_name: str):
    try:
        # Get achievement id; if non-existant, break
        cur.execute('SELECT id_conquista FROM Conquista WHERE nome = ?', (achievement_name,))
        achievement_data = cur.fetchone()
        if not achievement_data:
            await ctx.send(f"A conquista '{achievement_name}' não foi encontrada.")
            return

        achievement_id = achievement_data[0]

        # User list; if none, break
        cur.execute('''
            SELECT Usuario.nome
            FROM Usuario
            INNER JOIN UsuarioConquista ON Usuario.id_usuario = UsuarioConquista.fk_id_usuario
            WHERE UsuarioConquista.fk_id_conquista = ? AND UsuarioConquista.completo = TRUE
        ''', (achievement_id,))
        users_with_achievement = cur.fetchall()
        if not users_with_achievement:
            await ctx.send(f"Nenhum usuário desbloqueou a conquista '{achievement_name}'.")
            return

        user_list = "\n".join(user[0] for user in users_with_achievement)
        await ctx.send(f"Usuários que desbloquearam a conquista '{achievement_name}':\n{user_list}")

    except Exception as e:
        print(f"Error: {e}")
        await ctx.send("ERRO.")

@bot.command(name='showserver', help='Mostra membros registrados de um servidor pelo nome.')
async def showserver(ctx, server_name: str):
    try:
        cur.execute("SELECT id_servidor FROM Servidor WHERE nome = ?", (server_name,))
        server_data = cur.fetchone()
        if not server_data:
            await ctx.send(f"Servidor '{server_name}' não encontrado.")
            return

        server_id = server_data[0]

        cur.execute("""
            SELECT Usuario.nome 
            FROM Usuario
            INNER JOIN UsuarioServidor ON Usuario.id_usuario = UsuarioServidor.fk_id_usuario
            WHERE UsuarioServidor.fk_id_servidor = ?
        """, (server_id,))
        
        members = cur.fetchall()
        if not members:
            await ctx.send(f"Nenhum membro registrado no servidor '{server_name}'.")
            return

        member_list = "\n".join(member[0] for member in members)
        await ctx.send(f"**Membros registrados no servidor '{server_name}':**\n```{member_list}```")

    except Exception as e:
        print(f"Error: {e}")
        await ctx.send("ERRO.")

@bot.command(name='hasitem', help='Mostra todos os usuários que possuem um determinado item.')
async def whohas(ctx, item_name: str):
    try:
        cur.execute("SELECT id_item FROM Item WHERE nome = ?", (item_name,))
        item_data = cur.fetchone()
        if not item_data:
            await ctx.send(f"Item '{item_name}' não encontrado.")
            return

        item_id = item_data[0]

        cur.execute("""
            SELECT Usuario.nome 
            FROM Usuario
            INNER JOIN UsuarioItem ON Usuario.id_usuario = UsuarioItem.fk_id_usuario
            WHERE UsuarioItem.fk_id_item = ?
        """, (item_id,))
        
        users = cur.fetchall()

        if not users:
            await ctx.send(f"Nenhum usuário possui o item '{item_name}'.")
            return

        user_list = "\n".join(user[0] for user in users)
        await ctx.send(f"**Usuários que possuem o item '{item_name}':**\n```{user_list}```")

    except Exception as e:
        print(f"Error: {e}")
        await ctx.send("ERRO.")

@bot.command(name='showach', help='Mostra usuários e o número de conquistas.')
async def showach(ctx):
    try:
        cur.execute("""
            SELECT Usuario.nome, COUNT(UsuarioConquista.fk_id_conquista) AS total_conquistas
            FROM Usuario
            LEFT JOIN UsuarioConquista ON Usuario.id_usuario = UsuarioConquista.fk_id_usuario
            GROUP BY Usuario.id_usuario
            ORDER BY total_conquistas DESC;
        """)
        # LEFT JOIN to include users with 0 achievements
        users = cur.fetchall()

        if not users:
            await ctx.send("Nenhum usuário encontrado.")
            return

        embed = discord.Embed(title="Conquistas dos Usuários", color=discord.Color.blue())
        
        for user_name, achievement_count in users:
            embed.add_field(name=user_name, value=f"Conquistas: {achievement_count}", inline=False)

        await ctx.send(embed=embed)

    except Exception as e:
        print(f"Error: {e}")
        await ctx.send("ERRO.")

@bot.command(name='showroles', help='Mostra todos os usuários registrados e seus cargos.')
async def showroles(ctx):
    try:
        cur.execute("""
            SELECT Usuario.nome, Cargo.nome
            FROM Usuario
            LEFT JOIN UsuarioCargo ON Usuario.id_usuario = UsuarioCargo.fk_id_usuario
            LEFT JOIN Cargo ON UsuarioCargo.fk_id_cargo = Cargo.id_cargo
            ORDER BY Cargo.prioridade DESC, Usuario.nome ASC;
        """)

        users = cur.fetchall()

        if not users:
            await ctx.send("Nenhum usuário registrado encontrado.")
            return

        embed = discord.Embed(title="Usuários Registrados e seus Cargos", color=discord.Color.blue())

        for user_name, role_name in users:
            role_display = role_name if role_name else "Sem cargo"
            embed.add_field(name=user_name, value=f"Cargo: {role_display}", inline=False)

        await ctx.send(embed=embed)

    except Exception as e:
        print(f"Error: {e}")
        await ctx.send("ERRO.")

############################################ CONSULTAS SUGERIDAS ############################################
############################################ DEBUG ############################################
@bot.command(name='checkuser', help='Verifica se um usuário está registrado.')
async def checkuser(ctx, user_id: int):
    try:
        # Fetch user; if not found, break
        cur.execute('SELECT * FROM Usuario WHERE id_usuario = ?', (user_id,))
        user_data = cur.fetchone()
        if user_data:
            id_usuario, nome, pontos, saldo = user_data
            # Fetch role
            cur.execute('''
                SELECT c.nome
                FROM UsuarioCargo uc
                JOIN Cargo c ON uc.fk_id_cargo = c.id_cargo
                WHERE uc.fk_id_usuario = ?
            ''', (user_id,))
            role_data = cur.fetchone()

            if role_data:
                role_name = role_data[0]
            else: # error
                role_name = "Sem cargo."
            # Print data
            await ctx.send(f"Usuário encontrado:\nID: {id_usuario}\nNome: {nome}\nCargo: {role_name}\nPontos: {pontos}\nSaldo: {saldo}")
        else:
            await ctx.send(f"Usuário {user_id} não encontrado.")
    except Exception as e:
        print(f"Error: {e}")
        await ctx.send("ERRO.")

#@checkuser.error
#async def checkuser_error(ctx, error):
#    if isinstance(error, commands.BadArgument):
#        await ctx.send("O ID do usuário deve ser um número inteiro.")
#    else:
#        await ctx.send("ERRO.")

@bot.command(name='reset', help='Zera pontuação e saldo do usuário.')
async def reset(ctx):
    user_id = ctx.author.id
    try:
        cur.execute('SELECT id_usuario FROM Usuario WHERE id_usuario = ?', (user_id,))
        user_exists = cur.fetchone()

        if not user_exists:
            await ctx.send("Usuário não registrado.")
            return
        cur.execute('UPDATE Usuario SET pontos = 0, saldo = 0 WHERE id_usuario = ?', (user_id,))
        db.commit()
        await ctx.send("Reset sucedido.")
    except Exception as e:
        print(f"Error: {e}")
        await ctx.send("ERRO.")

@bot.command(name='giverole', help='Atribui um cargo a um membro baseado na prioridade.')
async def giverole(ctx, priority: int):
    try:
        # Fetch role (priority based)
        cur.execute('SELECT id_cargo, nome FROM Cargo WHERE prioridade = ?', (priority,))
        role_data = cur.fetchone()
        # If non-existant, break
        if not role_data:
            await ctx.send(f"Não há cargo com a prioridade {priority}.")
            return

        role_id, role_name = role_data

        # Member data
        member = ctx.message.author
        user_id = member.id
        server_id = ctx.guild.id
        # If not registered (in Usuario), break
        cur.execute('SELECT id_usuario FROM Usuario WHERE id_usuario = ?', (user_id,))
        user_exists = cur.fetchone()
        if not user_exists:
            await ctx.send("Usuário não registrado no sistema.")
            return

        # Check if registered IN SERVER
        cur.execute('SELECT 1 FROM UsuarioServidor WHERE fk_id_usuario = ? AND fk_id_servidor = ?', (user_id, server_id))
        relation_exists = cur.fetchone()
        if not relation_exists:
            await ctx.send(f"O usuário não está registrado neste servidor.")
            return
        # Erase previous role
        cur.execute('DELETE FROM UsuarioCargo WHERE fk_id_usuario = ?', (user_id,))
        db.commit()
        # New role
        cur.execute('''
            INSERT INTO UsuarioCargo (fk_id_usuario, fk_id_cargo)
            VALUES (?, ?)
        ''', (user_id, role_id))
        db.commit()

        await ctx.send(f"Cargo '{role_name}' atribuído a {member.mention}.")

    except Exception as e:
        print(f"Error: {e}")
        await ctx.send("ERRO.")
############################################ DEBUG ############################################

@bot.command(name='addmsg', help='Adiciona mensagem customizada.')
async def addmsg(ctx, texto: str):
    user_priority = get_prio(ctx.author.id)

    if int(user_priority) <= 2:
        await ctx.send("Sem permissão para usar este comando.")
        return

    if not ctx.message.attachments:
        await ctx.send("Sem imagem anexada.")
        return

    attachment = ctx.message.attachments[0]
    
    # Download and save
    image_data = await attachment.read()
    cur.execute("""
        INSERT INTO Mensagem (fk_id_usuario, tipo_evento, texto, media_blob) 
        VALUES (?, ?, ?, ?)
    """, (ctx.author.id, "custom", texto, image_data))
    db.commit()

    await ctx.send("Message salva!")

@bot.command(name='sendmsg', help='Envia mensagem customizada.')
async def sendmsg(ctx, custom: str):
    cur.execute("SELECT texto, media_blob FROM Mensagem WHERE tipo_evento = ?", (custom,))
    result = cur.fetchone()
    if result:
        texto, media_blob = result

        embed = discord.Embed(title=f"Message: {custom}", description=texto, color=discord.Color.blue())

        if media_blob:
            image_file = discord.File(io.BytesIO(media_blob), filename="image.png")
            embed.set_image(url="attachment://image.png")
            await ctx.send(embed=embed, file=image_file)
        else:
            await ctx.send(embed=embed)
    else:
        await ctx.send("Mensagem não encontrada.")

@bot.command()
async def debug(ctx, tarefa, tabela, pk):
    tarefas = ["DELETE FROM ", "UPDATE ", "INSERT INTO ", "SELECT "] # 0 = Delete, 1 = Update, 2 = Insert, 3 = Visualize
    try:
        tarefa = int(tarefa)
        tarefa_query = tarefas[tarefa]
    except:
        await ctx.send("Operação invalida?")
        return
    sqliteConnection = sqlite3.connect('bot.db')    # DB connection
    cursor = sqliteConnection.cursor()
    cursor.execute(pk_tabela_query, (tabela,))
    pk_tabela = cursor.fetchone()
    if pk_tabela == None:
        cursor.execute("SELECT * FROM pragma_foreign_key_list(?) LIMIT 1", (tabela,))
        pk_tabela = cursor.fetchone()
    await ctx.send("Aplicando " + tarefa_query + "em " + tabela + " pk: " + str(pk_tabela[0]))
    if tarefa == 0:
        full_debug_query = tarefa_query + tabela + " WHERE " + str(pk_tabela[0]) + " = " + pk
        cursor.execute(full_debug_query)
    elif tarefa == 1:
        await ctx.send("Nome da key a ser editada?")
        key = await bot.wait_for('message', timeout=10)
        key = key.content
        await ctx.send("Novo valor?")
        val = await bot.wait_for('message', timeout=10)
        val = val.content
        full_debug_query = tarefa_query + tabela + " SET " + key + " = " + val + " WHERE " + str(pk_tabela[0]) + " = " + pk
        cursor.execute(full_debug_query)
    elif tarefa == 2:
        cursor.execute(n_pk_tabela_query, (tabela,))
        column_names = [row[0] for row in cursor.fetchall()]
        valores = []
        column_names.insert(0, str(pk_tabela[0]))
        for i in column_names:
            await ctx.send("Valor para " + str(i) + "?")
            val = await bot.wait_for('message', timeout=10)
            val = val.content
            valores.append(val)
        full_debug_query = tarefa_query + tabela + f"({','.join(column_names)})" + " VALUES " + f"({','.join(['?' for i in valores])})"
        print(full_debug_query)
        try:
            cursor.execute(full_debug_query, tuple(valores))
        except:
            full_debug_query = tarefa_query + tabela + f"({','.join(column_names[1::])})" + " VALUES " + f"({','.join(['?' for i in valores[1::]])})"
            cursor.execute(full_debug_query, tuple(valores[1::]))
    elif tarefa == 3:
        full_debug_query = tarefa_query + "* FROM " + tabela + " WHERE " + str(pk_tabela[0]) + " = " + pk
        cursor.execute(full_debug_query)
        data = cursor.fetchall()
        await ctx.send(str(data))
        sqliteConnection.commit()
        sqliteConnection.close()
        return
    sqliteConnection.commit()
    sqliteConnection.close()
    await ctx.send("Editados os valores.")        

if __name__ == '__main__':
    f = open("secret.txt", "r")
    token = f.read()
    bot.run(token)