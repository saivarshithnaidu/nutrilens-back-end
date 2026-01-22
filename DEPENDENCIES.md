# Backend Dependencies Note

## "ImportError: email-validator is not installed"
This project uses Pydantic's `EmailStr` type for robust email validation. This feature requires the optional `email-validator` package.

## How to Fix
We have updated `requirements.txt` to include `pydantic[email]`. 

Run the following command to install all necessary dependencies:

```bash
pip install -r requirements.txt
```

This ensures that `email-validator` is installed alongside Pydantic.
