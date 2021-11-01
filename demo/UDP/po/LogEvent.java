package com.example.jmh.nettytest.udp.po;

import java.net.InetSocketAddress;

/**
 * @auther liuhe
 * @className LogEvent
 * @description TODO
 * @date 2021/4/28 1:26 下午
 */
public class LogEvent {

    public static final byte SEPARATOR = (byte) ':';
    private final InetSocketAddress source;
    private final String logFile;
    private final String msg;
    private final long received;

    /**
     * 使用于发送消息
     */
    public LogEvent(String logFile, String msg) {
        this(null, logFile, msg, -1);
    }

    /**
     * 适用于接收消息
     */
    public LogEvent(InetSocketAddress source, String logFile, String msg, long received) {
        this.source = source;
        this.logFile = logFile;
        this.msg = msg;
        this.received = received;
    }

    public InetSocketAddress getSource() {
        return source;
    }

    public String getLogFile() {
        return logFile;
    }

    public String getMsg() {
        return msg;
    }

    public long getReceived() {
        return received;
    }
}
