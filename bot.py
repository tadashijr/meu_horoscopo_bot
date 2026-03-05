import os
import logging
import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler,                        ConversationHandler, MessageHandler, ContextTypes, filters
import requests
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Wedge

# Configurações
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
API_KEY = os.getenv('FREE_ASTRO_API_KEY')
API_URL = "https://api.freeastroapi.com/v1"

# Signos
SIGNS = {
    'aries': ('Áries', '♈', '21/03 - 19/04'),
    'touro': ('Touro', '♉', '20/04 - 20/05'),
    'gemeos': ('Gêmeos', '♊', '21/05 - 20/06'),
    'cancer': ('Câncer', '♋', '21/06 - 22/07'),
    'leao': ('Leão', '♌', '23/07 - 22/08'),
    'virgem': ('Virgem', '♍', '23/08 - 22/09'),
    'libra': ('Libra', '♎', '23/09 - 22/10'),
    'escorpiao': ('Escorpião', '♏', '23/10 - 21/11'),
    'sagitario': ('Sagitário', '♐', '22/11 - 21/12'),
    'capricornio': ('Capricórnio', '♑', '22/12 - 19/01'),
    'aquario': ('Aquário', '♒', '20/01 - 18/02'),
    'peixes': ('Peixes', '♓', '19/02 - 20/03')
}

# Estados
DATE, TIME, CITY = range(3)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_horoscope(sign):
    """Busca horóscopo da API ou gera localmente"""
    try:
        if API_KEY:
            headers = {'Authorization': f'Bearer {API_KEY}'}
            response = requests.get(f'{API_URL}/horoscope/daily', 
                                  headers=headers, 
                                  params={'sign': sign, 'day': 'today'},
                                  timeout=10)
            if response.status_code == 200:
                data = response.json()
                return f"""
🔮 *Horóscopo de {SIGNS[sign][0]}* {SIGNS[sign][1]}

📅 {datetime.now().strftime('%d/%m/%Y')}

{data.get('prediction', 'As estrelas estão alinhadas para você!')}

⭐ *Energia:* {data.get('mood', 'Positiva')}
💼 *Trabalho:* {data.get('career', 'Bom dia para networking')}
❤️ *Amor:* {data.get('love', 'Comunicação é fundamental')}
💰 *Dinheiro:* {data.get('finance', 'Cautela nos gastos')}
🍀 *Números:* {data.get('lucky_numbers', f'{random.randint(1,99)}, {random.randint(1,99)}')}
"""
    except Exception as e:
        logger.error(f"API Error: {e}")
    
    # Fallback local
    predictions = [
        "Hoje é dia de novas oportunidades! Aproveite as chances que surgirem.",
        "A energia cósmica favorece relacionamentos. Ótimo dia para reconciliações.",
        "Momento de introspecção. Medite e ouça sua intuição.",
        "Criatividade em alta! Ideal para projetos artísticos.",
        "Dia de sorte em assuntos financeiros. Confie na sua intuição."
    ]
    
    return f"""
🔮 *Horóscopo de {SIGNS[sign][0]}* {SIGNS[sign][1]}

📅 {datetime.now().strftime('%d/%m/%Y')}

{random.choice(predictions)}

⭐ *Energia:* {random.choice(['Positiva', 'Criativa', 'Calma', 'Social'])}
💼 *Trabalho:* Momento favorável para novos projetos
❤️ *Amor:* Dia propício para demonstrar sentimentos
💰 *Dinheiro:* Avalie bem antes de gastar
🍀 *Números:* {random.randint(1,99)}, {random.randint(10,99)}, {random.randint(10,99)}
"""

def generate_chart_image(name, date, sign):
    """Gera imagem do mapa astral"""
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.set_aspect('equal')
    ax.axis('off')
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#1a1a2e')
    
    # Círculos
    outer = Circle((0, 0), 1, fill=False, color='#e94560', linewidth=3)
    inner = Circle((0, 0), 0.6, fill=False, color='#16213e', linewidth=2)
    ax.add_patch(outer)
    ax.add_patch(inner)
    
    # 12 signos
    symbols = ['♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒', '♓']
    for i in range(12):
        angle = np.radians(i * 30 + 15)
        x, y = 0.8 * np.cos(angle), 0.8 * np.sin(angle)
        ax.text(x, y, symbols[i], fontsize=24, ha='center', va='center', color='white')
        
        # Linhas
        angle_line = np.radians(i * 30)
        x1, y1 = 0.6 * np.cos(angle_line), 0.6 * np.sin(angle_line)
        x2, y2 = np.cos(angle_line), np.sin(angle_line)
        ax.plot([x1, x2], [y1, y2], color='#0f3460', linewidth=1)
    
    # Planetas aleatórios para visual
    planets = ['☉', '☽', '☿', '♀', '♂', '♃']
    for i, planet in enumerate(planets):
        angle = random.uniform(0, 360)
        r = random.uniform(0.3, 0.5)
        x, y = r * np.cos(np.radians(angle)), r * np.sin(np.radians(angle))
        ax.text(x, y, planet, fontsize=16, ha='center', va='center', 
               color='#e94560', fontweight='bold')
    
    # Título
    ax.text(0, 1.1, f'Mapa Astral - {name}', fontsize=14, ha='center', 
           color='white', fontweight='bold')
    ax.text(0, -1.1, f'{date} | Signo: {sign}', fontsize=10, ha='center', color='#a0a0a0')
    
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=150, facecolor='#1a1a2e', 
               bbox_inches='tight', pad_inches=0.2)
    buf.seek(0)
    plt.close()
    return buf

