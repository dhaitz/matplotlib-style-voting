# encoding: utf-8

from flask import Flask, render_template
import json
import os
import re
from requests_futures import sessions

import plot

app = Flask(__name__)
session = sessions.FuturesSession()

POLL_URL = f"https://api.gh-polls.com/poll/{os.environ['POLL_ID']}/"
DEFAULT_INFO_URL = "https://matplotlib.org//tutorials/introductory/customizing.html"


def init_styles(styles_filename):
    """Load the styles dict from JSON and construct the necessary URL properties"""

    with open(styles_filename, 'rb') as f:
        styles = json.load(f)

    for (style, style_properties) in styles.items():
        style_properties['poll_img_url'] = POLL_URL + style
        style_properties['info_url'] = style_properties.get('info_url', DEFAULT_INFO_URL)
        style_properties['poll_vote_url'] = style_properties['poll_img_url'] + '/vote'
        style_properties['votes'] = 0

    return styles


STYLES = init_styles(styles_filename='styles.json')


@app.route('/')
def main():
    styles_sorted = query_votes_and_update_style_order(STYLES)
    return render_template('index.html', styles=styles_sorted)


def query_votes_and_update_style_order(styles):
    """Since querying the number of votes takes some time, do it only every N minutes"""
    # use multiprocessing to get votes, then assign to dict
    style_list = list(styles.keys())
    urls = [POLL_URL + style for style in style_list]

    futures = [session.get(url) for url in urls]  # https://julien.danjou.info/python-and-fast-http-clients/
    contents = [f.result().content for f in futures]

    for style, content in zip(style_list, contents):
        votes = get_vote_from_content(content)
        styles[style]['votes'] = votes
        print(f" {style}: {votes} votes")

    # re-order according to votes
    styles_sorted_by_votes = sorted(styles.items(), key=lambda x: x[1]['votes'], reverse=True)  # list of tuples: [(style_A, style_A_properties), ...]
    styles = {style_name: style_properties for style_name, style_properties in styles_sorted_by_votes}
    print("Style order:", ", ".join(styles.keys()))
    return styles


def get_vote_from_content(content):
    """Because we can't query the number of votes directly: get the SVG and extract the number from there via regex."""
    result = re.search('<tspan x="386" y="30">(.*)</tspan>', content.decode())
    if result:
        return int(result.group(1))
    else:
        return 0


def create_images(output_folder, styles):
    """The style demo images are dynamically generated at startup.
       This allows easy adding styles via PR, without having to add an image.
    """
    for style, style_properties in styles.items():
        style_argument = style_properties.get('style_argument', style)
        plot.plot_and_save(output_folder=output_folder, style_name=style, style=style_argument)


if __name__ == '__main__':
    # create_images(output_folder='static/img/')
    app.run()
