from ..entities.fragments import Fragment


class OldTraverser(Fragment):
    def exchange_value(self):
        pass

    def traverse(self, scenario=None, observed=False, frags_seen=None):
        if isinstance(scenario, set):
            scenarios = set(scenario)
        elif isinstance(scenario, tuple) or isinstance(scenario, list):
            scenarios = set(scenario)
        elif scenario is None:
            if observed:
                scenarios = {1}
            else:
                scenarios = None
        else:
            scenarios = {scenario}
        ffs, _ = self._traverse_node(1.0, scenarios, frags_seen=frags_seen)
        return ffs

    def _traverse_fg_node(self, ff, scenarios, frags_seen):
        """
        Handle foreground nodes and processes--> these can be quantity-conserving, but except for
        balancing flows the flow magnitudes are determined at the time of construction (or scenario specification).

        Balancing flow exchange values are always determined with respect to a unit activity of the terminal node.

        This is messy so it deserves some notes.
        the fragment's exchange value specifies the scaling factor for the terminal node, EXCEPT if the
        fragment is a reference fragment (no parent) AND the terminal node is in the foreground.  In this case
        ONLY, the exchange value functions as an inbound exchange value, and the node weight should be 1.0.
        The prototypical example of this is a fragment for cultivation of 1 ha of corn, with the reference
        flow being (e.g.) 9300 kg of corn.  The reference fragment's exchange value is 9300 kg; the reference
         node's node weight is 1.0

        If the reference node has a balancing flow (say, we want to balance carbon content), then the stock
        value is the reference flow converted to the conservation quantity, e.g. 9300 * 0.43 = 3999 kg C, sign
        negative since it's going out (note that the reference fragment's direction is 'Input' in this case
        because direction is always interpreted relative to the parent).

        So then we traverse the child flows, let's say none of them have kg C characterization, and so our stock
        remains -3999 kg. WHen we hit the balancing fragment "atmospheric carbon in", we catch the FoundBalanceFlow
        and come back to it.

        When we come back, we re-negate the stock to +3999 and pass that as _balance to the balancing flow, which
        becomnes that flow's exchange value (again w.r.t. this node's unit node weight).

        IF the terminal node is a process, or if the node is an interior (non-reference) fragment, it's much easier.
        The stock is simply the process's inbound exchange value (with respect to a unit activity level), or if
        it's a foreground node then the stock is simply 1, and the node_weight already accounts for the exchange
        value and scales the balancing flow correctly.

        Were we to do this non-'live' or with some kind of stack, we could conceivably balance multiple quantities with
        additional fragment flows, but I'm pretty sure the same effect can be achieved by nesting conserving fragments.
        This also requires the modeler to specify a resolution order and cuts the need for elaborate error checking.

        :param ff: a FragmentFlow containing the foreground termination to recurse into
        :param scenarios:
        :param frags_seen:
        :return: a list of FragmentFlows in the order encountered, with input ff in position 0
        """
        term = ff.term
        node_weight = ff.node_weight
        ffs = [ff]
        stock_inflow = stock_outflow = 0.0  # keep track of total inflows to detect+quash near-zero (floating-point-tolerance) balances

        if term.is_fg or not term.valid:
            if self.reference_entity is None:
                # inbound exchange value w.r.t. term node's unit magnitude
                stock = self.exchange_value(scenarios)
            else:
                stock = 1.0  # balance measurement w.r.t. term node's unit magnitude
        else:
            stock = term.inbound_exchange_value  # balance measurement w.r.t. term node's unit magnitude
        bal_f = None
        if self.is_conserved_parent:
            stock *= self.balance_magnitude
            if self.direction == 'Input':  # convention: inputs to self are positive
                #  direction w.r.t. parent so self.direction == 'Input' is an input to parent = output from node
                stock *= -1
            self.dbg_print('%g inbound-balance' % stock, level=2)

        if stock > 0:
            stock_inflow += stock
        else:
            stock_outflow -= stock
        # TODO: Handle auto-consumption!  test child flows for flow identity and null term; cumulate; scale node_weight

        for f in self.child_flows:
            try:  # now that we are storing _balance_child we can just skip it instead of try-catch. but whatever.
                # traverse child, collecting conserved value if applicable
                child_ff, cons = f._traverse_node(node_weight, scenarios,
                                                  frags_seen=frags_seen, conserved_qty=self.conserved_quantity)
                if cons is None:
                    self.dbg_print('-- returned cons_value', level=3)
                else:
                    self.dbg_print('%g returned cons_value' % cons, level=2)
                    stock += cons
                    if cons > 0:
                        stock_inflow += cons
                    else:
                        stock_outflow -= cons
            except FoundBalanceFlow:
                self.dbg_print('%g bal magnitude on %.3s' % (stock, f.uuid), level=3)
                bal_f = f
                child_ff = []

            ffs.extend(child_ff)

        stock_max = max([abs(stock_inflow), abs(stock_outflow)])

        if bal_f is not None:
            # balance reports net inflows; positive value is more coming in than out
            # if balance flow is an input, its exchange must be the negative of the balance
            # if it is an output, its exchange must equal the balance
            if stock != 0 and (abs(stock) / stock_max < 1e-10):
                self.dbg_print('Quashing <1e-10 balance flow (%g vs %g)' % (stock, stock_inflow), level=1)
                stock = 0.0
            if bal_f.direction == 'Input':
                stock *= -1
                self.dbg_print('%.3s Input: negating balance value' % bal_f.uuid)
            else:
                self.dbg_print('%.3s Output: maintaining balance value' % bal_f.uuid)
            self.dbg_print('%g balance value passed to %.3s' % (stock, bal_f.uuid))
            bal_ff, _ = bal_f._traverse_node(node_weight, scenarios,
                                             frags_seen=set(frags_seen), conserved_qty=None, _balance=stock)
            ffs.extend(bal_ff)

        return ffs

    def _traverse_subfragment(self, ff, scenarios, frags_seen):
        """
        handle sub-fragments, including background flows--
        for sub-fragments, the flow magnitudes are determined at the time of traversal and must be pushed out to
         child flows
        for LOCAL background flows, the background ff should replace the current ff, maintaining self as fragment

        subfragment activity level is determined as follows:
         - if the subfragment is a background fragment, it MUST have a unity inbound_exchange_value; this is enforced:
           - for background processes, because FlowTermination._unobserved_exchanges() uses term_node.lci(ref_flow)
           - for background fragments, in the yet-to-be-implemented bg_lcia method  (part of the foreground interface??)
           in any case, the background term is swapped into the foreground node.

         - otherwise, the subfragment inventory is taken and grouped, and the matching flow is found, and the magnitude
           of the matching flow is used to normalize the downstream node weight.

         - then the inventory of the subfragment is used to apply exchange values to child fragments, and traversal
           recursion continues.


        :param ff: a FragmentFlow containing the non-fg subfragment termination to recurse into
        :param scenarios:
        :param frags_seen:
        :return:
        """
        '''
        '''

        term = ff.term
        if 0:  #  term.term_is_bg: this is deprecated
            pass
            '''
            if term.term_flow == term.term_node.flow:
                # collapse trivial bg terminations into the parent fragment flow
                bg_ff, _ = term.term_node._traverse_node(ff.node_weight, scenario, observed=observed)
                assert len(bg_ff) == 1, (self.uuid, term.term_node.external_ref)
                bg_ff[0].fragment = self
                return bg_ff
            '''

        # traverse the subfragment, match the driven flow, compute downstream node weight and normalized inventory
        try:
            ffs, unit_inv, downstream_nw = _do_subfragment_traversal(ff, scenarios, frags_seen)
        except ZeroInboundExchange:
            self.dbg_print('subfragment divide by zero', 1)
            return [ff]

        # next we traverse our own child flows, determining the exchange values from the normalized unit inventory
        for f in self.child_flows:
            self.dbg_print('Handling child flow %s' % f, 4)
            ev = 0.0
            try:
                m = next(j for j in unit_inv if j.fragment.flow == f.flow)
                if m.fragment.direction == f.direction:
                    self.dbg_print('  ev += %g' % m.magnitude, 4)
                    ev += m.magnitude
                else:
                    self.dbg_print('  ev -= %g' % m.magnitude, 4)
                    ev -= m.magnitude
                unit_inv.remove(m)
            except StopIteration:
                self.dbg_print('  no driving flows found')
                continue

            self.dbg_print('traversing with ev = %g' % ev, 4)
            child_ff, _ = f._traverse_node(downstream_nw, scenarios,
                                           frags_seen=frags_seen, _balance=ev)
            ffs.extend(child_ff)

        # remaining un-accounted io flows are getting appended, so do scale
        for x in unit_inv:
            x.scale(downstream_nw)
        ffs.extend(list(unit_inv))

        return ffs

    def _traverse_node(self, upstream_nw, scenarios,
                       frags_seen=None, conserved_qty=None, _balance=None):

        """
        If the node has a non-null termination, use that; follow child flows.

        If the node's termination is null- then look for matching background fragments. If one is found, adopt its
        termination, and return.

        else: assume it is a null foreground node; follow child flows

        :param upstream_nw: upstream node weight
        :param scenarios: set of scenario values
        #:param observed: whether to use observed or cached evs (overridden by scenario specification)
        :param frags_seen: carried along to catch recursion loops
        :param conserved_qty: in case the parent node is a conservation node
        :param _balance: used when flow magnitude is determined during traversal, i.e. for balance flows and
        children of fragment nodes
        :return: 2-tuple: ffs, conserved_val
          ffs = an array of FragmentFlow records reporting the traversal, beginning with self
          conserved_val = the magnitude of the flow with respect to the conserved quantity, if applicable (or None)
        """

        # first check for cycles
        if frags_seen is None:
            frags_seen = set()

        if self.reference_entity is None:
            if self.uuid in frags_seen:
                # this should really get resolved into a loop-closing algorithm
                raise InvalidParentChild('Frag %s seeing self\n %s' % (self.uuid, '; '.join(frags_seen)))
            frags_seen.add(self.uuid)

        if _balance is None:
            _scen_ev = self._match_scenario_ev(scenarios)
            ev = self.exchange_value(_scen_ev)
        else:
            _scen_ev = None
            self.dbg_print('%g balance' % _balance, level=2)
            ev = _balance
            '''
            if self._check_observability(scenario):
                self._cache_balance_ev(_balance, scenario, observed)
            '''

        magnitude = upstream_nw * ev
        _scen_term = self._match_scenario_term(scenarios)
        term = self._terminations[_scen_term]

        if self.reference_entity is None:
            node_weight = upstream_nw
            if magnitude == 0:
                self.dbg_print('Unobserved reference fragment')
                node_weight = 0
        else:
            node_weight = magnitude

        f_conv = term.node_weight_multiplier

        node_weight *= f_conv

        self.dbg_print('magnitude: %g f_conv: %g node_weight: %g' % (magnitude, f_conv, node_weight))

        conserved_val = None
        if conserved_qty is not None:
            if self.is_balance:
                self.dbg_print('Found balance flow')
                raise FoundBalanceFlow  # to be caught
            cf = conserved_qty.cf(self.flow)
            self.dbg_print('consrv cf %g for qty %s' % (cf, conserved_qty), level=3)
            conserved_val = ev * cf
            if conserved_val == 0:
                conserved = False
            else:
                conserved = True
                if self.direction == 'Output':  # convention: inputs to parent are positive
                    conserved_val *= -1
                self.dbg_print('conserved_val %g' % conserved_val, level=2)
        elif self.is_balance:
            # traversing balance flow after FoundBalanceFlow exception
            conserved = True
        else:
            conserved = self.conserved

        # print('%6f %6f %s' % (magnitude, node_weight, self))
        # this is the only place a FragmentFlow is created
        # TODO: figure out how to cache + propagate matched scenarios ... in progress
        ff = FragmentFlow(self, magnitude, node_weight, term, conserved, match_ev=_scen_ev, match_term=_scen_term,
                          flow_conversion=f_conv)

        '''
        now looking forward: is our termination a cutoff, background, foreground or subfragment?
        '''
        if magnitude == 0:
            # no flow to follow
            self.dbg_print('zero magnitude')
            return [ff], conserved_val
        elif term.is_null or term.is_context:
            # cutoff /context and background end traversal
            self.dbg_print('cutoff or bg')
            return [ff], conserved_val

        if term.is_fg or term.is_process or not term.valid:
            self.dbg_print('fg')
            ffs = self._traverse_fg_node(ff, scenarios, frags_seen)

        else:
            self.dbg_print('subfrag')
            ffs = self._traverse_subfragment(ff, scenarios, frags_seen)

        return ffs, conserved_val


