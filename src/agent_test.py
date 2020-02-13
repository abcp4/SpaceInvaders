from tensorforce.agents import Agent
import numpy as np

# Instantiate a Tensorforce agent
agent = Agent.create(
    agent='tensorforce',
    states=dict(type='float', shape=(10,)),
    actions=dict(type='int', shape=(3),num_values=2),
    max_episode_timesteps=100,
    memory=10000,
    update=dict(unit='timesteps', batch_size=64),
    optimizer=dict(type='adam', learning_rate=3e-4),
    policy=dict(network='auto'),
    objective='policy_gradient',
    reward_estimation=dict(horizon=20)
)

# Retrieve the latest (observable) environment state
state = np.zeros(10)

# Query the agent for its action decision
action = agent.act(states=state)  # (scalar between 0 and 4)

print(action)
reward = 0
# Pass feedback about performance (and termination) to the agent
agent.observe(reward=reward, terminal=False)


