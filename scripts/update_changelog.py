from pathlib import Path

from p4.docs.changelog import append_changelog

if __name__ == "__main__":
    print(append_changelog(Path.cwd()))