def _do_subfragment_traversal(ff, scenarios, frags_seen):
    """
    This turns out to be surprisingly complicated. So we now have:
     - LcFragment._traverse_node <-- which is called recursively
      + scenario matching + finds ev and term
      - selects handler based on term type:
       - LcFragment._subfragment_traversal
       |- invokes (static) _do_subfragment_traversal (YOU ARE HERE)
       ||- calls [internally recursive] term_node.unit_flows, which is just a wrapper for
       || - (static) group_ios
       ||  + reference flow and autoconsumption handling
       || /
       ||/
       |+ reference flow matching and normalizing
       + child flow matching and further recursion --> into LcFragment._traverse_node
      /
     /
     ffs, conserved_val


     - (static) group_ios
     - nested inside LcFragment.unit_flows, which is really just a wrapper
     - called from
     - called from

    :param ff: The FragmentFlow whose subfragment is being traversed
    :param scenarios: to pass to subfragment
    :return: ffs [subfragment traversal appended], unit_inv [with reference flow removed], downstream node weight
    """
    term = ff.term  # note that we ignore term.direction in subfragment traversal
    node_weight = ff.node_weight
    self = ff.fragment

    unit_inv, subfrags = term.term_node.unit_flows(scenario=scenarios, frags_seen=frags_seen)

    # find the inventory flow that matches us
    # use term_flow over term_node.flow because that allows client code to specify inverse traversal knowing
    #  only the sought flow.
    # unit_flows guarantees that there is exactly one of these flows (except in the case of cumulating flows!
    # see group_ios)
    try:
        match = next(k for k in unit_inv if k.fragment.flow == term.term_flow)
    except StopIteration:
        print('Flow mismatch Traversing:\n%s' % self)
        print('Term flow: %s' % term.term_flow.link)
        print(term.serialize())
        for k in unit_inv:
            print('%s' % k.fragment.flow.link)
        raise MissingFlow('Term flow: %s' % term.term_flow.link)
    self.dbg_print('matched flow %s' % match.fragment.flow.link)

    unit_inv.remove(match)

    in_ex = match.magnitude  # this is the inbound exchange value for the driven fragment
    if in_ex == 0:
        # this indicates a non-consumptive pass-thru fragment.
        print('Frag %.5s: Zero inbound exchange' % self.uuid)
        raise ZeroInboundExchange
    if match.fragment.direction == self.direction:  # match direction is w.r.t. subfragment
        # self is driving subfragment in reverse
        self.dbg_print('reverse-driven subfragment %.3s' % match.fragment.uuid)
        in_ex *= -1

    # node weight for the driven [downstream] fragment
    downstream_nw = node_weight / in_ex

    '''
    # then we add the results of the subfragment, either in aggregated or disaggregated form
    if term.descend:
        # if appending, we are traversing in situ, so do scale
        self.dbg_print('descending', level=0)
        for i in subfrags:
            i.scale(downstream_nw)
        ffs = [ff]
        ffs.extend(subfrags)
    else:
        # if aggregating, we are only setting unit scores- so don't scale
        self.dbg_print('aggregating', level=0)
        ff.aggregate_subfragments(subfrags, scenarios=scenarios)  # include params to reproduce
        ff.node_weight = downstream_nw  # NOTE: this may be problematic; undone in lca_disclosures
        ffs = [ff]
    '''
    # now, we abolish descend as a traversal parameter and make it only an LCIA parameter
    # therefore, we retain subfragments always, we just have to decide how to scale them
    self.dbg_print('%d subfrags resulting from this traversal' % len(subfrags), 1)
    ff.aggregate_subfragments(subfrags, scenarios=scenarios)
    ff.node_weight = downstream_nw
    ffs = [ff]

    return ffs, unit_inv, downstream_nw
