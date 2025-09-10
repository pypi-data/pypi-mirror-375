from typing import Sequence
from dataclasses import dataclass
from typing_extensions import TypeVar
import random

from marlenv import RLEnvWrapper, MARLEnv
from marlenv.models import Space

ActionSpaceType = TypeVar("ActionSpaceType", bound=Space, default=Space)


@dataclass
class EnvPool(RLEnvWrapper[ActionSpaceType]):
    envs: Sequence[MARLEnv[ActionSpaceType]]

    def __init__(self, envs: Sequence[MARLEnv[ActionSpaceType]]):
        assert len(envs) > 0, "EnvPool must contain at least one environment"
        self.envs = envs
        for env in envs[1:]:
            assert env.has_same_inouts(self.envs[0]), "All environments must have the same inputs and outputs"
        super().__init__(self.envs[0])

    def seed(self, seed: int):
        random.seed(seed)
        for env in self.envs:
            env.seed(seed)

    def reset(self):
        self.wrapped = random.choice(self.envs)
        return super().reset()
