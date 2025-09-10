Toupie
================================================================================

🗣️ Pronunciation: too-PEE. 🇫🇷 French word for "spinning top".

![Toupie](https://unsplash.com/photos/LiLPRqxWI9I/download?ixid=M3wxMjA3fDB8MXxzZWFyY2h8NHx8c3Bpbm5pbmclMjB0b3B8ZW58MHx8fHwxNzU1NTI1MTgzfDA&force=true&w=900)

<!--
Photo by <a href="https://unsplash.com/@ashamplifies?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash">Ash Amplifies</a> on <a href="https://unsplash.com/photos/gold-pyramid-on-brown-wooden-table-LiLPRqxWI9I?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash">Unsplash</a>
-->      


Getting Started
--------------------------------------------------------------------------------

Get [uv] and spin a toupie server with

```bash
uvx --from git+https://github.com/boisgera/toupie toupie
```

If you need additional Python dependencies, use the `--with` option.
For example:

```bash
uvx --with raylib --from git+https://github.com/boisgera/toupie toupie
```

> [!CAUTION]  
> Anyone who gets access to your spinning toupie server can do [a lot of damage]!

### Sanity check

To check that your toupie server works as expected, do

```bash
curl -X POST http://127.0.0.1:8000 -H "Content-Type: text/plain" --data-binary "print(1+1)"
```

or if `curl` is not available

```bash
uvx --with requests python -c "import requests; r = requests.post(url='http://127.0.0.1:8000', headers={'Content-Type': 'text/plain'}, data='print(1+1)'); print(r.text)"
```

In any case, you should see `2` should printed in your terminal.


[uv]: https://docs.astral.sh/uv/
[a lot of damage]: https://www.youtube.com/watch?v=JZLAHGfznlY