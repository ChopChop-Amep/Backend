# ChopChop backend
![Static Badge](https://img.shields.io/badge/Python-3.12-gray?style=for-the-badge&logo=python&logoColor=white&labelColor=%233671a2) ![Static Badge](https://img.shields.io/badge/Nix-24.11-gray?style=for-the-badge&logo=nixos&logoColor=white&labelColor=%237eb7e1) ![Static Badge](https://img.shields.io/badge/License-MIT%2FApache-gray?style=for-the-badge&logo=gitbook&logoColor=white&labelColor=blue)

## Setup
 - Install the Nix package manager on your system. [**[Instructions »]**](https://nixos.org/download/)
 - Run `nix develop --experimental-features 'nix-command flakes'` to enter the developement environment
 - Add the authentication secret key to your environment: `export SECRET_KEY="secret_key_here!"`
 - Add the database URL to your environment: `export DATABASE_URL="postgresql://postgres.wldvmdxarlazwsswoywc:DB_PASSWORD@aws-0-us-east-2.pooler.supabase.com:6543/postgres"`

## Run
You can run a developement instance of the project with the following command:
```
fastapi dev src/main.py
```

## Notes
You **Must** format your code before pushing to remote. You can use the following command:
```bash
autopep8 --in-place --recursive src/
```
