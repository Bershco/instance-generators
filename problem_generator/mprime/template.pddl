(define (problem ${instance_name})
  (:domain mystery-prime-typed)
  (:objects
    ${foods_list} - food
    ${pleasures_list} - pleasure
    ${pains_list} - pain
  )

  (:init
    ${initial_eats}

    ${initial_craves}

    ${initial_fluents}
  )

  (:goal (and
    ${goal_conditions}
  ))
)
