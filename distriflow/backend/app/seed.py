"""Compatibility entry point: schema migration only. Never creates business data."""

from app.setup.migrate import upgrade


def main():
    upgrade()
    print(
        "Schema ready. No demo warehouses, partners, SKUs, stock or documents were created."
    )


if __name__ == "__main__":
    main()
