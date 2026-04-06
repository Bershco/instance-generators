(define (problem ${instance_name})
(:domain TPP-Metric)
(:objects
	${markets_list} - market
	depot0 - depot
	truck0 - truck
	${goods_list} - goods)
(:init
	${initial_fluents}
	(= (total-cost) 0))

(:goal (and
	${goal_conditions}
	(loc truck0 depot0)))

(:metric minimize (total-cost))
)
