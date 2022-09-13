# Bilibili discord music bot
Made for fun. Don't abuse.

## How to use
  - Host the bot
    - Find a server/use your own, and deploy this repo.
    - Work for me with given `requirements.txt` and `runtime.txt`.
    - Other system dependencies:
      - libopus0
      - ffmpeg
  - Configure on discord
    - Create Discord application and bot on [Developer portal](https://discord.com/developers/applications).
    - (Optional) Register slash command.
    - Invite bot to your server with appropriate permissions.
  - Use
    - Default play and stop command is `/bp <BVID|URL>` and `/bs`.
      - Looking for BVID in parameter using regex.
      - Modify the name on line #29 and #71 if necessary.
    - Queue is not supported. Feel free to implement yours.

## Known issue
  - Since update of `discord.py`, I occassionally get this error: `pipe:: Invalid data found when processing input`