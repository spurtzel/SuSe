package com.huberlin;

import com.huberlin.config.QueryInformation;
import com.huberlin.event.Event;
import com.huberlin.event.SimpleEvent;
import org.apache.flink.cep.pattern.Pattern;
import org.apache.flink.cep.pattern.conditions.SimpleCondition;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.function.Predicate;

public class Pattern_SEQ3 {

    static public ArrayList<Pattern<Event, ?>> create(QueryInformation query_information) {
        ArrayList<Pattern<Event, ?>> pattern = new ArrayList<>(2);
        Pattern<Event, ?> SEQ3 = Pattern.<Event>begin("first").where(new SimpleCondition<Event>() {
            @Override
            public boolean filter(Event first) throws Exception {
		System.out.println("Trying first" + first);	
                if (first.getEventType().equals("A")) { //A
		   System.out.println("First" + first);
                    return true;
                } else {
                    return false;
                }
            }
        }).followedByAny("second").where(new SimpleCondition<Event>() {
            @Override
            public boolean filter(Event first) throws Exception {

                if (first.getEventType().equals("B")) { //B
		   System.out.println("Second" + first);	
                    return true;
                } else {
                    return false;
                }
            }
        }).followedByAny("third").where(new SimpleCondition<Event>() {
            @Override
            public boolean filter(Event first) throws Exception {

                if (first.getEventType().equals("C")) { //B
		   System.out.println("Third" + first);	
                    return true;
                } else {
                    return false;
                }
            }
        }).followedByAny("fourth").where(new SimpleCondition<Event>() {
            @Override
            public boolean filter(Event first) throws Exception {
		System.out.println("Trying fourth" + first);	
                if (first.getEventType().equals("D")) { //B
		    System.out.println("Fourth" + first);	
                    return true;
                } else {
                    return false;
                }
            }
        }).within(Time.milliseconds(600000000));

        pattern.add(SEQ3);
        pattern.add(SEQ3);

        return pattern;
    }
}
