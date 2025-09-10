# Python Standard Library
import ast
import logging
from multiprocessing import Process


# Third-Party Librairies
from flask import Flask, request
import requests
from rich.logging import RichHandler
import typer
from typing_extensions import Annotated
import waitress

# Constants
HOST = "127.0.0.1"
PORT = "8000"

app = Flask(__name__)

OK = requests.codes.ok
BAD = requests.codes.bad


@app.route("/", methods=["POST"])
def handler() -> tuple[str, int]:
    code = request.data.decode("utf-8").strip()
    logger.info(code)
    output = ""
    status = OK
    try:
        try:
            ast.parse(code, mode="eval")
            obj = eval(code, globals())
            # The 'str' transform makes it possible to output strings unquoted.
            # The user can still wrap its request into a 'repr' to get the variant.
            output = str(obj)
        except SyntaxError:  # not an expression, try to interpret as a statement
            exec(code, globals())
    except Exception as e:
        error = f"{type(e).__name__}: {e}"
        logger.error(error)
        output = error
        status = BAD

    if status == OK and output != "":
        logger.info(output)
    elif status == BAD:
        logger.error(output)
    return output, status


def interpret(code: str, port: int = PORT) -> str:
    response = requests.post(
        url=f"http://127.0.0.1:{port}",
        headers={"Content-Type": "text/plain"},
        data=code,
    )
    return response


def spin(
    port: int = PORT, verbose: bool = False, background: bool = False
) -> Process | None:
    global logger
    if background:
        p = Process(target=lambda: spin(port=port, verbose=verbose), daemon=True)
        p.start()
        return p
    else:
        logging.basicConfig(
            level="INFO" if verbose else "WARNING",
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler()],
        )
        logger = logging.getLogger("toupie")
        logger.info(f"Toupie spinning at http://{HOST}:{port}")
        logging.getLogger("waitress").setLevel(logging.ERROR)
        waitress.serve(app, host=HOST, port=port, threads=1)


def main() -> None:
    return typer.run(spin)
