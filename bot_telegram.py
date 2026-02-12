# ==========================================
# 🤖 BOT TELEGRAM COMERCIAL PARA RENDER (FREE)
# ==========================================

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import csv
import os
import threading
from flask import Flask

# ==========================================
# 🌐 SERVIDOR WEB MÍNIMO (Render necesita esto)
# ==========================================

web_app = Flask(__name__)

@web_app.route("/")
def home():
    print("🌐 Ping recibido en /")
    return "Bot comercial activo en Telegram"


# ==========================================
# 🔑 TOKEN
# ==========================================

# En Render usa variable de entorno
# Local puedes dejar tu token directo para pruebas
#TOKEN = os.getenv("TOKEN") or "Token"
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("❌ La variable de entorno TOKEN no está definida.")


# ==========================================
# 🛍️ CATÁLOGO DE PRODUCTOS
# ==========================================

catalogo = {
    "curso python": 49,
    "bot whatsapp": 99,
    "asesoría datos": 30
}


# ==========================================
# 🧠 MEMORIA DE USUARIOS
# ==========================================

usuarios = {}


# ==========================================
# 💾 GUARDAR LEADS EN CSV
# ==========================================

def guardar_lead(nombre, email, producto):
    archivo = "leads_ventas.csv"
    existe = os.path.isfile(archivo)

    with open(archivo, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not existe:
            writer.writerow(["Nombre", "Email", "Producto"])

        writer.writerow([nombre, email, producto])

    print(f"💾 Lead guardado: {nombre} - {email} - {producto}")


# ==========================================
# 🤖 RESPUESTAS DEL BOT
# ==========================================

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    mensaje = update.message.text.lower()

    # PRINT para ver actividad
    print(f"📩 Mensaje de {user_id}: {mensaje}")

    if user_id not in usuarios:
        usuarios[user_id] = {"estado": "inicio"}

    estado = usuarios[user_id]["estado"]

    # ===== SALUDO =====
    if mensaje == "hola":
        await update.message.reply_text(
            "¡Hola! 😊 Soy *Yessica Bot Comercial* 🛍️\n\n"
            "Puedo ayudarte con cursos, bots y asesorías.\n"
            "Escribe *productos* para ver el catálogo.",
            parse_mode="Markdown"
        )

    # ===== CATÁLOGO =====
    elif "producto" in mensaje:
        texto = "🛍️ *Catálogo disponible:*\n\n"

        for nombre, precio in catalogo.items():
            texto += f"• *{nombre.title()}* — 💲 ${precio} USD\n"

        texto += "\nEscribe *comprar* para iniciar tu pedido."

        await update.message.reply_text(texto, parse_mode="Markdown")

    # ===== INICIAR COMPRA =====
    elif "comprar" in mensaje:
        usuarios[user_id]["estado"] = "nombre"

        await update.message.reply_text(
            "¡Excelente decisión! 🛒✨\n\nPrimero necesito tu *nombre*.",
            parse_mode="Markdown"
        )

    # ===== NOMBRE =====
    elif estado == "nombre":
        usuarios[user_id]["nombre"] = mensaje
        usuarios[user_id]["estado"] = "email"

        await update.message.reply_text(
            f"Gracias *{mensaje.title()}* 😊\n\nAhora tu *email*.",
            parse_mode="Markdown"
        )

    # ===== EMAIL =====
    elif estado == "email":
        usuarios[user_id]["email"] = mensaje
        usuarios[user_id]["estado"] = "producto"

        texto = "Perfecto 👍\n\n¿Qué producto deseas?\n\n"

        for nombre in catalogo:
            texto += f"• {nombre.title()}\n"

        await update.message.reply_text(texto)

    # ===== PRODUCTO =====
    elif estado == "producto":
        producto = mensaje

        if producto not in catalogo:
            await update.message.reply_text(
                "❌ Producto no válido.\nEscribe uno del catálogo."
            )
            return

        usuarios[user_id]["producto"] = producto

        guardar_lead(
            usuarios[user_id]["nombre"],
            usuarios[user_id]["email"],
            producto
        )

        precio = catalogo[producto]

        await update.message.reply_text(
            f"✅ *Pedido registrado*\n\n"
            f"🛍️ Producto: {producto.title()}\n"
            f"💲 Precio: ${precio} USD\n\n"
            "Te enviaré el link de pago en breve 💳",
            parse_mode="Markdown"
        )

        usuarios[user_id]["estado"] = "inicio"

    # ===== DEFAULT =====
    else:
        await update.message.reply_text(
            "No entendí tu mensaje 🤔\nEscribe *productos* para ver el catálogo.",
            parse_mode="Markdown"
        )


# ==========================================
# 🚀 INICIAR BOT
# ==========================================

def iniciar_bot():
    print("🤖 Bot comercial iniciado correctamente")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(
        MessageHandler(filters.TEXT & (~filters.COMMAND), responder)
    )

    app.run_polling()


# ==========================================
# ▶️ EJECUCIÓN PRINCIPAL
# ==========================================

if __name__ == "__main__":

    # Hilo para el bot
    bot_thread = threading.Thread(target=iniciar_bot)
    bot_thread.start()

    # Servidor web para Render
    web_app.run(host="0.0.0.0", port=10000)
