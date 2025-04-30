import json
import openai
import os
import random
import requests
from openai import OpenAI

from .utils import create_game_id

MODEL_CHOICES = [
    "o1-mini",
    "gpt-4o",
    "gpt-3.5-turbo",
    "gpt-4o-mini",
]


def validate_model(model):
    if model not in MODEL_CHOICES:
        print(f"Not a valid model, using default, {MODEL_CHOICES[0]}")
        model = MODEL_CHOICES[0]

    return model


def load_json(file_path):
    with open(file_path, "r") as file:
        return json.load(file)


def generate_random_game_prompt():
    classic_games = load_json("classic_games.json")["classic_games"]
    game = random.choice(classic_games)
    prompt = f"Develop a basic '{game}' game."
    return prompt


def apply_oblique_strategy(prompt):
    oblique_strategies = load_json("oblique_strategies.json")["oblique_strategies"]
    strategy = random.choice(oblique_strategies)
    prompt += f" Modify it by applying the oblique strategy: '{strategy}'."
    return prompt


def generate_name(prompt, model="gpt-4o"):
    """Generates remediation's using OpenAI API and Autogen."""

    client = OpenAI()

    model = validate_model(model)

    completion = client.chat.completions.create(
        model=model,
        temperature=0.7,
        top_p=0.8,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that generates concise, standalone "
                "names for video games. Your answers have no preamble or summary. "
                "You provide them in text only without markdown.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    response = completion.choices[0].message.content

    # Remove any unintended leading/trailing quotes
    if response.startswith('"') and response.endswith('"'):
        response = response[1:-1]

    return response


def generate_branding(prompt_task, prompt_name, model="gpt-4o"):
    """Generates remediation's using OpenAI API and Autogen."""

    client = OpenAI()

    model = validate_model(model)

    completion = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that generates metadata about video games."
                "Your answers have no preamble or summary. "
                "You provide a short description, detailed description, and appropriate set of tags."
                "The response should be valid json of the form "
                "{'short_description': 'string', 'detailed_description': string, 'tags': list}",
            },
            {
                "role": "user",
                "content": f"The game concept is {prompt_task}, and the name of the game is {prompt_name}, "
                f"Provide the details for this game.",
            },
        ],
    )

    response = completion.choices[0].message.content

    # Remove any unintended leading/trailing quotes
    if response.startswith('"') and response.endswith('"'):
        response = response[1:-1]

    response = response.strip("```json").strip("```")

    return response


def generate_cover(prompt_task, prompt_name, timestamp):
    """Generate and save a pixel art cover image for a game, ensuring the directory exists."""

    client = OpenAI()

    # Generate the image prompt
    prompt = (
        f"Generate a pixel art cover image for the game {prompt_name} {prompt_task} "
        f"a project for itch.io. The specifications are as follows: "
        f"The cover image is used whenever itch.io wants to link to your project "
        f"from another part of the site. Required (Minimum: 315x250, Recommended: 630x500)."
    )

    try:
        # Request image generation from OpenAI
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        # Retrieve image URL
        image_url = response.data[0].url
        game_id = create_game_id(prompt_name)

        # Define the directory and ensure it exists
        dir_path = os.path.join("Branding", game_id)
        os.makedirs(dir_path, exist_ok=True)

        # Define image file path
        image_path = os.path.join(dir_path, "cover.png")

        # Download and save the image
        image_data = requests.get(image_url).content
        with open(image_path, "wb") as file:
            file.write(image_data)

        print(f"Image saved as {image_path}")
        print(f"View online at {image_url}")

    except openai.OpenAIError as e:
        print(e.http_status)
        print(e.error)
