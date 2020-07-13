# encoding: utf-8

from datetime import timedelta
from flask import Flask, render_template
import json
import os
import re
import timeloop
import urllib.request

import plot

app = Flask(__name__)

styles = None

POLL_URL = f"https://api.gh-polls.com/poll/{os.environ['POLL_ID']}/"
MINUTES_BETWEEN_VOTE_QUERY = int(os.environ['MINUTES_BETWEEN_VOTE_QUERY'])
DEFAULT_INFO_URL = "https://matplotlib.org//tutorials/introductory/customizing.html"

tl = timeloop.Timeloop()


@app.route('/')
def main():
    return render_template('index.html', styles=styles, minutes_between_vote_query=MINUTES_BETWEEN_VOTE_QUERY)


def init_styles(styles_filename):
    """Load the styles dict from JSON and construct the necessary URL properties"""
    global styles

    with open(styles_filename, 'rb') as f:
        styles = json.load(f)

    for (style, style_properties) in styles.items():
        style_properties['poll_img_url'] = POLL_URL + style
        style_properties['info_url'] = style_properties.get('info_url', DEFAULT_INFO_URL)
        style_properties['poll_vote_url'] = style_properties['poll_img_url'] + '/vote'

    query_votes_and_update_style_order()


@tl.job(interval=timedelta(minutes=MINUTES_BETWEEN_VOTE_QUERY))
def query_votes_and_update_style_order():
    """Since querying the number of votes takes some time, do it only every N minutes"""
    global styles

    for style, style_properties in styles.items():
        style_properties['votes'] = get_votes_for_style(POLL_URL + style)
        print(f" {style}: {style_properties['votes']} votes")

    # re-order according to votes
    styles_sorted_by_votes = sorted(styles.items(), key=lambda x: x[1]['votes'], reverse=True)  # list of tuples: [(style_A, style_A_properties), ...]
    styles = {style_name: style_properties for style_name, style_properties in styles_sorted_by_votes}
    print("Style order:", ", ".join(styles.keys()))


def get_votes_for_style(img_url):
    """Because we can't query the number of votes directly: get the SVG and extract the number from there via regex."""
    try:
        content = urllib.request.urlopen(img_url).read()
        print(f"Getting votes from {img_url}")
    except urllib.error.HTTPError:
        return 0

    result = re.search('<tspan x="386" y="30">(.*)</tspan>', content.decode())
    if result:
        return int(result.group(1))
    else:
        return 0


def create_images(output_folder):
    """The style demo images are dynamically generated at startup.
       This allows easy adding styles via PR, without having to add an image.
    """
    for style, style_properties in styles.items():
        style_argument = style_properties.get('style_argument', style)
        plot.plot_and_save(output_folder=output_folder, style_name=style, style=style_argument)


init_styles(styles_filename='styles.json')
tl.start()

if __name__ == '__main__':
    create_images(output_folder='static/img/')
    app.run()
