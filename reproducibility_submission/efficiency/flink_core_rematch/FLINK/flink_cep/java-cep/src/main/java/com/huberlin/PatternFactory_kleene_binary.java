package com.huberlin;

import com.huberlin.config.QueryInformation;
import com.huberlin.event.Event;
import org.apache.flink.cep.pattern.Pattern;
import org.apache.flink.cep.pattern.conditions.IterativeCondition;
import org.apache.flink.cep.pattern.conditions.SimpleCondition;
import org.apache.flink.streaming.api.windowing.time.Time;
import com.huberlin.event.SimpleEvent;

import java.util.ArrayList;
import java.util.List;

public class PatternFactory_kleene_binary {

    static public ArrayList<Pattern<Event, ?>> create(QueryInformation queryInformation) {

        ArrayList<Pattern<Event, ?>> pattern = new ArrayList<>(2);
        final long TIME_WINDOW_SIZE_US = queryInformation.processing.time_window_size * 1_000_000;

        // Define a Kleene pattern
        Pattern<Event, ?> kleenePattern = Pattern.<Event>begin("first_1")
                .where(new SimpleCondition<Event>() {
                    @Override
                    public boolean filter(Event first) throws Exception {
                        return first.getEventType().equals(queryInformation.processing.input_1); // Kleene type
                    }
                })
                .where(new IterativeCondition<Event>() {
                    @Override
                    public boolean filter(Event new_event, Context<Event> ctx) throws Exception {
                        for (Event old_event : ctx.getEventsForPattern("first_1")) {

                            for (List<String> predicate_constraint : queryInformation.processing.predicate_constraints) {
                                String first_eventtype = predicate_constraint.get(0); // from input1
                                String second_eventtype = predicate_constraint.get(0); // from input2

                                SimpleEvent e1 = old_event.getEventOfType(first_eventtype); // Use first_eventtype
                                SimpleEvent e2 = new_event.getEventOfType(second_eventtype); // Use second_eventtype

                                SimpleEvent old_event_at = null;
                                SimpleEvent new_event_at = null;

                                try {
                                    if (e1.timestamp < e2.timestamp) {
                                        old_event_at = e1;
                                        new_event_at = e2;
                                    }
                                    if (e2.timestamp < e1.timestamp) {
                                        old_event_at = e2;
                                        new_event_at = e1;
                                    }
                                } catch (NullPointerException e) {
                                    if (e1 == null)
                                        System.out.println("Returned null from .getEventOfType(" + first_eventtype + ") with event " + old_event);
                                    if (e2 == null)
                                        System.out.println("Returned null from .getEventofType(" + first_eventtype + ") with event " + new_event);
                                    throw e;
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

                            // Check for other constraints (e.g., id_constraints)
                            for (String idConstraint : queryInformation.processing.id_constraints) {
                                if (!old_event.getEventIdOf(idConstraint).equals(new_event.getEventIdOf(idConstraint))) {
                                    return false;
                                }
                            }
                        }
                        return true;
                    }
                })
                .oneOrMore()
                .within(Time.milliseconds(1000000 * queryInformation.processing.time_window_size));

        // Define Kleene1 pattern
        Pattern<Event, ?> kleene1 = kleenePattern
                .allowCombinations()
                .followedByAny("second_1")
                .where(new SimpleCondition<Event>() {
                    @Override
                    public boolean filter(Event first) throws Exception {
                        return first.getEventType().equals(queryInformation.processing.input_2); // Non-Kleene input
                    }
                })
                .where(new IterativeCondition<Event>() {
                    @Override
                    public boolean filter(Event new_event, Context<Event> ctx) throws Exception {
                        // New event is of type second_1
                        Iterable<Event> events = ctx.getEventsForPattern("first_1");
                        Event oldEvent = null;
                        for (Event e : events) {
                            oldEvent = e;
                        }

                        for (List<String> predicate_constraint : queryInformation.processing.predicate_constraints) {
                            String first_eventtype = predicate_constraint.get(0); // from input1
                            String second_eventtype = predicate_constraint.get(1); // from input2

                            SimpleEvent e1 = oldEvent.getEventOfType(first_eventtype); // Use first_eventtype
                            SimpleEvent e2 = new_event.getEventOfType(second_eventtype); // Use second_eventtype

                            if (e1 == null || e2 == null) {
                                e1 = oldEvent.getEventOfType(second_eventtype); // Use first_eventtype
                                e2 = new_event.getEventOfType(first_eventtype); // Use second_eventtype
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

                            // Check attributes based on attribute indices (7 for mem_request, 4 for priority, 6 for cpu_request)
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
                        return true;
                    }
                })
                .within(Time.milliseconds(1000000 * queryInformation.processing.time_window_size)); // Time window

        // Define Kleene2 pattern
        Pattern<Event, ?> kleene2 = Pattern.<Event>begin("first_2")
                .where(new SimpleCondition<Event>() {
                    @Override
                    public boolean filter(Event first) throws Exception {
                        return first.getEventType().equals(queryInformation.processing.input_2); // Non-Kleene input
                    }
                })
                .followedByAny("second_2")
                .where(new SimpleCondition<Event>() {
                    @Override
                    public boolean filter(Event first) throws Exception {
                        return first.getEventType().equals(queryInformation.processing.input_1); // Kleene type
                    }
                })
                .where(new IterativeCondition<Event>() {
                    @Override
                    public boolean filter(Event new_event, Context<Event> ctx) throws Exception {
                        for (Event old_event : ctx.getEventsForPattern("first_2")) {
                            for (List<String> predicate_constraint : queryInformation.processing.predicate_constraints) {
                                String first_eventtype = predicate_constraint.get(1); // from input1
                                String second_eventtype = predicate_constraint.get(0); // from input2

                                SimpleEvent e1 = old_event.getEventOfType(first_eventtype); // Use first_eventtype
                                SimpleEvent e2 = new_event.getEventOfType(second_eventtype); // Use second_eventtype

                                if (e1 == null || e2 == null) {
                                    e1 = old_event.getEventOfType(second_eventtype); // Use first_eventtype
                                    e2 = new_event.getEventOfType(first_eventtype); // Use second_eventtype
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
                                if (Float.parseFloat(old_event_at.attributeList.get(7)) <= Float.parseFloat(new_event_at.attributeList.get(7))) {
                                    return false;
                                }
                                if (Float.parseFloat(old_event_at.attributeList.get(6)) <= Float.parseFloat(new_event_at.attributeList.get(6))) {
                                    return false;
                                }
                            }

                        }
                        return true;
                    }
                })
                .oneOrMore()
                .allowCombinations()
                .within(Time.milliseconds(60000000)); // Time window

        pattern.add(kleene1);
        pattern.add(kleene2);

        return pattern;
    }
}

