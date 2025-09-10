from pathlib import Path
from mcp.server.fastmcp import FastMCP
from qqwry import QQwry

mcp = FastMCP("IP2Location")


@mcp.tool()
def lookup_ip(ip_address):
    """Lookup IP address"""
    db_file = Path(__file__).parent / "data" / "qqwry.dat"
    print(db_file)
    q = QQwry()
    q.load_file(str(db_file))
    res = q.lookup(ip_address)
    if not res or len(res) != 2:
        return "Unknown"
    return f"{res[0]} {res[1]}"


def main():
    # mcp.run(transport='stdio')
    pass


if __name__ == "__main__":
    main()
