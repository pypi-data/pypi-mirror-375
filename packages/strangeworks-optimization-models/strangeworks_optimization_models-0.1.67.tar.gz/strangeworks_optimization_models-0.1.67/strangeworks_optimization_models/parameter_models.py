import json
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional


class SWHybridParameterModel:
    def __init__(
        self,
        workflow_path: Optional[Path] = None,
        decompose_size: Optional[int] = None,
        convergence: Optional[float] = None,
        tags: Optional[list] = None,
        sampler_parameters: Optional[Dict[Any, Any]] = None,
    ) -> None:
        # Path to the python file containing the workflow function. If None, the Strangeworks
        # default hybrid workflow will be used.
        if workflow_path:
            file_list = []
            with open(workflow_path) as fh:
                for line in fh:
                    file_list.append(line)
            self.json_file: str | None = json.dumps(file_list)
        else:
            self.json_file = None

        # Max size of decomposed sub problems. If None, the default value of 50 is used. Only applies
        # to the default strangeworks hybrid workflow
        self.decompose_size = decompose_size
        # Convergence threshhold for the hybrid workflow. If None the default value of 3 us used.
        # Only applies to the default strangeworks hybrid workflow
        self.convergence = convergence

        # List of string tags to be added to the parent hybrid job
        self.tags = tags

        # Sampler parameters, for the base solver system, to be used in the hybrid workflow.
        # Each sub problem sent to a solver will use these parameters.
        self.sampler_parameters: Dict | None = sampler_parameters

    def serialize_options(self) -> None:
        if self.sampler_parameters:
            sampler_parameters = self.sampler_parameters
            self.sampler_parameters = {}
            for spkey in sampler_parameters:
                sp = sampler_parameters[spkey]
                if sp:
                    temp_sampler_parameters = sp.__dict__
                    for k in list(temp_sampler_parameters.keys()):
                        if temp_sampler_parameters[k] is None:
                            del temp_sampler_parameters[k]
                    self.sampler_parameters[spkey] = temp_sampler_parameters
                else:
                    self.sampler_parameters[spkey] = None


class EmbeddingParameterModel:
    def __init__(
        self,
        max_no_improvement: Optional[int] = None,
        random_seed: Optional[int] = None,
        timeout: Optional[int] = None,
        max_beta: Optional[float] = None,
        tries: Optional[int] = None,
        inner_rounds: Optional[int] = None,
        chainlength_patience: Optional[int] = None,
        max_fill: Optional[int] = None,
        threads: Optional[int] = None,
        return_overlap: Optional[bool] = None,
        skip_initialization: Optional[bool] = None,
        verbose: Optional[int] = None,
        interactive: Optional[bool] = None,
        initial_chains: Optional[dict] = None,
        fixed_chains: Optional[dict] = None,
        restrict_chains: Optional[dict] = None,
        suspend_chains: Optional[dict] = None,
    ) -> None:
        # Embedding Parameters
        # -- see: https://docs.ocean.dwavesys.com/en/stable/docs_system/reference/generated/minorminer.find_embedding.html
        # max_no_improvement (int, optional, default=10):
        # Maximum number of failed iterations to improve the current solution, where each iteration attempts to find an
        # embedding for each variable of S such that it is adjacent to all its neighbours.
        self.max_no_improvement = max_no_improvement

        # random_seed (int, optional, default=None):
        # Seed for the random number generator. If None, seed is set by os.urandom().
        self.random_seed = random_seed

        # timeout (int, optional, default=1000):
        # Algorithm gives up after timeout seconds.
        self.timeout = timeout

        # max_beta (double, optional, max_beta=None):
        # Qubits are assigned weight according to a formula (beta^n) where n is the number of chains containing that qubit.
        # This value should never be less than or equal to 1. If None, max_beta is effectively infinite.
        self.max_beta = max_beta

        # tries (int, optional, default=10):
        # Number of restart attempts before the algorithm stops. On D-WAVE 2000Q, a typical restart takes between 1 and
        # 60 seconds.
        self.tries = tries

        # inner_rounds (int, optional, default=None):
        # The algorithm takes at most this many iterations between restart attempts; restart attempts are typically
        # terminated due to max_no_improvement. If None, inner_rounds is effectively infinite.
        self.inner_rounds = inner_rounds

        # chainlength_patience (int, optional, default=10):
        # Maximum number of failed iterations to improve chain lengths in the current solution, where each iteration
        # attempts to find an embedding for each variable of S such that it is adjacent to all its neighbours.
        self.chainlength_patience = chainlength_patience

        # max_fill (int, optional, default=None):
        # Restricts the number of chains that can simultaneously incorporate the same qubit during the search. Values above
        # 63 are treated as 63. If None, max_fill is effectively infinite.
        self.max_fill = max_fill

        # threads (int, optional, default=1):
        # Maximum number of threads to use. Note that the parallelization is only advantageous where the expected degree of
        # variables is significantly greater than the number of threads. Value must be greater than 1.
        self.threads = threads

        # return_overlap (bool, optional, default=False):
        # This function returns an embedding, regardless of whether or not qubits are used by multiple variables. return_overlap
        # determines the function’s return value. If True, a 2-tuple is returned, in which the first element is the embedding
        # and the second element is a bool representing the embedding validity. If False, only an embedding is returned.
        self.return_overlap = return_overlap

        # skip_initialization (bool, optional, default=False):
        # Skip the initialization pass. Note that this only works if the chains passed in through initial_chains and
        # fixed_chains are semi-valid. A semi-valid embedding is a collection of chains such that every adjacent pair
        # of variables (u,v) has a coupler (p,q) in the hardware graph where p is in chain(u) and q is in chain(v).
        # This can be used on a valid embedding to immediately skip to the chain length improvement phase. Another good
        # source of semi-valid embeddings is the output of this function with the return_overlap parameter enabled.
        self.skip_initialization = skip_initialization

        # verbose (int, optional, default=0):
        # Level of output verbosity.
        # When set to 0:
        # Output is quiet until the final result.

        #   When set to 1:
        #   Output looks like this:

        #       initialized
        #       max qubit fill 3; num maxfull qubits=3
        #       embedding trial 1
        #       max qubit fill 2; num maxfull qubits=21
        #       embedding trial 2
        #       embedding trial 3
        #       embedding trial 4
        #       embedding trial 5
        #       embedding found.
        #       max chain length 4; num max chains=1
        #       reducing chain lengths
        #       max chain length 3; num max chains=5

        #   When set to 2:
        #   Output the information for lower levels and also report progress on minor statistics (when searching for an
        # embedding, this is when the number of maxfull qubits decreases; when improving, this is when the number of max
        # chains decreases).

        #   When set to 3:
        #   Report before each pass. Look here when tweaking tries, inner_rounds, and chainlength_patience.

        #   When set to 4:
        #   Report additional debugging information. By default, this package is built without this functionality. In the
        # C++ headers, this is controlled by the CPPDEBUG flag.
        self.verbose = verbose

        # interactive (bool, optional, default=False):
        # If logging is None or False, the verbose output will be printed to stdout/stderr as appropriate, and keyboard
        # interrupts will stop the embedding process and the current state will be returned to the user. Otherwise, output
        # will be directed to the logger logging.getLogger(minorminer.__name__) and keyboard interrupts will be propagated
        # back to the user. Errors will use logger.error(), verbosity levels 1 through 3 will use logger.info() and level 4
        # will use logger.debug().
        self.interactive = interactive

        # initial_chains (dict, optional):
        # Initial chains inserted into an embedding before fixed_chains are placed, which occurs before the initialization
        # pass. These can be used to restart the algorithm in a similar state to a previous embedding; for example, to
        # improve chain length of a valid embedding or to reduce overlap in a semi-valid embedding (see skip_initialization)
        # previously returned by the algorithm. Missing or empty entries are ignored. Each value in the dictionary is a list
        # of qubit labels.
        self.initial_chains = initial_chains

        # fixed_chains (dict, optional):
        # Fixed chains inserted into an embedding before the initialization pass. As the algorithm proceeds, these chains are
        # not allowed to change, and the qubits used by these chains are not used by other chains. Missing or empty entries
        # are ignored. Each value in the dictionary is a list of qubit labels.
        self.fixed_chains = fixed_chains

        # restrict_chains (dict, optional):
        # Throughout the algorithm, it is guaranteed that chain[i] is a subset of restrict_chains[i] for each i, except
        # those with missing or empty entries. Each value in the dictionary is a list of qubit labels.
        self.restrict_chains = restrict_chains

        # suspend_chains (dict, optional):
        # This is a metafeature that is only implemented in the Python interface. suspend_chains[i] is an iterable of
        # iterables; for example, suspend_chains[i] = [blob_1, blob_2], with each blob_j an iterable of target node labels.
        self.suspend_chains = suspend_chains


