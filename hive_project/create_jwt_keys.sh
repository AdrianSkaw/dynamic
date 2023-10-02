# Description: Generate private and public keys for JWT authentication
#!/bin/bash

mkdir hive_project/resources
# Generate private key
openssl genrsa -out hive_project/resources/private_key.pem 2048

# Generate public key
openssl rsa -in hive_project/resources/private_key.pem -outform PEM -pubout -out hive_project/resources/public_key.pem