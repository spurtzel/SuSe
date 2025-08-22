package com.huberlin.util;

public final class ThroughputLogger {
    private long countEventsProcessed = 0;
    private final Thread my_therad = new Thread(this::run);

    synchronized public void incrementEventCount(){
        countEventsProcessed++;
    }

    public void run() {
        long previousCountEventsProcessed = 0;
        long secondsPassed = 0;
        while (true) {
            try {
                Thread.sleep(1000);
            } catch (InterruptedException ex) {
                Thread.currentThread().interrupt();
            }
            //log throughput
            System.out.println(++secondsPassed + "seconds have passed; Throughput per second:" + (countEventsProcessed - previousCountEventsProcessed));
            previousCountEventsProcessed = countEventsProcessed;
        }
    }

    public void start(){
        my_therad.start();
    }
}
