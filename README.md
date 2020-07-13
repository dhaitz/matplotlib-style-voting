# Matplotlib Style Voting

- See it live [here](https://matplotlib-style-voting.herokuapp.com)

- Originated from [this tweet](https://twitter.com/d_haitz/status/1280773487628517377?s=20)

- The polling is currently implemented via [gh-polls](https://github.com/apex/gh-polls), a simple online tool which generates images that show the current vote count (voting via link)
  - ⚠️ gh-polls doesn't allow adding options to an existing poll
  - gh-polls doesnt allow to query the number of votes per style directly, only the images (SVG).
  As they are needed for the order of the styles, the vote count is extracted from the SVG via regex ...

- The style demo images are not checked in, but are dynamically generated at app startup.
This would allow easy adding of new styles via pull request (add a new style with URL in `styles.json`).
  - ⚠️ However, as adding new styles would require the creation of a new poll, not accepting any PRs at the moment

- Possible improvements:
  - A polling system which allows to add voting options
  - The possibility to upload stylesheeta or add information via an online submission form
  - Voting and submission authenticated with GitHub account
  - Long-term vision: a 'stylesheet' marketplace, as e.g. for browser extensions
