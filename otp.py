import secrets
secretsgen = secrets.SystemRandom()
print("Generating 6 digits random OTP ")
otp = secretsgen.randrange(100000,999999)
print("Secure random One-Time-Password(OTP) ", otp)