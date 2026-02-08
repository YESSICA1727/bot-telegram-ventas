# ==========================================
# 🤖 BOT TELEGRAM COMERCIAL CON FLUJO VENTAS
# ==========================================

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import csv
import os

# 🔑 TOKEN DESDE VARIABLE DE ENTORNO (SEGURO PARA GITHUB / RENDER)
TOKEN = os.getenv("TOKEN")

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

# ==========================================
# 🤖 RESPUESTA PRINCIPAL
# ==========================================

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.message.from_user.id
    mensaje = update.message.text.lower()

    # Crear usuario si no existe
    if user_id not in usuarios:
        usuarios[user_id] = {"estado": "inicio"}

    estado = usuarios[user_id]["estado"]

    # ======================================
    # 🔹 SALUDO
    # ======================================

    if mensaje == "hola":

        await update.message.reply_text(
            "¡Hola! 😊 Soy *Yessica Bot Comercial* 🛍️\n\n"
            "Puedo ayudarte con cursos, bots y asesorías.\n"
            "Escribe *productos* para ver el catálogo.",
            parse_mode="Markdown"
        )

    # ======================================
    # 🔹 CATÁLOGO
    # ======================================

    elif "producto" in mensaje:

        texto = "🛍️ *Catálogo disponible:*\n\n"

        for nombre, precio in catalogo.items():
            texto += f"• *{nombre.title()}* — 💲 ${precio} USD\n"

        texto += "\nEscribe *comprar* para iniciar tu pedido."

        await update.message.reply_text(texto, parse_mode="Markdown")

    # ======================================
    # 🔹 INICIAR COMPRA
    # ======================================

    elif "comprar" in mensaje:

        usuarios[user_id]["estado"] = "nombre"

        await update.message.reply_text(
            "¡Excelente decisión! 🛒✨\n\n"
            "Primero necesito tu *nombre*.",
            parse_mode="Markdown"
        )

    # ======================================
    # 🔹 CAPTURAR NOMBRE
    # ======================================

    elif estado == "nombre":

        usuarios[user_id]["nombre"] = mensaje
        usuarios[user_id]["estado"] = "email"

        await update.message.reply_text(
            f"Gracias *{mensaje.title()}* 😊\n\n"
            "Ahora tu *email*.",
            parse_mode="Markdown"
        )

    # ======================================
    # 🔹 CAPTURAR EMAIL
    # ======================================

    elif estado == "email":

        usuarios[user_id]["email"] = mensaje
        usuarios[user_id]["estado"] = "producto"

        texto = "Perfecto 👍\n\n¿Qué producto deseas?\n\n"

        for nombre in catalogo:
            texto += f"• {nombre.title()}\n"

        await update.message.reply_text(texto)

    # ======================================
    # 🔹 CAPTURAR PRODUCTO
    # ======================================

    elif estado == "producto":

        producto = mensaje

        if producto not in catalogo:

            await update.message.reply_text(
                "❌ Producto no válido.\n"
                "Escribe uno del catálogo."
            )
            return

        usuarios[user_id]["producto"] = producto

        # Guardar lead
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

    # ======================================
    # 🔹 MENSAJE GENERAL
    # ======================================

    else:

        await update.message.reply_text(
            "No entendí tu mensaje 🤔\n"
            "Escribe *productos* para ver el catálogo.",
            parse_mode="Markdown"
        )

# ==========================================
# 🚀 INICIAR BOT
# ==========================================

def main():

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT, responder))

    print("🤖 Bot comercial activo en Telegram...")

    app.run_polling()

# ==========================================
# ▶️ EJECUCIÓN
# ==========================================

if __name__ == "__main__":
    main()
