from typing import Any

from libsms.api import check_simulation_status, download_analysis_output, get_analysis_manifest, run_simulation, get_simulation_log
from libsms.data_model import EcoliExperiment, SimulationRun

__all__ = ["analysis_manifest", "analysis_output", "ecoli_experiment", "simulation_status", "simulation_log"]


async def ecoli_experiment(
    config_id: str, max_retries: int = 20, delay_s: float = 1.0, verbose: bool = False, **body: dict[str, Any]
) -> EcoliExperiment | None:
    return await run_simulation(config_id, max_retries, delay_s, verbose, **body)


async def simulation_status(
    experiment: EcoliExperiment, max_retries: int = 20, delay_s: float = 1.0, verbose: bool = False
) -> SimulationRun | None:
    return await check_simulation_status(experiment, max_retries, delay_s, verbose)


async def analysis_manifest(
    experiment: EcoliExperiment, max_retries: int = 20, delay_s: float = 1.0, verbose: bool = False
) -> dict[str, Any] | None | Any:
    return await get_analysis_manifest(experiment, max_retries, delay_s, verbose)


async def analysis_output(
    experiment: EcoliExperiment,
    filename: str,
    variant: int = 0,
    lineage_seed: int = 0,
    generation: int = 1,
    agent_id: int = 0,
    max_retries: int = 20,
    delay_s: float = 1.0,
    verbose: bool = False,
) -> Any | None:
    return await download_analysis_output(
        experiment, filename, variant, lineage_seed, generation, agent_id, max_retries, delay_s, verbose
    )


async def simulation_log(experiment: EcoliExperiment) -> str:
    return get_simulation_log(experiment)