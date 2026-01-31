from cryptography.fernet import Fernet

# Generate a new key
fernet_key = Fernet.generate_key()

# Decode it to a string for easier handling if needed
print(fernet_key.decode())