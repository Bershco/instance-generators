;;Instance with ${max_x}x${max_y}x${max_z} points
(define (problem ${instance_name}) (:domain drone)
(:objects 
${location_objects}
) 
(:init (= (x) 0) (= (y) 0) (= (z) 0)
 (= (min_x) 0)  (= (max_x) ${max_x}) 
 (= (min_y) 0)  (= (max_y) ${max_y}) 
 (= (min_z) 0)  (= (max_z) ${max_z}) 
${coordinate_values}
(= (battery-level) ${battery_level})
(= (battery-level-full) ${battery_level})
)
(:goal (and 
${goal_conditions}(= (x) 0) (= (y) 0) (= (z) 0) ))
);; end of the problem instance
