import datetime
import os
from datetime import date

import requests
import typer
from PIL import Image


def serve_lunch(date_string: str):
    with open(f"{date_string}.png", "wb") as f:
        response = requests.get(
            "https://www.tu.no/?module=TekComics&service=image&id=lunch&key=" + date_string
        )
        f.write(response.content)
        try:
            response.raise_for_status()
        except requests.HTTPError:
            print("Terribly sorry, we're all out of that particular lunch")
            return -1

    img = Image.open(f"{date_string}.png")
    img.show()
    print("Lunch is served")
    os.remove(f"{date_string}.png")
    return 1


def main():
    today = date.today()
    today_string = f"{today.year}-{today.month}-{today.day}"
    serve_lunch(today_string)
    still_hungry = "y"
    no_of_servings = 1

    while (still_hungry == "y") & (no_of_servings < 20):
        still_hungry = input("Are you still hungry? y/n")
        if still_hungry != "y":
            break
        today -= datetime.timedelta(days=1)
        today_string = f"{today.year}-{today.month}-{today.day}"
        lunch_left = serve_lunch(today_string)
        if not lunch_left:
            break
        no_of_servings += 1


def run():
    typer.run(main)


if __name__ == "__main__":
    run()
