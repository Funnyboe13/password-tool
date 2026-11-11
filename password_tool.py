import argparse
import getpass
import secrets
import string

COMMON_PASSWORDS = {
    "password", "123456", "12345678", "123456789", "qwerty", "abc123",
    "password1", "111111", "iloveyou", "admin", "welcome", "letmein",
    "monkey", "dragon", "football",
}

SYMBOLS = "!@#$%^&*()-_=+[]{};:,.?"


def check_password(password):
    """Return (score, tips). The score is from 0 to 100."""
    score = 0
    tips = []

    # Length: up to 40 points
    length = len(password)
    if length >= 16:
        score += 40
    elif length >= 12:
        score += 30
    elif length >= 8:
        score += 20
        tips.append("Longer is stronger: aim for 12 or more characters.")
    else:
        score += 5
        tips.append("Use at least 12 characters.")

    # Character variety: 15 points each, up to 60
    checks = [
        (any(c.islower() for c in password), "Add lowercase letters."),
        (any(c.isupper() for c in password), "Add uppercase letters."),
        (any(c.isdigit() for c in password), "Add numbers."),
        (any(not c.isalnum() for c in password), "Add symbols like ! @ # $."),
    ]
    for passed, message in checks:
        if passed:
            score += 15
        else:
            tips.append(message)

    # Too many repeated characters, like "aaaa1111"
    if len(set(password)) <= len(password) // 2:
        score -= 10
        tips.append("Too many repeated characters.")

    # Short passwords can never be better than "Weak"
    if length < 10:
        score = min(score, 55)

    # Very common passwords are always weak
    if password.lower() in COMMON_PASSWORDS:
        score = min(score, 10)
        tips.append("This is a very common password. Never use it.")

    return max(0, min(score, 100)), tips


def rate(score):
    """Turn a score into a rating word."""
    if score >= 80:
        return "Strong"
    if score >= 60:
        return "Good"
    if score >= 40:
        return "Weak"
    return "Very weak"


def generate_password(length=16, use_symbols=True):
    """Generate a random password using the secure 'secrets' module."""
    pools = [string.ascii_lowercase, string.ascii_uppercase, string.digits]
    if use_symbols:
        pools.append(SYMBOLS)

    # Make sure there is at least one character from every group
    chars = [secrets.choice(pool) for pool in pools]

    # Fill the rest with random characters from all groups
    all_chars = "".join(pools)
    chars += [secrets.choice(all_chars) for _ in range(length - len(chars))]

    # Shuffle so the guaranteed characters are not always at the start
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)


def cmd_check(args):
    password = getpass.getpass("Enter a password to check (typing is hidden): ")

    if not password:
        print("No password entered.")
        return

    score, tips = check_password(password)

    print(f"\nScore : {score}/100")
    print(f"Rating: {rate(score)}")

    if tips:
        print("\nTips:")
        for tip in tips:
            print(f"  - {tip}")
    else:
        print("\nNo problems found. Great password!")


def cmd_generate(args):
    if not 8 <= args.length <= 128:
        print("Length must be between 8 and 128.")
        return
    if not 1 <= args.count <= 50:
        print("Count must be between 1 and 50.")
        return

    for _ in range(args.count):
        password = generate_password(args.length, not args.no_symbols)
        score, _tips = check_password(password)
        print(f"{password}   [{rate(score)}]")


def main():
    parser = argparse.ArgumentParser(
        description="Check password strength or generate strong passwords."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_parser = subparsers.add_parser(
        "check", help="check the strength of a password"
    )
    check_parser.set_defaults(func=cmd_check)

    gen_parser = subparsers.add_parser(
        "generate", help="generate random passwords"
    )
    gen_parser.add_argument(
        "-l", "--length", type=int, default=16,
        help="password length (default: 16)",
    )
    gen_parser.add_argument(
        "-n", "--count", type=int, default=1,
        help="how many passwords to generate (default: 1)",
    )
    gen_parser.add_argument(
        "--no-symbols", action="store_true",
        help="use only letters and numbers",
    )
    gen_parser.set_defaults(func=cmd_generate)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()