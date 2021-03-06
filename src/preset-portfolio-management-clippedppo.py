from rl_coach.agents.clipped_ppo_agent import ClippedPPOAgentParameters
from rl_coach.architectures.layers import Dense, Conv2d
from rl_coach.base_parameters import VisualizationParameters, PresetValidationParameters
from rl_coach.base_parameters import MiddlewareScheme, DistributedCoachSynchronizationType
from rl_coach.core_types import TrainingSteps, EnvironmentEpisodes, EnvironmentSteps, RunPhase
from rl_coach.environments.gym_environment import GymVectorEnvironment, ObservationSpaceType
from rl_coach.exploration_policies.e_greedy import EGreedyParameters
from rl_coach.graph_managers.basic_rl_graph_manager import BasicRLGraphManager
from rl_coach.graph_managers.graph_manager import ScheduleParameters
from rl_coach.schedules import LinearSchedule

####################
# Graph Scheduling #
####################

schedule_params = ScheduleParameters()
schedule_params.improve_steps = TrainingSteps(20000)
schedule_params.steps_between_evaluation_periods = EnvironmentSteps(2048)
schedule_params.evaluation_steps = EnvironmentEpisodes(5)
schedule_params.heatup_steps = EnvironmentSteps(0)

#########
# Agent #
#########

agent_params = ClippedPPOAgentParameters()

# Input Embedder with no CNN
# agent_params.network_wrappers['main'].input_embedders_parameters['observation'].scheme = [Dense(71)]
# agent_params.network_wrappers['main'].input_embedders_parameters['observation'].activation_function = 'tanh'
# agent_params.network_wrappers['main'].middleware_parameters.scheme = [Dense(128)]
# agent_params.network_wrappers['main'].middleware_parameters.activation_function = 'tanh'

# Input Embedder used in sample notebook
agent_params.network_wrappers['main'].input_embedders_parameters['observation'].scheme = [Conv2d(32, [3, 1], 1)]
# agent_params.network_wrappers['main'].middleware_parameters.scheme = MiddlewareScheme.Empty
agent_params.network_wrappers['main'].middleware_parameters.scheme = [Dense(128)]
agent_params.network_wrappers['main'].middleware_parameters.activation_function = 'tanh'

agent_params.network_wrappers['main'].learning_rate = 0.0001
agent_params.network_wrappers['main'].batch_size = 64
agent_params.algorithm.clipping_decay_schedule = LinearSchedule(1.0, 0, 150000)
agent_params.algorithm.discount = 0.99
agent_params.algorithm.num_steps_between_copying_online_weights_to_target = EnvironmentSteps(2048)

# Distributed Coach synchronization type.
agent_params.algorithm.distributed_coach_synchronization_type = DistributedCoachSynchronizationType.SYNC

agent_params.exploration = EGreedyParameters()
agent_params.exploration.epsilon_schedule = LinearSchedule(1.0, 0.01, 10000)

###############
# Environment #
###############

env_params = GymVectorEnvironment(level='portfolio_env:PortfolioEnv')
env_params.__dict__['observation_space_type'] = ObservationSpaceType.Tensor

########
# Test #
########

preset_validation_params = PresetValidationParameters()
preset_validation_params.test = True

graph_manager = BasicRLGraphManager(agent_params=agent_params, env_params=env_params,
                                    schedule_params=schedule_params, vis_params=VisualizationParameters(),
                                    preset_validation_params=preset_validation_params)
