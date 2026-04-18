import sys
import time
import termios
import tty
import hashlib
import os
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

class BiometricKeystrokeCrypt:
    def __init__(self, phrase):
        self.phrase = phrase
        self.signature = None
        self.key = None

    def _capture_keystroke_timings(self, prompt):
        print(prompt, end='', flush=True)
        orig_settings = termios.tcgetattr(sys.stdin)
        tty.setraw(sys.stdin)
        timings = []
        chars = []
        prev_time = None

        try:
            while True:
                ch = sys.stdin.read(1)
                now = time.time()
                if ch in ['\n', '\r']:
                    print()
                    break
                chars.append(ch)
                if prev_time is not None:
                    timings.append(int((now - prev_time)*1000))  # ms cinsinden
                prev_time = now
                print(ch, end='', flush=True)
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, orig_settings)

        return ''.join(chars), timings

    def enroll(self):
        print("\nbiyometrik şifre oluşturuluyor!")
        from numpy import array, mean, std
        enrollment_timings = []
        for i in range(3):
            while True:
                sentence, timings = self._capture_keystroke_timings(
                    f"({i+1}/3) '{self.phrase}' cümlenizi tam ve doğru olarak yazın ve Enter'a basın:\n>")
                if sentence == self.phrase:
                    enrollment_timings.append(timings)
                    break
                else:
                    print("Yanlış cümle yazıldı. Lütfen tekrar deneyin.")
        timings_matrix = array([
            t + [0]*(len(self.phrase)-1-len(t)) for t in enrollment_timings
        ])
        mean_vector = timings_matrix.mean(axis=0)
        std_vector = timings_matrix.std(axis=0)
        std_vector[std_vector == 0] = 1
        tempo_matrix = []
        for i, t in enumerate(mean_vector):
            color = int(255*(t/(t+std_vector[i]))) if (t+std_vector[i])>0 else 0
            tempo_matrix.append(color)
        self.signature = bytes(tempo_matrix)
        hex_rows = [self.signature[i:i+8] for i in range(0, len(self.signature), 8)]
        print("\nKeystroke 'biyometrik matrisi':")
        for row in hex_rows:
            print(' '.join(f"{b:02X}" for b in row))
        self.key = self._derive_aes_key(self.signature)
        print("Biyometrik Anahtar başarıyla üretildi!")

    def _derive_aes_key(self, signature):
        
        hasher = hashlib.sha512()
        hasher.update(signature)
        hasher.update(self.phrase.encode('utf-8'))
        full_hash = hasher.digest()
        return full_hash[:32]
    
    def encrypt(self, plaintext):
        iv = get_random_bytes(16)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        padlen = 16 - (len(plaintext) % 16)
        data = plaintext.encode() + bytes([padlen])*padlen
        ciphertext = cipher.encrypt(data)
        return iv + ciphertext

    def decrypt(self, encrypted, verification_timings):
        check_sig = self._timings_to_signature(verification_timings)
        similarity = self._match_score(self.signature, check_sig)
        print(f"\nBiometrik Ritim Benzerlik Oranı: %{int(similarity*100)}")
        if similarity < 0.90:
            raise Exception("Biyometrik imzanız uyuşmuyor! Şifre Çözümü REDDEDİLDİ")
        key_try = self._derive_aes_key(check_sig)
        iv = encrypted[:16]
        cipher = AES.new(key_try, AES.MODE_CBC, iv)
        try:
            decrypted = cipher.decrypt(encrypted[16:])
            padlen = decrypted[-1]
            return decrypted[:-padlen].decode()
        except Exception as ex:
            raise Exception("Şifre çözülürken hata oluştu veya anahtar uyuşmuyor!") from ex

    def _timings_to_signature(self, timings):
        from numpy import array
        t = array(timings)
        std = t.std() if t.std() != 0 else 1
        mean = t.mean()
        tempo_matrix = []
        for i, tt in enumerate(t):
            color = int(255*(tt/(tt+std))) if (tt+std)>0 else 0
            tempo_matrix.append(color)
        return bytes(tempo_matrix + [0]*(len(self.signature)-len(tempo_matrix)))
    
    def _match_score(self, sig1, sig2):
        minlen = min(len(sig1), len(sig2))
        equalcount = 0
        for a, b in zip(sig1[:minlen], sig2[:minlen]):
            if abs(a - b) <= 8:
                equalcount += 1
        return equalcount / max(len(sig1), len(sig2))

def main():
    print("\n>>> GHOST CRYP - Biyometrik Şifreleme <<<\n")
    phrase = input("Biyometrik ritim için kullanılacak cümleyi belirleyin:\n> ")
    cryp = BiometricKeystrokeCrypt(phrase)
    cryp.enroll()

    choice = input("Şifrelemek için (e), Çözmek için (d) girin: ").lower()
    if choice == "e":
        plaintext = input("Şifrelenecek metni girin:\n> ")
        ciphertext = cryp.encrypt(plaintext)
        with open('ghostcryp.enc', 'wb') as f:
            f.write(ciphertext)
        print("\n--- METİN ŞİFRELENDİ ve 'ghostcryp.enc' dosyasına kaydedildi ---")
    elif choice == "d":
        if not os.path.exists('ghostcryp.enc'):
            print("Şifrelenmiş dosya bulunamadı.")
            return
        with open('ghostcryp.enc', 'rb') as f:
            ciphertext = f.read()
        print(f"(*) {phrase} cümlesini şifreni açmak için tekrar yazmalısın!")
        _, timings = cryp._capture_keystroke_timings("> ")
        try:
            plaintext = cryp.decrypt(ciphertext, timings)
            print("\n--- ŞİFRE ÇÖZÜLDÜ ---")
            print("Çözülen Metin:", plaintext)
        except Exception as ex:
            print(f"HATA: {ex}")
    else:
        print("Geçersiz seçim!")

if __name__ == "__main__":
    main()