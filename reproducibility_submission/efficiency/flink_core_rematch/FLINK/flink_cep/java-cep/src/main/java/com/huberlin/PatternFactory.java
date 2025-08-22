package com.huberlin;

import com.huberlin.config.QueryInformation;
import com.huberlin.event.Event;
import com.huberlin.event.SimpleEvent;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.cep.pattern.Pattern;
import org.apache.flink.cep.pattern.conditions.SimpleCondition;
import org.apache.flink.cep.pattern.conditions.IterativeCondition;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.io.FileWriter;
import java.io.IOException;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Predicate;




class ThroughputLogger extends Thread {
    private final AtomicInteger counter;
    private final String file_path;

    public ThroughputLogger(AtomicInteger counter, String file_path) {
        this.counter = counter;
        this.file_path = file_path;
    }

    @Override
    public void run() {
        try (FileWriter writer = new FileWriter(file_path, true)) {
            while (!Thread.currentThread().isInterrupted()) {
                try {
                    Thread.sleep(10000);
                    int count = counter.getAndSet(0);
                    String log_line = count + "\n";
                    writer.write(log_line);
                    writer.flush();
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                } catch (IOException e) {
                    e.printStackTrace();
                    break;
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}



public class PatternFactory {
    static private final Logger log = LoggerFactory.getLogger(PatternFactory.class);
    static private AtomicInteger timestamp_counter = new AtomicInteger(0);	
    static public ArrayList<Pattern<Event, ?>> create(QueryInformation query_information) {

	        ThroughputLogger counter_logger = new ThroughputLogger(timestamp_counter, "throughput_node_" + query_information.forwarding.node_id + ".csv");
     		counter_logger.setDaemon(true); // Make sure the thread doesn't prevent the JVM from exiting
       		counter_logger.start();
		

		ArrayList<Pattern<Event, ?>> pattern = new ArrayList<>(2);
		final long TIME_WINDOW_SIZE_US = query_information.processing.time_window_size * 1_000_000;
		
Pattern<Event,?> seq1 = Pattern.<Event>begin("first_1")
    		    .where(new SimpleCondition<Event>() {
		        String latest_eventID = "";
    		        @Override
    		        public boolean filter(Event first) throws Exception {

                 	   String simp_eventID = first.getID();
                 	   if (!simp_eventID.equals(latest_eventID))
                 	   {
                     	   latest_eventID = simp_eventID;
                 	   timestamp_counter.incrementAndGet();
                 	   }


    		            if (first.getEventType().equals(query_information.processing.input_1)) { //A
    		                return true;}
    		            else
    		            	return false;
    		        }    		        
    		    }).followedByAny("second_1").where(new SimpleCondition<Event>() {
    		        @Override
    		        public boolean filter(Event first) throws Exception {
    		            if (first.getEventType().equals(query_information.processing.input_2)) { //B

    		                return true;}
    		            else
    		            	return false;
    		        }    		        
    		    }).where(new IterativeCondition<Event>() { 
			

			
    		        @Override
    		        public boolean filter(Event new_event, Context<Event> ctx) throws Exception { 			    	
			    
			    			        	
    		            if (new_event.getEventType().equals(query_information.processing.input_2)){
					// new_event is second


				Iterable<Event> events = ctx.getEventsForPattern("first_1");
				Event old_event = null;
				for (Event e : events) {
                    			old_event = e;

               			 }

				 LocalDateTime now = LocalDateTime.now();        
      			  	 DateTimeFormatter formatter = DateTimeFormatter.ofPattern("HH:mm:ss.SSS");  
                                 System.out.println("Comparing " + old_event.getID() +" " + new_event.getID()+ " " + now.format(formatter)); 

					
				 // TIMEWINDOW	
				 if (Math.abs(old_event.getHighestTimestamp() - new_event.getLowestTimestamp()) > TIME_WINDOW_SIZE_US ||
                        	 Math.abs(new_event.getHighestTimestamp() - old_event.getLowestTimestamp()) > TIME_WINDOW_SIZE_US)
                   		 return false;


                                 // SELECTIVTIES// ADD REAL PREDICATE CHECKS HERE:	
				 // unpack simple events in complex events, order by timestamp				


				 for (List<String> predicate_constraint : query_information.processing.predicate_constraints) {
					   	
					    String first_eventtype = predicate_constraint.get(0); // from input1
					    String second_eventtype = predicate_constraint.get(1); // from input2

					    SimpleEvent e2 = old_event.getEventOfType(first_eventtype); // Use first_eventtype
					    SimpleEvent e1 = new_event.getEventOfType(second_eventtype); // Use second_eventtype

					    if (e2 == null || e1 == null) {
					    e2 = old_event.getEventOfType(first_eventtype); // Use first_eventtype
					    e1 = new_event.getEventOfType(second_eventtype); // Use second_eventtype
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
					    if (Float.parseFloat(old_event_at.attributeList.get(2)) <= Float.parseFloat(new_event_at.attributeList.get(2))) {
						return false;
					    }
					    if (Float.parseFloat(old_event_at.attributeList.get(7)) <= Float.parseFloat(new_event_at.attributeList.get(7))) {
						return false;
					    }
					    if (Float.parseFloat(old_event_at.attributeList.get(6)) <= Float.parseFloat(new_event_at.attributeList.get(6))) {
						return false;
					    }
					}


					
				 // REAL WORLD

				 for (String id_constraint : query_information.processing.id_constraints) {
				 if (!old_event.getEventIdOf(id_constraint).equals(new_event.getEventIdOf(id_constraint)))
				 return false;
				}
				
				// SEQUENCE CONSTRAINTS
				for (List<String> sequence_constraint : query_information.processing.sequence_constraints) {
				    String first_eventtype = sequence_constraint.get(0);
				    String second_eventtype = sequence_constraint.get(1);

				    // Sequence constraint check (for both directions)
				    if (old_event.getTimestampOf(first_eventtype) != null &&
				            new_event.getTimestampOf(second_eventtype) != null &&
				            old_event.getTimestampOf(first_eventtype) >= new_event.getTimestampOf(second_eventtype)) {
				        return false;
				    }

				    if (new_event.getTimestampOf(first_eventtype) != null &&
				            old_event.getTimestampOf(second_eventtype) != null &&
				            new_event.getTimestampOf(first_eventtype) >=  old_event.getTimestampOf(second_eventtype)){
				        return false;
				    }
				}
					
					return true;}
			    else
				//return false;}}).within(Time.milliseconds(1000000*query_information.processing.time_window_size));		
				return false;}}).within(Time.milliseconds(1000000*query_information.processing.time_window_size));


Pattern<Event,?> seq2 = Pattern.<Event>begin("first_2")
    		    .where(new SimpleCondition<Event>() {
    		        @Override
    		        public boolean filter(Event first) throws Exception {
    		            if (first.getEventType().equals(query_information.processing.input_2)) { //B

    		                return true;}
    		            else
    		            	return false;
    		        }    		        
    		    }).followedByAny("second_2").where(new SimpleCondition<Event>() {
    		        @Override
    		        public boolean filter(Event first) throws Exception {
    		            if (first.getEventType().equals(query_information.processing.input_1)) { //A
    		                return true;}
    		            else
    		            	return false;
    		        }    		        
    		    }).where(new IterativeCondition<Event>() { 
			

    		        @Override
    		        public boolean filter(Event new_event, Context<Event> ctx) throws Exception { 

    		            if (new_event.getEventType().equals(query_information.processing.input_1)){
					// new_event is second
				Iterable<Event> events = ctx.getEventsForPattern("first_2");
				Event old_event = null;
				for (Event e : events) {
                    			old_event = e;

               			}
				LocalDateTime now = LocalDateTime.now();        
      			  	DateTimeFormatter formatter = DateTimeFormatter.ofPattern("HH:mm:ss.SSS");  
                                System.out.println("Comparing " + old_event.getID() +" " + new_event.getID()+ " " + now.format(formatter)); 

				 if (Math.abs(old_event.getHighestTimestamp() - new_event.getLowestTimestamp()) > TIME_WINDOW_SIZE_US ||
                        	 Math.abs(new_event.getHighestTimestamp() - old_event.getLowestTimestamp()) > TIME_WINDOW_SIZE_US)
                   		 return false;

                                 // SELECTIVTIES// ADD REAL WORLD PREDICATE CHECKS HERE:	
				 // (same as sequence consraint checks) iterate over tuples in predicate constraints
				 // for type in tuple, get respective event in primitive events of [old_event, new_event]
				 // determine order of tuple of primitive events, set to old_event_at, new_event_at, then check predicate (<,> at positions)		

				 for (List<String> predicate_constraint : query_information.processing.predicate_constraints) {

					    String first_eventtype = predicate_constraint.get(0); // from input1
					    String second_eventtype = predicate_constraint.get(1); // from input2

					    SimpleEvent e1 = old_event.getEventOfType(second_eventtype); // Use first_eventtype
					    SimpleEvent e2 = new_event.getEventOfType(first_eventtype); // Use second_eventtype

					    if (e2 == null || e1 == null) {
					    e2 = old_event.getEventOfType(first_eventtype); // Use first_eventtype
					    e1 = new_event.getEventOfType(second_eventtype); // Use second_eventtype
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
					    if (Float.parseFloat(old_event_at.attributeList.get(2)) <= Float.parseFloat(new_event_at.attributeList.get(2))) {
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
								
				 for (String id_constraint : query_information.processing.id_constraints) {
				 if (!old_event.getEventIdOf(id_constraint).equals(new_event.getEventIdOf(id_constraint)))
				 return false;
				}

				for (List<String> sequence_constraint : query_information.processing.sequence_constraints) {
				    String first_eventtype = sequence_constraint.get(0);
				    String second_eventtype = sequence_constraint.get(1);

				    // Sequence constraint check (for both directions)
				    if (old_event.getTimestampOf(first_eventtype) != null &&
				            new_event.getTimestampOf(second_eventtype) != null &&
				            old_event.getTimestampOf(first_eventtype) >= new_event.getTimestampOf(second_eventtype)) {
				        return false;
				    }

				    if (new_event.getTimestampOf(first_eventtype) != null &&
				            old_event.getTimestampOf(second_eventtype) != null &&
				            new_event.getTimestampOf(first_eventtype) >=  old_event.getTimestampOf(second_eventtype)){
				        return false;
				    }
				}
					
					return true;}
			    else
				//return false;}}).within(Time.milliseconds(1000000*query_information.processing.time_window_size));
				return false;}}).within(Time.milliseconds(1000000*query_information.processing.time_window_size));


         pattern.add(seq1);
	 pattern.add(seq2);
    	
	return pattern;
    };
}