def calculate_sign(day, month):
    """Calcula signo solar"""
    dates = [(1, 20, 'capricornio'), (2, 19, 'aquario'), (3, 21, 'peixes'),
            (4, 20, 'aries'), (5, 21, 'touro'), (6, 21, 'gemeos'),
            (7, 23, 'cancer'), (8, 23, 'leao'), (9, 23, 'virgem'),
            (10, 23, 'libra'), (11, 22, 'escorpiao'), (12, 22, 'sagitario'),
            (12, 32, 'capricornio')]
    for m, d, sign in dates:
        if month == m and day <= d:
            return sign
    return 'capricornio'

# Comandos
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔮 Horóscopo Diário", callback_data='daily')],
        [InlineKeyboardButton("📊 Análise por Data", callback_data='analysis')],
        [InlineKeyboardButton("⭐ Mapa Astral", callback_data='chart')],
        [InlineKeyboardButton("❓ Ajuda", callback_data='help')]
    ]
    await update.message.reply_text(
        "✨ *Bem-vindo ao Bot de Horóscopo!* ✨\n\n"
        "Escolha uma opção abaixo:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gerencia todos os botões inline com tratamento de erro"""
    try:
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        # DEBUG: Log para ver qual botão foi pressionado
        logger.info(f"Botão pressionado: {data}")
        
        if data == 'daily':
            await show_signs_menu(query, "daily")
            
        elif data == 'analysis':
            await query.edit_message_text(
                "📅 *Análise por Data de Nascimento*\n\n"
                "Envie sua data no formato: *DD/MM/AAAA*\n"
                "Exemplo: 15/03/1995",
                parse_mode='Markdown'
            )
            return DATE
            
        elif data == 'chart':
            await query.edit_message_text(
                "⭐ *Mapa Astral Completo*\n\n"
                "Vou precisar de algumas informações.\n\n"
                "1️⃣ Primeiro, envie sua *data de nascimento* (DD/MM/AAAA):",
                parse_mode='Markdown'
            )
            context.user_data['chart_step'] = 'date'
            return DATE
            
        elif data == 'help':
            await query.edit_message_text(
                "🔮 *Como usar o bot:*\n\n"
                "• Use os botões para navegar\n"
                "• Horóscopo diário atualizado\n"
                "• Mapa astral visual\n"
                "• Análise baseada na data\n\n"
                "💡 Dica: Para mapa astral preciso, informe a hora exata!",
                parse_mode='Markdown'
            )
            
        elif data == 'back':
            # Volta ao menu principal
            keyboard = [
                [InlineKeyboardButton("🔮 Horóscopo Diário", callback_data='daily')],
                [InlineKeyboardButton("📊 Análise por Data", callback_data='analysis')],
                [InlineKeyboardButton("⭐ Mapa Astral", callback_data='chart')],
                [InlineKeyboardButton("❓ Ajuda", callback_data='help')]
            ]
            await query.edit_message_text(
                "✨ *Menu Principal* ✨\n\nEscolha uma opção:",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
            
        elif data.startswith('horo_'):
            sign = data.replace('horo_', '')
            logger.info(f"Buscando horóscopo para: {sign}")
            
            # Verifica se signo existe
            if sign not in SIGNS:
                logger.error(f"Signo não encontrado: {sign}")
                await query.edit_message_text(
                    "❌ Signo não reconhecido. Tente novamente.",
                    parse_mode='Markdown'
                )
                return
                
            horoscope = get_horoscope(sign)
            await query.edit_message_text(horoscope, parse_mode='Markdown')
            
            # Botão voltar
            keyboard = [[InlineKeyboardButton("🔙 Menu Principal", callback_data='back')]]
            await query.message.reply_text(
                "Quer mais previsões?",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
        elif data.startswith('sign_'):
            # Compatibilidade com código antigo
            sign = data.replace('sign_', '')
            if sign in SIGNS:
                horoscope = get_horoscope(sign)
                await query.edit_message_text(horoscope, parse_mode='Markdown')
            else:
                await query.edit_message_text("❌ Erro: Signo inválido")
                
        else:
            logger.warning(f"Callback desconhecido: {data}")
            await query.edit_message_text("❌ Opção não reconhecida. Use /start")
            
    except Exception as e:
        logger.error(f"ERRO no button_handler: {e}", exc_info=True)
        try:
            await query.edit_message_text(
                "❌ Ocorreu um erro. Tente novamente com /start"
            )
        except:
            pass  # Se não conseguir editar, ignora
    
    return None  # Importante para ConversationHandler
async def receive_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        day, month, year = map(int, text.split('/'))
        sign = calculate_sign(day, month)
        sign_name = SIGNS[sign][0]
        sign_symbol = SIGNS[sign][1]
        
        # Se veio do mapa astral
        if context.user_data.get('chart_step') == 'date':
            context.user_data['birth_date'] = text
            context.user_data['sign'] = sign_name
            await update.message.reply_text(
                f"✅ Data: {text}\nSigno: {sign_symbol} {sign_name}\n\n"
                f"⏰ Agora envie a *hora* de nascimento (HH:MM):",
                parse_mode='Markdown'
            )
            context.user_data['chart_step'] = 'time'
            return TIME
        
        # Se veio da análise simples
        numero = sum(int(d) for d in text.replace('/', ''))
        while numero > 9:
            numero = sum(int(d) for d in str(numero))
        
        elementos = {
            'aries': 'Fogo 🔥', 'leao': 'Fogo 🔥', 'sagitario': 'Fogo 🔥',
            'touro': 'Terra 🌍', 'virgem': 'Terra 🌍', 'capricornio': 'Terra 🌍',
            'gemeos': 'Ar 💨', 'libra': 'Ar 💨', 'aquario': 'Ar 💨',
            'cancer': 'Água 💧', 'escorpiao': 'Água 💧', 'peixes': 'Água 💧'
        }
        
        await update.message.reply_text(
            f"🔮 *Análise Astrológica* 🔮\n\n"
            f"{sign_symbol} *Signo Solar:* {sign_name}\n"
            f"🌟 *Elemento:* {elementos.get(sign, 'Desconhecido')}\n"
            f"📅 *Data:* {text}\n"
            f"🔢 *Número da Vida:* {numero}\n\n"
            f"*Características:*\n"
            f"• Energia forte em {elementos.get(sign, 'equilíbrio').split()[0]}\n"
            f"• Potencial de liderança natural\n"
            f"• Desafios trazem crescimento\n\n"
            f"✨ _Consulte /start para mais opções_",
            parse_mode='Markdown'
        )
        return ConversationHandler.END
        
    except ValueError:
        await update.message.reply_text(
            "❌ Formato inválido! Use *DD/MM/AAAA*\nExemplo: 15/03/1995",
            parse_mode='Markdown'
        )
        return DATE

async def receive_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        hour, minute = map(int, text.split(':'))
        context.user_data['birth_time'] = text
        
        await update.message.reply_text(
            f"✅ Hora: {text}\n\n"
            f"📍 Agora envie sua *cidade* de nascimento:",
            parse_mode='Markdown'
        )
        return CITY
    except ValueError:
        await update.message.reply_text(
            "❌ Formato inválido! Use *HH:MM*\nExemplo: 14:30",
            parse_mode='Markdown'
        )
        return TIME

async def receive_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text
    user = update.effective_user
    date = context.user_data.get('birth_date', '01/01/2000')
    sign = context.user_data.get('sign', 'Desconhecido')
    
    # Gerar imagem do mapa astral
    await update.message.reply_text("🎨 Gerando seu mapa astral... Aguarde!")
    
    try:
        chart_image = generate_chart_image(user.first_name, date, sign)
        
        await update.message.reply_photo(
            photo=chart_image,
            caption=f"""
⭐ *Mapa Astral de {user.first_name}* ⭐

📅 {date} às {context.user_data.get('birth_time', '00:00')}
📍 {city}
☉ Signo Solar: {sign}

💫 Este é um mapa astral básico. Para análise completa com casas astrológicas detalhadas, consulte um astrólogo profissional!

🔄 Use /start para novo mapa
""",
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Chart error: {e}")
        await update.message.reply_text(
            "❌ Erro ao gerar mapa. Tente novamente com /start"
        )
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operação cancelada. Use /start")
    return ConversationHandler.END

def main():
    if not TOKEN:
        logger.error("TOKEN não configurado!")
        return
    
    application = Application.builder().token(TOKEN).build()

    # Conversation handlers
    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(button_handler, pattern='^(analysis|chart)$')
        ],
        states={
            DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_date)],
            TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_time)],
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_city)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_message=True,  # Resolve o warning
        name="main_conversation"
    )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Loga erros e envia mensagem amigável ao usuário"""
    logger.error(f"Exceção: {context.error}", exc_info=context.error)
    
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "❌ Ops! Algo deu errado. Tente novamente com /start"
        )

def main():
    if not TOKEN:
        logger.error("TOKEN não configurado!")
        return
    
    # Cria a aplicação
    application = Application.builder().token(TOKEN).build()
    
    # Handler de erros global (ADICIONAR AQUI, DEPOIS DE CRIAR application)
    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Loga erros e envia mensagem amigável ao usuário"""
        logger.error(f"Exceção: {context.error}", exc_info=context.error)
        
        if isinstance(update, Update) and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Ops! Algo deu errado. Tente novamente com /start"
            )
    
    application.add_error_handler(error_handler)
    
    # Conversation handlers
    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(button_handler, pattern='^(analysis|chart)$')
        ],
        states={
            DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_date)],
            TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_time)],
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_city)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_message=True,
        name="main_conversation"
    )
    
    # Adiciona handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(button_handler))
    
    logger.info("Bot iniciado!")
    application.run_polling()
