import discord
import face_recognition
import os
from PIL import Image
import numpy as np
import requests
from dotenv import load_dotenv
import collections

load_dotenv()
TOKEN = os.environ.get("TOKEN")
client = discord.Client()

image_types = ["png", "jpg", "jpeg"]
image_encodings = collections.defaultdict(dict)


def encode(attachment):
	im = Image.open(requests.get(attachment.url, stream=True).raw)
	im = im.convert("RGB")
	return face_recognition.face_encodings(np.array(im))

@client.event
async def on_ready():
	print("We have logged in as {0.user}".format(client))

@client.event
async def on_message(message):
	username = str(message.author).split("#")[0]
	user_message = str(message.content)
	channel = str(message.channel.name)
	server_id = str(message.guild.id)
	print(f"{username}: {user_message} ({channel})");

	if message.author == client.user:
		return

	if user_message.startswith("!add_face"):
		name = user_message.split(" ")[1]
		for attachment in message.attachments:
			if any(attachment.filename.lower().endswith(image) for image in image_types):
				image_encoding = encode(attachment)
				if len(image_encoding) != 0:
					image_encodings[server_id][name] = image_encoding[0]
					await message.delete()
					await message.channel.send(f"{name}'s face has been added!")
				else:
					await message.channel.send("Not a face")

	elif user_message.startswith("!remove_face"):
		name = user_message.split(" ")[1]
		if name in image_encodings[server_id]:
			image_encodings[server_id].pop(name, None)
			await message.channel.send(f"{name}'s face has been removed!")
		else:
			await message.channel.send(f"{name}'s face hasn't been added")

	elif user_message == "!list_faces":
		response = "Faces added:"
		for name in list(image_encodings[server_id]):
			response += "\n" + name
		await message.channel.send(response)

	else:
		for attachment in message.attachments:
			if any(attachment.filename.lower().endswith(image) for image in image_types):
				unknown_image_encoding = encode(attachment)
				if len(unknown_image_encoding) != 0: 
					results = face_recognition.compare_faces(list(image_encodings[server_id].values()), unknown_image_encoding[0])
					for i in range(len(image_encodings[server_id])):
						if results[i] == True:
							await message.delete()
							await message.channel.send(f"You can't send {list(image_encodings[server_id])[i]}'s face!")
							break

client.run(TOKEN)