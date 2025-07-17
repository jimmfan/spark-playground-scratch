import subprocess
import os

def convert_rsa_to_pkcs8(input_key_path, output_key_path):
    input_key_path = os.path.expanduser(input_key_path)
    output_key_path = os.path.expanduser(output_key_path)

    if not os.path.isfile(input_key_path):
        raise FileNotFoundError(f"❌ Input key not found: {input_key_path}")

    print(f"🔄 Converting RSA private key to PKCS#8 format:\n  From: {input_key_path}\n  To:   {output_key_path}")

    try:
        subprocess.run([
            "openssl", "pkcs8",
            "-topk8",
            "-inform", "PEM",
            "-outform", "PEM",
            "-nocrypt",
            "-in", input_key_path,
            "-out", output_key_path
        ], check=True)

        print("✅ Conversion complete.")
    except subprocess.CalledProcessError as e:
        print("❌ OpenSSL command failed.")
        print(e)
    except Exception as ex:
        print("❌ Unexpected error:")
        print(ex)

# Example usage:
convert_rsa_to_pkcs8("~/.ssh/your_old_key.pem", "~/.ssh/snowflake_key.p8")