class DwaveSamplerParameterModel:
    def __init__(
        self,
        num_reads: Optional[int] = 1,
        chain_strength: Optional[int] = None,
        anneal_offsets: Optional[List[float]] = None,
        anneal_schedule: Optional[List[List[float]]] = None,
        annealing_time: Optional[float] = None,
        auto_scale: Optional[bool] = None,
        fast_anneal: Optional[bool] = None,
        flux_biases: Optional[List[float]] = None,
        flux_drift_compensation: Optional[bool] = None,
        h_gain_schedule: Optional[List[List[float]]] = None,
        initial_state: Optional[dict] = None,
        max_answers: Optional[int] = None,
        num_spin_reversal_transforms: Optional[int] = None,
        programming_thermalization: Optional[float] = None,
        readout_thermalization: Optional[float] = None,
        reduce_intersample_correlation: Optional[bool] = None,
        reinitialize_state: Optional[bool] = None,
        embedding_parameters: Optional[EmbeddingParameterModel] = None,
    ) -> None:
        # See https://docs.dwavesys.com/docs/latest/c_solver_parameters.html
        # for details

        # Number of samples to run
        self.num_reads = num_reads
        # Weight of the links between qubits representig on variable
        self.chain_strength = chain_strength
        # Provides offsets to annealing paths, per qubit
        self.anneal_offsets = anneal_offsets
        # Introduces variations to the global anneal schedule.
        self.anneal_schedule = anneal_schedule
        # Sets the duration, in microseconds with a resolution of 0.01 𝜇𝑠
        # of quantum annealing time, per read
        self.annealing_time = annealing_time
        # Indicates whether ℎ and 𝐽 values are rescaled:
        self.auto_scale = auto_scale
        # When set to True, the fast-anneal protocol is used instead of the standard anneal.
        # https://docs.dwavesys.com/docs/latest/c_qpu_annealing.html#qpu-annealprotocol-fast
        self.fast_anneal = fast_anneal
        # List of flux-bias offset values with which to calibrate a chain.
        self.flux_biases = flux_biases
        # Boolean flag indicating whether the D-Wave system compensates for flux drift.
        self.flux_drift_compensation = flux_drift_compensation
        # Sets a time-dependent gain for linear coefficients (qubit biases, see the h parameter) in the Hamiltonian.
        self.h_gain_schedule = h_gain_schedule
        # Initial state to which the system is set for reverse annealing.
        self.initial_state = initial_state
        # Limits the returned values to the first max_answers of num_reads samples.
        self.max_answers = max_answers
        # Specifies the number of spin-reversal transforms to perform.
        self.num_spin_reversal_transforms = num_spin_reversal_transforms
        # Sets the time, in microseconds with a resolution of 0.01 𝜇𝑠,
        # to wait after programming the QPU for it to cool back to base
        # temperature (i.e., post-programming thermalization time).
        self.programming_thermalization = programming_thermalization
        # Sets the time, in microseconds with a resolution of 0.01 𝜇𝑠,
        # to wait after each state is read from the QPU for it to cool
        # back to base temperature (i.e., post-readout thermalization time).
        self.readout_thermalization = readout_thermalization
        # Reduces sample-to-sample correlations caused by the spin-bath polarization
        # effect by adding a delay between reads.
        self.reduce_intersample_correlation = reduce_intersample_correlation
        # When using the reverse annealing feature, you must supply the initial state
        # to which the system is set; see the initial_state parameter
        self.reinitialize_state = reinitialize_state

        if embedding_parameters:
            temp_embedding_parameters = embedding_parameters.__dict__
            for k in list(temp_embedding_parameters.keys()):
                if temp_embedding_parameters[k] is None:
                    del temp_embedding_parameters[k]
            self.embedding_parameters: dict | None = temp_embedding_parameters
        else:
            self.embedding_parameters = None


class DwaveLeapParameterModel:
    def __init__(
        self,
        time_limit: Optional[float] = None,
    ) -> None:
        # See https://docs.dwavesys.com/docs/latest/c_solver_parameters.html
        # for details

        # Specifies the maximum run time, in seconds, the solver is allowed to work on the given problem.
        self.time_limit = time_limit


class DwaveSWHybridParameterModel:
    def __init__(
        self,
        decompose_size: Optional[int] = None,
        convergence: Optional[float] = None,
        sampler_parameters: Optional[DwaveSamplerParameterModel] = None,
    ) -> None:
        # Max size of decomposed sub problems. If None, the default value of 50 is used.
        self.decompose_size = decompose_size
        # Convergence threshhold for the hybrid workflow. If None the default value of 3 us used.
        self.convergence = convergence

        # Sampler parameters, for the D-Wave system, to be used in the hybrid workflow.
        # Each sub problem sent to an advantage sampler will use these parameters.
        if sampler_parameters:
            temp_sampler_parameters = sampler_parameters.__dict__
            for k in list(temp_sampler_parameters.keys()):
                if temp_sampler_parameters[k] is None:
                    del temp_sampler_parameters[k]
            self.sample_parameters: dict | None = temp_sampler_parameters
        else:
            self.sample_parameters = None


class JijParameterModel:
    def __init__(self, use_sos1: Optional[Literal["disabled", "auto", "forced"]] = None) -> None:
        self.use_sos1 = use_sos1


class AquilaParameterModel:
    def __init__(
        self,
        unit_disk_radius: float,
        shots: Optional[int] = 100,
    ) -> None:
        # Radius of interactions for specified graph
        self.unit_disk_radius = unit_disk_radius
        # Number of times experiemnt will be run and qubits will be measured
        self.shots = shots


class NEC2ParameterModel:
    def __init__(
        self,
        offset: Optional[float] = 0.0,
        num_reads: Optional[int] = None,
        num_results: Optional[int] = None,
        num_sweeps: Optional[int] = None,
        beta_range: Optional[List[float]] = None,
        beta_list: Optional[List[float]] = None,
        dense: Optional[bool] = None,
        vector_mode: Optional[str] = None,
        timeout: Optional[int] = None,
        Ve_num: Optional[int] = None,
        onehot: Optional[int] = None,
        fixed: Optional[list] | Optional[dict] = None,
        andzero: Optional[list] = None,
        orone: Optional[list] = None,
        supplement: Optional[list] = None,
        maxone: Optional[list] = None,
        minmaxone: Optional[list] = None,
        init_spin: Optional[list] | Optional[dict] = None,
        spin_list: Optional[list] = None,
    ) -> None:
        # Offset for the normalized weight information stored in the qubo
        self.offset = offset
        # VA sampling rate
        self.num_reads = num_reads
        # Number of VA annealing results
        self.num_results = num_results
        # Number of VA annealing sweeps
        self.num_sweeps = num_sweeps
        # VA beta value [start, end, steps] format
        self.beta_range = beta_range
        # Beta value array for each VA sweep
        self.beta_list = beta_list
        # VA matrix mode
        self.dense = dense
        # Mode during VA annealing
        self.vector_mode = vector_mode
        # Job execution timeout
        self.timeout = timeout
        # Number of VEs used in VA annealing
        self.Ve_num = Ve_num
        # VA onehot constraint parameter
        self.onehot = onehot
        # VA fixed constraint parameter
        self.fixed = fixed
        # VA andzero constraint parameter
        self.andzero = andzero
        # VA orone constraint parameter
        self.orone = orone
        # VA supplement constraint parameter
        self.supplement = supplement
        # VA maxone constraint parameter
        self.maxone = maxone
        # VA minmaxone constraint parameter
        self.minmaxone = minmaxone
        # VA initial spin parameter
        self.init_spin = init_spin
        # VA spin list parameter
        self.spin_list = spin_list


