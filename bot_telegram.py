# ==========================================
# 🤖 BOT TELEGRAM COMERCIAL + PAYMENT LINKS
# 🌐 RENDER WEBHOOK - v20+
# ==========================================

import os
import psycopg2
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# ==========================================
# 🔑 TOKEN TELEGRAM + PORT
# ==========================================
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("❌ La variable de entorno TOKEN no está definida.")

PORT = int(os.environ.get("PORT", 10000))

# ==========================================
# 🗄️ CONEXIÓN POSTGRESQL (RENDER)
# ==========================================
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL no está definida.")

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS leads (
    id SERIAL PRIMARY KEY,
    nombre TEXT,
    email TEXT,
    producto TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()

# ==========================================
# 🛍️ CATÁLOGO ACTUALIZADO
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
# 💾 GUARDAR LEADS EN POSTGRESQL
# ==========================================
def guardar_lead(nombre, email, producto):
    cursor.execute(
        "INSERT INTO leads (nombre, email, producto) VALUES (%s, %s, %s)",
        (nombre, email, producto)
    )
    conn.commit()
    print(f"💾 Lead guardado en PostgreSQL: {nombre} - {producto}")

# ==========================================
# 🤖 RESPUESTAS BOT
# ==========================================
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    mensaje = update.message.text.lower().strip()

    print(f"📩 Mensaje de {user_id}: {mensaje}")

    if user_id not in usuarios:
        usuarios[user_id] = {"estado": "inicio"}

    estado = usuarios[user_id]["estado"]

    # --------------------------------------
    # SALUDO
    # --------------------------------------
    if mensaje == "hola":
        await update.message.reply_text(
            "¡Hola! 😊 Soy *Yessica Bot Comercial* 🛍️\n\n"
            "Puedo ayudarte con cursos, bots y plantillas digitales.\n"
            "Escribe *productos* para ver el catálogo.",
            parse_mode="Markdown"
        )

    # --------------------------------------
    # CATÁLOGO
    # --------------------------------------
    elif "producto" in mensaje:
        texto = "🛍️ *Catálogo disponible:*\n\n"

        for nombre, precio in catalogo.items():
            texto += f"• *{nombre.title()}* — 💲 ${precio} USD\n"

        texto += "\nEscribe *comprar* para iniciar tu pedido."

        await update.message.reply_text(texto, parse_mode="Markdown")

    # --------------------------------------
    # INICIAR COMPRA
    # --------------------------------------
    elif "comprar" in mensaje:
        usuarios[user_id]["estado"] = "nombre"

        await update.message.reply_text(
            "¡Excelente decisión! 🛒✨\n\n"
            "Primero necesito tu *nombre*.",
            parse_mode="Markdown"
        )

    # --------------------------------------
    # NOMBRE
    # --------------------------------------
    elif estado == "nombre":
        usuarios[user_id]["nombre"] = mensaje
        usuarios[user_id]["estado"] = "email"

        await update.message.reply_text(
            f"Gracias *{mensaje.title()}* 😊\n\nAhora tu *email*.",
            parse_mode="Markdown"
        )

    # --------------------------------------
    # EMAIL
    # --------------------------------------
    elif estado == "email":
        usuarios[user_id]["email"] = mensaje
        usuarios[user_id]["estado"] = "producto"

        texto = "Perfecto 👍\n\n¿Qué producto deseas?\n\n"

        for nombre in catalogo:
            texto += f"• {nombre.title()}\n"

        await update.message.reply_text(texto)

    # --------------------------------------
    # PRODUCTO + LINK DE PAGO
    # --------------------------------------
    elif estado == "producto":
        producto = mensaje

        if producto not in catalogo:
            await update.message.reply_text(
                "❌ Producto no válido.\nEscribe uno del catálogo exactamente igual."
            )
            return

        usuarios[user_id]["producto"] = producto

        guardar_lead(
            usuarios[user_id]["nombre"],
            usuarios[user_id]["email"],
            producto
        )

        precio = catalogo[producto]
        link_pago = links_pago[producto]

        await update.message.reply_text(
            f"✅ Pedido registrado\n\n"
            f"🛍️ Producto: {producto.title()}\n"
            f"💲 Precio: ${precio} USD\n\n"
            f"💳 Paga aquí:\n{link_pago}"
        )

        usuarios[user_id]["estado"] = "inicio"

    # --------------------------------------
    # DEFAULT
    # --------------------------------------
    else:
        await update.message.reply_text(
            "No entendí tu mensaje 🤔\n"
            "Escribe *productos* para ver el catálogo.",
            parse_mode="Markdown"
        )

# ==========================================
# 🚀 APP TELEGRAM
# ==========================================
app_telegram = ApplicationBuilder().token(TOKEN).build()

app_telegram.add_handler(
    MessageHandler(filters.TEXT & (~filters.COMMAND), responder)
)

# ==========================================
# ▶️ WEBHOOK RENDER
# ==========================================
if __name__ == "__main__":
    print(
        "🌐 Iniciando bot en Render con webhook:\n"
        f"https://bot-telegram-ventas.onrender.com/{TOKEN}"
    )

    app_telegram.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"https://bot-telegram-ventas.onrender.com/{TOKEN}"
    )