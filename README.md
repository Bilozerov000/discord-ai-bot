# Discord Voice Chat LLM

This Discord bot uses voice recognition to interact with users in a voice channel through transcription, processing with a Large Language Model (LLM), and responding with synthesized voice. The bot converts spoken audio to text, sends it to an LLM for processing, and uses Text-to-Speech (TTS) to voice the response.

Additionally, you can just use the bot in text channels.

## Features
- __Conversation:__ Engage in a conversation with the bot using voice or text input.

## Prerequisites

- Node.js and npm installed
- A Discord Bot Token
- Fully local, checkout `openedai-whisper`, `ollama` and `openedai-speech`)

## Installation

1. **Clone the Repository:**
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Install Dependencies:**
   ```bash
   npm install
   ```

3. **Configure the Environment:**
- Rename `.env.example` to `.env`.
- Update the `.env` file with your specific credentials and API endpoints.

## Usage
1. **Start the Bot:**
   ```bash
   node bot.js
   ```

2. **Invite the Bot to Your Discord Server:**
- Use the invite link generated through your Discord application page. Here is a quick link with all the permissions the bot should ever need:
https://discord.com/oauth2/authorize?client_id=REPLACEME&permissions=964220516416&scope=bot

(Change "REPLACEME" with your bot's ID)

3. **Using the Bot in Discord:**
### Voice Chat
- Ensure the bot has permission to join voice channels and speak.
- In a Discord server where the bot is a member, join a voice channel and type the command `>join` or `>join free`.
- The bot will join the channel and start listening to users who are speaking. Spoken phrases are processed and responded to in real-time.

### Text Chat
- To start a new conversation, mention the bot in your message.
- To continue a conversation, just reply to the bot's message.
- You can also continue conversations by creating a thread from the bot's message. In that case, you no longer need to reply or mention the bot within the thread.

## Commands
- `/join`: Command for the bot to join the voice channel you are currently in. The bot will listen to voice input, transcribe it, send it to the LLM if you used a trigger word, and respond with a spoken answer using TTS.
- `/join free`: Similar to `>join`, but will respond to everything without using trigger words. Best for solo usage.
- `/join silent`: Similar to `>join`, but no confirmation sound will play when trigger is detected/llm responded.
- `/join transcribe`: Similar to `>join`, but will save the transcriptions to a file and send it once you use the `>leave` command.
- `/leave`: Command for the bot to leave the voice channel. You may also say `leave voice chat` in voice chat.
- `/help`: Display the list of available commands.

__You may at any time say `stop` to stop the bot while it is speaking.__

## Troubleshooting
- **Bot Doesn't Join Channel**: Ensure the bot has the correct permissions in your Discord server, including the ability to join and speak in voice channels.
- **No Audio from Bot**: Check that the TTS API is returning valid MP3 audio data and that the bot has permissions to play audio in the channel.
- **Errors in Transcription or Response**: Verify that the API endpoints and models specified in the `.env` file are correct and that the APIs are operational.