class NECParameterModel(NEC2ParameterModel):
    # for backward compatibility
    pass


class NEC3ParameterModel:
    def __init__(
        self,
        offset: Optional[float] = 0.0,
        num_reads: Optional[int] = None,
        num_results: Optional[int] = None,
        num_sweeps: Optional[int] = None,
        beta_range: Optional[List[float]] = None,
        beta_list: Optional[List[float]] = None,
        dense: Optional[bool] = None,
        num_threads: Optional[int] = None,
        vector_mode: Optional[str] = None,
        precision: Optional[int] = None,
        onehot: Optional[int] = None,
        fixed: Optional[list] | Optional[dict] = None,
        andzero: Optional[list] = None,
        orone: Optional[list] = None,
        supplement: Optional[list] = None,
        maxone: Optional[list] = None,
        minmaxone: Optional[list] = None,
        high_order: Optional[dict] = None,
        pattern: Optional[list] = None,
        weighted_sum: Optional[list] = None,
        init_spin: Optional[list] | Optional[dict] = None,
        timeout: Optional[int] = None,
    ) -> None:
        # Offset for the normalized weight information stored in the qubo
        self.offset = offset
        # VA sampling rate
        self.num_reads = num_reads
        # Number of VA annealing results
        self.num_results = num_results
        # Number of VA annealing sweeps
        self.num_sweeps = num_sweeps
        # VA beta value [start, end, steps] format
        self.beta_range = beta_range
        # Beta value array for each VA sweep
        self.beta_list = beta_list
        # VA matrix mode
        self.dense = dense
        # Number of threads in parallel used in VA annealing
        self.num_threads = num_threads
        # Mode during VA annealing
        self.vector_mode = vector_mode
        # Accuracy of floating point algebra in VA annealing
        self.precision = precision
        # VA onehot constraint parameter
        self.onehot = onehot
        # VA fixed constraint parameter
        self.fixed = fixed
        # VA andzero constraint parameter
        self.andzero = andzero
        # VA orone constraint parameter
        self.orone = orone
        # VA supplement constraint parameter
        self.supplement = supplement
        # VA maxone constraint parameter
        self.maxone = maxone
        # VA minmaxone constraint parameter
        self.minmaxone = minmaxone
        # VA high order constraint parameter
        self.high_order = high_order
        # VA pattern constraint parameter
        self.pattern = pattern
        # VA weighted sum constraint parameter
        self.weighted_sum = weighted_sum
        # VA initial spin parameter
        self.init_spin = init_spin
        # Job execution timeout
        self.timeout = timeout


class QuantagoniaParameterModel:
    def __init__(
        self,
        sense: Optional[str] = "MINIMIZE",
        timelimit: Optional[float] = 60,
        relative_gap: Optional[float] = 1e-4,
        absolute_gap: Optional[float] = 1e-9,
        # the following options only affect QUBOs, for MIPs they are ignored
        heuristics_only: Optional[bool] = False,
    ) -> None:
        # Type of cost function: MINIMIZE or MAXIMIZE
        self.sense = sense
        self.timelimit = timelimit
        self.relative_gap = relative_gap
        self.absolute_gap = absolute_gap
        # the following options only affect QUBOs, for MIPs they are ignored
        self.heuristics_only = heuristics_only


