;; Enrico Scala (enricos83@gmail.com) and Miquel Ramirez (miquel.ramirez@gmail.com)
(define (problem ${instance_name})
  (:domain fo-counters)
  (:objects
    ${counters_list} - counter
  )

  (:init
    (= (max_int) ${max_int_value})
        ${counters_initial_values}

        ${counters_rate_values}
        (= (total-cost) 0)
  )

  (:goal (and
    ${counters_final_values}
  ))
  (:metric minimize (total-cost))
)
