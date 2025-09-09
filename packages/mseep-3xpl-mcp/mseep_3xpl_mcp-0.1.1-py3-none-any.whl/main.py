from src.server import server

def main():
    import sys

    try:
        server.run(transport="stdio")
    except Exception as e:
        print(e, file=sys.stderr)
