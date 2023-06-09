import collections, util, copy

SEED = 4512

############################################################
# Problem 0

# Hint: Take a look at the CSP class and the CSP examples in util.py
def create_chain_csp(n):
    # same domain for each variable
    domain = [0, 1]
    # name variables as x_1, x_2, ..., x_n
    variables = ['x%d'%i for i in range(1, n+1)]
    csp = util.CSP()
    # Problem 0a
    # BEGIN_YOUR_ANSWER (our solution is 5 lines of code, but don't worry if you deviate from this)
    csp.add_variable(variables[0], [0, 1])
    for i in range(1, len(variables)):
        csp.add_variable(variables[i], [0, 1])
        csp.add_binary_factor(variables[i - 1], variables[i], lambda x, y: x != y)
    # raise Exception("Not implemented yet")
    # END_YOUR_ANSWER
    return csp


############################################################
# Problem 1

def create_nqueens_csp(n = 8):
    """
    Return an N-Queen problem on the board of size |n| * |n|.
    You should call csp.add_variable() and csp.add_binary_factor().

    @param n: number of queens, or the size of one dimension of the board.

    @return csp: A CSP problem with correctly configured factor tables
        such that it can be solved by a weighted CSP solver.
    """
    csp = util.CSP()
    # Problem 1a
    # BEGIN_YOUR_ANSWER (our solution is 7 lines of code, but don't worry if you deviate from this)
    variables = ['x%d'%i for i in range(1, n+1)]
    for row, var in enumerate(variables):
        csp.add_variable(var, [(row, col) for col in range(n)])
    def factor(v1, v2):
        return all([v1[1] != v2[1],
                    v1[0] - v1[1] != v2[0] - v2[1],
                    v1[0] + v1[1] != v2[0] + v2[1]])
    for i in range(n):
        for j in range(i, n):
            r1 = variables[i]
            r2 = variables[j]
            if r1 != r2:
                csp.add_binary_factor(r1, r2, factor)
    # raise Exception("Not implemented yet")
    # END_YOUR_ANSWER
    return csp

