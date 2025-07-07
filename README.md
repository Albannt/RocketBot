# RocketBot
This was the first time i had the chance to use Python for work, it is a very basic script to periodically run and sync your AD users with Rocket.Chat. It adds and removes users from teams based on mapped security group membership, creates and updates the main user list (in the form of a message in the user hub channel).
### Notes
This app is very proprietary and a couple years old. I took the chance to refactor it a bit recently, but there's still a ton of work to be done and documented.
## Setup
- Make a copy of `config_example.py` and rename it to `config.py`, then fill it in with your own environment constants, same with `teams_data_example.json` and Team data
- Do the same thing with `txtData_example.json`, but don't change the file contents
- Run through all files and read comments detailing what changes what, proper documentation TBA (?)
## Startup
run `main.py`