class GurobiParameterModel:
    # https://www.gurobi.com/documentation/10.0/refman/parameters.html#sec:Parameters

    def __init__(
        self,
        # Basic Parameters
        BarIterLimit: Optional[int] = None,  # Barrier iteration limit
        BestBdStop: Optional[float] = None,  # Best objective bound to stop
        BestObjStop: Optional[float] = None,  # Best objective value to stop
        Cutoff: Optional[float] = None,  # Objective cutoff
        IterationLimit: Optional[int] = None,  # Simplex iteration limit
        MemLimit: Optional[float] = None,  # Memory limit
        NodeLimit: Optional[int] = None,  # MIP node limit
        SoftMemLimit: Optional[float] = None,  # Soft memory limit
        SolutionLimit: Optional[int] = None,  # MIP feasible solution limit
        TimeLimit: Optional[float] = None,  # Time limit
        WorkLimit: Optional[int] = None,  # Work limit
        # Tolerances
        BarConvTol: Optional[float] = None,  # Barrier convergence tolerance
        BarQCPConvTol: Optional[float] = None,  # Barrier QCP convergence tolerance
        FeasibilityTol: Optional[float] = None,  # Primal feasibility tolerance
        IntFeasTol: Optional[float] = None,  # Integer feasibility tolerance
        MarkowitzTol: Optional[float] = None,  # Threshold pivoting tolerance
        MIPGap: Optional[float] = None,  # Relative MIP optimality gap
        MIPGapAbs: Optional[float] = None,  # Absolute MIP optimality gap
        OptimalityTol: Optional[float] = None,  # Dual feasibility tolerance
        PSDTol: Optional[float] = None,  # Positive semi-definite tolerance
        # Simplex Parameters
        InfUnbdInfo: Optional[bool] = None,  # Generate additional info for infeasible/unbounded models
        LPWarmStart: Optional[bool] = None,  # Warm start usage in simplex
        NetworkAlg: Optional[int] = None,  # Network simplex algorithm
        NormAdjust: Optional[int] = None,  # Simplex pricing norm
        PerturbValue: Optional[float] = None,  # Simplex perturbation magnitude
        Quad: Optional[bool] = None,  # Quad precision computation in simplex
        Sifting: Optional[bool] = None,  # Sifting within dual simplex
        SiftMethod: Optional[int] = None,  # LP method used to solve sifting sub-problems
        SimplexPricing: Optional[int] = None,  # Simplex variable pricing strategy
        # Barrier Parameters
        BarCorrectors: Optional[int] = None,  # Central correction limit
        BarHomogeneous: Optional[bool] = None,  # Barrier homogeneous algorithm
        BarOrder: Optional[int] = None,  # Barrier ordering algorithm
        Crossover: Optional[bool] = None,  # Barrier crossover strategy
        CrossoverBasis: Optional[int] = None,  # Crossover initial basis construction strategy
        QCPDual: Optional[bool] = None,  # Compute dual variables for QCP models
        # Scaling Parameters
        ObjScale: Optional[float] = None,  # Objective scaling
        ScaleFlag: Optional[bool] = None,  # Model scaling
        # MIP Parameters
        BranchDir: Optional[int] = None,  # Branch direction preference
        ConcurrentJobs: Optional[int] = None,  # Enables distributed concurrent solver
        ConcurrentMIP: Optional[bool] = None,  # Enables concurrent MIP solver
        ConcurrentSettings: Optional[str] = None,  # Create concurrent environments from a list of .prm files
        DegenMoves: Optional[int] = None,  # Degenerate simplex moves
        Disconnected: Optional[int] = None,  # Disconnected component strategy
        DistributedMIPJobs: Optional[int] = None,  # Enables the distributed MIP solver
        Heuristics: Optional[float] = None,  # Turn MIP heuristics up or down
        ImproveStartGap: Optional[float] = None,  # Trigger solution improvement
        ImproveStartNodes: Optional[int] = None,  # Trigger solution improvement
        ImproveStartTime: Optional[float] = None,  # Trigger solution improvement
        LazyConstraints: Optional[bool] = None,  # Programs that add lazy constraints must set this parameter
        MinRelNodes: Optional[int] = None,  # Minimum relaxation heuristic control
        MIPFocus: Optional[int] = None,  # Set the focus of the MIP solver
        MIQCPMethod: Optional[int] = None,  # Method used to solve MIQCP models
        NLPHeur: Optional[bool] = None,  # Controls the NLP heuristic for non-convex quadratic models
        NodefileDir: Optional[str] = None,  # Directory for MIP node files
        NodefileStart: Optional[float] = None,  # Memory threshold for writing MIP tree nodes to disk
        NodeMethod: Optional[int] = None,  # Method used to solve MIP node relaxations
        NonConvex: Optional[int] = None,  # Control how to deal with non-convex quadratic programs
        NoRelHeurTime: Optional[float] = None,  # Limits the amount of time (in seconds) spent in the NoRel heuristic
        NoRelHeurWork: Optional[float] = None,  # Limits the amount of work performed by the NoRel heuristic
        OBBT: Optional[bool] = None,  # Controls aggressiveness of Optimality-Based Bound Tightening
        PartitionPlace: Optional[int] = None,  # Controls when the partition heuristic runs
        PumpPasses: Optional[int] = None,  # Feasibility pump heuristic control
        RINS: Optional[bool] = None,  # RINS heuristic
        SolFiles: Optional[str] = None,  # Location to store intermediate solution files
        SolutionNumber: Optional[int] = None,  # Sub-optimal MIP solution retrieval
        StartNodeLimit: Optional[int] = None,  # Node limit for MIP start sub-MIP
        StartNumber: Optional[int] = None,  # Set index of MIP start
        SubMIPNodes: Optional[int] = None,  # Nodes explored by sub-MIP heuristics
        Symmetry: Optional[int] = None,  # Symmetry detection
        VarBranch: Optional[int] = None,  # Branch variable selection strategy
        ZeroObjNodes: Optional[int] = None,  # Zero objective heuristic control
        # Presolve Parameters
        AggFill: Optional[int] = None,  # Allowed fill during presolve aggregation
        Aggregate: Optional[bool] = None,  # Presolve aggregation control
        DualReductions: Optional[bool] = None,  # Disables dual reductions in presolve
        PreCrush: Optional[
            bool
        ] = None,  # Allows presolve to translate constraints on the original model to equivalent constraints on the presolved model
        PreDepRow: Optional[bool] = None,  # Presolve dependent row reduction
        PreDual: Optional[bool] = None,  # Presolve dualization
        PreMIQCPForm: Optional[int] = None,  # Format of presolved MIQCP model
        PrePasses: Optional[int] = None,  # Presolve pass limit
        PreQLinearize: Optional[bool] = None,  # Presolve Q matrix linearization
        Presolve: Optional[int] = None,  # Presolve level
        PreSOS1BigM: Optional[float] = None,  # Controls largest coefficient in SOS1 reformulation
        PreSOS1Encoding: Optional[int] = None,  # Controls SOS1 reformulation
        PreSOS2BigM: Optional[float] = None,  # Controls largest coefficient in SOS2 reformulation
        PreSOS2Encoding: Optional[int] = None,  # Controls SOS2 reformulation
        PreSparsify: Optional[bool] = None,  # Presolve sparsify reduction
        # Tuning Parameters
        TuneBaseSettings: Optional[str] = None,  # Comma-separated list of base parameter settings
        TuneCleanup: Optional[bool] = None,  # Enables a tuning cleanup phase
        TuneCriterion: Optional[int] = None,  # Specify tuning criterion
        TuneJobs: Optional[int] = None,  # Enables distributed tuning
        TuneMetric: Optional[int] = None,  # Metric to aggregate results into a single measure
        TuneOutput: Optional[int] = None,  # Tuning output level
        TuneResults: Optional[int] = None,  # Number of improved parameter sets returned
        TuneTargetMIPGap: Optional[float] = None,  # A target gap to be reached
        TuneTargetTime: Optional[float] = None,  # A target runtime in seconds to be reached
        TuneTimeLimit: Optional[float] = None,  # Time limit for tuning
        TuneTrials: Optional[
            int
        ] = None,  # Perform multiple runs on each parameter set to limit the effect of random noise
        # Multiple Solutions Parameters
        PoolGap: Optional[float] = None,  # Relative gap for solutions in pool
        PoolGapAbs: Optional[float] = None,  # Absolute gap for solutions in pool
        PoolSearchMode: Optional[int] = None,  # Choose the approach used to find additional solutions
        PoolSolutions: Optional[int] = None,  # Number of solutions to keep in pool
        # MIP Cuts Parameters
        BQPCuts: Optional[int] = None,  # BQP cut generation
        Cuts: Optional[int] = None,  # Global cut generation control
        CliqueCuts: Optional[int] = None,  # Clique cut generation
        CoverCuts: Optional[int] = None,  # Cover cut generation
        CutAggPasses: Optional[int] = None,  # Constraint aggregation passes performed during cut generation
        CutPasses: Optional[int] = None,  # Root cutting plane pass limit
        FlowCoverCuts: Optional[int] = None,  # Flow cover cut generation
        FlowPathCuts: Optional[int] = None,  # Flow path cut generation
        GomoryPasses: Optional[int] = None,  # Root Gomory cut pass limit
        GUBCoverCuts: Optional[int] = None,  # GUB cover cut generation
        ImpliedCuts: Optional[int] = None,  # Implied bound cut generation
        InfProofCuts: Optional[int] = None,  # Infeasibility proof cut generation
        LiftProjectCuts: Optional[int] = None,  # Lift-and-project cut generation
        MIPSepCuts: Optional[int] = None,  # MIP separation cut generation
        MIRCuts: Optional[int] = None,  # MIR cut generation
        ModKCuts: Optional[int] = None,  # Mod-k cut generation
        NetworkCuts: Optional[int] = None,  # Network cut generation
        ProjImpliedCuts: Optional[int] = None,  # Projected implied bound cut generation
        PSDCuts: Optional[int] = None,  # PSD cut generation
        RelaxLiftCuts: Optional[int] = None,  # Relax-and-lift cut generation
        RLTCuts: Optional[int] = None,  # RLT cut generation
        StrongCGCuts: Optional[int] = None,  # Strong-CG cut generation
        SubMIPCuts: Optional[int] = None,  # Sub-MIP cut generation
        ZeroHalfCuts: Optional[int] = None,  # Zero-half cut generation
        # Distributed Algorithms Parameters
        WorkerPassword: Optional[str] = None,  # Password for distributed worker cluster
        WorkerPool: Optional[str] = None,  # Distributed worker cluster
        # # Cloud Parameters
        # CloudAccessID: Optional[str] = None,  # Access ID for Gurobi Instant Cloud
        # CloudHost: Optional[str] = None,  # Host for the Gurobi Cloud entry point
        # CloudSecretKey: Optional[str] = None,  # Secret Key for Gurobi Instant Cloud
        # CloudPool: Optional[str] = None,  # Cloud pool to use for Gurobi Instant Cloud instance
        # Compute Server Parameters
        ComputeServer: Optional[str] = None,  # Name of a node in the Remote Services cluster.
        ServerPassword: Optional[str] = None,  # Client password for Remote Services cluster (or token server).
        ServerTimeout: Optional[float] = None,  # Network timeout interval
        CSPriority: Optional[int] = None,  # Job priority for Remote Services job
        CSQueueTimeout: Optional[float] = None,  # Queue timeout for new jobs
        CSRouter: Optional[str] = None,  # Router node for Remote Services cluster
        CSGroup: Optional[str] = None,  # Group placement request for cluster
        CSTLSInsecure: Optional[bool] = None,  # Use insecure mode in Transport Layer Security (TLS)
        CSIdleTimeout: Optional[float] = None,  # Idle time before Compute Server kills a job
        JobID: Optional[str] = None,  # Job ID of current job
        # Cluster Manager Parameters
        CSAPIAccessID: Optional[str] = None,  # Access ID for Gurobi Cluster Manager
        CSAPISecret: Optional[str] = None,  # Secret key for Gurobi Cluster Manager
        CSAppName: Optional[str] = None,  # Application name of the batches or jobs
        CSAuthToken: Optional[str] = None,  # Token used internally for authentication
        CSBatchMode: Optional[bool] = None,  # Controls Batch-Mode optimization
        CSClientLog: Optional[bool] = None,  # Turns logging on or off
        CSManager: Optional[str] = None,  # URL for the Cluster Manager
        UserName: Optional[str] = None,  # User name to use when connecting to the Cluster Manager
        # Token Server Parameters
        TokenServer: Optional[str] = None,  # Name of your token server.
        TSPort: Optional[int] = None,  # Token server port number.
        # Web License Service Parameters
        LicenseID: Optional[str] = None,  # License ID.
        WLSAccessID: Optional[str] = None,  # WLS access ID.
        WLSSecret: Optional[str] = None,  # WLS secret.
        WLSToken: Optional[str] = None,  # WLS token.
        WLSTokenDuration: Optional[float] = None,  # WLS token duration.
        WLSTokenRefresh: Optional[float] = None,  # Relative WLS token refresh interval.
        # Other Parameters
        DisplayInterval: Optional[int] = None,  # Frequency at which log lines are printed
        FeasRelaxBigM: Optional[float] = None,  # Big-M value for feasibility relaxations
        FuncPieceError: Optional[float] = None,  # Error allowed for PWL translation of function constraint
        FuncPieceLength: Optional[float] = None,  # Piece length for PWL translation of function constraint
        FuncPieceRatio: Optional[
            float
        ] = None,  # Controls whether to under- or over-estimate function values in PWL approximation
        FuncPieces: Optional[int] = None,  # Sets strategy for PWL function approximation
        FuncMaxVal: Optional[float] = None,  # Maximum value for x and y variables in function constraints
        IgnoreNames: Optional[bool] = None,  # Indicates whether to ignore names provided by users
        IISMethod: Optional[int] = None,  # IIS method
        InputFile: Optional[str] = None,  # File to be read before optimization commences
        IntegralityFocus: Optional[int] = None,  # Set the integrality focus
        JSONSolDetail: Optional[int] = None,  # Controls the level of detail stored in generated JSON solution
        LogFile: Optional[str] = None,  # Log file name
        LogToConsole: Optional[bool] = None,  # Console logging
        Method: Optional[int] = None,  # Algorithm used to solve continuous models
        MultiObjMethod: Optional[int] = None,  # Warm-start method to solve for subsequent objectives
        MultiObjPre: Optional[bool] = None,  # Initial presolve on multi-objective models
        MultiObjSettings: Optional[str] = None,  # Create multi-objective settings from a list of .prm files
        NumericFocus: Optional[int] = None,  # Set the numerical focus
        ObjNumber: Optional[int] = None,  # Set index of multi-objectives
        OutputFlag: Optional[bool] = None,  # Solver output control
        Record: Optional[bool] = None,  # Enable API call recording
        ResultFile: Optional[str] = None,  # Result file written upon completion of optimization
        ScenarioNumber: Optional[int] = None,  # Set index of scenario in multi-scenario models
        Seed: Optional[int] = None,  # Modify the random number seed
        SolutionTarget: Optional[int] = None,  # Specify the solution target for LP
        Threads: Optional[int] = None,  # Number of parallel threads to use
        UpdateMode: Optional[int] = None,  # Change the behavior of lazy updates
        max_seconds: Optional[
            int
        ] = None,  # Maximum time in seconds to run the optimization. Included for backward compatability  # noqa: E501
        # Attributes
        ModelSense: Optional[int] = None,  # Default 1, 1 for minimization, -1 for maximization
    ) -> None:
        self.max_seconds = (
            max_seconds  #  Included for backward compatability. if TimeLimit is specified, that value is used
        )
        # Initialize each parameter with the provided value or default
        self.BarIterLimit = BarIterLimit
        self.BestBdStop = BestBdStop
        self.BestObjStop = BestObjStop
        self.Cutoff = Cutoff
        self.IterationLimit = IterationLimit
        self.MemLimit = MemLimit
        self.NodeLimit = NodeLimit
        self.SoftMemLimit = SoftMemLimit
        self.SolutionLimit = SolutionLimit
        self.TimeLimit = TimeLimit
        self.WorkLimit = WorkLimit
        # Initialize Tolerances
        self.BarConvTol = BarConvTol
        self.BarQCPConvTol = BarQCPConvTol
        self.FeasibilityTol = FeasibilityTol
        self.IntFeasTol = IntFeasTol
        self.MarkowitzTol = MarkowitzTol
        self.MIPGap = MIPGap
        self.MIPGapAbs = MIPGapAbs
        self.OptimalityTol = OptimalityTol
        self.PSDTol = PSDTol
        # Initialize Simplex Parameters
        self.InfUnbdInfo = InfUnbdInfo
        self.LPWarmStart = LPWarmStart
        self.NetworkAlg = NetworkAlg
        self.NormAdjust = NormAdjust
        self.PerturbValue = PerturbValue
        self.Quad = Quad
        self.Sifting = Sifting
        self.SiftMethod = SiftMethod
        self.SimplexPricing = SimplexPricing
        # Initialize Barrier Parameters
        self.BarCorrectors = BarCorrectors
        self.BarHomogeneous = BarHomogeneous
        self.BarOrder = BarOrder
        self.Crossover = Crossover
        self.CrossoverBasis = CrossoverBasis
        self.QCPDual = QCPDual
        # Initialize Scaling Parameters
        self.ObjScale = ObjScale
        self.ScaleFlag = ScaleFlag
        # Initialize MIP Parameters
        self.BranchDir = BranchDir
        self.ConcurrentJobs = ConcurrentJobs
        self.ConcurrentMIP = ConcurrentMIP
        self.ConcurrentSettings = ConcurrentSettings
        self.DegenMoves = DegenMoves
        self.Disconnected = Disconnected
        self.DistributedMIPJobs = DistributedMIPJobs
        self.Heuristics = Heuristics
        self.ImproveStartGap = ImproveStartGap
        self.ImproveStartNodes = ImproveStartNodes
        self.ImproveStartTime = ImproveStartTime
        self.LazyConstraints = LazyConstraints
        self.MinRelNodes = MinRelNodes
        self.MIPFocus = MIPFocus
        self.MIQCPMethod = MIQCPMethod
        self.NLPHeur = NLPHeur
        self.NodefileDir = NodefileDir
        self.NodefileStart = NodefileStart
        self.NodeMethod = NodeMethod
        self.NonConvex = NonConvex
        self.NoRelHeurTime = NoRelHeurTime
        self.NoRelHeurWork = NoRelHeurWork
        self.OBBT = OBBT
        self.PartitionPlace = PartitionPlace
        self.PumpPasses = PumpPasses
        self.RINS = RINS
        self.SolFiles = SolFiles
        self.SolutionNumber = SolutionNumber
        self.StartNodeLimit = StartNodeLimit
        self.StartNumber = StartNumber
        self.SubMIPNodes = SubMIPNodes
        self.Symmetry = Symmetry
        self.VarBranch = VarBranch
        self.ZeroObjNodes = ZeroObjNodes
        # Initialize Presolve Parameters
        self.AggFill = AggFill
        self.Aggregate = Aggregate
        self.DualReductions = DualReductions
        self.PreCrush = PreCrush
        self.PreDepRow = PreDepRow
        self.PreDual = PreDual
        self.PreMIQCPForm = PreMIQCPForm
        self.PrePasses = PrePasses
        self.PreQLinearize = PreQLinearize
        self.Presolve = Presolve
        self.PreSOS1BigM = PreSOS1BigM
        self.PreSOS1Encoding = PreSOS1Encoding
        self.PreSOS2BigM = PreSOS2BigM
        self.PreSOS2Encoding = PreSOS2Encoding
        self.PreSparsify = PreSparsify
        # Initialize Tuning Parameters
        self.TuneBaseSettings = TuneBaseSettings
        self.TuneCleanup = TuneCleanup
        self.TuneCriterion = TuneCriterion
        self.TuneJobs = TuneJobs
        self.TuneMetric = TuneMetric
        self.TuneOutput = TuneOutput
        self.TuneResults = TuneResults
        self.TuneTargetMIPGap = TuneTargetMIPGap
        self.TuneTargetTime = TuneTargetTime
        self.TuneTimeLimit = TuneTimeLimit
        self.TuneTrials = TuneTrials
        # Initialize Multiple Solutions Parameters
        self.PoolGap = PoolGap
        self.PoolGapAbs = PoolGapAbs
        self.PoolSearchMode = PoolSearchMode
        self.PoolSolutions = PoolSolutions
        # Initialize MIP Cuts Parameters
        self.BQPCuts = BQPCuts
        self.Cuts = Cuts
        self.CliqueCuts = CliqueCuts
        self.CoverCuts = CoverCuts
        self.CutAggPasses = CutAggPasses
        self.CutPasses = CutPasses
        self.FlowCoverCuts = FlowCoverCuts
        self.FlowPathCuts = FlowPathCuts
        self.GomoryPasses = GomoryPasses
        self.GUBCoverCuts = GUBCoverCuts
        self.ImpliedCuts = ImpliedCuts
        self.InfProofCuts = InfProofCuts
        self.LiftProjectCuts = LiftProjectCuts
        self.MIPSepCuts = MIPSepCuts
        self.MIRCuts = MIRCuts
        self.ModKCuts = ModKCuts
        self.NetworkCuts = NetworkCuts
        self.ProjImpliedCuts = ProjImpliedCuts
        self.PSDCuts = PSDCuts
        self.RelaxLiftCuts = RelaxLiftCuts
        self.RLTCuts = RLTCuts
        self.StrongCGCuts = StrongCGCuts
        self.SubMIPCuts = SubMIPCuts
        self.ZeroHalfCuts = ZeroHalfCuts
        # Initialize Distributed Algorithms Parameters
        self.WorkerPassword = WorkerPassword
        self.WorkerPool = WorkerPool
        # # Initialize Cloud Parameters
        # self.CloudAccessID = CloudAccessID
        # self.CloudHost = CloudHost
        # self.CloudSecretKey = CloudSecretKey
        # self.CloudPool = CloudPool
        # Initialize Compute Server Parameters
        self.ComputeServer = ComputeServer
        self.ServerPassword = ServerPassword
        self.ServerTimeout = ServerTimeout
        self.CSPriority = CSPriority
        self.CSQueueTimeout = CSQueueTimeout
        self.CSRouter = CSRouter
        self.CSGroup = CSGroup
        self.CSTLSInsecure = CSTLSInsecure
        self.CSIdleTimeout = CSIdleTimeout
        self.JobID = JobID
        # Initialize Cluster Manager Parameters
        self.CSAPIAccessID = CSAPIAccessID
        self.CSAPISecret = CSAPISecret
        self.CSAppName = CSAppName
        self.CSAuthToken = CSAuthToken
        self.CSBatchMode = CSBatchMode
        self.CSClientLog = CSClientLog
        self.CSManager = CSManager
        self.UserName = UserName
        # Initialize Token Server Parameters
        self.TokenServer = TokenServer
        self.TSPort = TSPort
        # Initialize Web License Service Parameters
        self.LicenseID = LicenseID
        self.WLSAccessID = WLSAccessID
        self.WLSSecret = WLSSecret
        self.WLSToken = WLSToken
        self.WLSTokenDuration = WLSTokenDuration
        self.WLSTokenRefresh = WLSTokenRefresh
        # Initialize Other Parameters
        self.DisplayInterval = DisplayInterval
        self.FeasRelaxBigM = FeasRelaxBigM
        self.FuncPieceError = FuncPieceError
        self.FuncPieceLength = FuncPieceLength
        self.FuncPieceRatio = FuncPieceRatio
        self.FuncPieces = FuncPieces
        self.FuncMaxVal = FuncMaxVal
        self.IgnoreNames = IgnoreNames
        self.IISMethod = IISMethod
        self.InputFile = InputFile
        self.IntegralityFocus = IntegralityFocus
        self.JSONSolDetail = JSONSolDetail
        self.LogFile = LogFile
        self.LogToConsole = LogToConsole
        self.Method = Method
        self.MultiObjMethod = MultiObjMethod
        self.MultiObjPre = MultiObjPre
        self.MultiObjSettings = MultiObjSettings
        self.NumericFocus = NumericFocus
        self.ObjNumber = ObjNumber
        self.OutputFlag = OutputFlag
        self.Record = Record
        self.ResultFile = ResultFile
        self.ScenarioNumber = ScenarioNumber
        self.Seed = Seed
        self.SolutionTarget = SolutionTarget
        self.Threads = Threads
        self.UpdateMode = UpdateMode
        # Attributes
        self.ModelSense = ModelSense


