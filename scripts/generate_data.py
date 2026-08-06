import sys

from app.cli import app


if __name__ == "__main__":
    app(args=["data", "generate", *sys.argv[1:]], prog_name="generate_data.py")
