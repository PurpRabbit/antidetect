from utils.paths import USER_AGENTS


with open(USER_AGENTS) as fp:
    user_agents = fp.readlines()

user_agents = list(map(str.strip, user_agents))