class ToshibaParameterModel:
    def __init__(
        self,
        steps: Optional[int] = None,
        loops: Optional[int] = None,
        timeout: Optional[int] = None,
        target: Optional[float] = None,
        maxout: Optional[int] = None,
        maxwait: Optional[int] = None,
        algo: Optional[int] = None,
        dt: Optional[float] = None,
        C: Optional[float] = None,
        blocks: Optional[int] = None,
        multishot: Optional[int] = None,
        PD3Orate: Optional[int] = None,
        phi: Optional[float] = None,
    ) -> None:
        # Parameters common to all solvers

        # Specifies the number of steps in a computation request.
        self.steps = steps
        # Specifies the number of loops in SQBM+ computation.
        self.loops = loops
        # Specifies the maximum computation time (timeout) in seconds.
        self.timeout = timeout
        # Specifies the end condition of a computation request.
        self.target = target
        # Specifies the upper limit of the number of solutions to be outputted.
        self.maxout = maxout
        # Specifies the upper limit of the number of solutions to be outputted.
        self.maxwait = maxwait

        # QUBO Solver-specific parameters

        # Specifies the algorithm to be used.
        # 0: If 0 (zero) is specified, SQBM+ searches for a solution using various algorithms.
        # Available Algorithms:
        # 15: bSB, the SQBM+ computation algorithm proposed in a paper by Goto et al. (2021).
        # 151: In addition to the processing of algo=15, C is automatically adjusted for each SB algorithm updates step. This may improve accuracy over specifying a fixed C.
        # 154: In addition to processing of algo=15, the impact size of the QUBO coefficient matrix on the SB algorithm is autoscaled. Precision may
        #       improve when the distribution of eigenvalues of the QUBO coefficient matrix is not even. 155 Both 151 and 154 are performed.
        # 20: dSB, the SQBM+ computation algorithm proposed in a paper by Goto et al. (2021).
        # 201: In addition to the processing of algo=20, C is automatically adjusted for each SB algorithm updates step. This may improve accuracy over specifying a fixed C.
        # 204: In addition to the processing of algo=20, the impact size of the QUBO coefficient matrix on the SB algorithm is autoscaled. Precision may improve when the distribution of eigenvalues of the QUBO coefficient matrix is not even.
        # 205: Both 201 and 204 are performed.
        # 25: Extension of 15. This algorithm more likely escape from local minimum. 251 Extension of 151. This algorithm more likely escape from local minimum.
        # 254: Extension of 154. This algorithm more likely escape from local minimum.
        # 255: Extension of 155. This algorithm more likely escape from local minimum.
        # 30: Extension of 20. This algorithm more likely escape from local minimum. 301 Extension of 201. This algorithm more likely escape from local minimum.
        # 304: Extension of 204. This algorithm more likely escape from local minimum.
        # 305: Extension of 205. This algorithm more likely escape from local minimum.
        self.algo = algo
        # Specifies the time per step.
        self.dt = dt
        # Corresponds to the constant ξ0, appearing in the paper by Goto,
        # Tatsumura, & Dixon (2019, p. 2), which is the theoretical basis of SQBM+.
        self.C = C
        # Specify the number of blocks of GPUs used to find a solution. If 0 (zero) is specified, the value of 'blocks' will be auto- adjusted. Specify an integer between 0 and 40.
        self.blocks = blocks
        # When you specify multishot, SQBM+ will get multiple solutions, which start from different initail decision variable values but other parameters are the same. The number of solution is multishot number. Default value is 0, which automatically decide multishot from problem size. If multishot > 1, SQBM+ will have less overhead.
        # Specify an integer between 0 and 10.
        self.multishot = multishot

        # QPLIB Solver-specific parameters

        # Parameter that determines the number of PD3O algorithm execution steps. SQBM+ searches for solutions using the SB algorithm, but if PD3Orate is set to anything other than 0, it also searches for solutions using another algorithm (called the PD3O algorithm). For the steps of the SB algorithm, the PD3O algorithm performs PD3Orate*steps times to update decision variables.
        self.PD3Orate = PD3Orate

        # Parameters that determine the behavior of the PD3O algorithm. Specify a real number between 0 and 1.
        # If it is close to 0, it behaves like the SB algorithm. If it is close to 1, it narrows the search range of solutions, but it may find a better solution than the SB algorithm.
        self.phi = phi


