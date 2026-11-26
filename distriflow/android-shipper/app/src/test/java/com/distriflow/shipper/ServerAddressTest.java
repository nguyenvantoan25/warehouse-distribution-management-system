package com.distriflow.shipper;
import com.distriflow.shipper.config.ServerAddress;
import org.junit.Test;
import static org.junit.Assert.*;

public class ServerAddressTest {
    @Test public void normalizesApiSuffix(){assertEquals("https://logistics.example",ServerAddress.normalize("https://logistics.example/api/v1/",false));}
    @Test public void debugAllowsEmulator(){assertEquals("http://10.0.2.2:8000",ServerAddress.normalize("http://10.0.2.2:8000",true));}
    @Test public void debugAllowsUsbReverse(){assertEquals("http://127.0.0.1:8000",ServerAddress.normalize("http://127.0.0.1:8000/",true));}
    @Test(expected=IllegalArgumentException.class) public void releaseRejectsHttp(){ServerAddress.normalize("http://192.168.1.5:8000",false);}
    @Test(expected=IllegalArgumentException.class) public void rejectsPublicHttp(){ServerAddress.normalize("http://8.8.8.8",true);}
    @Test(expected=IllegalArgumentException.class) public void rejectsUrlCredentials(){ServerAddress.normalize("https://admin:password@logistics.example",false);}
    @Test(expected=IllegalArgumentException.class) public void rejectsQuery(){ServerAddress.normalize("https://logistics.example?token=secret",false);}
    @Test(expected=IllegalArgumentException.class) public void rejectsUnexpectedPath(){ServerAddress.normalize("https://logistics.example/admin",false);}
    @Test public void rejectsInvalidPrivateAddress(){assertFalse(ServerAddress.isPrivateHost("192.168.999.1"));assertFalse(ServerAddress.isPrivateHost("172.32.0.1"));assertFalse(ServerAddress.isPrivateHost("010.0.0.1"));}
}
