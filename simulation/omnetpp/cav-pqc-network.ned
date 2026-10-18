import org.car2x.veins.modules.application.ieee80211p.DemoBaseApplLayer;
import org.car2x.veins.nodes.RSU;
import org.car2x.veins.nodes.Scenario;
import org.car2x.veins.nodes.Car;
import org.car2x.veins.base.modules.BaseWorldUtility;
import org.car2x.veins.base.connectionManager.ConnectionManager;
import org.car2x.veins.modules.mobility.LinearMobility;
import org.car2x.veins.modules.obstacle.ObstacleControl;

simple CAVApp extends DemoBaseApplLayer {
    parameters:
        string pseudonym = default("cav-001");
        string targetRsu = default("rsu-001");
        string nextRsu = default("rsu-002");
        int numRsus = default(5);
        double startAt @unit(s) = default(1s);
        double maxClockSkew @unit(s) = default(200ms);
        string kemAlgorithm = default("ML-KEM-768");
        string signatureAlgorithm = default("ML-DSA-65");
        @class(cavpqc::CAVApp);
}

simple RSUApp extends DemoBaseApplLayer {
    parameters:
        string rsuId = default("rsu-001");
        string nextRsu = default("");
        double tokenValidity @unit(s) = default(5s);
        double vehicleSpeedKmph = default(50);
        double vehicleHeadingDeg = default(0);
        double rsuSpacingMeters = default(400);
        double maxClockSkew @unit(s) = default(200ms);
        string kemAlgorithm = default("ML-KEM-768");
        string signatureAlgorithm = default("ML-DSA-65");
        @class(cavpqc::RSUApp);
}

network CavPqcNetwork extends Scenario {
    submodules:
        rsu[5]: RSU {
            parameters:
                applType = "RSUApp";
                appl.rsuId = "rsu-001";
                appl.nextRsu = "rsu-002";
                @display("p=150,140;i=veins/sign/yellowdiamond;is=vs");
        }
}

// Deterministic V2R validation topology. It exercises the same 802.11p,
// application, and liboqs paths without depending on a SUMO/TraCI release.
network CavPqcUnitNetwork {
    parameters:
        @display("bgb=1000,1000");
    submodules:
        world: BaseWorldUtility {
            parameters:
                playgroundSizeX = 1500m;
                playgroundSizeY = 1000m;
                playgroundSizeZ = 50m;
        }
        connectionManager: ConnectionManager {
            parameters:
                sendDirect = true;
                maxInterfDist = 1600m;
        }
        obstacles: ObstacleControl {
        }
        cav[1]: Car {
            parameters:
                applType = "CAVApp";
                veinsmobilityType = "LinearMobility";
                veinsmobility.x = 100;
                veinsmobility.y = 100;
                veinsmobility.z = 1.5;
                veinsmobility.speed = 0mps;
                veinsmobility.angle = 0deg;
                veinsmobility.acceleration = 0mpss;
                veinsmobility.updateInterval = 1s;
        }
        rsu[5]: RSU {
            parameters:
                applType = "RSUApp";
                mobility.x = 150;
                mobility.y = 100;
                mobility.z = 3;
        }
    connections allowunconnected:
}