class HitachiParameterModel:
    """
    Default parameters:
        type: Optional[int] = None,
        num_executions: Optional[int] = 1,
        temperature_num_steps: Optional[int] = 10,
        temperature_step_length: Optional[int] = 100,
        temperature_initial: Optional[float] = 10.0,
        temperature_target: Optional[float] = 0.01,
        energies: Optional[bool] = True,
        spins: Optional[bool] = True,
        execution_time: Optional[bool] = False,
        num_outputs: Optional[int] = 0,
        averaged_spins: Optional[bool] = False,
        averaged_energy: Optional[bool] = False,
    """

    def __init__(
        self,
        solver_type: Optional[int] = None,
        num_executions: Optional[int] = None,
        temperature_num_steps: Optional[int] = None,
        temperature_step_length: Optional[int] = None,
        temperature_initial: Optional[float] = None,
        temperature_target: Optional[float] = None,
        energies: Optional[bool] = None,
        spins: Optional[bool] = None,
        execution_time: Optional[bool] = True,
        num_outputs: Optional[int] = None,
        averaged_spins: Optional[bool] = None,
        averaged_energy: Optional[bool] = None,
        embedding_parameters: Optional[EmbeddingParameterModel] = None,
    ) -> None:
        self.solver_type = solver_type
        self.num_executions = num_executions
        self.temperature_num_steps = temperature_num_steps
        self.temperature_step_length = temperature_step_length
        self.temperature_initial = temperature_initial
        self.temperature_target = temperature_target
        self.energies = energies
        self.spins = spins
        self.execution_time = execution_time
        self.num_outputs = num_outputs
        self.averaged_spins = averaged_spins
        self.averaged_energy = averaged_energy

        if embedding_parameters:
            temp_embedding_parameters = embedding_parameters.__dict__
            for k in list(temp_embedding_parameters.keys()):
                if temp_embedding_parameters[k] is None:
                    del temp_embedding_parameters[k]
            self.embedding_parameters: dict | None = temp_embedding_parameters
        else:
            self.embedding_parameters = None

    def get_hitachi_api_parameters(self) -> dict:
        return {
            k: v
            for k, v in {
                "temperature_num_steps": self.temperature_num_steps,
                "temperature_step_length": self.temperature_step_length,
                "temperature_initial": self.temperature_initial,
                "temperature_target": self.temperature_target,
            }.items()
            if v is not None
        }

    def get_hitachi_api_output(self) -> dict:
        return {
            k: v
            for k, v in {
                "energies": self.energies,
                "spins": self.spins,
                "execution_time": self.execution_time,
                "num_outputs": self.num_outputs,
                "averaged_spins": self.averaged_spins,
                "averaged_energy": self.averaged_energy,
            }.items()
            if v is not None
        }


