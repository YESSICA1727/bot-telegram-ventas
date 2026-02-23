# ==========================================
# 🤖 BOT TELEGRAM COMERCIAL + PAYMENT LINKS
# 🌐 RENDER WEBHOOK - v20+ + PostgreSQL
# ==========================================

import os
import psycopg2
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# ==========================================
# 🔑 TOKEN TELEGRAM + PORT + DATABASE
# ==========================================
TOKEN = os.getenv("TOKEN")
PORT = int(os.environ.get("PORT", 10000))
DATABASE_URL = os.getenv("DATABASE_URL")

if not TOKEN:
    raise ValueError("❌ TOKEN no está definida.")
if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL no está definida.")

# ==========================================
# 🗄️ INICIALIZAR BASE DE DATOS
# ==========================================
def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id SERIAL PRIMARY KEY,
            nombre TEXT,
            email TEXT,
            producto TEXT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    cur.close()
    conn.close()

    print("✅ Base de datos lista")

# ==========================================
# 💾 GUARDAR LEAD
# ==========================================
async def guardar_lead(nombre, email, producto):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO leads(nombre, email, producto) VALUES(%s, %s, %s)",
        (nombre, email, producto)
    )

    conn.commit()
    cur.close()
    conn.close()

    print(f"💾 Lead guardado: {nombre} - {producto}")

# ==========================================
# 🛍️ CATÁLOGO
# ==========================================
catalogo = {
    "curso python": 49,
    "plantillas digitales": 39,
    "bot whatsapp": 99,
    "bot telegram": 79,
    "bot instagram": 119,
    "bot facebook": 119
}

# ==========================================
# 💳 LINKS DE PAGO STRIPE
# ==========================================
links_pago = {
    "curso python": "https://buy.stripe.com/test_cNi5kE7BU95b3zdcG56Vq00",
    "plantillas digitales": "https://buy.stripe.com/test_cNi5kE7BU95b3zdcG56Vq00",
    "bot whatsapp": "https://buy.stripe.com/test_cNi5kE7BU95b3zdcG56Vq00",
    "bot telegram": "https://buy.stripe.com/test_cNi5kE7BU95b3zdcG56Vq00",
    "bot instagram": "https://buy.stripe.com/test_cNi5kE7BU95b3zdcG56Vq00",
    "bot facebook": "https://buy.stripe.com/test_cNi5kE7BU95b3zdcG56Vq00"
}

# ==========================================
# 🧠 MEMORIA USUARIOS
# ==========================================
usuarios = {}

# ==========================================
# 🤖 RESPUESTAS BOT
# ==========================================
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    mensaje = update.message.text.lower().strip()

    if user_id not in usuarios:
        usuarios[user_id] = {"estado": "inicio"}

    estado = usuarios[user_id]["estado"]

    if mensaje == "hola":
        await update.message.reply_text(
            "¡Hola! 😊 Soy *Yessica Bot Comercial* 🛍️\n\n"
            "Escribe *productos* para ver el catálogo.",
            parse_mode="Markdown"
        )

    elif "producto" in mensaje:
        texto = "🛍️ *Catálogo disponible:*\n\n"
        for nombre, precio in catalogo.items():
            texto += f"• *{nombre.title()}* — 💲 ${precio} USD\n"
        texto += "\nEscribe *comprar* para iniciar tu pedido."
        await update.message.reply_text(texto, parse_mode="Markdown")

    elif "comprar" in mensaje:
        usuarios[user_id]["estado"] = "nombre"
        await update.message.reply_text("Primero necesito tu nombre.")

    elif estado == "nombre":
        usuarios[user_id]["nombre"] = mensaje
        usuarios[user_id]["estado"] = "email"
        await update.message.reply_text("Ahora tu email.")

    elif estado == "email":
        usuarios[user_id]["email"] = mensaje
        usuarios[user_id]["estado"] = "producto"

        texto = "¿Qué producto deseas?\n\n"
        for nombre in catalogo:
            texto += f"• {nombre.title()}\n"

        await update.message.reply_text(texto)

    elif estado == "producto":
        producto = mensaje

        if producto not in catalogo:
            await update.message.reply_text("Producto no válido.")
            return

        await guardar_lead(
            usuarios[user_id]["nombre"],
            usuarios[user_id]["email"],
            producto
        )

        precio = catalogo[producto]
        link_pago = links_pago[producto]

        await update.message.reply_text(
            f"✅ Pedido registrado\n\n"
            f"🛍️ {producto.title()}\n"
            f"💲 ${precio} USD\n\n"
            f"💳 Paga aquí:\n{link_pago}"
        )

        usuarios[user_id]["estado"] = "inicio"

    else:
        await update.message.reply_text(
            "Escribe *productos* para ver el catálogo.",
            parse_mode="Markdown"
        )

# ==========================================
# 🚀 APP TELEGRAM
# ==========================================

async def startup(app):
    init_db()
    print("🌐 Bot iniciado correctamente")

app = (
    ApplicationBuilder()
    .token(TOKEN)
    .post_init(startup)
    .build()
)

app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), responder))

# ==========================================
# ▶️ WEBHOOK RENDER
# ==========================================

if __name__ == "__main__":
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"https://bot-telegram-ventas.onrender.com/{TOKEN}"
    )