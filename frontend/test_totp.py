#!/usr/bin/env python
"""
Quick TOTP testing script
Usage: python test_totp.py <secret_key>
"""
import sys
from django_otp.oath import totp
import time

def hex_to_bin(hex_key):
    """Convert hex key to binary"""
    return bytes.fromhex(hex_key)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python test_totp.py <secret_key_in_hex>")
        print("Example: python test_totp.py b0644742993f6437251d3013b0ece1debd26e747")
        sys.exit(1)
    
    secret_key = sys.argv[1]
    
    print(f"Secret Key (hex): {secret_key}")
    print(f"Current time: {int(time.time())}")
    print(f"\nGenerating tokens...")
    
    try:
        bin_key = hex_to_bin(secret_key)
        
        # Generate current token
        current_token = totp(bin_key, step=30)
        print(f"\n✓ Valid token right now: {current_token:06d}")
        
        print("\nTokens for nearby time windows:")
        current_time = int(time.time())
        for offset in range(-2, 3):
            # Calculate time counter for each window
            time_counter = (current_time + (offset * 30)) // 30
            token = totp(bin_key, drift=offset, step=30)
            marker = " <-- CURRENT" if offset == 0 else ""
            print(f"  Offset {offset:+2d}: {token:06d}{marker}")
        
    except Exception as e:
        print(f"Error: {e}")
