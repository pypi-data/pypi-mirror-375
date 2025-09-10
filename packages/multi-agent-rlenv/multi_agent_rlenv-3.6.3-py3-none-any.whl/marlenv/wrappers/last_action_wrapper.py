from dataclasses import dataclass

import numpy as np
import numpy.typing as npt
from typing_extensions import TypeVar

from marlenv.models import ContinuousSpace, DiscreteSpace, MultiDiscreteSpace, Space, State

from .rlenv_wrapper import MARLEnv, RLEnvWrapper

AS = TypeVar("AS", bound=Space, default=Space)


@dataclass
class LastAction(RLEnvWrapper[AS]):
    """Env wrapper that adds the last action taken by the agents to the extra features."""

    def __init__(self, env: MARLEnv[AS]):
        assert len(env.extras_shape) == 1, "Adding last action is only possible with 1D extras"
        super().__init__(
            env,
            extra_shape=(env.extras_shape[0] + env.n_actions,),
            state_extra_shape=(env.state_extra_shape[0] + env.n_actions * env.n_agents,),
            extra_meanings=env.extras_meanings + ["Last action"] * env.n_actions,
        )
        self.state_extra_index = env.state_extra_shape[0]
        self.last_one_hot_actions = np.zeros((env.n_agents, env.n_actions), dtype=np.float32)

    def reset(self):
        obs, state = super().reset()
        self.last_one_hot_actions = np.zeros((self.n_agents, self.n_actions), dtype=np.float32)
        obs.add_extra(self.last_one_hot_actions)
        state.add_extra(self.last_one_hot_actions.flatten())
        return obs, state

    def step(self, actions):
        step = super().step(actions)
        match self.wrapped.action_space:
            case ContinuousSpace():
                self.last_actions = actions
            case DiscreteSpace() | MultiDiscreteSpace():
                self.last_one_hot_actions = self.compute_one_hot_actions(actions)
            case other:
                raise NotImplementedError(f"Action space {other} not supported")
        step.obs.add_extra(self.last_one_hot_actions)
        step.state.add_extra(self.last_one_hot_actions.flatten())
        return step

    def get_state(self):
        state = super().get_state()
        state.add_extra(self.last_one_hot_actions.flatten())
        return state

    def set_state(self, state: State):
        flattened_one_hots = state.extras[self.state_extra_index : self.state_extra_index + self.n_agents * self.n_actions]
        self.last_one_hot_actions = flattened_one_hots.reshape(self.n_agents, self.n_actions)
        return super().set_state(state)

    def compute_one_hot_actions(self, actions) -> npt.NDArray:
        one_hot_actions = np.zeros((self.n_agents, self.n_actions), dtype=np.float32)
        index = np.arange(self.n_agents)
        one_hot_actions[index, actions] = 1.0
        return one_hot_actions
