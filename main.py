import discord
import face_recognition
import os
from decouple import config

TOKEN = config("TOKEN")
client = discord.Client()

image_types = ["png", "jpg", "jpeg"]
image_encodings = {}

@client.event
async def on_ready():
	print("We have logged in as {0.user}".format(client))

@client.event
async def on_message(message):
	username = str(message.author).split("#")[0]
	user_message = str(message.content)
	channel = str(message.channel.name)
	print(f"{username}: {user_message} ({channel})");

	if message.author == client.user:
		return

	if user_message.startswith("!add_face"):
		name = user_message.split(" ")[1]
		for attachment in message.attachments:
			if any(attachment.filename.lower().endswith(image) for image in image_types):
				await attachment.save(attachment.filename)
				image_load = face_recognition.load_image_file(attachment.filename)
				image_encoding = face_recognition.face_encodings(image_load)
				if len(image_encoding) != 0:
					image_encodings[name] = image_encoding[0]
					await message.delete()
					await message.channel.send(f"{name}'s face has been added!")
				else:
					await message.channel.send("Not a face")
				os.remove(attachment.filename)

	elif user_message.startswith("!remove_face"):
		name = user_message.split(" ")[1]
		if name in image_encodings:
			image_encodings.pop(name, None)
			await message.channel.send(f"{name}'s face has been removed!")
		else:
			await message.channel.send(f"{name}'s face hasn't been added")

	elif user_message == "!list_faces":
		response = "Faces added:"
		for name in list(image_encodings):
			response += "\n" + name
		await message.channel.send(response)

	else:
		for attachment in message.attachments:
			if any(attachment.filename.lower().endswith(image) for image in image_types):
				await attachment.save(attachment.filename)
				unknown_image_load = face_recognition.load_image_file(attachment.filename)
				unknown_image_encoding = face_recognition.face_encodings(unknown_image_load)
				if len(unknown_image_encoding) != 0: 
					results = face_recognition.compare_faces(list(image_encodings.values()), unknown_image_encoding[0])
					for i in range(len(image_encodings)):
						if results[i] == True:
							await message.delete()
							await message.channel.send(f"You can't send {list(image_encodings)[i]}'s face!")
							break
				os.remove(attachment.filename)

client.run(TOKEN)