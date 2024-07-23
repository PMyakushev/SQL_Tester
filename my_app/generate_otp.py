import random
import string

def generate_otps(num_otps, length=30):
    # Используем как цифры, так и буквы в нижнем и верхнем регистрах для сложных паролей
    characters = string.ascii_letters + string.digits
    otps = [''.join(random.choices(characters, k=length)) for _ in range(num_otps)]
    return otps

def save_otps_to_file(filename, otps):
    with open(filename, 'a') as f:
        for otp in otps:
            f.write(f"{otp}\n")

if __name__ == "__main__":
    num_otps = 100  # Количество паролей
    otps = generate_otps(num_otps)
    save_otps_to_file('otps.txt', otps)
    print("One-time passwords generated and saved to otps.txt")
