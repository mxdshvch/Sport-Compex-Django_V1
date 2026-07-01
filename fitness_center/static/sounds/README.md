# Notification Sounds

This directory contains sound files for notifications in the chat system.

## Required Files

- `notification.mp3` - A short sound that plays when a new message is received

## Guidelines for Sound Selection

1. Keep sounds short (less than 1 second)
2. Use subtle sounds that won't startle users
3. Ensure the sound is clear and audible at low volumes
4. Test the sound on different devices to ensure compatibility

## How to Add a Sound

1. Choose an appropriate MP3 file
2. Name it `notification.mp3`
3. Place it in this directory
4. Make sure the file size is reasonable (under 100KB)
5. Run `python manage.py collectstatic` to update static files 