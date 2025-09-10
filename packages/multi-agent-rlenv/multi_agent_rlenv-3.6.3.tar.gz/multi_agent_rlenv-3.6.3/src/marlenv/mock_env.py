import numpy as np
from dataclasses import dataclass
from marlenv import MARLEnv, Observation, ContinuousSpace, Step, State, DiscreteSpace, MultiDiscreteSpace


@dataclass
class DiscreteMockEnv(MARLEnv[MultiDiscreteSpace]):
    def __init__(
        self,
        n_agents: int = 4,
        obs_size: int = 42,
        n_actions: int = 5,
        end_game: int = 30,
        reward_step: int | float | np.ndarray | list = 1,
        agent_state_size: int = 1,
        extras_size: int = 0,
    ) -> None:
        match reward_step:
            case int() | float():
                reward_step = np.array([reward_step])
            case list():
                reward_step = np.array(reward_step)
            case np.ndarray():
                reward_step = reward_step
            case _:
                raise ValueError("reward_step must be an int, float or np.ndarray")
        super().__init__(
            n_agents,
            DiscreteSpace(n_actions).repeat(n_agents),
            (obs_size,),
            (n_agents * agent_state_size,),
            extras_shape=(extras_size,),
            reward_space=ContinuousSpace.from_shape(reward_step.shape),
        )
        self.reward_step = reward_step
        self.obs_size = obs_size
        self.extra_size = extras_size
        self._agent_state_size = agent_state_size
        self.end_game = end_game
        self.t = 0
        self.actions_history = []
        self._seed = -1

    @property
    def agent_state_size(self):
        return self._agent_state_size

    def reset(self):
        self.t = 0
        self._seed += 1
        return self.get_observation(), self.get_state()

    def get_image(self):
        return np.zeros((100, 100, 3), dtype=np.uint8)

    def seed(self, seed_value: int):
        self._seed = seed_value

    def get_observation(self):
        obs_data = np.array(
            [self._seed + np.arange(self.t + agent, self.t + agent + self.obs_size) for agent in range(self.n_agents)],
            dtype=np.float32,
        )
        extras = np.arange(self.n_agents * self.extra_size, dtype=np.float32).reshape((self.n_agents, self.extra_size))
        return Observation(obs_data, self.available_actions(), extras)

    def get_state(self):
        return State(np.full((self.n_agents * self.agent_state_size,), self.t, dtype=np.float32))

    def set_state(self, state: State[np.ndarray]):
        self.t = int(state.data[0])

    def render(self, mode: str = "human"):
        return

    def step(self, actions):
        self.t += 1
        self.actions_history.append(actions)
        return Step(
            self.get_observation(),
            self.get_state(),
            self.reward_step,
            self.t >= self.end_game,
        )


class DiscreteMOMockEnv(MARLEnv[DiscreteSpace]):
    """Multi-Objective Mock Environment"""

    def __init__(
        self,
        n_agents: int = 4,
        n_objectives: int = 2,
        obs_size: int = 42,
        n_actions: int = 5,
        end_game: int = 30,
        reward_step: int = 1,
        agent_state_size: int = 1,
        extras_size: int = 0,
    ) -> None:
        super().__init__(
            n_agents,
            DiscreteSpace(n_actions),
            (obs_size,),
            (n_agents * agent_state_size,),
            extras_shape=(extras_size,),
            reward_space=ContinuousSpace.from_shape(n_objectives),
        )
        self.obs_size = obs_size
        self.extra_size = extras_size
        self._agent_state_size = agent_state_size
        self.end_game = end_game
        self.reward_step = np.full((n_objectives,), reward_step, dtype=np.float32)
        self.t = 0
        self.actions_history = []

    @property
    def agent_state_size(self):
        return self._agent_state_size

    def reset(self):
        self.t = 0
        return self.get_observation(), self.get_state()

    def get_observation(self):
        obs_data = np.array(
            [np.arange(self.t + agent, self.t + agent + self.obs_size) for agent in range(self.n_agents)],
            dtype=np.float32,
        )
        extras = np.arange(self.n_agents * self.extra_size, dtype=np.float32).reshape((self.n_agents, self.extra_size))
        return Observation(obs_data, self.available_actions(), extras)

    def get_state(self):
        s = State(np.full((self.n_agents * self.agent_state_size,), self.t, dtype=np.float32))
        s.add_extra(self.t)
        return s

    def step(self, action):
        self.t += 1
        self.actions_history.append(action)
        return Step(
            self.get_observation(),
            self.get_state(),
            self.reward_step,
            self.t >= self.end_game,
        )
