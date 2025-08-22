package com.huberlin.util;

import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketException;
import java.net.UnknownHostException;

public final class Functions {
    /**
     * Determine the IP address of the network interface on the route towards 8.8.8.8.
     *
     * @return
     * @throws SocketException
     * @throws UnknownHostException
     */
    public static String findOwnIp() throws SocketException, UnknownHostException {
        try (final DatagramSocket socket = new DatagramSocket()) {
            socket.connect(InetAddress.getByName("8.8.8.8"), 80);
            return socket.getLocalAddress().getHostAddress();
        } catch (Exception e) {
            System.err.println("Failed to find own IP.");
            e.printStackTrace();
            throw e;
        }
    }
}