class FujitsuParameterModel:
    def __init__(
        self,
        time_limit_sec: Optional[int] = None,
        target_energy: Optional[float] = None,
        num_run: Optional[int] = None,
        num_group: Optional[int] = None,
        num_output_solution: Optional[int] = None,
        gs_level: Optional[int] = None,
        gs_cutoff: Optional[int] = None,
        one_hot_level: Optional[int] = None,
        one_hot_cutoff: Optional[int] = None,
        internal_penalty: Optional[int] = None,
        penalty_auto_mode: Optional[int] = None,
        penalty_coef: Optional[int] = None,
        penalty_inc_rate: Optional[int] = None,
        max_penalty_coef: Optional[int] = None,
        guidance_config: Optional[dict] = None,
        fixed_config: Optional[dict] = None,
        one_way_one_hot_groups: Optional[dict] = None,
        two_way_one_hot_groups: Optional[dict] = None,
    ) -> None:
        #  For details: https://portal.aispf.global.fujitsu.com/apidoc/da/jp/api-ref/da-qubo-v3c-en.html#/v3c

        # Maximum running time of DA in seconds (int64 type)
        # Specifies the upper limit of running time. The unit is seconds.
        # The calculation is terminated when the running time reaches the upper limit time specified by time_limit_sec.
        # Specifies an integer from 1 to 3600. (Default: 10)
        self.time_limit_sec = time_limit_sec

        # Threshold energy for fast exit (double type)
        # Specifies the target energy value. If not specified, the calculation will be performed without setting the target energy value.
        # When the minimum energy value reaches the target energy value, the calculation is terminated even if the running time does not reach the upper limit time.
        # Specifies a value from -2126 to 2126. (Default: disabled)
        self.target_energy = target_energy

        # The number of parallel attempts of each groups (int64 type)
        # num_run x num_group specifies the number of parallel attempts.
        # Specifies an integer from 1 to 1024. (Default: 16)
        self.num_run = num_run

        # The number of groups of parallel attempts (int64 type)
        # num_run x num_group specifies the number of parallel attempts.
        # Specifies an integer from 1 to 16. (Default: 1)
        self.num_group = num_group

        # The number of output solutions of each groups (int64 type)
        # num_output_solution x num_group specifies the number of output solutions.
        # Specifies an integer from 1 to 1024. (Default: 5)
        self.num_output_solution = num_output_solution

        # Level of the global search (int64 type)
        # In the global search, the search starting point with local solution group escape is determined, and the constrained search combining various search methods is repeatedly executed as a processing unit. The higher the value, the longer the constraint exploitation search.
        # Specifies the level of the global search. Lower level is weak on Global Search.
        # If you specify one-way one-hot constraints (one_way_one_hot_groups) or two-way one-hot constraints (two_way_one_hot_groups), it is recommended to specify 0 for gs_level.
        # Specifies an integer from 0 to 100. (Default: 5)
        self.gs_level = gs_level

        # Global search cutoff level (int64 type)
        # Specifies the convergence judgment level for global search constraint usage search. The higher the value, the longer the period during which the constraint-based search energy on which convergence is based is not updated. Convergence assessment is turned off at 0.
        # Specifies an integer from 0 to 1000000. (Default: 8000)
        self.gs_cutoff = gs_cutoff

        # Level of the 1hot constraint search (int64 type)
        # Specifies the level of 1hot constraint search, which is one of the constraint exploitation searches. The higher the value, the longer the 1hot constraint search.
        # Specifies an integer from 0 to 100. (Default: 3)
        self.one_hot_level = one_hot_level

        # Level of the convergence for 1hot constraint search (int64 type)
        # Specifies the convergence level for 1hot constraint search, one of the constraint exploitation searches. The higher the value, the longer the non-renewal period of the energy used as a reference for the convergence determination in the 1hot constraint search. Convergence assessment is turned off at 0.
        # Specifies an integer from 0 to 1000000. (Default: 100)
        self.one_hot_cutoff = one_hot_cutoff

        # Mode of 1hot constraint internal generation (int64 type)
        # Specifies the 1hot constraint internal generation mode. 0 turns off 1hot constrained internal generation mode.
        # Specifies an integer 0 or 1. (Default: 0)
        # If 1way 1hot constraint (one_way_one_hot_groups) or a 2way 1hot constraint (two_way_one_hot_groups) is specified, it is recommended that 1 be specified for internal_penalty.
        # If internal_penalty is not specified, or if internal_penalty is specified as 0, then the BinaryPolynomial or PenaltyBinaryPolynomial for the combinatorial optimization problem must be a quadratic polynomial indicating a condition for the 1way 1hot constraint (one_way_one_hot_groups) or the 2way 1hot constraint (two_way_one_hot_groups).
        # If internal_penalty is 1, the BinaryPolynomial or PenaltyBinaryPolynomial for the combinatorial optimization problem need not be a quadratic polynomial indicating the condition of the 1way 1hot constraint (one_way_one_hot_groups) or the 2way 1hot constraint (two_way_one_hot_groups).
        # If 1way 1hot constraint (one_way_one_hot_groups) is specified, the variable with the lowest variable number must be specified as a quadratic polynomial even if the coefficient is 0.
        # If 2way 1hot constraint (two_way_one_hot_groups) is specified, all diagonal terms must be specified as quadratic polynomials even if the coefficient is 0.
        # 　Specification example: When the number of variables is 4.
        # 　　　　　"binary_polynomial":
        # 　　　　　　{ "terms":[
        # 　　　　　　　{ "p": [0, 0], "c": 0 },
        # 　　　　　　　{ "p": [1, 1], "c": 0 },
        # 　　　　　　　{ "p": [2, 2], "c": 0 },
        # 　　　　　　　{ "p": [3, 3], "c": 0 }] }
        self.internal_penalty = internal_penalty

        # Coefficient adjustment mode (int64 type)
        # Specifies the coefficient adjustment mode for constraint terms.
        # 0: behavior with fixed value specified by penalty_coef
        # 1-10000: internally autofit with penalty_coef as initial value
        # Specifies an integer from 0 to 10000. (Default: 1)
        self.penalty_auto_mode = penalty_auto_mode

        # Coefficient of the constraint term (int64 type)
        # Specifies the coefficient of the constraint term.
        # Specifies an integer from 1 to 9223372036854775807. (Default: 1)
        self.penalty_coef = penalty_coef

        # Parameters for automatic adjustment of constraint terms (int64 type)
        # Specifies the parameter for automatic adjustment of the constraint term in the global search.
        # Specifies an integer from 100 to 200. (Default: 150)
        self.penalty_inc_rate = penalty_inc_rate

        # Maximum constraint term coefficent (int64 type)
        # Specifies the maximum constraint term coefficent. Set to 0 for no maximum value.
        # Specifies an integer from 0 to 9223372036854775807. (Default: 0)
        self.max_penalty_coef = max_penalty_coef

        # {
        # description:
        # Initial value of each variable ("uint32 type":boolean type)

        # Specifies an initial value for each polynomial (problem) variable that is set to find an optimal solution.
        # By specifying a value that is close to the optimal solution, improvement in the accuracy of the optimal solution can be expected.

        # Specifies an initial value for each of the variables with the following format:
        # 　Format: {"VariableNumber":InitialValue, "VariableNumber":InitialValue, ...}
        # 　Specification example: When you specify an initial value for each variable of 2x1x2 - 4x2x4
        # 　　　　　{"1":false,"2":false,"4":false}

        # If you do not specify initial values, the solver sets values randomly.

        # integer($uint32)	boolean
        # }
        self.guidance_config = guidance_config

        # {
        # description:
        # Fixed value of each variable ("uint32 type":boolean type)

        # Specifies a fixed value for each polynomial (problem) variable that is set to find an optimal solution.
        # The specified variable is fixed at the specified value.
        # However, if fixing at the specified value does not result in the optimal solution, it may not be fixed at the specified value.

        # Specifies a fixed value for each of the variables with the following format:
        # 　Format: {"VariableNumber":FixedValue, "VariableNumber":FixedValue, ...}
        # 　Specification example: When fixed values (false) are specified for variables x1, x2, and x4 of 2x1x2 - 4x2x4 + 7x3x5
        # 　　　　　{"1":false,"2":false,"4":false}

        # Variables that are not specified are not fixed.

        # integer($uint32)	boolean
        # }
        self.fixed_config = fixed_config

        # {
        # description:
        # Specifies the number of variables in each group of one-way one-hot constraints.
        # When one_way_one_hot_groups is specified, search for the solution with one "True" value among the variables in the same group.
        # If internal_penalty is not specified, or if internal_penalty is specified as 0, then the BinaryPolynomial or PenaltyBinaryPolynomial for the combinatorial optimization problem must be a quadratic polynomial indicating a condition for the 1way 1hot constraint (one_way_one_hot_groups). The "numbers" has an array of the number of variables in the same group.
        # The starting index is the minimum variable number of the combinatorial optimization problem specified for the binary polynomial (BinaryPolynomial) or the penalty binary polynomial (PenaltyBinaryPolynomial).
        # If you specify one_way_one_hot_groups, it is recommended to create a combinatorial optimization problem with consecutive variable numbers.

        # Specifies the number of variables in each group in the following format:
        # Format: {"numbers": [Number of variables in group 1, Number of variables in group 2, ...]}
        # Specification example: When grouping variable numbers 0 to 11 into [0, 1, 2, 3], [4, 5, 6], [7, 8, 9, 10, 11] (Constraints that only one "True" value among the variable in each groups)
        # 　　　　　{"numbers": [4, 3, 5]}

        # numbers	[...]
        # }
        self.one_way_one_hot_groups = one_way_one_hot_groups

        # {
        # description:
        # Specifies the number of variables in each group of two-way one-hot constraints.
        # When two_way_one_hot_groups is specified, search for the solution with one "True" value among the columns and rows of square consisting of variables of rows and columns in the same group.
        # If internal_penalty is not specified, or if internal_penalty is specified as 0, then the BinaryPolynomial or PenaltyBinaryPolynomial for the combinatorial optimization problem must be a quadratic polynomial indicating a condition for the 2way 1hot constraint (two_way_one_hot_groups). The "numbers" has an array of the number of variables in the same group. Values in the numbers array must be the squared number.
        # The starting index is the minimum variable number of the combinatorial optimization problem specified for the binary polynomial (BinaryPolynomial) or the penalty binary polynomial (PenaltyBinaryPolynomial).
        # If you specify two_way_one_hot_groups, it is recommended to create a combinatorial optimization problem with consecutive variable numbers.

        # Specifies the number of variables in each group in the following format:
        # 　Format: {"numbers": [Number of variables in group 1, Number of variables in group 2, ...]}
        # 　Specification example: Specifies 16 for a 4x4 group, 25 for a 5x5 group, and 36 for a 6x6 group.
        # 　　　　　{"numbers": [16, 25, 36]}

        # numbers	[...]
        # }
        self.two_way_one_hot_groups = two_way_one_hot_groups


