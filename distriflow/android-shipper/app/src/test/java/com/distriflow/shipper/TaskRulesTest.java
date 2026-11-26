package com.distriflow.shipper;
import com.distriflow.shipper.data.TaskRules;
import org.junit.Test;
import java.util.List;
import java.util.Set;
import static org.junit.Assert.*;

public class TaskRulesTest {
    @Test public void needsArrival(){assertFalse(TaskRules.canScan("ready_for_handover",true,false));}
    @Test public void needsAcceptance(){assertFalse(TaskRules.canScan("ready_for_handover",false,true));}
    @Test public void allPackagesMustMatch(){assertTrue(TaskRules.canConfirm("ready_for_handover",true,true,List.of("P1","P2"),Set.of("P1","P2")));}
    @Test public void sameCountWrongCodeDoesNotPass(){assertFalse(TaskRules.canConfirm("ready_for_handover",true,true,List.of("P1","P2"),Set.of("P1","WRONG")));}
    @Test public void emptyPackagesNeverConfirm(){assertFalse(TaskRules.canConfirm("ready_for_handover",true,true,List.of(),Set.of()));}
    @Test public void completedCannotScan(){assertFalse(TaskRules.canScan("handed_over",true,true));}
}
