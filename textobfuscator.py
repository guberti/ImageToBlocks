import string, random
text = raw_input("Text to encode:")
words = string.split(text, " ")
output = ""

for word in words:
	if len(word) > 1:
		output += word[0]
	for i in range(1, len(word) - 1):
		output += random.choice(string.ascii_letters[:26])
	output += word[len(word) - 1] + " "
print output