class LightSolverParameterModel:
    def __init__(
        self,
        timeout: Optional[float] = None,
    ) -> None:
        # - `timeout` : (optional) the running timeout, in seconds for the algorithm, must be in the range 0.001 - 60 (default: 10).
        self.timeout = timeout


class QAOAParameterModel:
    def __init__(
        self,
        maxiter: Optional[int] = None,
        shotsin: Optional[int] = None,
        p: Optional[int] = None,
        theta0: Optional[List[float]] = None,
        alpha: Optional[float] = None,
        optimizer: Optional[str] = None,
        ansatz: Optional[str] = None,
        ising: Optional[List[bool]] = None,
        warm_start: Optional[bool] = None,
        qrr: Optional[bool] = None,
    ) -> None:
        #  For details: https://docs.strangeworks.com/algorithms/qaoa

        # Maximum number of iterations in algorithm
        self.maxiter = maxiter
        # Number of times quantum circuit is measured at each iteration
        self.shotsin = shotsin
        # Optional Input: Controls the depth of the Quantum Circuit ansatz. Default p=1
        self.p = p
        # Optional Input: Starting point for variational parameters. If specified must be equal to 2p
        self.theta0 = theta0
        # Optional Input: Cvar parameter, float between 0 and 1 - https://arxiv.org/pdf/1907.04769.pdf. Default alpha=1.0
        self.alpha = alpha
        # Optional Input: Classical optimizer to use:
        # Possible Values:
        # 'COBYLA' (Default), 'Nelder-Mead', 'Powell', 'CG', 'BFGS', 'Newton-CG', 'L-BFGS-B', 'TNC',
        # 'SLSQP', 'trust-constr', 'dogleg', 'trust-ncg', 'trust-exact', 'trust-krylov'
        # Additionals for IBM backends: 'SPSA', 'NFT'
        self.optimizer = optimizer

        # QAOA quantum ansatz circuit to use. Either "qaoa_strangeworks" or "RealAmplitudes" currently available
        self.ansatz = ansatz

        # Optional Input: is the problem an Ising problem or a QUBO problem, i.e. are the values of the variables {-1/2,+1/2} (Ising) or {0,1} (QUBO, Default)
        self.ising = ising
        # Optional Input: Run warm start qaoa or not - https://arxiv.org/abs/2009.10095. Default False: Standard QAOA ansatz
        self.warm_start = warm_start
        # Optional Input: Quantum Relax and Round QAOA algorithm - https://arxiv.org/abs/2307.05821. Default False: Standard QAOA
        self.qrr = qrr
