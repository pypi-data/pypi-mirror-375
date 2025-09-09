from os import path

import networkx as nx

try:
    import matplotlib.pyplot as plt

    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.util import CommandError

from pylembic.exceptions import CircularDependencyError
from pylembic.logger import configure_logger


logger = configure_logger()


class Validator:
    """This class provides methods to validate Alembic migrations for linearity,
    missing nodes, and circular dependencies.

    Here is a summary of the checks performed:
        - Linearity: Ensures a clean and predictable migration chain.
        - Circular dependencies: Prevents migration failures due to loops in the
        dependency chain.
        - Disconnected roots: Identifies migrations improperly created without linking
        to the base.
        - Disconnected leaves: Flags migrations that are improperly disconnected from
        subsequent migrations.
        - Multiple roots/heads: Warns about unintentional forks or branching.
        - Branching: Identifies migrations that have multiple parents or children.
        - Graph visualization: Provides a visual way to catch anomalies and understand
        migration flow.
    """

    ALEMBIC_CONFIG_FILE = "alembic.ini"

    def __init__(
        self, alembic_config_path: str, alembic_config_file: str = None
    ) -> None:
        if not path.exists(alembic_config_path):
            raise FileNotFoundError(f"Path '{alembic_config_path}' does not exist!")

        self.alembic_config_path = alembic_config_path
        self.alembic_config_file = alembic_config_file or self.ALEMBIC_CONFIG_FILE
        self.verbose = False
        self.script: ScriptDirectory = None

        # Load the Alembic configuration
        self._load_alembic_config()

        # Build the migration graph
        self.graph = self._build_graph()

    @property
    def migrations_count(self) -> int:
        """Returns the total number of migrations."""
        return len(list(self.script.walk_revisions()))

    def _load_alembic_config(self) -> None:
        """Loads the Alembic configuration file and initializes the script directory."""
        alembic_config = Config(
            path.join(self.alembic_config_path, self.alembic_config_file)
        )
        alembic_config.set_main_option("script_location", self.alembic_config_path)
        self.script = ScriptDirectory.from_config(alembic_config)

    def _build_graph(self) -> None:
        """Builds a directed graph of migrations."""
        graph = nx.DiGraph()
        try:
            for revision in self.script.walk_revisions():
                graph.add_node(revision.revision)
                if revision.down_revision:
                    if isinstance(revision.down_revision, tuple):
                        # Handle branching migrations
                        for down_rev in revision.down_revision:
                            graph.add_edge(revision.revision, down_rev)
                    else:
                        graph.add_edge(revision.revision, revision.down_revision)
        except CommandError as exc:
            raise CircularDependencyError(str(exc)) from exc

        return graph

    def _orphans(self) -> bool:
        """
        Checks for orphan migrations in the Alembic script directory.
        As the orphan migrations are not connected to the migration graph, they are
        considered as a valid base and head.
        If the migration graph has only one migration, it is skipped.

        Returns:
            bool: True if orphan migrations are found.
        """
        if self.migrations_count == 1:
            logger.info("Only one migration detected. Skipping orphan check.")
            return False

        bases = set(self.script.get_bases())
        heads = set(self.script.get_heads())
        orphans = bases.intersection(heads)
        if orphans:
            logger.error("Orphan migrations detected.", extra={"orphans": orphans})
            return True

        logger.info("No orphan migrations detected.")
        return False

    def _multiple_bases_or_heads(self) -> bool:
        """
        Checks if there are multiple bases or heads in the migration graph.

        Returns:
            bool: True if multiple bases or heads are found.
        """
        bases = set(self.script.get_bases())
        if len(bases) > 1:
            logger.error("Multiple bases detected", extra={"bases": bases})
            return True

        heads = set(self.script.get_heads())
        if len(heads) > 1:
            logger.error("Multiple heads detected", extra={"heads": heads})
            return True

        logger.info("No multiple bases or heads detected.")

        return False

    def _branches(self) -> bool:
        """
        Checks for branching migrations in the Alembic script directory.

        Returns:
            bool: True if branching migrations are found.
        """
        branches = False
        for node in self.graph.nodes:
            if self.graph.out_degree(node) > 1:
                branches = True
                logger.error(
                    "Branching migration detected.",
                    extra={
                        "migration": node,
                        "down_revisions": list(self.graph.successors(node)),
                    },
                )
            if self.graph.in_degree(node) > 1:
                branches = True
                logger.error(
                    "Branching migration detected.",
                    extra={
                        "migration": node,
                        "up_revisions": list(self.graph.predecessors(node)),
                    },
                )

        if not branches:
            logger.info("No branching migrations detected.")

        return branches

    def validate(self, detect_branches: bool = False, verbose: bool = False) -> bool:
        """This method validates the Alembic migrations for linearity and missing nodes.

        Args:
            branching (bool): If True, checks for branching migrations.
            verbose (bool): If True, the logger verbosity is increased.

        Returns:
            bool: True if the migrations are valid.
        """
        # Reconfigure the logger verbosity
        global logger
        logger = configure_logger(verbose)  # noqa F841

        # Check for branching migrations
        branches = self._branches() if detect_branches else False

        # Perform validation checks within the graph
        return not (self._orphans() or self._multiple_bases_or_heads() or branches)

    def show_graph(self) -> None:
        """
        Visualizes the migration dependency graph.
        """
        if not HAS_MATPLOTLIB:
            raise ImportError(
                "Graph visualization requires matplotlib. "
                "Install with 'pip install pylembic[all]' to enable this feature."
            )

        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(self.graph)
        labels = {node: f"{node[:8]}" for node in self.graph.nodes}  # Short revision ID
        nx.draw(
            self.graph,
            pos,
            labels=labels,
            node_size=3000,
            node_color="lightblue",
            font_size=10,
            font_weight="bold",
            label="Alembic Migration Graph",
        )
        # Set the custom window title
        manager = plt.get_current_fig_manager()
        manager.set_window_title("Alembic Migration Dependency Graph")
        plt.show()
