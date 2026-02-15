# ==========================================
# 🤖 BOT TELEGRAM COMERCIAL + STRIPE (RENDER WEBHOOK) - v20+
# ==========================================

import os
import csv
import stripe
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
# 🔑 STRIPE CONFIG
# ==========================================
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
if not STRIPE_SECRET_KEY:
    raise ValueError("❌ Falta STRIPE_SECRET_KEY")

stripe.api_key = STRIPE_SECRET_KEY

# ==========================================
# 🛍️ CATÁLOGO
# ==========================================
catalogo = {
    "curso python": 49,
    "bot whatsapp": 99,
    "asesoría datos": 30
}

# ==========================================
# 🧠 MEMORIA USUARIOS
# ==========================================
usuarios = {}

# ==========================================
# 💾 GUARDAR LEADS CSV
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
# 💳 CREAR LINK DE PAGO STRIPE
# ==========================================
def crear_link_pago(nombre_producto, precio):
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": nombre_producto.title(),
                    },
                    "unit_amount": int(precio * 100),
                },
                "quantity": 1,
            }],
            mode="payment",

            # 🔁 Cambia luego por tu dominio real
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
        )

        return session.url

    except Exception as e:
        print(f"❌ Error Stripe: {e}")
        return None

# ==========================================
# 🤖 RESPUESTAS BOT
# ==========================================
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    mensaje = update.message.text.lower()

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
            "Puedo ayudarte con cursos, bots y asesorías.\n"
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
    # PRODUCTO + STRIPE
    # --------------------------------------
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

        # 💳 Crear link Stripe
        link_pago = crear_link_pago(producto, precio)

        if not link_pago:
            await update.message.reply_text(
                "❌ Hubo un problema generando el link de pago."
            )
            return

        await update.message.reply_text(
            f"✅ *Pedido registrado*\n\n"
            f"🛍️ Producto: {producto.title()}\n"
            f"💲 Precio: ${precio} USD\n\n"
            f"💳 *Paga aquí:* \n{link_pago}",
            parse_mode="Markdown"
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
