(define (problem ${instance_name}) (:domain rover)
(:objects
	general - lander
	colour high_res low_res - mode
	${rovers_list} - rover
	${stores_list} - store
	${waypoints_list} - waypoint
	${cameras_list} - camera
	${objectives_list} - objective
)
(:init
	${initial_fluents}
	${initial_predicates}
)

(:goal (and
${goal_conditions}
	)
)

(:metric minimize (recharges))
)
