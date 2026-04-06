(define (problem ${instance_name})
(:domain zenotravel)
(:objects
	${aircraft_list} - aircraft
	${people_list} - person
	${cities_list} - city
	)
(:init
	${initial_predicates}
	${initial_fluents}
)
(:goal (and
	${goal_conditions}
	))
(:metric minimize ${metric_expression})

)