# A backtracking algorithm that solves weighted CSP.
# Usage:
#   search = BacktrackingSearch()
#   search.solve(csp)
class BacktrackingSearch():

    def reset_results(self):
        """
        This function resets the statistics of the different aspects of the
        CSP solver. We will be using the values here for grading, so please
        do not make any modification to these variables.
        """
        # Keep track of the best assignment and weight found.
        self.optimalAssignment = {}
        self.optimalWeight = 0

        # Keep track of the number of optimal assignments and assignments. These
        # two values should be identical when the CSP is unweighted or only has binary
        # weights.
        self.numOptimalAssignments = 0
        self.numAssignments = 0

        # Keep track of the number of times backtrack() gets called.
        self.numOperations = 0

        # Keep track of the number of operations to get to the very first successful
        # assignment (doesn't have to be optimal).
        self.firstAssignmentNumOperations = 0

        # List of all solutions found.
        self.allAssignments = []

    def print_stats(self):
        """
        Prints a message summarizing the outcome of the solver.
        """
        if self.optimalAssignment:
            print("Found %d optimal assignments with weight %f in %d operations" % \
                (self.numOptimalAssignments, self.optimalWeight, self.numOperations))
            print("First assignment took %d operations" % self.firstAssignmentNumOperations)
        else:
            print("No solution was found.")

    def get_delta_weight(self, assignment, var, val):
        """
        Given a CSP, a partial assignment, and a proposed new value for a variable,
        return the change of weights after assigning the variable with the proposed
        value.

        @param assignment: A dictionary of current assignment. Unassigned variables
            do not have entries, while an assigned variable has the assigned value
            as value in dictionary. e.g. if the domain of the variable A is [5,6],
            and 6 was assigned to it, then assignment[A] == 6.
        @param var: name of an unassigned variable.
        @param val: the proposed value.

        @return w: Change in weights as a result of the proposed assignment. This
            will be used as a multiplier on the current weight.
        """
        assert var not in assignment
        w = 1.0
        if self.csp.unaryFactors[var]:
            w *= self.csp.unaryFactors[var][val]
            if w == 0: return w
        for var2, factor in self.csp.binaryFactors[var].items():
            if var2 not in assignment: continue  # Not assigned yet
            w *= factor[val][assignment[var2]]
            if w == 0: return w
        #print(w)
        return w

    def solve(self, csp, mcv = False, ac3 = False):
        """
        Solves the given weighted CSP using heuristics as specified in the
        parameter. Note that unlike a typical unweighted CSP where the search
        terminates when one solution is found, we want this function to find
        all possible assignments. The results are stored in the variables
        described in reset_result().

        @param csp: A weighted CSP.
        @param mcv: When enabled, Most Constrained Variable heuristics is used.
        @param ac3: When enabled, AC-3 will be used after each assignment of an
            variable is made.
        """
        # CSP to be solved.
        self.csp = csp

        # Set the search heuristics requested asked.
        self.mcv = mcv
        self.ac3 = ac3

        # Reset solutions from previous search.
        self.reset_results()

        # The dictionary of domains of every variable in the CSP.
        self.domains = {var: list(self.csp.values[var]) for var in self.csp.variables}

        # Perform backtracking search.
        self.backtrack({}, 0, 1)
        # Print summary of solutions.
        self.print_stats()

    def backtrack(self, assignment, numAssigned, weight):
        """
        Perform the back-tracking algorithms to find all possible solutions to
        the CSP.

        @param assignment: A dictionary of current assignment. Unassigned variables
            do not have entries, while an assigned variable has the assigned value
            as value in dictionary. e.g. if the domain of the variable A is [5,6],
            and 6 was assigned to it, then assignment[A] == 6.
        @param numAssigned: Number of currently assigned variables
        @param weight: The weight of the current partial assignment.
        """

        self.numOperations += 1
        assert weight > 0
        if numAssigned == self.csp.numVars:
            # A satisfiable solution have been found. Update the statistics.
            self.numAssignments += 1
            newAssignment = {}
            for var in self.csp.variables:
                newAssignment[var] = assignment[var]
            self.allAssignments.append(newAssignment)

            if len(self.optimalAssignment) == 0 or weight >= self.optimalWeight:
                if weight == self.optimalWeight:
                    self.numOptimalAssignments += 1
                else:
                    self.numOptimalAssignments = 1
                self.optimalWeight = weight

                self.optimalAssignment = newAssignment
                if self.firstAssignmentNumOperations == 0:
                    self.firstAssignmentNumOperations = self.numOperations
            return

        # Select the next variable to be assigned.
        var = self.get_unassigned_variable(assignment)
        # Get an ordering of the values.
        ordered_values = self.domains[var]

        # Continue the backtracking recursion using |var| and |ordered_values|.
        if not self.ac3:
            # When arc consistency check is not enabled.
            for val in ordered_values:
                deltaWeight = self.get_delta_weight(assignment, var, val)
                if deltaWeight > 0:
                    assignment[var] = val
                    self.backtrack(assignment, numAssigned + 1, weight * deltaWeight)
                    del assignment[var]
        else:
            # Arc consistency check is enabled.
            # Problem 1c: skeleton code for AC-3
            # You need to implement arc_consistency_check().
            for val in ordered_values:
                deltaWeight = self.get_delta_weight(assignment, var, val)
                if deltaWeight > 0:
                    assignment[var] = val
                    # create a deep copy of domains as we are going to look
                    # ahead and change domain values
                    localCopy = copy.deepcopy(self.domains)
                    # fix value for the selected variable so that hopefully we
                    # can eliminate values for other variables
                    self.domains[var] = [val]

                    # enforce arc consistency
                    self.arc_consistency_check(var)

                    self.backtrack(assignment, numAssigned + 1, weight * deltaWeight)
                    # restore the previous domains
                    self.domains = localCopy
                    del assignment[var]

    def get_unassigned_variable(self, assignment):
        """
        Given a partial assignment, return a currently unassigned variable.

        @param assignment: A dictionary of current assignment. This is the same as
            what you've seen so far.

        @return var: a currently unassigned variable.
        """

        if not self.mcv:
            # Select a variable without any heuristics.
            for var in self.csp.variables:
                if var not in assignment: return var
        else:
            # Problem 1b
            # Heuristic: most constrained variable (MCV)
            # Select a variable with the least number of remaining domain values.
            # Hint: given var, self.domains[var] gives you all the possible values
            # Hint: get_delta_weight gives the change in weights given a partial
            #       assignment, a variable, and a proposed value to this variable
            # Hint: for ties, choose the variable with lowest index in self.csp.variables
            # BEGIN_YOUR_ANSWER (our solution is 7 lines of code, but don't worry if you deviate from this)
            min_var, min_cnt = None, float('inf')
            for var in self.csp.variables:
                if var in assignment:
                    continue
                cnt = 0
                for val in self.domains[var]:
                    if self.get_delta_weight(assignment, var, val) > 0:
                        cnt += 1
                if cnt < min_cnt:
                    min_var, min_cnt = var, cnt
            return min_var
            # raise Exception("Not implemented yet")
            # END_YOUR_ANSWER

    def arc_consistency_check(self, var):
        """
        Perform the AC-3 algorithm. The goal is to reduce the size of the
        domain values for the unassigned variables based on arc consistency.

        @param var: The variable whose value has just been set.
        """
        # Problem 1c
        # Hint: How to get variables neighboring variable |var|?
        # => for var2 in self.csp.get_neighbor_vars(var):
        #       # use var2
        #
        # Hint: How to check if a value or two values are inconsistent?
        # - For unary factors
        #   => self.csp.unaryFactors[var1][val1] == 0
        #
        # - For binary factors
        #   => self.csp.binaryFactors[var1][var2][val1][val2] == 0
        #   (self.csp.binaryFactors[var1][var2] returns a nested dict of all assignments)

        # BEGIN_YOUR_ANSWER (our solution is 20 lines of code, but don't worry if you deviate from this)
        q = collections.deque([var])

        while q:
            var1 = q.popleft()
            for var2 in self.csp.get_neighbor_vars(var1):
                # check arc-consistency
                removed_value_set = set()
                for val2 in self.domains[var2]:
                    # unary case
                    if self.csp.unaryFactors[var2] is not None and\
                       self.csp.unaryFactors[var2][val2] == 0:
                        removed_value_set.add(val2)
                    # binary case
                    for val1 in self.domains[var1]:
                        if var2 in self.csp.binaryFactors[var1] and\
                           self.csp.binaryFactors[var1][var2][val1][val2] > 0:
                            break
                    else:
                        removed_value_set.add(val2)
                # add var2 if the domain is changed
                if removed_value_set:
                    self.domains[var2] = [val2 for val2 in self.domains[var2]
                                          if val2 not in removed_value_set]
                    q.append(var2)
        # raise Exception("Not implemented yet")
        # END_YOUR_ANSWER


