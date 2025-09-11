def main() -> None:
    from .touch import touch as _touch
    env = {}  # empty sandbox; users can import/retouch what they want
    _touch(env, env)

if __name__ == "__main__":
    main()
