package com.huberlin;

import com.huberlin.config.QueryInformation;
import com.huberlin.event.Event;
import com.huberlin.event.SimpleEvent;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.cep.pattern.Pattern;
import org.apache.flink.cep.pattern.conditions.IterativeCondition;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.*;
import java.util.function.Predicate;



public class PatternFactory_kleene_unary {
	
    static public ArrayList<Pattern<Event, ?>> create(QueryInformation query_information) {
    	        

		ArrayList<Pattern<Event, ?>> pattern = new ArrayList<>(2);
		Pattern<Event, ?> kleene_pattern = Pattern.<Event>begin("first")
    		    .where(new IterativeCondition<Event>() {
    		        @Override
    		        public boolean filter(Event new_event, Context<Event> ctx) throws Exception {
			    final Random rand = new Random(); 	
    		            if (new_event.getEventType().equals(query_information.processing.input_1)) { //kleene type
				for (Event old_event: ctx.getEventsForPattern("first")) { // add selectivity between kleene type

					  for (String id_constraint : query_information.processing.id_constraints) {
                   			  if (!old_event.getEventIdOf(id_constraint).equals(new_event.getEventIdOf(id_constraint)))
                      			  return false; }
              				  
					                                  // SELECTIVTIES// ADD REAL WORLD PREDICATE CHECKS HERE:	
				 // (same as sequence consraint checks) iterate over tuples in predicate constraints
				 // for type in tuple, get respective event in primitive events of [old_event, new_event]
				 // determine order of tuple of primitive events, set to old_event_at, new_event_at, then check predicate (<,> at positions)		

				 for (List<String> predicate_constraint : query_information.processing.predicate_constraints) {

					    String first_eventtype = predicate_constraint.get(0); // from input1
					    String second_eventtype = predicate_constraint.get(1); // from input2

					    SimpleEvent e1 = old_event.getEventOfType(first_eventtype); // Use first_eventtype
					    SimpleEvent e2 = new_event.getEventOfType(second_eventtype); // Use second_eventtype

					 if (e1 == null || e2 == null) {
						 e1 = old_event.getEventOfType(second_eventtype);
						 e2 = new_event.getEventOfType(first_eventtype);
					 }
				
					    SimpleEvent old_event_at = null;
					    SimpleEvent new_event_at = null;

					    if (e1.timestamp < e2.timestamp) {
						old_event_at = e1;
						new_event_at = e2;
					    }
					    if (e2.timestamp < e1.timestamp) {
						old_event_at = e2;
						new_event_at = e1;
					    }
	
					    // Check attributes based on attribute indices (0 for mem_request, 1 for priority, 2 for cpu_request)
					    if (Float.parseFloat(old_event_at.attributeList.get(4)) <= Float.parseFloat(new_event_at.attributeList.get(4))) {
						return false;
					    }
					    if (Float.parseFloat(old_event_at.attributeList.get(6)) <= Float.parseFloat(new_event_at.attributeList.get(6))) {
						return false;
					    }
					    if (Float.parseFloat(old_event_at.attributeList.get(7)) <= Float.parseFloat(new_event_at.attributeList.get(7))) {
						return false;
					    }
					}


				 ////////////////////////////////////////////////   
						 }			
    		                return true;}
    		            else
    		            	return false;
    		        }    		        
    		    }).oneOrMore().optional().allowCombinations().within(Time.milliseconds(60000000));
    	
	pattern.add(kleene_pattern);
	pattern.add(kleene_pattern);
    	
	return pattern;
    };
}