############################################################
# Problem 2a

def get_sum_variable(csp, name, variables, maxSum):
    """
    Given a list of |variables| each with non-negative integer domains,
    returns the name of a new variable with domain range(0, maxSum+1), such that
    it's consistent with the value |n| iff the assignments for |variables|
    sums to |n|.

    @param name: Prefix of all the variables that are going to be added.
        Can be any hashable objects. For every variable |var| added in this
        function, it's recommended to use a naming strategy such as
        ('sum', |name|, |var|) to avoid conflicts with other variable names.
    @param variables: A list of variables that are already in the CSP that
        have non-negative integer values as its domain.
    @param maxSum: An integer indicating the maximum sum value allowed. You
        can use it to get the auxiliary variables' domain

    @return result: The name of a newly created variable with domain range
        [0, maxSum] such that it's consistent with an assignment of |n|
        iff the assignment of |variables| sums to |n|.
    """
    # BEGIN_YOUR_ANSWER (our solution is 18 lines of code, but don't worry if you deviate from this)
    get_var = lambda i: ('sum', name, i)

    # define the result variable
    result = get_var('result')
    csp.add_variable(result, list(range(maxSum + 1)))

    if len(variables) == 0:
        csp.add_unary_factor(result, lambda val: val == 0)
        return result

    # define first auxiliary variable
    domain0 = [(0, val) for val in csp.values[variables[0]]]
    csp.add_variable(get_var(0), domain0)

    domainj = domain0

    # define other auxiliary variables
    for i in range(1, len(variables)):
        domaini = list({(valj[1], valj[1] + valx)
                        for valj in domainj for valx in csp.values[variables[i]]
                        if valj[1] + valx <= maxSum})
        csp.add_variable(get_var(i), domaini)
        domainj = domaini
    X_0 = variables[0]
    A_0 = get_var(0)

    # add an unary and binary factors for the first auxiliary variable
    csp.add_unary_factor(A_0, lambda x: x[0] == 0)
    csp.add_binary_factor(X_0, A_0, lambda x, a: a[1] == a[0] + x)

    # add binary factors
    A_i = A_0
    for i in range(1, len(variables)):
        X_i = variables[i]

        A_i = get_var(i)
        A_j = get_var(i - 1)

        csp.add_binary_factor(X_i, A_i, lambda x, a: a[1] == a[0] + x)
        csp.add_binary_factor(A_j, A_i, lambda aj, ai: aj[1] == ai[0])

    # add a binary factor between last auxiliary variable and the result variable
    csp.add_binary_factor(A_i, result, lambda a, r: a[1] == r)

    return result
    # raise Exception("Not implemented yet")
    # END_YOUR_ANSWER

def create_lightbulb_csp(buttonSets, numButtons):
    """
    Return an light-bulb problem for the given buttonSets.
    You can exploit get_sum_variable().

    @param buttonSets: buttonSets is a tuple of sets of buttons. buttonSets[i] is a set including all indices of buttons which toggle the i-th light bulb.
    @param numButtons: the number of all buttons

    @return csp: A CSP problem with correctly configured factor tables
        such that it can be solved by a weighted CSP solver.
    """
    numBulbs = len(buttonSets)
    csp = util.CSP()

    assert all(all(0 <= buttonIndex < numButtons
                   for buttonIndex in buttonSet)
               for buttonSet in buttonSets)

    # Problem 2b
    # BEGIN_YOUR_ANSWER
    def get_button_variable(buttonIndex):
        return ('button', buttonIndex)

    all_button_variables = tuple(map(get_button_variable, range(numButtons)))
    for var in all_button_variables:
        csp.add_variable(var, [0, 1])

    def get_button_variables(bulbIndex):
        return tuple(map(get_button_variable, buttonSets[bulbIndex]))

    button_sum_variables = tuple(
        get_sum_variable(csp, ('button-sum', bulbIndex),
                         get_button_variables(bulbIndex), len(buttonSets[bulbIndex]))
        for bulbIndex in range(numBulbs))

    def factor(val):
        return val % 2 == 1

    for var in button_sum_variables:
        csp.add_unary_factor(var, factor)
    # END_YOUR_ANSWER
    return csp
