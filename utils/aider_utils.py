from aider.coders import Coder, ArchitectCoder
from aider.models import Model
from aider.io import InputOutput


def create_coder(model_name, auto_commits, dirty_commits, dry_run, files=None):
    """
    Create and return an ArchitectCoder instance with the specified configuration.

    Args:
        model_name (str): The name of the model to use.
        files (list, optional): List of filenames to be read-only. Defaults to None.
        auto_commits (bool): Whether to enable automatic commits.
        dirty_commits (bool): Whether to allow commits with uncommitted changes.
        dry_run (bool): Whether to run in dry-run mode.

    Returns:
        ArchitectCoder: Configured ArchitectCoder instance.
    """

    try:
        # Create InputOutput for non-interactive mode with all confirmations disabled
        io = InputOutput(yes=True, pretty=False)

        # Create model instance
        model = Model(model=model_name)

        # Create ArchitectCoder instance
        # coder = ArchitectCoder.create(
        #     main_model=model,
        #     fnames=[],
        #     read_only_fnames=files if files else [],
        #     io=io,
        #     auto_commits=auto_commits,
        #     dirty_commits=dirty_commits,
        #     dry_run=dry_run,
        # )

        # Create Coder instance
        coder = ArchitectCoder.create(
            main_model=model,
            io=io,
            auto_commits=auto_commits,
            dirty_commits=dirty_commits,
            dry_run=dry_run,
        )

        return coder

    except Exception as e:
        raise RuntimeError(f"Failed to initialize model/coder: {str(e)}")


def execute_instruction(coder, instruction):
    """
    Execute the given instruction using the provided coder instance.

    Args:
        coder (ArchitectCoder): The coder instance to use for execution.
        instruction (str): The instruction to execute.

    Returns:
        str: The result of the execution.
    """

    try:
        result = coder.run(instruction)
        return result
    except Exception as e:
        raise RuntimeError(f"Failed to execute instruction: {str(e)}")
