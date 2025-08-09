import os
import yagmail
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from video_config import VIDEO_ID  # Import the VIDEO_ID from the config file

# --- Configuration ---
TELEGRAM_BOT_TOKEN = '7989024669:AAF3WZNZtBatFnivCzweR_ftsFYMrgyDb-4'
GMAIL_USERNAME = 'testemailacosta38@gmail.com'     
OAUTH_GOOGLE = '~/credentials.json' 

# --- Bot Command Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    await update.message.reply_text(
        "Welcome to the Email Sender Bot! 📧\n\n"
        "Use the /send command to send an email:\n"
        "/send recipient@example.com Subject of the email The body of the email"
    )
# import video-id from the config file
try:
    from video_config import VIDEO_ID
except ImportError:
    VIDEO_ID = None # Set to None if the config file doesn't exist yet
    print("❌ Video ID not found. Please run the setup script first.")

async def reply_with_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a greeting message when the /hey command is issued."""
    """Checks for the word 'hey' and replies with a local video."""
    message_text = update.message.text.lower()
    # Check if the message is exactly 'hey'
    if message_text == 'hey' or message_text == 'hey!' or message_text == 'bakit niya ako iniwan?':
        # Check if the VIDEO_ID was imported successfully
        if VIDEO_ID:
            try:
                # Send the video using the ID. This is almost instant.
                await update.message.reply_video(video=VIDEO_ID)
            except Exception as e:
                print(f"Error sending video by ID: {e}")
                await update.message.reply_text("I had a problem sending that video.")
        else:
            # If the ID isn't available, inform the user.
            await update.message.reply_text(
                "The video feature is not configured. "
                "Please run the `setup.py` script first."
            )

'''async def reply_with_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_text = update.message.text.lower()
    if message_text == 'hey':
        try:
            # Send the video from the local file
            sent_message = await update.message.reply_video(video=open('/home/carleaux/python-telegram-bot/media/media.mp4', 'rb'))
            
            # Get the file_id from the message you just sent and print it
            video_file_id = sent_message.video.file_id
            print("--- VIDEO FILE ID ---")
            print(video_file_id)
            print("--- COPY THIS ID ---")

        except FileNotFoundError:
            await update.message.reply_text("Sorry, I can't find my video file right now!") '''


# Directory to temporarily save downloaded images
DOWNLOAD_DIR = "downloads"

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles receiving a photo. It downloads the highest resolution image
    and stores its file path for the user to send later.
    """
    # Create the download directory if it doesn't exist
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
        
    try:
        # Get the highest resolution photo file
        photo_file = await update.message.photo[-1].get_file()
        
        # Create a unique path to save the image
        file_path = os.path.join(DOWNLOAD_DIR, f"{photo_file.file_id}.jpg")

        # Download the file
        await photo_file.download_to_drive(custom_path=file_path)

        # IMPORTANT: Store the file path in `context.user_data`.
        # This saves the path for this specific user, so we can find it later.
        context.user_data['photo_path'] = file_path

        await update.message.reply_text(
            "✅ Photo received and saved!\n\n"
            "Now, use the /send command to email it as an attachment."
        )
    except Exception as e:
        print(f"Error handling photo: {e}")
        await update.message.reply_text("❌ Sorry, I had trouble processing that photo.")

async def send_email_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Sends an email. If a photo has been sent by the user beforehand,
    it attaches that photo to the email.
    """
    try:
        args = context.args
        if len(args) < 3:
            await update.message.reply_text(
                "Invalid format. Please use:\n"
                "/send recipient@example.com Subject Body"
            )
            return

        recipient = args[0]
        subject = args[1]
        body = " ".join(args[2:])
        
        # Check `user_data` to see if a photo path was stored from a previous message
        attachment_path = context.user_data.get('photo_path')
        
        # Prepare the contents for yagmail
        email_contents = [body]
        if attachment_path and os.path.exists(attachment_path):
            email_contents.append(attachment_path)
            success_message = f"✅ Email with attachment successfully sent to {recipient}!"
        else:
            # This allows the user to still send text-only emails
            success_message = f"✅ Text-only email successfully sent to {recipient}!"


        # Send the email using yagmail.
        with yagmail.SMTP(GMAIL_USERNAME, oauth2_file="~/credentials.json") as yag:
            yag.send(
                to=recipient,
                subject=subject,
                contents=email_contents
            )

        await update.message.reply_text(success_message)

        # Clean up: if there was an attachment, delete the file and remove its path
        if attachment_path and os.path.exists(attachment_path):
            os.remove(attachment_path)
            del context.user_data['photo_path']

    except Exception as e:
        print(f"Error sending email: {e}")
        await update.message.reply_text("❌ An error occurred while sending the email. Please check your format and try again.")

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("send", send_email_command))
    application.add_handler(CommandHandler("hey", reply_with_video))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_with_video))

    # This handler listens for any message that is a PHOTO.
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == '__main__':
    main()
