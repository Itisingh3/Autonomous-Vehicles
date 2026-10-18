simple CAVApp
{
    parameters:
        string pseudonym = default("PID-CAV-001");
        string rsuId = default("RSU-A");
        int maxClockSkewMs = default(200);
        @display("i=vehicle");
        @signal[cryptoProcessingMs](type=double);
        @signal[v2rSuccess](type=long);
        @signal[v2rFailure](type=long);
        @signal[messageOverheadBytes](type=long);
        @statistic[cryptoProcessingMs](source=cryptoProcessingMs; record=vector,mean,max);
        @statistic[v2rSuccess](source=v2rSuccess; record=vector,count);
        @statistic[v2rFailure](source=v2rFailure; record=vector,count);
        @statistic[messageOverheadBytes](source=messageOverheadBytes; record=vector,sum);
    gates:
        input in;
        output out;
}

simple RSUApp
{
    parameters:
        string rsuId = default("RSU-A");
        int maxClockSkewMs = default(200);
        @display("i=block/wifilans");
        @signal[cryptoProcessingMs](type=double);
        @signal[handshakeLatency](type=simtime_t);
        @signal[v2rSuccess](type=long);
        @signal[v2rFailure](type=long);
        @signal[messageOverheadBytes](type=long);
        @statistic[cryptoProcessingMs](source=cryptoProcessingMs; record=vector,mean,max);
        @statistic[handshakeLatency](source=handshakeLatency; record=vector,mean,max);
        @statistic[v2rSuccess](source=v2rSuccess; record=vector,count);
        @statistic[v2rFailure](source=v2rFailure; record=vector,count);
        @statistic[messageOverheadBytes](source=messageOverheadBytes; record=vector,sum);
    gates:
        input in;
        output out;
}

network CavPqcNetwork
{
    parameters:
        double linkDelay @unit(s) = default(1ms);
        double linkDataRate @unit(bps) = default(6Mbps);
    submodules:
        cav: CAVApp { @display("p=180,180"); }
        rsu: RSUApp { @display("p=420,180"); }
    connections allowunconnected:
        cav.out --> { delay = parent.linkDelay; datarate = parent.linkDataRate; } --> rsu.in;
        rsu.out --> { delay = parent.linkDelay; datarate = parent.linkDataRate; } --> cav.in;
}
