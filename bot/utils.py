
num_emoji = {
    '0': '0️⃣',
    '1': '1️⃣',
    '2': '2️⃣',
    '3': '3️⃣',
    '4': '4️⃣',
    '5': '5️⃣',
    '6': '6️⃣',
    '7': '7️⃣',
    '8': '8️⃣',
    '9': '9️⃣',    
}

def numbers_emojify(num_string: str):
    emoji_result = ''
    for item in num_string:
        emoji_result += num_emoji.get(item, item)
    return emoji_result

# print(numbers_emojify('13123'))
# print(numbers_emojify('1234567890'))
# print(numbers_emojify('2309823'))
