(define (problem ${instance_name})
  (:domain mt-block-grouping)
  (:objects
    ${blocks_list} - block
  )

  (:init
    ${initial_fluents}
  )

  (:goal (and
    ${goal_constraints}
  ))
)
